#ifndef DNNREADER
#define DNNREADER

// Evaluate the frozen SSWW polarisation networks inside the generated C++.
//
// The DNN project (sibling repository `DNN/`) trains the models and freezes
// each one with `scripts/export_dnn_reader.py` into a plain-text file holding
// the fitted preprocessing, the dense layers of every cross-fit fold and one
// monotone table per observable cell. Everything below is a matrix-vector loop
// over that file: no torch, no onnxruntime, no SOFIE, nothing to put on the
// link line and nothing to ship to the batch node beyond the weights.
//
// The file format is documented by the exporter. In outline:
//
//   DNNREADER 1 / KIND <multiclass|twostage> / FEATURES n <names>
//   NSTAGES s
//     STAGE i <n_classes> <n_models> / NAMES ... then per model
//       MODEL <n_layers> <n_indicators> / INDICATORS ...
//       MEDIAN n ... / MEAN n ... / SCALE n ...
//       LAYER <n_in> <n_out> <gelu|linear> / W n ... / B n ...
//   CELLS k [CELLEDGES <category> n ...]  then per cell
//     CDF <k> n / <x nodes> / <F nodes>
//   END
//
// One event's inputs arrive as a single RVec<float> in the exact order of the
// FEATURES list, which is what the `dnn_inputs` alias builds, so the two
// models share one input vector and cannot be fed in different orders. The
// second argument is the event number, which the FOLDRULE uses.
//
// FOLDRULE says how the cross-fit fold models combine:
//
//   ensemble  the mean of all of them. The only thing a batch job can do when
//             the training folds came from a StratifiedKFold over a table it
//             cannot see, and the right thing for data and for anything the
//             networks never trained on -- but simulation they DID train on
//             is then scored partly in sample and its templates are
//             optimistically sharp.
//   parity    model `event % n_models` alone. A batch job can reproduce that,
//             so every simulated event is scored out of sample -- valid only
//             for a training that held its folds out the same way.
//
// The output is an RVec<float> laid out as
//
//   [ probabilities of every stage, in order | axis | cell | unrolled ]
//
// `axis` is the continuous quantity being binned -- the winning probability
// for a multiclass file, the stage-1 signal probability for a two-stage one.
// `cell` is the categorical part: the argmax for a multiclass file, and
// `argmax(stage 2) * b_bins + sub-bin of the winning probability` for a
// two-stage one. `unrolled` is `cell + F_cell(axis)`, with F the empirical
// CDF of the reference population frozen in the file.
//
// That last column is the one to histogram. Because F is the reference CDF,
// `n` *uniform* bins of `unrolled` inside one cell are exactly the `n`
// quantile bins of that cell, so a `(cells * n, 0, cells)` range in
// variables.py chooses the bin count without re-deriving a quantile rule next
// to the histogram. Only multiples of the cell count are meaningful: a bin
// that straddles two cells mixes two categories.
//
// Absent inputs are not a special case for the caller. A value that is not
// finite, or that equals one of the training sentinels -9999, -1 or -99, is
// replaced by the training-fold median and flagged in an indicator input,
// exactly as the python preprocessing does it -- which is why a missing third
// jet or an undefined angle must be passed through as its sentinel rather
// than patched in the alias.

#include <algorithm>
#include <cmath>
#include <fstream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>

#include "ROOT/RVec.hxx"
#include "TFile.h"
#include "TObjString.h"

class dnn_reader {
 public:
  explicit dnn_reader(const std::string& path) {
    auto held = std::make_shared<payload>();
    std::istringstream buffer(slurp(path));
    load(buffer, path, *held);
    d_ = held;
  }

  // `event` selects the fold model under the `parity` rule and is ignored
  // under `ensemble`. It is taken even when unused so that switching a model
  // from one rule to the other is a re-export and not an aliases.py change.
  ROOT::VecOps::RVec<float> operator()(const ROOT::VecOps::RVec<float>& inputs,
                                       unsigned long long event) const {
    const payload& p = *d_;
    if (static_cast<std::size_t>(inputs.size()) != p.features.size())
      throw std::runtime_error("dnn_reader: " + p.path + " wants " +
                               std::to_string(p.features.size()) + " inputs, got " +
                               std::to_string(inputs.size()));

    // One absence mask for the whole event: every fold model shares the
    // sentinel convention and differs only in what it imputes.
    std::vector<unsigned char> absent(inputs.size());
    for (std::size_t i = 0; i < absent.size(); ++i) {
      const float v = inputs[i];
      absent[i] = (!std::isfinite(v) || v == -9999.f || v == -1.f || v == -99.f);
    }

    ROOT::VecOps::RVec<float> out(p.n_probabilities + 3, 0.f);
    std::size_t offset = 0;
    for (const stage& s : p.stages) {
      std::vector<double> mean(s.names.size(), 0.0);
      if (p.parity) {
        // One model, the one whose held-out fold this event is in. The whole
        // point of the rule is that both the training and the batch job can
        // compute that from the event number alone, so the deployed column is
        // out of sample for every simulated event rather than only for the
        // ones the networks never saw.
        mean = evaluate(s.models[event % s.models.size()], inputs, absent);
      } else {
        for (const model& m : s.models) {
          const std::vector<double> q = evaluate(m, inputs, absent);
          for (std::size_t c = 0; c < q.size(); ++c) mean[c] += q[c] / s.models.size();
        }
      }
      for (std::size_t c = 0; c < mean.size(); ++c)
        out[offset + c] = static_cast<float>(mean[c]);
      offset += mean.size();
    }

    // Which stage carries the axis and which the category is the one thing
    // that differs between the two kinds of file.
    const stage& categorical = p.stages.back();
    const std::size_t cat_begin = p.n_probabilities - categorical.names.size();
    std::size_t argmax = 0;
    for (std::size_t c = 1; c < categorical.names.size(); ++c)
      if (out[cat_begin + c] > out[cat_begin + argmax]) argmax = c;
    const double winning = out[cat_begin + argmax];

    double axis = winning;
    std::size_t cell = argmax;
    if (p.two_stage) {
      // The stage-1 signal probability: everything that is not background.
      const stage& first = p.stages.front();
      axis = 0.0;
      for (std::size_t c = 0; c < first.names.size(); ++c)
        if (first.names[c] != "background") axis += out[c];
      const std::vector<double>& edges = p.cell_edges[argmax];
      std::size_t sub = 0;
      while (sub < edges.size() && winning >= edges[sub]) ++sub;
      cell = argmax * (edges.size() + 1) + sub;
    }
    if (cell >= p.cdf.size())
      throw std::runtime_error("dnn_reader: cell out of range in " + p.path);

    out[p.n_probabilities + 0] = static_cast<float>(axis);
    out[p.n_probabilities + 1] = static_cast<float>(cell);
    out[p.n_probabilities + 2] =
        static_cast<float>(cell + interpolate(p.cdf[cell], axis));
    return out;
  }

  //! Output index of the first probability of stage `i`, for the aliases.
  std::size_t probability_offset(std::size_t i) const {
    std::size_t offset = 0;
    for (std::size_t s = 0; s < i && s < d_->stages.size(); ++s)
      offset += d_->stages[s].names.size();
    return offset;
  }
  std::size_t n_cells() const { return d_->cdf.size(); }
  const std::string& fold_rule() const { return d_->fold_rule; }
  std::size_t size() const { return d_->n_probabilities + 3; }

 private:
  struct layer {
    std::size_t n_in = 0, n_out = 0;
    bool gelu = false;
    std::vector<double> w, b;   // w is row-major, n_out rows of n_in
  };
  struct model {
    std::vector<double> median, mean, scale;
    std::vector<int> indicators;
    std::vector<layer> layers;
  };
  struct stage {
    std::vector<std::string> names;
    std::vector<model> models;
  };
  struct table {
    std::vector<double> x, f;
  };

  static constexpr double kInvSqrt2 = 0.70710678118654752440;
  //! The CDF is capped just below 1 so that an event at the very top of a
  //! cell's score range stays in that cell's last bin instead of spilling
  //! into the next category. The exporter caps it identically.
  static constexpr double kMaxCdf = 1.0 - 1e-6;
  struct payload {
    std::string path, kind, fold_rule;
    bool two_stage = false;
    bool parity = false;
    std::vector<std::string> features;
    std::vector<stage> stages;
    std::vector<std::vector<double>> cell_edges;
    std::vector<table> cdf;
    std::size_t n_probabilities = 0;
  };

  // `Define` takes the callable by value, so the reader has to stay copyable:
  // the weights live behind a shared_ptr and no destructor is declared.
  std::shared_ptr<const payload> d_;

  static std::string slurp(const std::string& path) {
    // A .root wrapper exists so the weights can sit on EOS and be reached
    // through xrootd from a batch node, the way the fake-rate and b-tag maps
    // already are. A bare path is read directly, which is what a local run or
    // an eosfuse mount wants.
    if (path.size() > 5 && path.compare(path.size() - 5, 5, ".root") == 0) {
      std::unique_ptr<TFile> f(TFile::Open(path.c_str()));
      if (!f || f->IsZombie())
        throw std::runtime_error("dnn_reader: cannot open " + path);
      auto* s = dynamic_cast<TObjString*>(f->Get("weights"));
      if (!s)
        throw std::runtime_error("dnn_reader: " + path + " holds no TObjString 'weights'");
      return std::string(s->GetString().Data());
    }
    std::ifstream in(path);
    if (!in)
      throw std::runtime_error("dnn_reader: cannot open " + path);
    std::ostringstream all;
    all << in.rdbuf();
    return all.str();
  }

  static void expect(std::istream& in, const std::string& keyword,
                     const std::string& path) {
    std::string token;
    if (!(in >> token) || token != keyword)
      throw std::runtime_error("dnn_reader: " + path + ": expected '" + keyword +
                               "', found '" + token + "'");
  }

  template <typename T>
  static std::vector<T> read_block(std::istream& in, const std::string& keyword,
                                   const std::string& path, long expected = -1) {
    expect(in, keyword, path);
    long n = 0;
    in >> n;
    if (expected >= 0 && n != expected)
      throw std::runtime_error("dnn_reader: " + path + ": " + keyword + " has " +
                               std::to_string(n) + " entries, expected " +
                               std::to_string(expected));
    std::vector<T> v(static_cast<std::size_t>(n));
    for (long i = 0; i < n; ++i) in >> v[static_cast<std::size_t>(i)];
    if (!in)
      throw std::runtime_error("dnn_reader: " + path + ": truncated " + keyword);
    return v;
  }

  static void load(std::istream& in, const std::string& path, payload& p) {
    p.path = path;
    expect(in, "DNNREADER", path);
    int version = 0;
    in >> version;
    if (version != 1 && version != 2)
      throw std::runtime_error("dnn_reader: " + path + ": unsupported format version " +
                               std::to_string(version));
    expect(in, "KIND", path);
    in >> p.kind;
    // Version 1 predates the fold rule and is always an ensemble.
    p.fold_rule = "ensemble";
    if (version >= 2) {
      expect(in, "FOLDRULE", path);
      in >> p.fold_rule;
      if (p.fold_rule != "ensemble" && p.fold_rule != "parity")
        throw std::runtime_error("dnn_reader: " + path + ": unknown fold rule " +
                                 p.fold_rule);
    }
    p.parity = (p.fold_rule == "parity");
    p.two_stage = (p.kind == "twostage");
    if (!p.two_stage && p.kind != "multiclass")
      throw std::runtime_error("dnn_reader: " + path + ": unknown kind " + p.kind);

    expect(in, "FEATURES", path);
    long n_features = 0;
    in >> n_features;
    p.features.resize(static_cast<std::size_t>(n_features));
    for (auto& name : p.features) in >> name;

    expect(in, "NSTAGES", path);
    long n_stages = 0;
    in >> n_stages;
    for (long s = 0; s < n_stages; ++s) {
      expect(in, "STAGE", path);
      long index = 0, n_classes = 0, n_models = 0;
      in >> index >> n_classes >> n_models;
      if (index != s)
        throw std::runtime_error("dnn_reader: " + path + ": stages out of order");
      stage st;
      expect(in, "NAMES", path);
      st.names.resize(static_cast<std::size_t>(n_classes));
      for (auto& name : st.names) in >> name;
      for (long k = 0; k < n_models; ++k) {
        expect(in, "MODEL", path);
        long n_layers = 0, n_indicators = 0;
        in >> n_layers >> n_indicators;
        model m;
        m.indicators = read_block<int>(in, "INDICATORS", path, n_indicators);
        m.median = read_block<double>(in, "MEDIAN", path, n_features);
        m.mean = read_block<double>(in, "MEAN", path, n_features);
        m.scale = read_block<double>(in, "SCALE", path, n_features);
        for (long l = 0; l < n_layers; ++l) {
          expect(in, "LAYER", path);
          std::string activation;
          layer lay;
          long n_in = 0, n_out = 0;
          in >> n_in >> n_out >> activation;
          lay.n_in = static_cast<std::size_t>(n_in);
          lay.n_out = static_cast<std::size_t>(n_out);
          lay.gelu = (activation == "gelu");
          if (!lay.gelu && activation != "linear")
            throw std::runtime_error("dnn_reader: " + path +
                                     ": unknown activation " + activation);
          lay.w = read_block<double>(in, "W", path, n_in * n_out);
          lay.b = read_block<double>(in, "B", path, n_out);
          m.layers.push_back(std::move(lay));
        }
        if (m.layers.empty())
          throw std::runtime_error("dnn_reader: " + path + ": a model has no layers");
        if (m.layers.front().n_in != m.median.size() + m.indicators.size())
          throw std::runtime_error("dnn_reader: " + path +
                                   ": first layer width does not match the preprocessing");
        if (m.layers.back().n_out != st.names.size())
          throw std::runtime_error("dnn_reader: " + path +
                                   ": head width does not match the class list");
        for (int i : m.indicators)
          if (i < 0 || static_cast<std::size_t>(i) >= m.median.size())
            throw std::runtime_error("dnn_reader: " + path + ": indicator out of range");
        st.models.push_back(std::move(m));
      }
      if (st.models.empty())
        throw std::runtime_error("dnn_reader: " + path + ": a stage has no models");
      p.n_probabilities += st.names.size();
      p.stages.push_back(std::move(st));
    }

    expect(in, "CELLS", path);
    long n_cells = 0;
    in >> n_cells;
    p.cell_edges.assign(p.stages.back().names.size(), {});
    std::string token;
    while (in >> token && token == "CELLEDGES") {
      long category = 0, n = 0;
      in >> category >> n;
      if (category < 0 ||
          static_cast<std::size_t>(category) >= p.cell_edges.size())
        throw std::runtime_error("dnn_reader: " + path + ": CELLEDGES category out of range");
      std::vector<double> edges(static_cast<std::size_t>(n));
      for (auto& e : edges) in >> e;
      p.cell_edges[static_cast<std::size_t>(category)] = std::move(edges);
    }
    p.cdf.resize(static_cast<std::size_t>(n_cells));
    for (long k = 0; k < n_cells; ++k) {
      if (token != "CDF")
        throw std::runtime_error("dnn_reader: " + path + ": expected 'CDF', found '" +
                                 token + "'");
      long index = 0, n = 0;
      in >> index >> n;
      if (index != k)
        throw std::runtime_error("dnn_reader: " + path + ": CDF tables out of order");
      table t;
      t.x.resize(static_cast<std::size_t>(n));
      t.f.resize(static_cast<std::size_t>(n));
      for (auto& v : t.x) in >> v;
      for (auto& v : t.f) in >> v;
      if (!in)
        throw std::runtime_error("dnn_reader: " + path + ": truncated CDF table");
      p.cdf[static_cast<std::size_t>(k)] = std::move(t);
      if (k + 1 < n_cells) in >> token;
    }
    expect(in, "END", path);

    // A two-stage file must have one cell per category per sub-bin, and a
    // multiclass one exactly one cell per category. Checking it here turns a
    // mismatched export into a job that refuses to start.
    const std::size_t categories = p.stages.back().names.size();
    if (p.two_stage) {
      const std::size_t sub = p.cell_edges.front().size() + 1;
      for (const auto& e : p.cell_edges)
        if (e.size() + 1 != sub)
          throw std::runtime_error("dnn_reader: " + path +
                                   ": categories have different sub-bin counts");
      if (p.cdf.size() != categories * sub)
        throw std::runtime_error("dnn_reader: " + path + ": CELLS does not match "
                                 "categories times sub-bins");
    } else if (p.cdf.size() != categories) {
      throw std::runtime_error("dnn_reader: " + path +
                               ": a multiclass file needs one cell per category");
    }
  }

  static std::vector<double> evaluate(const model& m,
                                      const ROOT::VecOps::RVec<float>& inputs,
                                      const std::vector<unsigned char>& absent) {
    std::vector<double> x(m.layers.front().n_in);
    for (std::size_t i = 0; i < m.median.size(); ++i) {
      const double v = absent[i] ? m.median[i] : static_cast<double>(inputs[i]);
      x[i] = (v - m.mean[i]) / m.scale[i];
    }
    for (std::size_t k = 0; k < m.indicators.size(); ++k)
      x[m.median.size() + k] = absent[static_cast<std::size_t>(m.indicators[k])] ? 1.0 : 0.0;

    std::vector<double> y;
    for (const layer& l : m.layers) {
      y.assign(l.n_out, 0.0);
      for (std::size_t r = 0; r < l.n_out; ++r) {
        const double* row = l.w.data() + r * l.n_in;
        double sum = l.b[r];
        for (std::size_t c = 0; c < l.n_in; ++c) sum += row[c] * x[c];
        // The exact erf form, which is torch's nn.GELU default. The tanh
        // approximation differs in the fourth decimal and would move events
        // across bin boundaries for no reason.
        y[r] = l.gelu ? 0.5 * sum * (1.0 + std::erf(sum * kInvSqrt2)) : sum;
      }
      x.swap(y);
    }
    const double top = *std::max_element(x.begin(), x.end());
    double norm = 0.0;
    for (double& v : x) {
      v = std::exp(v - top);
      norm += v;
    }
    for (double& v : x) v /= norm;
    return x;
  }

  static double interpolate(const table& t, double value) {
    if (t.x.size() < 2) return 0.0;
    if (value <= t.x.front()) return t.f.front();
    if (value >= t.x.back()) return std::min(t.f.back(), kMaxCdf);
    const auto it = std::upper_bound(t.x.begin(), t.x.end(), value);
    const std::size_t hi = static_cast<std::size_t>(it - t.x.begin());
    const std::size_t lo = hi - 1;
    const double span = t.x[hi] - t.x[lo];
    const double w = span > 0.0 ? (value - t.x[lo]) / span : 0.0;
    return std::min(t.f[lo] + w * (t.f[hi] - t.f[lo]), kMaxCdf);
  }
};

static_assert(std::is_copy_constructible_v<dnn_reader>,
              "RDataFrame::Define takes the callable by value");

#endif
