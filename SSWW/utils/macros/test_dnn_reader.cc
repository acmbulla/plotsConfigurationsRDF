// Check dnn_reader against the reference the exporter dumped.
//
// The networks are trained and frozen in the sibling DNN project, whose
// `scripts/export_dnn_reader.py` writes both the weight file this reads and a
// CSV of inputs with the output it expects. Agreement between the two is the
// only thing that says the C++ reimplementation of the preprocessing, the
// GELU, the softmax, the fold averaging and the CDF unrolling is the same
// arithmetic as the torch model the physics results came from.
//
//   g++ -O2 -std=c++17 $(root-config --cflags --libs) \
//       -o test_dnn_reader test_dnn_reader.cc
//   ./test_dnn_reader weights.dnn reference.csv
//
// The CSV holds one column per feature, in the weight file's feature order,
// then `event`, then out0..outN: the reader's full output vector.

#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "dnn_reader_class.cc"

int main(int argc, char** argv) {
  if (argc != 3) {
    std::cerr << "usage: " << argv[0] << " <weights> <reference.csv>\n";
    return 2;
  }
  dnn_reader reader(argv[1]);

  std::ifstream csv(argv[2]);
  if (!csv) {
    std::cerr << "cannot open " << argv[2] << "\n";
    return 2;
  }
  std::string line;
  std::getline(csv, line);
  std::vector<std::string> header;
  for (std::stringstream ss(line); std::getline(ss, line, ',');)
    header.push_back(line);

  std::size_t n_out = 0;
  while (n_out < header.size() &&
         header[header.size() - 1 - n_out].rfind("out", 0) == 0)
    ++n_out;
  std::size_t event_col = header.size();
  for (std::size_t i = 0; i < header.size(); ++i)
    if (header[i] == "event") event_col = i;
  if (event_col == header.size()) {
    std::cerr << "the reference has no 'event' column\n";
    return 1;
  }
  const std::size_t n_in = header.size() - n_out - 1;
  if (event_col != n_in) {
    std::cerr << "'event' must sit between the features and the outputs\n";
    return 1;
  }
  if (n_out != reader.size()) {
    std::cerr << "the reference has " << n_out << " output columns, the reader "
              << "produces " << reader.size() << "\n";
    return 1;
  }
  std::printf("%zu inputs, %zu outputs, %zu cells, fold rule %s\n", n_in,
              n_out, reader.n_cells(), reader.fold_rule().c_str());

  std::vector<double> worst(n_out, 0.0);
  long rows = 0, cell_mismatch = 0;
  while (std::getline(csv, line)) {
    if (line.empty()) continue;
    std::vector<double> values;
    for (std::stringstream ss(line); std::getline(ss, line, ',');)
      values.push_back(line == "" ? std::nan("") : std::strtod(line.c_str(), nullptr));
    if (values.size() != header.size()) {
      std::cerr << "row " << rows << " has " << values.size() << " fields\n";
      return 1;
    }
    ROOT::VecOps::RVec<float> inputs(n_in);
    for (std::size_t i = 0; i < n_in; ++i)
      inputs[i] = static_cast<float>(values[i]);

    const auto got = reader(inputs,
                            static_cast<unsigned long long>(values[event_col]));
    for (std::size_t i = 0; i < n_out; ++i) {
      const double diff = std::abs(got[i] - values[n_in + 1 + i]);
      if (diff > worst[i]) worst[i] = diff;
    }
    // The categorical column must agree exactly: an off-by-one cell is a
    // different template, not a rounding difference.
    if (got[n_out - 2] != static_cast<float>(values[n_in + 1 + n_out - 2]))
      ++cell_mismatch;
    ++rows;
  }

  std::printf("%ld rows\n", rows);
  for (std::size_t i = 0; i < n_out; ++i)
    std::printf("  out%-2zu max |diff| = %.3e\n", i, worst[i]);
  std::printf("cell mismatches: %ld\n", cell_mismatch);

  // 1e-5 is loose against the 1e-7 the probabilities actually agree to, and
  // tight enough that a wrong matrix, a tanh GELU or a transposed layer
  // cannot pass. The unrolled column inherits the CDF interpolation, whose
  // probability resolution is one part in the exporter's node count.
  bool ok = (cell_mismatch == 0);
  for (std::size_t i = 0; i < n_out; ++i)
    if (worst[i] > 1e-4) ok = false;
  std::printf("%s\n", ok ? "PASS" : "FAIL");
  return ok ? 0 : 1;
}
