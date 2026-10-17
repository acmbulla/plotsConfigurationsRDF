#ifndef BTAGLIGHTSF
#define BTAGLIGHTSF

#include <algorithm>
#include <cstddef>
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

// --- BTag SF class for light jets ---
class btagSFlight {

  public:
    btagSFlight(TString eff_map, const std::string corr_year, const std::string WP,
               const std::string shift, const std::string tagger,
               const std::string eff_map_year);

    std::shared_ptr<TH2F> h_ljet_eff;
    // shared_ptr rather than unique_ptr: RDataFrame's typed Define() takes the
    // callable by value, so this class must stay copyable. Copies share the
    // efficiency maps and the CorrectionSet instead of reloading them.
    std::shared_ptr<CorrectionSet> cset;

    // fixed per instance — one instance per (WP, shift) variation
    std::string WP_;
    std::string shift_;
    std::string eff_map_year_;

    // resolved once in the constructor instead of on every event
    correction::Correction::Ref cset_btag_light_;
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
        // nCleanJet is a counter branch; the arrays are the truth. In a varied
        // tree the two do not have to come from the same place -- a suffix
        // production carries the collections it recomputes and nothing else --
        // and an unchecked loop then reads past the end of the RVec, which is a
        // segmentation violation rather than a wrong number. Same for jetIdx
        // into the Jet collection, which is not varied at all. So the loop is
        // bounded by what is actually there, and a jet pointing outside the
        // Jet collection is skipped.
        const std::size_t nJets = std::min({static_cast<std::size_t>(nCleanJet),
                                            CleanJet_pt.size(),
                                            CleanJet_eta.size(),
                                            CleanJet_jetIdx.size()});
        for (std::size_t iJ = 0; iJ < nJets; ++iJ)
        {
            if (CleanJet_pt[iJ] <= 20. || std::abs(CleanJet_eta[iJ]) >= 2.5) continue;

            const std::size_t jetIdx = static_cast<std::size_t>(CleanJet_jetIdx[iJ]);
            if (jetIdx >= Jet_btag.size() || jetIdx >= Jet_hadronFlavour.size()) continue;

            if (Jet_btag[jetIdx] > cset_btag_wps_->evaluate({WP_})) 
            {
                if (Jet_hadronFlavour[jetIdx] == 0) 
                    btag_sf *= cset_btag_light_->evaluate({shift_, WP_, 0, std::abs(CleanJet_eta[iJ]), CleanJet_pt[iJ]});
            }
            else 
            {
                float btag_eff = getEff(CleanJet_pt[iJ], CleanJet_eta[iJ], Jet_hadronFlavour[jetIdx]);
                if (btag_eff == 1.) continue;

                if (Jet_hadronFlavour[jetIdx] == 0)
                    btag_sf *= (1-btag_eff*cset_btag_light_->evaluate({shift_, WP_, 0, std::abs(CleanJet_eta[iJ]), CleanJet_pt[iJ]}))/(1-btag_eff);
            }
        }
        return btag_sf;
    }

  private:
    float getEff(float pt, float eta, int flavour);
};

btagSFlight::btagSFlight(TString eff_map, const std::string corr_year, const std::string WP,
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
      cset_btag_light_ = cset->at(tagger + "_negtagDY");
    else
      cset_btag_light_ = cset->at(tagger + "_light");
    cset_btag_wps_ = cset->at(tagger + "_wp_values");

    TFile *reff = TFile::Open(eff_map, "READ");
    if (!reff || reff->IsZombie()) {
        std::cerr << "Error opening file " << eff_map << std::endl;
        return;
    }

    //h_ljet_eff = (TH2F*)reff->Get("ljet_eff")->Clone();
    //if (h_ljet_eff) h_ljet_eff->SetDirectory(0);
    //reff->Close();
    if (auto* _h = dynamic_cast<TH2F*>(reff->Get("ljet_eff"))) {
      auto* _clone = static_cast<TH2F*>(_h->Clone());
      _clone->SetDirectory(nullptr);
      h_ljet_eff.reset(_clone);
    }
}

float btagSFlight::getEff(float pt, float eta, int flavour) {
    if (flavour != 0 || !h_ljet_eff) return 1.;

    int xbin = h_ljet_eff->GetXaxis()->FindBin(pt);
    int ybin = h_ljet_eff->GetYaxis()->FindBin(eta);
    return h_ljet_eff->GetBinContent(xbin, ybin);
}

#endif