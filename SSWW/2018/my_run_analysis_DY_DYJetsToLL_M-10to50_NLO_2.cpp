

#include "library_utils.h"

#include "ROOT/RDataFrame.hxx"
#include "ROOT/RDFHelpers.hxx"
#include "ROOT/RVec.hxx"

#include <iostream>
#include <algorithm>

#include "TFile.h"
#include "TH1D.h"
#include "TDirectory.h"
#include "TChain.h"
#include <map>
#include <vector>
#include <iostream>
#include <string>
#include <typeinfo>

#include <regex>

#include "TMVA/RReader.hxx"
#include "TMVA/RInferenceUtils.hxx"


// --- Automatically generated: code to be added for additional functions ---


#include <cmath>
float calculate_mass(float pt1, float eta1, float phi1, float pt2, float eta2, float phi2) {
  return std::sqrt(2 * pt1 * pt2 * (std::cosh(eta1 - eta2) - std::cos(phi1-phi2)));
}


//------------------------------------------------------------------------------------------------------
//------------------------------------------------------------------------------------------------------
//------------------------------------------------------------------------------------------------------
//------------------------------------------------------------------------------------------------------

#include "correction.h"
// --- JER Evaluator Helper Class ---
class JERSmearer {
public:
  JERSmearer(const std::string& jsonPath, const std::string& algo) {
    // Load the centralized JERC correction set
    auto cset = correction::CorrectionSet::from_file(jsonPath);

    // Use the official CMS 2018 UL JER keys
    std::string jer_tag = "Summer19UL18_JRV2_MC";

    cl_res = cset->at(jer_tag + "_PtResolution_" + algo); // e.g. Summer19UL18_JRV2_MC_PtResolution_AK4PFchs
    cl_sf  = cset->at(jer_tag + "_ScaleFactor_"  + algo); // e.g. Summer19UL18_JRV2_MC_ScaleFactor_AK4PFchs

  }

  // Hybrid Smearing Method
  ROOT::RVecF smear(const ROOT::RVecF& jet_pt,
                    const ROOT::RVecF& jet_eta,
                    const ROOT::RVecF& jet_phi,
                    const ROOT::RVecF& gen_pt,
                    double rho,
                    const std::string& systematic,
                    int seed
                    ) {

    ROOT::RVecF smeared_pt;
    smeared_pt.reserve(jet_pt.size());

    for (size_t i = 0; i < jet_pt.size(); ++i) {
      float pt = jet_pt[i];
      float eta = jet_eta[i];

      // 1. Get the resolution (sigma_MC)
      float sigma_mc = cl_res->evaluate({eta, pt, rho});

      // 2. Get the Scale Factor (nominal, up, or down)
      float sf = cl_sf->evaluate({eta, systematic});

      float smear_factor = 1.0;

      // 3. Apply Hybrid Smearing (Gen-matching vs Stochastic)
      if (i < gen_pt.size() && gen_pt[i] > 0) {
        // Gen-matched method
        float dpt = pt - gen_pt[i];
        if (std::abs(dpt) < 3.0 * sigma_mc * pt) {
          smear_factor = 1.0 + (sf - 1.0) * dpt / pt;
        }
      } else {
        //
        // https://github.com/latinos/mkShapesRDF/blob/master/mkShapesRDF/processor/modules/JMECalculator.py#L208
        // f"(run<<20) + (luminosityBlock<<10) + event + 1 + int(Jet_eta.size()>0 ? Jet_eta[0]/.01 : 0)"
        //
        // Stochastic/Data-saving method (using a dummy deterministic hash for reproducible results per event)
        // float pseudo_random = std::sin(jet_phi[i] * 1000.0 ) * std::cos(pt);
        float pseudo_random = std::sin(jet_phi[i] * (1000.0 + seed) ) * std::cos(pt);
        if (sf > 1.0) {
          smear_factor = 1.0 + pseudo_random * sigma_mc * std::sqrt(sf * sf - 1.0);
        }
      }

      // Guard against negative/unphysical values
      smeared_pt.push_back(std::max(float(0.0), pt * smear_factor));
    }
    return smeared_pt;
                    }

private:
  std::shared_ptr<const correction::Correction> cl_res;
  std::shared_ptr<const correction::Correction> cl_sf;
};


auto get_sorting_indices = [](const ROOT::RVecF& pt) {
  auto indices = ROOT::VecOps::Argsort(pt);
  std::reverse(indices.begin(), indices.end()); // Flips to highest pt first
  return indices;
};




// ----------------------------------------




int main() {
    ROOT::EnableImplicitMT();


    // Path to your JSON on CVMFS
    std::string json_path = "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/2018_UL/jet_jerc.json.gz";
    std::string jet_algo  = "AK4PFchs";

    // Initialize our helper
    static JERSmearer jer(json_path, jet_algo);


    // --- Automatically generated input root files ---

    //  Nominal input files
    auto* nominal = new TChain("Events");
    nominal->Add("root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9/nanoLatino_DYJetsToLL_M-50__part30.root");
    // nominal->Add("root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9/nanoLatino_DYJetsToLL_M-50__part31.root");
    // nominal->Add("root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9/nanoLatino_DYJetsToLL_M-50__part32.root");
    
    auto nominalBranches = getBranchNames(nominal);
    

//  Variations input files (if any)
    // auto* friend_ElepTup = new TChain("Events");
    // auto* friend_ElepTdo = new TChain("Events");
    // friend_ElepTup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_ElepTdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_ElepTup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_ElepTdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_ElepTup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_ElepTdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_ElepTup, "ElepTup");
    // nominal->AddFriend(friend_ElepTdo, "ElepTdo");
    // auto varBranches_ElepTup = getBranchNames(friend_ElepTup);
    // auto varBranches_ElepTdo = getBranchNames(friend_ElepTdo);
    // auto* friend_MupTup = new TChain("Events");
    // auto* friend_MupTdo = new TChain("Events");
    // friend_MupTup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__MupTup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_MupTdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__MupTdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_MupTup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__MupTup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_MupTdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__MupTdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_MupTup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__MupTup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_MupTdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__MupTdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_MupTup, "MupTup");
    // nominal->AddFriend(friend_MupTdo, "MupTdo");
    // auto varBranches_MupTup = getBranchNames(friend_MupTup);
    // auto varBranches_MupTdo = getBranchNames(friend_MupTdo);
    // auto* friend_JESAbsoluteup = new TChain("Events");
    // auto* friend_JESAbsolutedo = new TChain("Events");
    // friend_JESAbsoluteup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESAbsolutedo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESAbsoluteup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESAbsolutedo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESAbsoluteup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_JESAbsolutedo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_JESAbsoluteup, "JESAbsoluteup");
    // nominal->AddFriend(friend_JESAbsolutedo, "JESAbsolutedo");
    // auto varBranches_JESAbsoluteup = getBranchNames(friend_JESAbsoluteup);
    // auto varBranches_JESAbsolutedo = getBranchNames(friend_JESAbsolutedo);
    // auto* friend_JESAbsolute_2018up = new TChain("Events");
    // auto* friend_JESAbsolute_2018do = new TChain("Events");
    // friend_JESAbsolute_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESAbsolute_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESAbsolute_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESAbsolute_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESAbsolute_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_JESAbsolute_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_JESAbsolute_2018up, "JESAbsolute_2018up");
    // nominal->AddFriend(friend_JESAbsolute_2018do, "JESAbsolute_2018do");
    // auto varBranches_JESAbsolute_2018up = getBranchNames(friend_JESAbsolute_2018up);
    // auto varBranches_JESAbsolute_2018do = getBranchNames(friend_JESAbsolute_2018do);
    // auto* friend_JESBBEC1up = new TChain("Events");
    // auto* friend_JESBBEC1do = new TChain("Events");
    // friend_JESBBEC1up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESBBEC1do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESBBEC1up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESBBEC1do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESBBEC1up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_JESBBEC1do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_JESBBEC1up, "JESBBEC1up");
    // nominal->AddFriend(friend_JESBBEC1do, "JESBBEC1do");
    // auto varBranches_JESBBEC1up = getBranchNames(friend_JESBBEC1up);
    // auto varBranches_JESBBEC1do = getBranchNames(friend_JESBBEC1do);
    // auto* friend_JESBBEC1_2018up = new TChain("Events");
    // auto* friend_JESBBEC1_2018do = new TChain("Events");
    // friend_JESBBEC1_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESBBEC1_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESBBEC1_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESBBEC1_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESBBEC1_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_JESBBEC1_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_JESBBEC1_2018up, "JESBBEC1_2018up");
    // nominal->AddFriend(friend_JESBBEC1_2018do, "JESBBEC1_2018do");
    // auto varBranches_JESBBEC1_2018up = getBranchNames(friend_JESBBEC1_2018up);
    // auto varBranches_JESBBEC1_2018do = getBranchNames(friend_JESBBEC1_2018do);
    // auto* friend_JESEC2up = new TChain("Events");
    // auto* friend_JESEC2do = new TChain("Events");
    // friend_JESEC2up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESEC2do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESEC2up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESEC2do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESEC2up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_JESEC2do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_JESEC2up, "JESEC2up");
    // nominal->AddFriend(friend_JESEC2do, "JESEC2do");
    // auto varBranches_JESEC2up = getBranchNames(friend_JESEC2up);
    // auto varBranches_JESEC2do = getBranchNames(friend_JESEC2do);
    // auto* friend_JESEC2_2018up = new TChain("Events");
    // auto* friend_JESEC2_2018do = new TChain("Events");
    // friend_JESEC2_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESEC2_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESEC2_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESEC2_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESEC2_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_JESEC2_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_JESEC2_2018up, "JESEC2_2018up");
    // nominal->AddFriend(friend_JESEC2_2018do, "JESEC2_2018do");
    // auto varBranches_JESEC2_2018up = getBranchNames(friend_JESEC2_2018up);
    // auto varBranches_JESEC2_2018do = getBranchNames(friend_JESEC2_2018do);
    // auto* friend_JESFlavorQCDup = new TChain("Events");
    // auto* friend_JESFlavorQCDdo = new TChain("Events");
    // friend_JESFlavorQCDup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESFlavorQCDdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESFlavorQCDup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESFlavorQCDdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESFlavorQCDup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_JESFlavorQCDdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_JESFlavorQCDup, "JESFlavorQCDup");
    // nominal->AddFriend(friend_JESFlavorQCDdo, "JESFlavorQCDdo");
    // auto varBranches_JESFlavorQCDup = getBranchNames(friend_JESFlavorQCDup);
    // auto varBranches_JESFlavorQCDdo = getBranchNames(friend_JESFlavorQCDdo);
    // auto* friend_JESHFup = new TChain("Events");
    // auto* friend_JESHFdo = new TChain("Events");
    // friend_JESHFup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESHFdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESHFup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESHFdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESHFup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_JESHFdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_JESHFup, "JESHFup");
    // nominal->AddFriend(friend_JESHFdo, "JESHFdo");
    // auto varBranches_JESHFup = getBranchNames(friend_JESHFup);
    // auto varBranches_JESHFdo = getBranchNames(friend_JESHFdo);
    // auto* friend_JESHF_2018up = new TChain("Events");
    // auto* friend_JESHF_2018do = new TChain("Events");
    // friend_JESHF_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESHF_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESHF_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESHF_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESHF_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_JESHF_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_JESHF_2018up, "JESHF_2018up");
    // nominal->AddFriend(friend_JESHF_2018do, "JESHF_2018do");
    // auto varBranches_JESHF_2018up = getBranchNames(friend_JESHF_2018up);
    // auto varBranches_JESHF_2018do = getBranchNames(friend_JESHF_2018do);
    // auto* friend_JESRelativeBalup = new TChain("Events");
    // auto* friend_JESRelativeBaldo = new TChain("Events");
    // friend_JESRelativeBalup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESRelativeBaldo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESRelativeBalup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESRelativeBaldo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESRelativeBalup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_JESRelativeBaldo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_JESRelativeBalup, "JESRelativeBalup");
    // nominal->AddFriend(friend_JESRelativeBaldo, "JESRelativeBaldo");
    // auto varBranches_JESRelativeBalup = getBranchNames(friend_JESRelativeBalup);
    // auto varBranches_JESRelativeBaldo = getBranchNames(friend_JESRelativeBaldo);
    // auto* friend_JESRelativeSample_2018up = new TChain("Events");
    // auto* friend_JESRelativeSample_2018do = new TChain("Events");
    // friend_JESRelativeSample_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESRelativeSample_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JESRelativeSample_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESRelativeSample_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JESRelativeSample_2018up->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_JESRelativeSample_2018do->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__RDF__JESdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_JESRelativeSample_2018up, "JESRelativeSample_2018up");
    // nominal->AddFriend(friend_JESRelativeSample_2018do, "JESRelativeSample_2018do");
    // auto varBranches_JESRelativeSample_2018up = getBranchNames(friend_JESRelativeSample_2018up);
    // auto varBranches_JESRelativeSample_2018do = getBranchNames(friend_JESRelativeSample_2018do);
    // auto* friend_JERup = new TChain("Events");
    // auto* friend_JERdo = new TChain("Events");
    // friend_JERup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__JERup_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JERdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__JERdo_suffix/nanoLatino_DYJetsToLL_M-50__part30.root");
    // friend_JERup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__JERup_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JERdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__JERdo_suffix/nanoLatino_DYJetsToLL_M-50__part31.root");
    // friend_JERup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__JERup_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // friend_JERdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__JERdo_suffix/nanoLatino_DYJetsToLL_M-50__part32.root");
    // nominal->AddFriend(friend_JERup, "JERup");
    // nominal->AddFriend(friend_JERdo, "JERdo");
    // auto varBranches_JERup = getBranchNames(friend_JERup);
    // auto varBranches_JERdo = getBranchNames(friend_JERdo);
    ROOT::RDataFrame base_df(*nominal);
    auto varied_df = ROOT::RDF::RNode(base_df);



    // Define lambda wrappers so RDataFrame can cleanly loop them
    auto jer_nom = [](const ROOT::RVecF& pt, const ROOT::RVecF& eta, const ROOT::RVecF& phi, const ROOT::RVecF& gpt, float rho, int seed) {
      return jer.smear(pt, eta, phi, gpt, rho, "nom", seed);
    };
    auto jer_up = [](const ROOT::RVecF& pt, const ROOT::RVecF& eta, const ROOT::RVecF& phi, const ROOT::RVecF& gpt, float rho, int seed) {
      return jer.smear(pt, eta, phi, gpt, rho, "up", seed);
    };
    auto jer_down = [](const ROOT::RVecF& pt, const ROOT::RVecF& eta, const ROOT::RVecF& phi, const ROOT::RVecF& gpt, float rho, int seed) {
      return jer.smear(pt, eta, phi, gpt, rho, "down", seed);
    };



    // varied_df = varied_df.Define("temp_Jet_pt_JERNom",   jer_nom,  {"CleanJet_pt", "CleanJet_eta", "CleanJet_phi", "GenJet_pt", "fixedGridRhoFastjetAll"})
    // .Define("temp_Jet_pt_myJERUp",    jer_up,   {"CleanJet_pt", "CleanJet_eta", "CleanJet_phi", "GenJet_pt", "fixedGridRhoFastjetAll"})
    // .Define("temp_Jet_pt_myJERDown",  jer_down, {"CleanJet_pt", "CleanJet_eta", "CleanJet_phi", "GenJet_pt", "fixedGridRhoFastjetAll"});
    //
    // varied_df = varied_df
    //      .Define("temp_idx_Up", get_sorting_indices, {"temp_Jet_pt_myJERUp"})
    //      .Define("CleanJet_pt_myJERUp",  "ROOT::VecOps::Take(temp_Jet_pt_myJERUp, temp_idx_Up)")
    //      .Define("CleanJet_eta_myJERUp", "ROOT::VecOps::Take(CleanJet_eta, temp_idx_Up)")
    //      .Define("CleanJet_phi_myJERUp", "ROOT::VecOps::Take(CleanJet_phi, temp_idx_Up)")
    //      .Define("CleanJet_jetIdx_myJERUp", "ROOT::VecOps::Take(CleanJet_jetIdx, temp_idx_Up)")
    //
    //      .Define("temp_idx_Down", get_sorting_indices, {"temp_Jet_pt_myJERDown"})
    //      .Define("CleanJet_pt_myJERDown",  "ROOT::VecOps::Take(temp_Jet_pt_myJERDown, temp_idx_Down)")
    //      .Define("CleanJet_eta_myJERDown", "ROOT::VecOps::Take(CleanJet_eta, temp_idx_Down)")
    //      .Define("CleanJet_phi_myJERDown", "ROOT::VecOps::Take(CleanJet_phi, temp_idx_Down)")
    //      .Define("CleanJet_jetIdx_myJERDown", "ROOT::VecOps::Take(CleanJet_jetIdx, temp_idx_Down)");


    //
    // run it 100 times ...
    //

    int Nvariation = 3;

    for (int ivariation = 0; ivariation<Nvariation; ivariation++) {
      std::string ivariation_col_name = "ivariation_val_" + std::to_string(ivariation);

      varied_df = varied_df
            .Define(ivariation_col_name, [ivariation]() { return ivariation; })
            .Define("__" + std::to_string(ivariation) + "_NORM_temp_Jet_pt_JERNom",    jer_nom,  {"CleanJet_pt", "CleanJet_eta", "CleanJet_phi", "GenJet_pt", "fixedGridRhoFastjetAll", ivariation_col_name})
            .Define("__" + std::to_string(ivariation) + "_NORM_temp_Jet_pt_myJERUp",    jer_up,   {"CleanJet_pt", "CleanJet_eta", "CleanJet_phi", "GenJet_pt", "fixedGridRhoFastjetAll", ivariation_col_name})
            .Define("__" + std::to_string(ivariation) + "_NORM_temp_Jet_pt_myJERDown",  jer_down, {"CleanJet_pt", "CleanJet_eta", "CleanJet_phi", "GenJet_pt", "fixedGridRhoFastjetAll", ivariation_col_name});

      varied_df = varied_df
                           .Define("__" + std::to_string(ivariation) + "_temp_idx_Up", get_sorting_indices, {"__" + std::to_string(ivariation) + "_NORM_temp_Jet_pt_myJERUp"})
                           .Define("__" + std::to_string(ivariation) + "CleanJet_pt_myJERUp",  "ROOT::VecOps::Take(__" + std::to_string(ivariation) + "_NORM_temp_Jet_pt_myJERUp, __" +  std::to_string(ivariation) + "_temp_idx_Up)")
                           .Define("__" + std::to_string(ivariation) + "CleanJet_eta_myJERUp", "ROOT::VecOps::Take(CleanJet_eta, __" + std::to_string(ivariation) + "_temp_idx_Up)")
                           .Define("__" + std::to_string(ivariation) + "CleanJet_phi_myJERUp", "ROOT::VecOps::Take(CleanJet_phi, __" + std::to_string(ivariation) + "_temp_idx_Up)")
                           .Define("__" + std::to_string(ivariation) + "CleanJet_jetIdx_myJERUp", "ROOT::VecOps::Take(CleanJet_jetIdx, __" + std::to_string(ivariation) + "_temp_idx_Up)")

                           .Define("__" + std::to_string(ivariation) + "_temp_idx_Down", get_sorting_indices, {"__" + std::to_string(ivariation) + "_NORM_temp_Jet_pt_myJERDown"})
                           .Define("__" + std::to_string(ivariation) + "CleanJet_pt_myJERDown",  "ROOT::VecOps::Take(__" + std::to_string(ivariation) + "_NORM_temp_Jet_pt_myJERDown, __" +  std::to_string(ivariation) + "_temp_idx_Down)")
                           .Define("__" + std::to_string(ivariation) + "CleanJet_eta_myJERDown", "ROOT::VecOps::Take(CleanJet_eta, __" + std::to_string(ivariation) + "_temp_idx_Down)")
                           .Define("__" + std::to_string(ivariation) + "CleanJet_phi_myJERDown", "ROOT::VecOps::Take(CleanJet_phi, __" + std::to_string(ivariation) + "_temp_idx_Down)")
                           .Define("__" + std::to_string(ivariation) + "CleanJet_jetIdx_myJERDown", "ROOT::VecOps::Take(CleanJet_jetIdx, __" + std::to_string(ivariation) + "_temp_idx_Down)");
    }




    // ----------------------------------------

    std::map<std::string, std::vector<ROOT::RDF::RResultPtr<TH1D>>> hist_map_1D;
    std::map<std::string, std::vector<ROOT::RDF::RResultPtr<TH2D>>> hist_map_2D;

    // --- Automatically generated register nuisances variations for alternative trees ---
    //        Alternative trees variation nuisances to be defined at the beginning because they might change the
    //        variables that are defined downstream, e.g. njet, BDT(ptjet, ptlepton, ...)
    //

    
    int suffix_size = 0;
    suffix_size = 8;
//     for (const auto& branch : varBranches_ElepTup) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "ElepTup") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "scale_e_2018_UL"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 8;
//     for (const auto& branch : varBranches_ElepTdo) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "ElepTdo") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "scale_e_2018_UL"
//                                     );
//         };
//       };
//     };
//     suffix_size = 7;
//     for (const auto& branch : varBranches_MupTup) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "MupTup") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_scale_m_2018"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 7;
//     for (const auto& branch : varBranches_MupTdo) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "MupTdo") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_scale_m_2018"
//                                     );
//         };
//       };
//     };
//     suffix_size = 14;
//     for (const auto& branch : varBranches_JESAbsoluteup) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESAbsoluteup") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_scale_JESAbsolute"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 14;
//     for (const auto& branch : varBranches_JESAbsolutedo) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESAbsolutedo") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_scale_JESAbsolute"
//                                     );
//         };
//       };
//     };
//     suffix_size = 19;
//     for (const auto& branch : varBranches_JESAbsolute_2018up) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESAbsolute_2018up") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_scale_JESAbsolute_2018"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 19;
//     for (const auto& branch : varBranches_JESAbsolute_2018do) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESAbsolute_2018do") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_scale_JESAbsolute_2018"
//                                     );
//         };
//       };
//     };
//     suffix_size = 11;
//     for (const auto& branch : varBranches_JESBBEC1up) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESBBEC1up") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_scale_JESBBEC1"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 11;
//     for (const auto& branch : varBranches_JESBBEC1do) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESBBEC1do") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_scale_JESBBEC1"
//                                     );
//         };
//       };
//     };
//     suffix_size = 16;
//     for (const auto& branch : varBranches_JESBBEC1_2018up) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESBBEC1_2018up") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_scale_JESBBEC1_2018"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 16;
//     for (const auto& branch : varBranches_JESBBEC1_2018do) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESBBEC1_2018do") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_scale_JESBBEC1_2018"
//                                     );
//         };
//       };
//     };
//     suffix_size = 9;
//     for (const auto& branch : varBranches_JESEC2up) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESEC2up") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_scale_JESEC2"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 9;
//     for (const auto& branch : varBranches_JESEC2do) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESEC2do") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_scale_JESEC2"
//                                     );
//         };
//       };
//     };
//     suffix_size = 14;
//     for (const auto& branch : varBranches_JESEC2_2018up) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESEC2_2018up") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_scale_JESEC2_2018"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 14;
//     for (const auto& branch : varBranches_JESEC2_2018do) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESEC2_2018do") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_scale_JESEC2_2018"
//                                     );
//         };
//       };
//     };
//     suffix_size = 15;
//     for (const auto& branch : varBranches_JESFlavorQCDup) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESFlavorQCDup") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_scale_JESFlavorQCD"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 15;
//     for (const auto& branch : varBranches_JESFlavorQCDdo) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESFlavorQCDdo") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_scale_JESFlavorQCD"
//                                     );
//         };
//       };
//     };
//     suffix_size = 8;
//     for (const auto& branch : varBranches_JESHFup) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESHFup") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_scale_JESHF"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 8;
//     for (const auto& branch : varBranches_JESHFdo) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESHFdo") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_scale_JESHF"
//                                     );
//         };
//       };
//     };
//     suffix_size = 13;
//     for (const auto& branch : varBranches_JESHF_2018up) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESHF_2018up") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_scale_JESHF_2018"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 13;
//     for (const auto& branch : varBranches_JESHF_2018do) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESHF_2018do") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_scale_JESHF_2018"
//                                     );
//         };
//       };
//     };
//     suffix_size = 17;
//     for (const auto& branch : varBranches_JESRelativeBalup) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESRelativeBalup") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_scale_JESRelativeBal"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 17;
//     for (const auto& branch : varBranches_JESRelativeBaldo) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESRelativeBaldo") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_scale_JESRelativeBal"
//                                     );
//         };
//       };
//     };
//     suffix_size = 25;
//     for (const auto& branch : varBranches_JESRelativeSample_2018up) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESRelativeSample_2018up") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_scale_JESRelativeSample_2018"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 25;
//     for (const auto& branch : varBranches_JESRelativeSample_2018do) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JESRelativeSample_2018do") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_scale_JESRelativeSample_2018"
//                                     );
//         };
//       };
//     };

//     suffix_size = 6;
//     for (const auto& branch : varBranches_JERup) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JERup") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"up"},
//                                     "CMS_res_j_2018"
//                                     );
//         };
//       };
//     };
//
//     suffix_size = 6;
//     for (const auto& branch : varBranches_JERdo) {
//       if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JERdo") == 0 ) {
//         std::string nomCol = branch.substr(0, branch.size() - suffix_size);
//         if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
//           std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
//           varied_df = varied_df.Vary(
//                                     nomCol,
//                                     expression,
//                                     {"do"},
//                                     "CMS_res_j_2018"
//                                     );
//         };
//       };
//     };



//
// myJER
//

    suffix_size = 4;
    std::cout << "suffix_size = " << suffix_size << std::endl;


    // varied_df = varied_df.Vary(
    //   "CleanJet_pt",
    //   "ROOT::RVec<ROOT::RVecF>{CleanJet_pt_myJERUp, CleanJet_pt_myJERDown}",
    //   {"up","do"},
    //   "CMS_my_res_j_XXXX"
    // );
    // varied_df = varied_df.Vary(
    //   "CleanJet_eta",
    //   "ROOT::RVec<ROOT::RVecF>{CleanJet_eta_myJERUp, CleanJet_eta_myJERDown}",
    //   {"up","do"},
    //   "CMS_my_res_j_XXXX"
    // );
    // varied_df = varied_df.Vary(
    //   "CleanJet_phi",
    //   "ROOT::RVec<ROOT::RVecF>{CleanJet_phi_myJERUp, CleanJet_phi_myJERDown}",
    //   {"up","do"},
    //   "CMS_my_res_j_XXXX"
    // );

    for (int ivariation = 0; ivariation<Nvariation; ivariation++) {
      varied_df = varied_df.Vary(
        "CleanJet_pt",
        "ROOT::RVec<ROOT::RVecF>{__" + std::to_string(ivariation) + "CleanJet_pt_myJERUp, __" + std::to_string(ivariation) + "CleanJet_pt_myJERDown}",
        {"up","do"},
        "__NORM__" + std::to_string(ivariation) + "_CMS_my_res_j_XXXX"
      );
      varied_df = varied_df.Vary(
        "CleanJet_eta",
        "ROOT::RVec<ROOT::RVecF>{__" + std::to_string(ivariation) + "CleanJet_eta_myJERUp, __" + std::to_string(ivariation) + "CleanJet_eta_myJERDown}",
        {"up","do"},
        "__NORM__" + std::to_string(ivariation) + "_CMS_my_res_j_XXXX"
      );
      varied_df = varied_df.Vary(
        "CleanJet_phi",
        "ROOT::RVec<ROOT::RVecF>{__" + std::to_string(ivariation) + "CleanJet_phi_myJERUp, __" + std::to_string(ivariation) + "CleanJet_phi_myJERDown}",
        {"up","do"},
        "__NORM__" + std::to_string(ivariation) + "_CMS_my_res_j_XXXX"
      );
    }

    // suffix_size = 6;
    // for (const auto& branch : varBranches_JERup) {
    //   if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "myJERup") == 0 ) {
    //     std::string nomCol = branch.substr(0, branch.size() - suffix_size);
    //     std::cout << " nomCol = " << nomCol << std::endl;
    //     if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
    //       std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
    //       varied_df = varied_df.Vary(
    //         nomCol,
    //         expression,
    //         {"up"},
    //         "CMS_res_j_2018"
    //       );
    //     };
    //   };
    // };
    //
    // suffix_size = 6;
    // for (const auto& branch : varBranches_JERdo) {
    //   if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "myJERdo") == 0 ) {
    //     std::string nomCol = branch.substr(0, branch.size() - suffix_size);
    //     if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
    //       std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
    //       varied_df = varied_df.Vary(
    //         nomCol,
    //         expression,
    //         {"do"},
    //         "CMS_res_j_2018"
    //       );
    //     };
    //   };
    // };

    // --- Automatically generated define aliases ---

    //  aliases/define needed
    varied_df = SafeDefine(varied_df, "PromptGenLepMatch2l", "(Lepton_promptgenmatched.size() > 0 ? Lepton_promptgenmatched[0] : 0.) * (Lepton_promptgenmatched.size() > 1 ? Lepton_promptgenmatched[0] : 0.)");
    varied_df = SafeDefine(varied_df, "mumu", "(Lepton_pdgId.size() > 0 ? Lepton_pdgId[0] : -99) * (Lepton_pdgId.size() > 1 ? Lepton_pdgId[1]: -99) == -13*13");
    varied_df = SafeDefine(varied_df, "ee", "(Lepton_pdgId.size() > 0 ? Lepton_pdgId[0] : -99) * (Lepton_pdgId.size() > 1 ? Lepton_pdgId[1]: -99) == -11*11");
    varied_df = SafeDefine(varied_df, "LepWPCut", "LepCut2l__ele_mvaFall17V2Iso_WP90_SS_tthmva_70__mu_cut_Tight_HWWW_tthmva_80");
    varied_df = SafeDefine(varied_df, "bVeto", "ROOT::VecOps::Sum(Take(Jet_btagDeepB,CleanJet_jetIdx)[CleanJet_pt > 20 && abs(CleanJet_eta) < 2.5] > 0.4184) == 0");
    varied_df = SafeDefine(varied_df, "bReq", "ROOT::VecOps::Sum(Take(Jet_btagDeepB,CleanJet_jetIdx)[CleanJet_pt > 20 && abs(CleanJet_eta) < 2.5] > 0.4184) >= 1");
    varied_df = SafeDefine(varied_df, "bVetoSF", "ROOT::VecOps::Product(Take(Jet_btagSF_deepcsv_shape,CleanJet_jetIdx)[CleanJet_pt > 20 && abs(CleanJet_eta) < 2.5])");
    varied_df = SafeDefine(varied_df, "bReqSF", "ROOT::VecOps::Product(Take(Jet_btagSF_deepcsv_shape,CleanJet_jetIdx)[CleanJet_pt > 30 && abs(CleanJet_eta) < 2.5])");
    varied_df = SafeDefine(varied_df, "btagSF", "bVeto*bVetoSF + bReq*bReqSF");
    varied_df = SafeDefine(varied_df, "Jet_PUIDSF", "ROOT::VecOps::Product(Jet_PUIDSF_loose[Jet_jetId>=2])");
    varied_df = SafeDefine(varied_df, "Jet_PUIDSF_up", "ROOT::VecOps::Product(Jet_PUIDSF_loose_up[Jet_jetId>=2])");
    varied_df = SafeDefine(varied_df, "Jet_PUIDSF_down", "ROOT::VecOps::Product(Jet_PUIDSF_loose_down[Jet_jetId>=2])");
    varied_df = SafeDefine(varied_df, "LepWPSF", "LepSF2l__ele_mvaFall17V2Iso_WP90_SS_tthmva_70__mu_cut_Tight_HWWW_tthmva_80");
    varied_df = SafeDefine(varied_df, "SFweightEleUp", "LepSF2l__ele_mvaFall17V2Iso_WP90_SS_tthmva_70__Up");
    varied_df = SafeDefine(varied_df, "SFweightEleDown", "LepSF2l__ele_mvaFall17V2Iso_WP90_SS_tthmva_70__Do");
    varied_df = SafeDefine(varied_df, "SFweightMuUp", "LepSF2l__mu_cut_Tight_HWWW_tthmva_80__Up");
    varied_df = SafeDefine(varied_df, "SFweightMuDown", "LepSF2l__mu_cut_Tight_HWWW_tthmva_80__Do");
    varied_df = SafeDefine(varied_df, "ptj1", "CleanJet_pt.size() > 0 ? CleanJet_pt[0] : -9999.");
    varied_df = SafeDefine(varied_df, "njet", "Sum(CleanJet_pt>30)");


    // ----------------------------------------

    // --- Automatically generated define aliases for functions, no JIT ---

    //  aliases of functions
    varied_df = varied_df
                     .Define("_var_myVariableMll_0", "Lepton_pt[0]")
                     .Define("_var_myVariableMll_1", "Lepton_eta[0]")
                     .Define("_var_myVariableMll_2", "Lepton_phi[0]")
                     .Define("_var_myVariableMll_3", "Lepton_pt[1]")
                     .Define("_var_myVariableMll_4", "Lepton_eta[1]")
                     .Define("_var_myVariableMll_5", "Lepton_phi[1]");

    varied_df = varied_df.Define("myVariableMll", calculate_mass, { "_var_myVariableMll_0", "_var_myVariableMll_1", "_var_myVariableMll_2", "_var_myVariableMll_3", "_var_myVariableMll_4", "_var_myVariableMll_5" } );

    varied_df = varied_df
                     .Define("_var_myVariableBDT_0_f", "(float)pt1")
                     .Define("_var_myVariableBDT_1_f", "(float)ptj1")
                     .Define("_var_myVariableBDT_2_f", "(float)mll")
                     .Define("_var_myVariableBDT_3_f", "(float)njet");

    TMVA::Experimental::RReader my_model_myVariableBDT("/afs/cern.ch/work/a/amassiro/Latinos/Framework/RDF/plotsConfigurationsRDF/WW/2018/code/TMVAClassification_BDTG.weights.xml");
    varied_df = varied_df.Define("myVariableBDT",
                     TMVA::Experimental::Compute<4, float>(my_model_myVariableBDT),
                     { "_var_myVariableBDT_0_f", "_var_myVariableBDT_1_f", "_var_myVariableBDT_2_f", "_var_myVariableBDT_3_f" });



    // ----------------------------------------

    // --- Automatically generated define weights ---

    //  weigths needed
    varied_df = SafeDefine(varied_df, "my_sample_weight", "(XSWeight * SFweight2l * LepWPCut * LepWPSF * Jet_PUIDSF * btagSF * METFilter_MC * PromptGenLepMatch2l) * 59.83");


    // ----------------------------------------


    // --- Automatically generated register nuisances variations ---

    //  Register the variations
    varied_df = varied_df.Vary(
      "my_sample_weight",
      "ROOT::RVecD{(my_sample_weight) * TriggerSFWeight_2l_u/TriggerSFWeight_2l,(my_sample_weight) * TriggerSFWeight_2l_d/TriggerSFWeight_2l}",
      {"up", "do"},
      "CMS_eff_hwwtrigger_2018"
      );
    // varied_df = varied_df.Vary(
    //   "my_sample_weight",
    //   "ROOT::RVecD{(my_sample_weight) * SFweightEleUp,(my_sample_weight) * SFweightEleDown}",
    //   {"up", "do"},
    //   "CMS_eff_e_2018"
    //   );
    // varied_df = varied_df.Vary(
    //   "my_sample_weight",
    //   "ROOT::RVecD{(XSWeight * SFweight2l * LepWPCut * LepWPSF*SFweightMuUp * Jet_PUIDSF * btagSF * METFilter_MC * PromptGenLepMatch2l) * 59.83,(XSWeight * SFweight2l * LepWPCut * LepWPSF*SFweightMuDown * Jet_PUIDSF * btagSF * METFilter_MC * PromptGenLepMatch2l) * 59.83}",
    //   {"up", "do"},
    //   "eff_m_2018"
    //   );
    // varied_df = varied_df.Vary(
    //   "my_sample_weight",
    //   "ROOT::RVecD{(my_sample_weight) * Jet_PUIDSF_up/Jet_PUIDSF,(my_sample_weight) * Jet_PUIDSF_down/Jet_PUIDSF}",
    //   {"up", "do"},
    //   "CMS_PUID_2018"
    //   );
    // varied_df = varied_df.Vary(
    //   "my_sample_weight",
    //   "ROOT::RVecD{(my_sample_weight) * PSWeight[2],(my_sample_weight) * PSWeight[0]}",
    //   {"up", "do"},
    //   "ps_isr"
    //   );
    // varied_df = varied_df.Vary(
    //   "my_sample_weight",
    //   "ROOT::RVecD{(my_sample_weight) * PSWeight[3],(my_sample_weight) * PSWeight[1]}",
    //   {"up", "do"},
    //   "ps_fsr"
    //   );


    // ----------------------------------------

    // --- Automatically generated ... just the main node ---

    //  Initial ...
    auto current_node = ROOT::RDF::RNode(varied_df);


    //
    // from now on: current_node
    // ----------------------------------------

    // --- Automatically generated define cuts and histograms ---

    //  I need to define the RNode, otherwise SafeDefine will not work
    // Define variables 
    current_node = SafeDefine(current_node, "events", "1");
    current_node = SafeDefine(current_node, "ptj1", "CleanJet_pt.size() > 0 ? CleanJet_pt[0] : -9999.");
    current_node = SafeDefine(current_node, "ptj2", "CleanJet_pt.size() > 1 ? CleanJet_pt[1] : -9999.");
    current_node = SafeDefine(current_node, "ptl1", "Lepton_pt.size() > 0 ? Lepton_pt[0] : -9999.");
    current_node = SafeDefine(current_node, "mll", "mll");
    current_node = SafeDefine(current_node, "mll_mybins", "mll");
    current_node = SafeDefine(current_node, "njet", "Sum(CleanJet_pt>30)");
    current_node = SafeDefine(current_node, "BDT", "myVariableBDT");
    current_node = current_node.Filter("  (Lepton_pdgId.size() > 0 ? Lepton_pt[0]: -99) > 25            && (Lepton_pdgId.size() > 1 ? Lepton_pt[1]: -99) > 10            && abs(Lepton_pdgId.size() > 0 ? Lepton_eta[0]: -99) < 2.5            && abs(Lepton_pdgId.size() > 1 ? Lepton_eta[1]: -99) < 2.5 ", "supercut");
    auto node_jets2 = current_node.Filter("njet==2", "jets2");
    ROOT::RDF::RNode node_jets2___DY_Low = node_jets2.Filter("mll<70", "cut_DY_Low");
    node_jets2___DY_Low = SafeDefine(node_jets2___DY_Low, "my_sample_weight_DY_Low", "(my_sample_weight)*1.34");
    ROOT::RDF::RNode node_jets2___DY_High = node_jets2.Filter("mll>70", "cut_DY_High");
    node_jets2___DY_High = SafeDefine(node_jets2___DY_High, "my_sample_weight_DY_High", "(my_sample_weight)*1.00");
    hist_map_1D["jets2"].push_back(node_jets2.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["jets2___DY_Low"].push_back(node_jets2___DY_Low.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_Low"));
    hist_map_1D["jets2___DY_High"].push_back(node_jets2___DY_High.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_High"));
    hist_map_1D["jets2"].push_back(node_jets2.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["jets2___DY_Low"].push_back(node_jets2___DY_Low.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_Low"));
    hist_map_1D["jets2___DY_High"].push_back(node_jets2___DY_High.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_High"));
    hist_map_1D["jets2"].push_back(node_jets2.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["jets2___DY_Low"].push_back(node_jets2___DY_Low.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_Low"));
    hist_map_1D["jets2___DY_High"].push_back(node_jets2___DY_High.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_High"));
    hist_map_1D["jets2"].push_back(node_jets2.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["jets2___DY_Low"].push_back(node_jets2___DY_Low.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_Low"));
    hist_map_1D["jets2___DY_High"].push_back(node_jets2___DY_High.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_High"));
    hist_map_1D["jets2"].push_back(node_jets2.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["jets2___DY_Low"].push_back(node_jets2___DY_Low.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_Low"));
    hist_map_1D["jets2___DY_High"].push_back(node_jets2___DY_High.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_High"));
    hist_map_1D["jets2"].push_back(node_jets2.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_1D["jets2___DY_Low"].push_back(node_jets2___DY_Low.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_Low"));
    hist_map_1D["jets2___DY_High"].push_back(node_jets2___DY_High.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_High"));
    hist_map_2D["jets2"].push_back(node_jets2.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_2D["jets2___DY_Low"].push_back(node_jets2___DY_Low.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_Low"));
    hist_map_2D["jets2___DY_High"].push_back(node_jets2___DY_High.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_High"));
    hist_map_1D["jets2"].push_back(node_jets2.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["jets2___DY_Low"].push_back(node_jets2___DY_Low.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_Low"));
    hist_map_1D["jets2___DY_High"].push_back(node_jets2___DY_High.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_High"));
    hist_map_1D["jets2"].push_back(node_jets2.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    hist_map_1D["jets2___DY_Low"].push_back(node_jets2___DY_Low.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_Low"));
    hist_map_1D["jets2___DY_High"].push_back(node_jets2___DY_High.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_High"));
    auto node_DrellYan_cr = current_node.Filter("(mll>70 && mll<120)", "DrellYan_cr");
    ROOT::RDF::RNode node_DrellYan_cr___DY_Low = node_DrellYan_cr.Filter("mll<70", "cut_DY_Low");
    node_DrellYan_cr___DY_Low = SafeDefine(node_DrellYan_cr___DY_Low, "my_sample_weight_DY_Low", "(my_sample_weight)*1.34");
    ROOT::RDF::RNode node_DrellYan_cr___DY_High = node_DrellYan_cr.Filter("mll>70", "cut_DY_High");
    node_DrellYan_cr___DY_High = SafeDefine(node_DrellYan_cr___DY_High, "my_sample_weight_DY_High", "(my_sample_weight)*1.00");
    hist_map_1D["DrellYan_cr"].push_back(node_DrellYan_cr.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["DrellYan_cr___DY_Low"].push_back(node_DrellYan_cr___DY_Low.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr___DY_High"].push_back(node_DrellYan_cr___DY_High.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr"].push_back(node_DrellYan_cr.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["DrellYan_cr___DY_Low"].push_back(node_DrellYan_cr___DY_Low.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr___DY_High"].push_back(node_DrellYan_cr___DY_High.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr"].push_back(node_DrellYan_cr.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["DrellYan_cr___DY_Low"].push_back(node_DrellYan_cr___DY_Low.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr___DY_High"].push_back(node_DrellYan_cr___DY_High.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr"].push_back(node_DrellYan_cr.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["DrellYan_cr___DY_Low"].push_back(node_DrellYan_cr___DY_Low.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr___DY_High"].push_back(node_DrellYan_cr___DY_High.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr"].push_back(node_DrellYan_cr.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["DrellYan_cr___DY_Low"].push_back(node_DrellYan_cr___DY_Low.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr___DY_High"].push_back(node_DrellYan_cr___DY_High.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr"].push_back(node_DrellYan_cr.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_1D["DrellYan_cr___DY_Low"].push_back(node_DrellYan_cr___DY_Low.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr___DY_High"].push_back(node_DrellYan_cr___DY_High.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_High"));
    hist_map_2D["DrellYan_cr"].push_back(node_DrellYan_cr.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_2D["DrellYan_cr___DY_Low"].push_back(node_DrellYan_cr___DY_Low.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_Low"));
    hist_map_2D["DrellYan_cr___DY_High"].push_back(node_DrellYan_cr___DY_High.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr"].push_back(node_DrellYan_cr.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["DrellYan_cr___DY_Low"].push_back(node_DrellYan_cr___DY_Low.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr___DY_High"].push_back(node_DrellYan_cr___DY_High.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr"].push_back(node_DrellYan_cr.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    hist_map_1D["DrellYan_cr___DY_Low"].push_back(node_DrellYan_cr___DY_Low.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr___DY_High"].push_back(node_DrellYan_cr___DY_High.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_High"));
    auto node_DrellYan_cr_eleele = node_DrellYan_cr.Filter("(ee)", "DrellYan_cr_eleele");
    ROOT::RDF::RNode node_DrellYan_cr_eleele___DY_Low = node_DrellYan_cr_eleele.Filter("mll<70", "cut_DY_Low");
    node_DrellYan_cr_eleele___DY_Low = SafeDefine(node_DrellYan_cr_eleele___DY_Low, "my_sample_weight_DY_Low", "(my_sample_weight)*1.34");
    ROOT::RDF::RNode node_DrellYan_cr_eleele___DY_High = node_DrellYan_cr_eleele.Filter("mll>70", "cut_DY_High");
    node_DrellYan_cr_eleele___DY_High = SafeDefine(node_DrellYan_cr_eleele___DY_High, "my_sample_weight_DY_High", "(my_sample_weight)*1.00");
    hist_map_1D["DrellYan_cr_eleele"].push_back(node_DrellYan_cr_eleele.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_eleele___DY_Low"].push_back(node_DrellYan_cr_eleele___DY_Low.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_eleele___DY_High"].push_back(node_DrellYan_cr_eleele___DY_High.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_eleele"].push_back(node_DrellYan_cr_eleele.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_eleele___DY_Low"].push_back(node_DrellYan_cr_eleele___DY_Low.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_eleele___DY_High"].push_back(node_DrellYan_cr_eleele___DY_High.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_eleele"].push_back(node_DrellYan_cr_eleele.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_eleele___DY_Low"].push_back(node_DrellYan_cr_eleele___DY_Low.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_eleele___DY_High"].push_back(node_DrellYan_cr_eleele___DY_High.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_eleele"].push_back(node_DrellYan_cr_eleele.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_eleele___DY_Low"].push_back(node_DrellYan_cr_eleele___DY_Low.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_eleele___DY_High"].push_back(node_DrellYan_cr_eleele___DY_High.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_eleele"].push_back(node_DrellYan_cr_eleele.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_eleele___DY_Low"].push_back(node_DrellYan_cr_eleele___DY_Low.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_eleele___DY_High"].push_back(node_DrellYan_cr_eleele___DY_High.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_eleele"].push_back(node_DrellYan_cr_eleele.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_eleele___DY_Low"].push_back(node_DrellYan_cr_eleele___DY_Low.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_eleele___DY_High"].push_back(node_DrellYan_cr_eleele___DY_High.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_High"));
    hist_map_2D["DrellYan_cr_eleele"].push_back(node_DrellYan_cr_eleele.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_2D["DrellYan_cr_eleele___DY_Low"].push_back(node_DrellYan_cr_eleele___DY_Low.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_Low"));
    hist_map_2D["DrellYan_cr_eleele___DY_High"].push_back(node_DrellYan_cr_eleele___DY_High.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_eleele"].push_back(node_DrellYan_cr_eleele.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_eleele___DY_Low"].push_back(node_DrellYan_cr_eleele___DY_Low.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_eleele___DY_High"].push_back(node_DrellYan_cr_eleele___DY_High.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_eleele"].push_back(node_DrellYan_cr_eleele.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_eleele___DY_Low"].push_back(node_DrellYan_cr_eleele___DY_Low.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_eleele___DY_High"].push_back(node_DrellYan_cr_eleele___DY_High.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_High"));
    auto node_DrellYan_cr_mumu = node_DrellYan_cr.Filter("(mumu)", "DrellYan_cr_mumu");
    ROOT::RDF::RNode node_DrellYan_cr_mumu___DY_Low = node_DrellYan_cr_mumu.Filter("mll<70", "cut_DY_Low");
    node_DrellYan_cr_mumu___DY_Low = SafeDefine(node_DrellYan_cr_mumu___DY_Low, "my_sample_weight_DY_Low", "(my_sample_weight)*1.34");
    ROOT::RDF::RNode node_DrellYan_cr_mumu___DY_High = node_DrellYan_cr_mumu.Filter("mll>70", "cut_DY_High");
    node_DrellYan_cr_mumu___DY_High = SafeDefine(node_DrellYan_cr_mumu___DY_High, "my_sample_weight_DY_High", "(my_sample_weight)*1.00");
    hist_map_1D["DrellYan_cr_mumu"].push_back(node_DrellYan_cr_mumu.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_mumu___DY_Low"].push_back(node_DrellYan_cr_mumu___DY_Low.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_mumu___DY_High"].push_back(node_DrellYan_cr_mumu___DY_High.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_mumu"].push_back(node_DrellYan_cr_mumu.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_mumu___DY_Low"].push_back(node_DrellYan_cr_mumu___DY_Low.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_mumu___DY_High"].push_back(node_DrellYan_cr_mumu___DY_High.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_mumu"].push_back(node_DrellYan_cr_mumu.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_mumu___DY_Low"].push_back(node_DrellYan_cr_mumu___DY_Low.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_mumu___DY_High"].push_back(node_DrellYan_cr_mumu___DY_High.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_mumu"].push_back(node_DrellYan_cr_mumu.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_mumu___DY_Low"].push_back(node_DrellYan_cr_mumu___DY_Low.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_mumu___DY_High"].push_back(node_DrellYan_cr_mumu___DY_High.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_mumu"].push_back(node_DrellYan_cr_mumu.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_mumu___DY_Low"].push_back(node_DrellYan_cr_mumu___DY_Low.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_mumu___DY_High"].push_back(node_DrellYan_cr_mumu___DY_High.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_mumu"].push_back(node_DrellYan_cr_mumu.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_mumu___DY_Low"].push_back(node_DrellYan_cr_mumu___DY_Low.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_mumu___DY_High"].push_back(node_DrellYan_cr_mumu___DY_High.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_High"));
    hist_map_2D["DrellYan_cr_mumu"].push_back(node_DrellYan_cr_mumu.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_2D["DrellYan_cr_mumu___DY_Low"].push_back(node_DrellYan_cr_mumu___DY_Low.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_Low"));
    hist_map_2D["DrellYan_cr_mumu___DY_High"].push_back(node_DrellYan_cr_mumu___DY_High.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_mumu"].push_back(node_DrellYan_cr_mumu.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_mumu___DY_Low"].push_back(node_DrellYan_cr_mumu___DY_Low.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_mumu___DY_High"].push_back(node_DrellYan_cr_mumu___DY_High.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_High"));
    hist_map_1D["DrellYan_cr_mumu"].push_back(node_DrellYan_cr_mumu.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    hist_map_1D["DrellYan_cr_mumu___DY_Low"].push_back(node_DrellYan_cr_mumu___DY_Low.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_Low"));
    hist_map_1D["DrellYan_cr_mumu___DY_High"].push_back(node_DrellYan_cr_mumu___DY_High.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_High"));
    
    std::vector<std::string> list_of_variables_1D;
    std::vector<std::string> list_of_variables_2D;
    std::vector<int> list_of_variables_fold_1D;
    std::vector<int> list_of_variables_fold_2D;
    list_of_variables_1D.push_back("events");
    list_of_variables_fold_1D.push_back(3);
    list_of_variables_1D.push_back("ptj1");
    list_of_variables_fold_1D.push_back(3);
    list_of_variables_1D.push_back("ptj2");
    list_of_variables_fold_1D.push_back(3);
    list_of_variables_1D.push_back("ptl1");
    list_of_variables_fold_1D.push_back(3);
    list_of_variables_1D.push_back("mll");
    list_of_variables_fold_1D.push_back(3);
    list_of_variables_1D.push_back("mll_mybins");
    list_of_variables_fold_1D.push_back(3);
    list_of_variables_2D.push_back("mllVSmth");
    list_of_variables_fold_2D.push_back(3);
    list_of_variables_1D.push_back("njet");
    list_of_variables_fold_1D.push_back(2);
    list_of_variables_1D.push_back("BDT");
    list_of_variables_fold_1D.push_back(3);


    // ----------------------------------------

    //
    // Define variations
    //

    std::vector<ROOT::RDF::Experimental::RResultMap<TH1D>> results_1D_variations;
    std::vector<ROOT::RDF::Experimental::RResultMap<TH2D>> results_2D_variations;

    std::vector<ROOT::RDF::RResultHandle> all_booking_1D;
    std::vector<ROOT::RDF::RResultHandle> all_booking_2D;
    // FIXME: can these be merged?


    for (auto& [cut_label, h_list] : hist_map_1D) {
      for (auto& h : h_list) {
        results_1D_variations.push_back( ROOT::RDF::Experimental::VariationsFor(h) );
        all_booking_1D.push_back(h);
      }
    }

    for (auto& [cut_label, h_list] : hist_map_2D) {
      for (auto& h : h_list) {
        results_2D_variations.push_back( ROOT::RDF::Experimental::VariationsFor(h) );
        all_booking_2D.push_back(h);
      }
    }

    //
    // Now and RunGraphs --> the actual loop on the events
    //

    std::cout << "   ROOT::RDF::RunGraphs 1D" << std::endl;
    if (!hist_map_1D.empty()) {
      ROOT::RDF::RunGraphs(all_booking_1D);
    }

    std::cout << "   ROOT::RDF::RunGraphs 2D" << std::endl;
    if (!hist_map_2D.empty()) {
      ROOT::RDF::RunGraphs(all_booking_2D);
    }


    std::cout << "   Done, now save in the final root file" << std::endl;


    //
    // Prepare to average histograms for specific nuisances
    //
    //         pattern    nuisance-name
    std::map<std::string, std::string> map_nuisances_name_for_averaged_histograms;
    map_nuisances_name_for_averaged_histograms["CMS_my_res_j_XXXX"] = "CMS_res_j_2018_fly";



    //
    // In root file:    <cut>/<variable>/histo_<sample>
    //

    TFile out_file("rootFile/root_file___DY_DYJetsToLL_M-50_10.root", "RECREATE");
    int big_loop = 0;
    for (auto& [cut_label, h_list] : hist_map_1D) {

      std::string current_cut = cut_label;
      // check if subsamples case: this_cutName___sampleName_sub_name
      std::string sub_name = "";
      std::string delimiter = "___";
      size_t pos_triple = cut_label.find(delimiter);
      if (pos_triple != std::string::npos) {
        std::string this_cutName = cut_label.substr(0, pos_triple);
        std::string rest = cut_label.substr(pos_triple + 3);
        std::string sampleName = "DY";
        size_t pos = rest.find(sampleName);
        sub_name = rest.substr(pos + sampleName.length() + 1);
        current_cut = this_cutName;
      }

      // Create a folder for this cut
      TDirectory *dir = out_file.GetDirectory(current_cut.c_str());
      if (!dir) {
        // If it doesn't exist, create it
        dir = out_file.mkdir(current_cut.c_str());
      }

      for (size_t ivar = 0; ivar < h_list.size(); ivar++) {
        dir->cd();
        TDirectory *subdir = out_file.GetDirectory( (current_cut+"/"+list_of_variables_1D.at(ivar)).c_str() );
        if (!subdir) {
          // If it doesn't exist, create it
          subdir = out_file.mkdir( (current_cut+"/"+list_of_variables_1D.at(ivar)).c_str() );
        }
        subdir->cd();

        // get the nominal and the variations too
        auto all_histos = results_1D_variations.at(big_loop);
        big_loop++;

        std::map<std::string, TH1D> map_nuisances_average_histogram;

        for (auto& [name, histo] : all_histos) {
          std::string temp_name;
          if (name == "nominal") {
            if (sub_name == "") temp_name = "histo_DY";
            else                temp_name = "histo_DY_" + sub_name;
          }
          else {
            temp_name = name.c_str();
            // scale_e_2018_UL:up --> scale_e_2018_ULup
            temp_name.erase(std::remove(temp_name.begin(), temp_name.end(), ':'), temp_name.end());
            //size_t pos = temp_name.find(':');
            //if (pos != std::string::npos) {
            //  temp_name = temp_name.substr(0, pos);
            //}
            if (sub_name == "") temp_name = ("histo_DY_" + temp_name);
            else                temp_name = ("histo_DY_" + sub_name + "_" + temp_name);
          }
          gDirectory = subdir;
          histo->SetName(temp_name.c_str());

          if (list_of_variables_fold_1D.at(ivar) != 0) FoldHistogram(histo.get(), list_of_variables_fold_1D.at(ivar));

          // check if it's a histogram to be averaged
          // std::regex pattern("histo_DY_" + "__NORM__[0-9]+_CMS_my_res_j_XXXX");


          bool found_any_nuisances_for_averaged_histograms = false;
          for (auto const& [string_pattern, nuisance_name] : map_nuisances_name_for_averaged_histograms) {

            std::string string_pattern_up = "histo_.*__NORM__.*_" + string_pattern + "up";
            std::string string_pattern_do = "histo_.*__NORM__.*_" + string_pattern + "do";

            std::regex pattern_up(string_pattern_up);
            std::regex pattern_do(string_pattern_do);

            if (std::regex_search(temp_name, pattern_up) || std::regex_search(temp_name, pattern_do)) {
              std::regex pattern_to_remove("__NORM__[0-9]+_");
              std::string histo_temp_name = std::regex_replace(temp_name, pattern_to_remove, "");
              std::regex pattern(string_pattern);

              histo_temp_name = std::regex_replace(histo_temp_name, pattern, nuisance_name); // replace with real nuisance name

              histo->SetName(histo_temp_name.c_str());

              if (std::regex_search(temp_name, pattern_up)) {
                if (auto it = map_nuisances_average_histogram.find(string_pattern + "up"); it != map_nuisances_average_histogram.end()) {
                  it->second.Add(histo.get(), 0.333); // 0.333 = 1/3.
                }
                else {
                  map_nuisances_average_histogram[nuisance_name + "up"] = (*histo);
                  found_any_nuisances_for_averaged_histograms = true;
                  break; // end loop over map to save time
                }
              }
              else {
                if (auto it = map_nuisances_average_histogram.find(string_pattern + "do"); it != map_nuisances_average_histogram.end()) {
                  it->second.Add(histo.get(), 0.333); // 0.333 = 1/3.
                }
                else {
                  map_nuisances_average_histogram[nuisance_name + "do"] = (*histo);
                  found_any_nuisances_for_averaged_histograms = true;
                  break; // end loop over map to save time
                }
              }
            }
          }
          // if it's NOT a histogram to be averaged, then write it directly
          if (not found_any_nuisances_for_averaged_histograms) {
            histo->Write();
          }
        }

        // now write all the averaged histograms, up and down variations
        for (auto const& [name, histo] : map_nuisances_average_histogram) {
          histo.Write();
        }

      }
      out_file.cd(); // Go back to root for the next directory
    }

    big_loop = 0;
    for (auto& [cut_label, h_list] : hist_map_2D) {

      std::string current_cut = cut_label;
      // check if subsamples case: this_cutName___sampleName_sub_name
      std::string sub_name = "";
      std::string delimiter = "___";
      size_t pos_triple = cut_label.find(delimiter);
      if (pos_triple != std::string::npos) {
        std::string this_cutName = cut_label.substr(0, pos_triple);
        std::string rest = cut_label.substr(pos_triple + 3);
        std::string sampleName = "DY";
        size_t pos = cut_label.find(sampleName);
        sub_name = cut_label.substr(pos + sampleName.length() + 1);
        current_cut = this_cutName;
      }

      // Create a folder for this cut
      TDirectory *dir = out_file.GetDirectory(current_cut.c_str());
      if (!dir) {
        // If it doesn't exist, create it
        dir = out_file.mkdir(current_cut.c_str());
      }
      for (size_t ivar = 0; ivar < h_list.size(); ivar++) {
        dir->cd();
        TDirectory *subdir = out_file.GetDirectory( (current_cut+"/"+list_of_variables_2D.at(ivar)).c_str() );
        if (!subdir) {
          // If it doesn't exist, create it
          subdir = out_file.mkdir( (current_cut+"/"+list_of_variables_2D.at(ivar)).c_str() );
        }
        subdir->cd();

        // get the nominal and the variations too
        auto all_histos = results_2D_variations.at(big_loop);
        big_loop++;

        for (auto& [name, histo] : all_histos) {
          std::string temp_name;
          if (name == "nominal") {
            if (sub_name == "") temp_name = "histo_DY";
            else                temp_name = "histo_DY_" + sub_name;
          }
          else {
            temp_name = name.c_str();
            // scale_e_2018_UL:up --> scale_e_2018_ULup
            temp_name.erase(std::remove(temp_name.begin(), temp_name.end(), ':'), temp_name.end());
            //size_t pos = temp_name.find(':');
            //if (pos != std::string::npos) {
            //  temp_name = temp_name.substr(0, pos);
            //}
            if (sub_name == "") temp_name = ("histo_DY_" + temp_name);
            else                temp_name = ("histo_DY_" + sub_name + "_" + temp_name);
          }
          gDirectory = subdir;
          histo->SetName(temp_name.c_str());


          if (list_of_variables_fold_2D.at(ivar) != 0) FoldHistogram(histo.get(), list_of_variables_fold_2D.at(ivar));

          UnrollHistogram(dynamic_cast<TH2D*>(histo.get()))->Write();

        }
      }
      out_file.cd(); // Go back to root for the next directory
    }



    out_file.Close();

    return 0;
}

        
