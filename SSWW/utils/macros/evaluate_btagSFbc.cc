#ifndef BTAGSF
#define BTAGSF

#include <vector>
#include <map>
#include <string>
#include <iostream>
#include "TVector2.h"
#include "Math/Vector4Dfwd.h"
#include "Math/GenVector/LorentzVector.h"
#include "Math/GenVector/PtEtaPhiM4D.h"
#include "TString.h"

#include "ROOT/RVec.hxx"
#include "TH2D.h"
#include "TFile.h"
#include "correction.h"
#include <memory>

using namespace ROOT;
using namespace ROOT::VecOps;
using correction::CorrectionSet;

// --- BTag SF class ---
class btagSFbc {

  public:
    btagSFbc(TString eff_map, const std::string corr_year, const std::string WP,
            const std::string shift, const std::string tagger,
            const std::string eff_map_year);

    std::shared_ptr<TH2F> h_bjet_eff;
    std::shared_ptr<TH2F> h_cjet_eff;
    
    // shared_ptr rather than unique_ptr: RDataFrame's typed Define() takes the
    // callable by value, so this class must stay copyable. Copies share the
    // efficiency maps and the CorrectionSet instead of reloading them.
    std::shared_ptr<CorrectionSet> cset;

    // fixed per instance — one instance per (WP, shift) variation
    std::string WP_;
    std::string shift_;
    std::string eff_map_year_;

    // resolved once in the constructor instead of on every event
    correction::Correction::Ref cset_btag_comb_;
    correction::Correction::Ref cset_btag_wps_;
 
    float operator()(
        RVecF CleanJet_pt,
        RVecF CleanJet_eta,
        RVec<ULong64_t> CleanJet_jetIdx,
        unsigned int nCleanJet,
        RVecI Jet_hadronFlavour,
        RVecF Jet_btag
      )
    {
      
        float btag_sf = 1.;
        for (unsigned iJ{0}; iJ != nCleanJet; ++iJ) 
        {
          if (CleanJet_pt[iJ] <= 20. || std::abs(CleanJet_eta[iJ]) >= 2.5) continue;

          if (Jet_btag[CleanJet_jetIdx[iJ]] > cset_btag_wps_->evaluate({WP_})) 
          {
            if (Jet_hadronFlavour[CleanJet_jetIdx[iJ]] == 5)
              btag_sf *= cset_btag_comb_->evaluate({shift_, WP_, 5, std::abs(CleanJet_eta[iJ]), CleanJet_pt[iJ]});
            else if (Jet_hadronFlavour[CleanJet_jetIdx[iJ]] == 4 && eff_map_year_ != "None")
              btag_sf *= cset_btag_comb_->evaluate({shift_, WP_, 4, std::abs(CleanJet_eta[iJ]), CleanJet_pt[iJ]});
          }
          else
          {
            float btag_eff = getEff(CleanJet_pt[iJ], CleanJet_eta[iJ], Jet_hadronFlavour[CleanJet_jetIdx[iJ]]);
            if (btag_eff == 1.) continue;

            if (Jet_hadronFlavour[CleanJet_jetIdx[iJ]] == 5)
              btag_sf *= (1-btag_eff*cset_btag_comb_->evaluate({shift_, WP_, 5, std::abs(CleanJet_eta[iJ]), CleanJet_pt[iJ]}))/(1-btag_eff);
            else if (Jet_hadronFlavour[CleanJet_jetIdx[iJ]] == 4 && eff_map_year_ != "None")
              btag_sf *= (1-btag_eff*cset_btag_comb_->evaluate({shift_, WP_, 4, std::abs(CleanJet_eta[iJ]), CleanJet_pt[iJ]}))/(1-btag_eff);
          }
        }
        return btag_sf;
    }

  private:
    float getEff(float pt, float eta, int flavour);
  
};

btagSFbc::btagSFbc(TString eff_map, const std::string corr_year, const std::string WP,
                  const std::string shift, const std::string tagger,
                  const std::string eff_map_year)
  : WP_(WP), shift_(shift), eff_map_year_(eff_map_year) {

    // --- Patch graphics classes first ---
    //const char* graphicsClasses[] = { "TPaletteAxis", "TCanvas", "TFrame", "TAttBBox2D", "TBox" };
    //for (auto clsname : graphicsClasses) {
    //    if (TClass* cl = TClass::GetClass(clsname)) cl->IgnoreTObjectStreamer();
    //}

  // std::string home = std::string(std::getenv("STARTPATH"));
  // std::string to_replace = "start.sh";
  // size_t start  = home.find(to_replace);
  // size_t stop   = to_replace.length();
  // home.replace(start, stop, "");
  
  if (corr_year == "None")
    {
        cset = CorrectionSet::from_file("/cvmfs/cms-griddata.cern.ch/cat/metadata/BTV/" + corr_year + "/latest/btagging_preliminary.json.gz");
    }
    else
    {
       cset = CorrectionSet::from_file("/cvmfs/cms-griddata.cern.ch/cat/metadata/BTV/" + corr_year + "/latest/btagging.json.gz"); 
    }

  // resolved here, once per job, rather than per event in operator()
  if (eff_map_year_ == "None")
    cset_btag_comb_ = cset->at(tagger + "_kinfit");
  else
    cset_btag_comb_ = cset->at(tagger + "_comb");
  cset_btag_wps_ = cset->at(tagger + "_wp_values");

  TFile *reff = TFile::Open(eff_map, "READ");
  if (!reff || reff->IsZombie()) {
      std::cerr << "Error opening file " << eff_map << std::endl;
      return;
  }

  //h_bjet_eff = (TH2F*)reff->Get("bjet_eff")->Clone();
  //h_cjet_eff = (TH2F*)reff->Get("cjet_eff")->Clone();
  if (auto* _h = dynamic_cast<TH2F*>(reff->Get("bjet_eff"))) {
    auto* _clone = static_cast<TH2F*>(_h->Clone());
    _clone->SetDirectory(nullptr);
    h_bjet_eff.reset(_clone);
  }
  if (auto* _h = dynamic_cast<TH2F*>(reff->Get("cjet_eff"))) {
    auto* _clone = static_cast<TH2F*>(_h->Clone());
    _clone->SetDirectory(nullptr);
    h_cjet_eff.reset(_clone);
  }
  reff->Close();
}

float btagSFbc::getEff(float pt, float eta, int flavour) {
  int xbin, ybin;
  float eff = 1.;
  if (flavour == 5) {
    xbin = h_bjet_eff->GetXaxis()->FindBin(pt);
    ybin = h_bjet_eff->GetYaxis()->FindBin(eta);
    eff  = h_bjet_eff->GetBinContent(xbin, ybin);
  }
  else if (flavour == 4) {
    if (!h_cjet_eff) return 1.0;
    xbin = h_cjet_eff->GetXaxis()->FindBin(pt);
    ybin = h_cjet_eff->GetYaxis()->FindBin(eta);
    eff  = h_cjet_eff->GetBinContent(xbin, ybin);
  }
  else 
  {
    eff   = 1.;
  }
  return eff;
}

#endif