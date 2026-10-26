/*
  Per-event fake-rate reader for the region-split maps written by
  SSWW/2024/FakesNum/measureFakeRate.py.

  That script writes, per working point, under <base>/<year>/<WP>/ :

    EleFR_1l_<bcat>.root        MuonFR_1l_<bcat>.root
    EleFR_ee_lep0_<bcat>.root   MuonFR_mumu_lep0_<bcat>.root
    EleFR_ee_lep1_<bcat>.root   MuonFR_mumu_lep1_<bcat>.root
    EleFR_emu_lep0_<bcat>.root  MuonFR_emu_lep0_<bcat>.root
    EleFR_emu_lep1_<bcat>.root  MuonFR_emu_lep1_<bcat>.root
    ElePR_ee_lep0.root          MuonPR_mumu_lep0.root
    ElePR_ee_lep1.root          MuonPR_mumu_lep1.root

  with <bcat> in {incl, bveto, btag}. The fake rate is split by b category
  because the rate of a lepton from a b decay is not the rate of a light-jet
  fake; the prompt rate is measured inclusively and carries no <bcat>, and
  it exists only in the same-flavour (Z peak) regions -- there is no emu or
  1l prompt rate, so an electron always reads ElePR_ee_lep*, a muon always
  MuonPR_mumu_lep*.

  Histogram names, as measureFakeRate.py:write_root writes them:
    FR -> "FR_pT_eta_EWKcorr"   (EWK-subtracted and DY-reweighted)
    PR -> "h_Ele_signal_pt_eta_bin" / "h_Muon_signal_pt_eta_bin"

  The maps are binned in pT and *signed* eta (measureFakeRate.py:26), so this
  reader looks them up with signed eta. The old fake_rate_reader_class.cc used
  abs(eta) against maps binned that way; do not copy that here.

  Three readers are wanted and they differ only in which map a lepton is sent
  to, so they are one class and a `mode` string rather than three near-copies:

    mode = "auto" : the region the event actually is in -- 1 lepton reads the
                    1l maps, 2 leptons read <pair>_lep<i> with the pair from
                    the two flavours and <i> the lepton's own slot.
    mode = "lep1" : always the lep1 maps (for the alternative sample).
    mode = "1l"   : always the 1l maps (FR only: there is no 1l prompt rate,
                    so the prompt rate still comes from the lep0 same-flavour
                    map).

  The weight is the matrix method, written as one signed coefficient per
  lepton so that it holds for any multiplicity:

    tight  lepton: P = +p(1-f)/(p-f)   F = -f(1-p)/(p-f)
    loose  lepton: P = -p f  /(p-f)    F = +f p    /(p-f)

  and the event weight is the sum over every prompt/fake assignment except
  all-prompt of the product of the coefficients. For two and three leptons
  this reproduces fake_rate_reader_class.cc term by term, signs included; for
  one lepton it gives the familiar f/(1-f) on a loose lepton and 0 on a tight
  one once p = 1.
*/

#ifndef FAKERATEREADERREGIONS
#define FAKERATEREADERREGIONS

#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <type_traits>

#include "TAxis.h"
#include "TFile.h"
#include "TH2F.h"
#include "TString.h"

#include "ROOT/RVec.hxx"

class fake_rate_reader_regions {
public:

  fake_rate_reader_regions(TString base,
                           TString year,
                           TString ele_WP,
                           TString muon_WP,
                           TString bcat    = "bveto",
                           TString mode    = "auto",
                           TString kind    = "nominal",
                           float   fr_pt_max = -1.);

  float operator()(ROOT::VecOps::RVec<int>   Lepton_pdgId,
                   ROOT::VecOps::RVec<float> Lepton_pt,
                   ROOT::VecOps::RVec<float> Lepton_eta,
                   ROOT::VecOps::RVec<int>   Lepton_isTightMuon,
                   ROOT::VecOps::RVec<int>   Lepton_isTightElectron) const;

private:

  // Shared, not owned per copy: Define() takes the callable by value, so every
  // copy -- one per RDataFrame slot -- has to share the histograms instead of
  // reopening the files. shared_ptr also keeps the class copyable, which the
  // typed Define() requires.
  std::shared_ptr<std::map<std::string, std::shared_ptr<TH2F>>> maps_;

  TString mode_;
  TString kind_;
  float   fr_pt_max_;

  void load(const std::string& key, TString path, TString histo);

  TH2F* map_for(const std::string& key) const;

  // value and statistical error of a map at (pt, signed eta)
  void rate(TH2F* h, double pt, double eta, double pt_max,
            double& value, double& error) const;

  // "ee", "mumu" or "emu" from two pdgIds
  static std::string pair_of(int pdg_a, int pdg_b);
};


fake_rate_reader_regions::fake_rate_reader_regions(TString base,
                                                   TString year,
                                                   TString ele_WP,
                                                   TString muon_WP,
                                                   TString bcat,
                                                   TString mode,
                                                   TString kind,
                                                   float   fr_pt_max)
  : maps_(std::make_shared<std::map<std::string, std::shared_ptr<TH2F>>>()),
    mode_(mode), kind_(kind), fr_pt_max_(fr_pt_max) {

  std::cout << "fake_rate_reader_regions: base " << base
            << " year " << year
            << " ele WP " << ele_WP
            << " muon WP " << muon_WP
            << " bcat " << bcat
            << " mode " << mode
            << " kind " << kind << std::endl;

  if (mode != "auto" && mode != "lep1" && mode != "1l")
    std::cout << "fake_rate_reader_regions: unknown mode '" << mode
              << "', falling back to the event's own region" << std::endl;

  const TString ele_dir  = base + "/" + year + "/" + ele_WP  + "/";
  const TString muon_dir = base + "/" + year + "/" + muon_WP + "/";

  // Everything is opened here, once, rather than on first use: the lookup runs
  // inside the event loop, where opening a file on several threads at once is
  // not safe and a miss would be silent.
  const TString fr_histo = "FR_pT_eta_EWKcorr";

  load("FR_ele_1l",  ele_dir  + "EleFR_1l_"   + bcat + ".root", fr_histo);
  load("FR_mu_1l",   muon_dir + "MuonFR_1l_"  + bcat + ".root", fr_histo);

  for (int i = 0; i < 2; ++i) {
    const TString slot = TString::Format("lep%d", i);
    load(Form("FR_ele_ee_%s", slot.Data()),
         ele_dir  + "EleFR_ee_"    + slot + "_" + bcat + ".root", fr_histo);
    load(Form("FR_ele_emu_%s", slot.Data()),
         ele_dir  + "EleFR_emu_"   + slot + "_" + bcat + ".root", fr_histo);
    load(Form("FR_mu_mumu_%s", slot.Data()),
         muon_dir + "MuonFR_mumu_" + slot + "_" + bcat + ".root", fr_histo);
    load(Form("FR_mu_emu_%s", slot.Data()),
         muon_dir + "MuonFR_emu_"  + slot + "_" + bcat + ".root", fr_histo);

    load(Form("PR_ele_%s", slot.Data()),
         ele_dir  + "ElePR_ee_"    + slot + ".root", "h_Ele_signal_pt_eta_bin");
    load(Form("PR_mu_%s", slot.Data()),
         muon_dir + "MuonPR_mumu_" + slot + ".root", "h_Muon_signal_pt_eta_bin");
  }
}


void fake_rate_reader_regions::load(const std::string& key,
                                    TString path,
                                    TString histo) {

  std::unique_ptr<TFile> file(TFile::Open(path.Data()));
  if (!file || file->IsZombie()) {
    std::cout << "fake_rate_reader_regions: cannot open " << path << std::endl;
    return;
  }

  TH2F* h = dynamic_cast<TH2F*>(file->Get(histo.Data()));
  if (!h) {
    std::cout << "fake_rate_reader_regions: no " << histo << " in " << path
              << std::endl;
    return;
  }

  // Clone and detach before the file closes: a histogram still owned by a
  // TFile dies with it, and leaving the files open would keep one xrootd
  // connection per map for the whole job.
  TH2F* copy = static_cast<TH2F*>(h->Clone((key + "_cached").c_str()));
  copy->SetDirectory(nullptr);
  (*maps_)[key] = std::shared_ptr<TH2F>(copy);
}


TH2F* fake_rate_reader_regions::map_for(const std::string& key) const {
  auto it = maps_->find(key);
  return it == maps_->end() ? nullptr : it->second.get();
}


std::string fake_rate_reader_regions::pair_of(int pdg_a, int pdg_b) {
  const bool a_ele = std::abs(pdg_a) == 11;
  const bool b_ele = std::abs(pdg_b) == 11;
  if (a_ele && b_ele)   return "ee";
  if (!a_ele && !b_ele) return "mumu";
  return "emu";
}


void fake_rate_reader_regions::rate(TH2F* h,
                                    double pt,
                                    double eta,
                                    double pt_max,
                                    double& value,
                                    double& error) const {

  value = 0.;
  error = 0.;
  if (!h) return;

  const TAxis* ax = h->GetXaxis();
  const TAxis* ay = h->GetYaxis();

  // Clamp into the measured range rather than falling into the under/overflow,
  // which is empty: a 150 GeV lepton gets the rate of the last pT bin.
  if (pt_max <= 0.) pt_max = ax->GetBinCenter(h->GetNbinsX());
  const double x = std::min(std::max(pt, ax->GetBinCenter(1)), pt_max);
  const double y = std::min(std::max(eta, ay->GetBinCenter(1)),
                            ay->GetBinCenter(h->GetNbinsY()));

  const int bin = h->FindBin(x, y);
  value = h->GetBinContent(bin);
  error = h->GetBinError(bin);
}


float fake_rate_reader_regions::operator()(
    ROOT::VecOps::RVec<int>   Lepton_pdgId,
    ROOT::VecOps::RVec<float> Lepton_pt,
    ROOT::VecOps::RVec<float> Lepton_eta,
    ROOT::VecOps::RVec<int>   Lepton_isTightMuon,
    ROOT::VecOps::RVec<int>   Lepton_isTightElectron) const {

  const unsigned int n = Lepton_pt.size();
  if (n == 0) return 0.;

  // The sum below is over 2^n assignments. Nothing in this analysis has more
  // than four selected leptons, and past that the enumeration is the wrong
  // tool anyway.
  if (n > 4) return 0.;

  double P[4];  // signed prompt coefficient, per lepton
  double F[4];  // signed fake coefficient, per lepton

  for (unsigned int i = 0; i < n; ++i) {

    const bool is_ele = std::abs(Lepton_pdgId[i]) == 11;
    const std::string flav = is_ele ? "ele" : "mu";

    const bool tight = is_ele ? Lepton_isTightElectron[i] == 1
                              : Lepton_isTightMuon[i] == 1;

    // Which slot this lepton reads. "lep1" forces the subleading map, "1l"
    // has no slots at all, and otherwise it is the lepton's own position --
    // capped at 1, which is as far as the maps go.
    const unsigned int slot = (mode_ == "lep1") ? 1u : std::min(i, 1u);

    // Which region. With one lepton there is no pair to form; with more, the
    // pair is this lepton's flavour against the other leading one, which for
    // the two-lepton case is exactly ee / emu / mumu.
    std::string fr_key;
    if (mode_ == "1l" || n == 1) {
      fr_key = "FR_" + flav + "_1l";
    } else {
      const unsigned int partner = (i == 0) ? 1u : 0u;
      const std::string pair = pair_of(Lepton_pdgId[i], Lepton_pdgId[partner]);
      fr_key = "FR_" + flav + "_" + pair + "_lep" + std::to_string(slot);
    }

    // The prompt rate has no 1l and no emu map, so it is always the
    // same-flavour one; in "1l" mode there is no slot to speak of, so lep0.
    const unsigned int pr_slot = (mode_ == "1l") ? 0u : slot;
    const std::string pr_key = "PR_" + flav + "_lep" + std::to_string(pr_slot);

    double f = 0., fe = 0., p = 1., pe = 0.;
    rate(map_for(fr_key), Lepton_pt[i], Lepton_eta[i], fr_pt_max_, f, fe);
    rate(map_for(pr_key), Lepton_pt[i], Lepton_eta[i], -1.,        p, pe);

    // Statistical variations of the fake rate, one flavour at a time, as in
    // fake_rate_reader_class.cc. The jet-pT variations it also carries have no
    // counterpart here: these maps are split by b category, not by jet pT.
    if (is_ele) {
      if      (kind_ == "StatEleUp")   f += fe;
      else if (kind_ == "StatEleDown") f -= fe;
    } else {
      if      (kind_ == "StatMuUp")    f += fe;
      else if (kind_ == "StatMuDown")  f -= fe;
    }

    // An empty or nonphysical bin must not turn into a huge weight. A prompt
    // rate outside (0,1] means the bin was not measured, and 1 -- every prompt
    // lepton is tight -- is the assumption that reduces the matrix method to
    // the plain fake-rate method.
    if (p <= 0. || p > 1.) p = 1.;
    if (f < 0.)    f = 0.;
    if (f > 0.99)  f = 0.99;

    if (p - f < 1e-6) return 0.;

    if (tight) {
      P[i] =  p * (1. - f) / (p - f);
      F[i] = -f * (1. - p) / (p - f);
    } else {
      P[i] = -p * f / (p - f);
      F[i] =  f * p / (p - f);
    }
  }

  // Every prompt/fake assignment except all-prompt. Bit i set = lepton i fake.
  double weight = 0.;
  for (unsigned int mask = 1; mask < (1u << n); ++mask) {
    double term = 1.;
    for (unsigned int i = 0; i < n; ++i)
      term *= (mask >> i & 1u) ? F[i] : P[i];
    weight += term;
  }

  return static_cast<float>(weight);
}

static_assert(std::is_copy_constructible_v<fake_rate_reader_regions>,
              "RDataFrame::Define takes the callable by value");

#endif
