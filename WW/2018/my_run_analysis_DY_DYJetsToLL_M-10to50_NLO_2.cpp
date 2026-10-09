

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






// ----------------------------------------



// --- Automatically generated: code to be added for special nuisances ---



// ----------------------------------------


int main() {
    ROOT::EnableImplicitMT();

    // --- Automatically generated input root files ---

    //  Nominal input files
    auto* nominal = new TChain("Events");
    nominal->Add("root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9/nanoLatino_DYJetsToLL_M-10to50_NLO__part6.root");
    nominal->Add("root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9/nanoLatino_DYJetsToLL_M-10to50_NLO__part7.root");
    nominal->Add("root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9/nanoLatino_DYJetsToLL_M-10to50_NLO__part8.root");
    
    auto nominalBranches = getBranchNames(nominal);
    
//  Variations input files (if any)
    auto* friend_JERup = new TChain("Events");
    auto* friend_JERdo = new TChain("Events");
    friend_JERup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__JERup_suffix/nanoLatino_DYJetsToLL_M-10to50_NLO__part6.root");
    friend_JERdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__JERdo_suffix/nanoLatino_DYJetsToLL_M-10to50_NLO__part6.root");
    friend_JERup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__JERup_suffix/nanoLatino_DYJetsToLL_M-10to50_NLO__part7.root");
    friend_JERdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__JERdo_suffix/nanoLatino_DYJetsToLL_M-10to50_NLO__part7.root");
    friend_JERup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__JERup_suffix/nanoLatino_DYJetsToLL_M-10to50_NLO__part8.root");
    friend_JERdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__JERdo_suffix/nanoLatino_DYJetsToLL_M-10to50_NLO__part8.root");
    nominal->AddFriend(friend_JERup, "JERup");
    nominal->AddFriend(friend_JERdo, "JERdo");
    auto varBranches_JERup = getBranchNames(friend_JERup);
    auto varBranches_JERdo = getBranchNames(friend_JERdo);
    ROOT::RDataFrame base_df(*nominal);
    auto varied_df = ROOT::RDF::RNode(base_df);


    // ----------------------------------------

    std::map<std::string, std::vector<ROOT::RDF::RResultPtr<TH1D>>> hist_map_1D;
    std::map<std::string, std::vector<ROOT::RDF::RResultPtr<TH2D>>> hist_map_2D;

    // --- Automatically generated register nuisances variations for alternative trees ---
    //        Alternative trees variation nuisances to be defined at the beginning because they might change the
    //        variables that are defined downstream, e.g. njet, BDT(ptjet, ptlepton, ...)
    //

    
    int suffix_size = 0;
    suffix_size = 6;
    for (const auto& branch : varBranches_JERup) {
      if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JERup") == 0 ) {
        std::string nomCol = branch.substr(0, branch.size() - suffix_size);
        if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
          std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
          varied_df = varied_df.Vary(
                                    nomCol,
                                    expression,
                                    {"up"},
                                    "CMS_res_j_2018"
                                    );
        };
      };
    };
    
    suffix_size = 6;
    for (const auto& branch : varBranches_JERdo) {
      if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "JERdo") == 0 ) {
        std::string nomCol = branch.substr(0, branch.size() - suffix_size);
        if (std::find(nominalBranches.begin(), nominalBranches.end(), nomCol) != nominalBranches.end()) {
          std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{static_cast<" + varied_df.GetColumnType(nomCol) + ">(" + branch + ")}";
          varied_df = varied_df.Vary(
                                    nomCol,
                                    expression,
                                    {"do"},
                                    "CMS_res_j_2018"
                                    );
        };
      };
    };




    // --- Automatically generated register nuisances variations for alternative-like trees, as they are calculated on the fly ---

    

    // ----------------------------------------

    // --- Automatically generated define aliases ---

    //  aliases/define needed
    varied_df = SafeDefine(varied_df, "PromptGenLepMatch2l", "(Lepton_promptgenmatched.size() > 0 ? Lepton_promptgenmatched[0] : 0.) * (Lepton_promptgenmatched.size() > 1 ? Lepton_promptgenmatched[0] : 0.)");
    varied_df = SafeDefine(varied_df, "mumu", "(Lepton_pdgId.size() > 0 ? Lepton_pdgId[0] : -99) * (Lepton_pdgId.size() > 1 ? Lepton_pdgId[1]: -99) == -13*13");
    varied_df = SafeDefine(varied_df, "ee", "(Lepton_pdgId.size() > 0 ? Lepton_pdgId[0] : -99) * (Lepton_pdgId.size() > 1 ? Lepton_pdgId[1]: -99) == -11*11");
    varied_df = SafeDefine(varied_df, "LepWPCut", "LepCut2l__ele_mvaFall17V2Iso_WP90_tthmva_70__mu_cut_Tight_HWWW_tthmva_80");
    varied_df = SafeDefine(varied_df, "bVeto", "ROOT::VecOps::Sum(Take(Jet_btagDeepB,CleanJet_jetIdx)[CleanJet_pt > 20 && abs(CleanJet_eta) < 2.5] > 0.4168) == 0");
    varied_df = SafeDefine(varied_df, "bReq", "ROOT::VecOps::Sum(Take(Jet_btagDeepB,CleanJet_jetIdx)[CleanJet_pt > 20 && abs(CleanJet_eta) < 2.5] > 0.4168) >= 1");
    varied_df = SafeDefine(varied_df, "bVetoSF", "ROOT::VecOps::Product(Take(Jet_btagSF_deepcsv_shape,CleanJet_jetIdx)[CleanJet_pt > 20 && abs(CleanJet_eta) < 2.5])");
    varied_df = SafeDefine(varied_df, "bReqSF", "ROOT::VecOps::Product(Take(Jet_btagSF_deepcsv_shape,CleanJet_jetIdx)[CleanJet_pt > 30 && abs(CleanJet_eta) < 2.5])");
    varied_df = SafeDefine(varied_df, "btagSF", "bVeto*bVetoSF + bReq*bReqSF");
    varied_df = SafeDefine(varied_df, "Jet_PUIDSF", "ROOT::VecOps::Product(Jet_PUIDSF_loose[Jet_jetId>=2])");
    varied_df = SafeDefine(varied_df, "Jet_PUIDSF_up", "ROOT::VecOps::Product(Jet_PUIDSF_loose_up[Jet_jetId>=2])");
    varied_df = SafeDefine(varied_df, "Jet_PUIDSF_down", "ROOT::VecOps::Product(Jet_PUIDSF_loose_down[Jet_jetId>=2])");
    varied_df = SafeDefine(varied_df, "LepWPSF", "LepSF2l__ele_mvaFall17V2Iso_WP90_tthmva_70__mu_cut_Tight_HWWW_tthmva_80");
    varied_df = SafeDefine(varied_df, "SFweightEleUp", "LepSF2l__ele_mvaFall17V2Iso_WP90_tthmva_70__Up");
    varied_df = SafeDefine(varied_df, "SFweightEleDown", "LepSF2l__ele_mvaFall17V2Iso_WP90_tthmva_70__Do");
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
    varied_df = varied_df.Vary(
      "my_sample_weight",
      "ROOT::RVecD{(my_sample_weight) * SFweightEleUp,(my_sample_weight) * SFweightEleDown}",
      {"up", "do"},
      "CMS_eff_e_2018"
      );
    varied_df = varied_df.Vary(
      "my_sample_weight",
      "ROOT::RVecD{(my_sample_weight) * SFweightMuUp,(my_sample_weight) * SFweightMuDown}",
      {"up", "do"},
      "CMS_eff_m_2018"
      );
    varied_df = varied_df.Vary(
      "my_sample_weight",
      "ROOT::RVecD{(my_sample_weight) * Jet_PUIDSF_up/Jet_PUIDSF,(my_sample_weight) * Jet_PUIDSF_down/Jet_PUIDSF}",
      {"up", "do"},
      "CMS_PUID_2018"
      );


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
    auto node_lowmll_ee = current_node.Filter("mll>40 && mll<120 && ee", "lowmll_ee");
    ROOT::RDF::RNode node_lowmll_ee___DY_Low = node_lowmll_ee.Filter("mll<70", "cut_DY_Low");
    node_lowmll_ee___DY_Low = SafeDefine(node_lowmll_ee___DY_Low, "my_sample_weight_DY_Low", "(my_sample_weight)*1.00");
    ROOT::RDF::RNode node_lowmll_ee___DY_High = node_lowmll_ee.Filter("mll>70", "cut_DY_High");
    node_lowmll_ee___DY_High = SafeDefine(node_lowmll_ee___DY_High, "my_sample_weight_DY_High", "(my_sample_weight)*1.00");
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["lowmll_ee___DY_Low"].push_back(node_lowmll_ee___DY_Low.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_ee___DY_High"].push_back(node_lowmll_ee___DY_High.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["lowmll_ee___DY_Low"].push_back(node_lowmll_ee___DY_Low.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_ee___DY_High"].push_back(node_lowmll_ee___DY_High.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["lowmll_ee___DY_Low"].push_back(node_lowmll_ee___DY_Low.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_ee___DY_High"].push_back(node_lowmll_ee___DY_High.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["lowmll_ee___DY_Low"].push_back(node_lowmll_ee___DY_Low.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_ee___DY_High"].push_back(node_lowmll_ee___DY_High.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["lowmll_ee___DY_Low"].push_back(node_lowmll_ee___DY_Low.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_ee___DY_High"].push_back(node_lowmll_ee___DY_High.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_1D["lowmll_ee___DY_Low"].push_back(node_lowmll_ee___DY_Low.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_ee___DY_High"].push_back(node_lowmll_ee___DY_High.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_High"));
    hist_map_2D["lowmll_ee"].push_back(node_lowmll_ee.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_2D["lowmll_ee___DY_Low"].push_back(node_lowmll_ee___DY_Low.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_Low"));
    hist_map_2D["lowmll_ee___DY_High"].push_back(node_lowmll_ee___DY_High.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["lowmll_ee___DY_Low"].push_back(node_lowmll_ee___DY_Low.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_ee___DY_High"].push_back(node_lowmll_ee___DY_High.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    hist_map_1D["lowmll_ee___DY_Low"].push_back(node_lowmll_ee___DY_Low.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_ee___DY_High"].push_back(node_lowmll_ee___DY_High.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_High"));
    auto node_highmll_ee = current_node.Filter("mll>120 && ee", "highmll_ee");
    ROOT::RDF::RNode node_highmll_ee___DY_Low = node_highmll_ee.Filter("mll<70", "cut_DY_Low");
    node_highmll_ee___DY_Low = SafeDefine(node_highmll_ee___DY_Low, "my_sample_weight_DY_Low", "(my_sample_weight)*1.00");
    ROOT::RDF::RNode node_highmll_ee___DY_High = node_highmll_ee.Filter("mll>70", "cut_DY_High");
    node_highmll_ee___DY_High = SafeDefine(node_highmll_ee___DY_High, "my_sample_weight_DY_High", "(my_sample_weight)*1.00");
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["highmll_ee___DY_Low"].push_back(node_highmll_ee___DY_Low.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_ee___DY_High"].push_back(node_highmll_ee___DY_High.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["highmll_ee___DY_Low"].push_back(node_highmll_ee___DY_Low.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_ee___DY_High"].push_back(node_highmll_ee___DY_High.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["highmll_ee___DY_Low"].push_back(node_highmll_ee___DY_Low.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_ee___DY_High"].push_back(node_highmll_ee___DY_High.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["highmll_ee___DY_Low"].push_back(node_highmll_ee___DY_Low.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_ee___DY_High"].push_back(node_highmll_ee___DY_High.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["highmll_ee___DY_Low"].push_back(node_highmll_ee___DY_Low.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_ee___DY_High"].push_back(node_highmll_ee___DY_High.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_1D["highmll_ee___DY_Low"].push_back(node_highmll_ee___DY_Low.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_ee___DY_High"].push_back(node_highmll_ee___DY_High.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_High"));
    hist_map_2D["highmll_ee"].push_back(node_highmll_ee.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_2D["highmll_ee___DY_Low"].push_back(node_highmll_ee___DY_Low.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_Low"));
    hist_map_2D["highmll_ee___DY_High"].push_back(node_highmll_ee___DY_High.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["highmll_ee___DY_Low"].push_back(node_highmll_ee___DY_Low.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_ee___DY_High"].push_back(node_highmll_ee___DY_High.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    hist_map_1D["highmll_ee___DY_Low"].push_back(node_highmll_ee___DY_Low.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_ee___DY_High"].push_back(node_highmll_ee___DY_High.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_High"));
    auto node_lowmll_mumu = current_node.Filter("mll>40 && mll<120  && mumu", "lowmll_mumu");
    ROOT::RDF::RNode node_lowmll_mumu___DY_Low = node_lowmll_mumu.Filter("mll<70", "cut_DY_Low");
    node_lowmll_mumu___DY_Low = SafeDefine(node_lowmll_mumu___DY_Low, "my_sample_weight_DY_Low", "(my_sample_weight)*1.00");
    ROOT::RDF::RNode node_lowmll_mumu___DY_High = node_lowmll_mumu.Filter("mll>70", "cut_DY_High");
    node_lowmll_mumu___DY_High = SafeDefine(node_lowmll_mumu___DY_High, "my_sample_weight_DY_High", "(my_sample_weight)*1.00");
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["lowmll_mumu___DY_Low"].push_back(node_lowmll_mumu___DY_Low.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_mumu___DY_High"].push_back(node_lowmll_mumu___DY_High.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["lowmll_mumu___DY_Low"].push_back(node_lowmll_mumu___DY_Low.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_mumu___DY_High"].push_back(node_lowmll_mumu___DY_High.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["lowmll_mumu___DY_Low"].push_back(node_lowmll_mumu___DY_Low.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_mumu___DY_High"].push_back(node_lowmll_mumu___DY_High.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["lowmll_mumu___DY_Low"].push_back(node_lowmll_mumu___DY_Low.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_mumu___DY_High"].push_back(node_lowmll_mumu___DY_High.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["lowmll_mumu___DY_Low"].push_back(node_lowmll_mumu___DY_Low.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_mumu___DY_High"].push_back(node_lowmll_mumu___DY_High.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_1D["lowmll_mumu___DY_Low"].push_back(node_lowmll_mumu___DY_Low.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_mumu___DY_High"].push_back(node_lowmll_mumu___DY_High.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_High"));
    hist_map_2D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_2D["lowmll_mumu___DY_Low"].push_back(node_lowmll_mumu___DY_Low.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_Low"));
    hist_map_2D["lowmll_mumu___DY_High"].push_back(node_lowmll_mumu___DY_High.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["lowmll_mumu___DY_Low"].push_back(node_lowmll_mumu___DY_Low.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_mumu___DY_High"].push_back(node_lowmll_mumu___DY_High.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_High"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    hist_map_1D["lowmll_mumu___DY_Low"].push_back(node_lowmll_mumu___DY_Low.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_Low"));
    hist_map_1D["lowmll_mumu___DY_High"].push_back(node_lowmll_mumu___DY_High.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_High"));
    auto node_highmll_mumu = current_node.Filter("mll>120 && mumu", "highmll_mumu");
    ROOT::RDF::RNode node_highmll_mumu___DY_Low = node_highmll_mumu.Filter("mll<70", "cut_DY_Low");
    node_highmll_mumu___DY_Low = SafeDefine(node_highmll_mumu___DY_Low, "my_sample_weight_DY_Low", "(my_sample_weight)*1.00");
    ROOT::RDF::RNode node_highmll_mumu___DY_High = node_highmll_mumu.Filter("mll>70", "cut_DY_High");
    node_highmll_mumu___DY_High = SafeDefine(node_highmll_mumu___DY_High, "my_sample_weight_DY_High", "(my_sample_weight)*1.00");
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["highmll_mumu___DY_Low"].push_back(node_highmll_mumu___DY_Low.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_mumu___DY_High"].push_back(node_highmll_mumu___DY_High.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["highmll_mumu___DY_Low"].push_back(node_highmll_mumu___DY_Low.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_mumu___DY_High"].push_back(node_highmll_mumu___DY_High.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["highmll_mumu___DY_Low"].push_back(node_highmll_mumu___DY_Low.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_mumu___DY_High"].push_back(node_highmll_mumu___DY_High.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["highmll_mumu___DY_Low"].push_back(node_highmll_mumu___DY_Low.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_mumu___DY_High"].push_back(node_highmll_mumu___DY_High.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["highmll_mumu___DY_Low"].push_back(node_highmll_mumu___DY_Low.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_mumu___DY_High"].push_back(node_highmll_mumu___DY_High.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_1D["highmll_mumu___DY_Low"].push_back(node_highmll_mumu___DY_Low.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_mumu___DY_High"].push_back(node_highmll_mumu___DY_High.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_High"));
    hist_map_2D["highmll_mumu"].push_back(node_highmll_mumu.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_2D["highmll_mumu___DY_Low"].push_back(node_highmll_mumu___DY_Low.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_Low"));
    hist_map_2D["highmll_mumu___DY_High"].push_back(node_highmll_mumu___DY_High.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["highmll_mumu___DY_Low"].push_back(node_highmll_mumu___DY_Low.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_mumu___DY_High"].push_back(node_highmll_mumu___DY_High.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_High"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    hist_map_1D["highmll_mumu___DY_Low"].push_back(node_highmll_mumu___DY_Low.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_Low"));
    hist_map_1D["highmll_mumu___DY_High"].push_back(node_highmll_mumu___DY_High.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_High"));
    auto node_DY_cr = current_node.Filter("(mll>70 && mll<120)", "DY_cr");
    ROOT::RDF::RNode node_DY_cr___DY_Low = node_DY_cr.Filter("mll<70", "cut_DY_Low");
    node_DY_cr___DY_Low = SafeDefine(node_DY_cr___DY_Low, "my_sample_weight_DY_Low", "(my_sample_weight)*1.00");
    ROOT::RDF::RNode node_DY_cr___DY_High = node_DY_cr.Filter("mll>70", "cut_DY_High");
    node_DY_cr___DY_High = SafeDefine(node_DY_cr___DY_High, "my_sample_weight_DY_High", "(my_sample_weight)*1.00");
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["DY_cr___DY_Low"].push_back(node_DY_cr___DY_Low.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr___DY_High"].push_back(node_DY_cr___DY_High.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["DY_cr___DY_Low"].push_back(node_DY_cr___DY_Low.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr___DY_High"].push_back(node_DY_cr___DY_High.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["DY_cr___DY_Low"].push_back(node_DY_cr___DY_Low.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr___DY_High"].push_back(node_DY_cr___DY_High.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["DY_cr___DY_Low"].push_back(node_DY_cr___DY_Low.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr___DY_High"].push_back(node_DY_cr___DY_High.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["DY_cr___DY_Low"].push_back(node_DY_cr___DY_Low.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr___DY_High"].push_back(node_DY_cr___DY_High.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_1D["DY_cr___DY_Low"].push_back(node_DY_cr___DY_Low.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr___DY_High"].push_back(node_DY_cr___DY_High.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_High"));
    hist_map_2D["DY_cr"].push_back(node_DY_cr.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_2D["DY_cr___DY_Low"].push_back(node_DY_cr___DY_Low.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_Low"));
    hist_map_2D["DY_cr___DY_High"].push_back(node_DY_cr___DY_High.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["DY_cr___DY_Low"].push_back(node_DY_cr___DY_Low.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr___DY_High"].push_back(node_DY_cr___DY_High.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    hist_map_1D["DY_cr___DY_Low"].push_back(node_DY_cr___DY_Low.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr___DY_High"].push_back(node_DY_cr___DY_High.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_High"));
    auto node_DY_cr_eleele = node_DY_cr.Filter("(ee)", "DY_cr_eleele");
    ROOT::RDF::RNode node_DY_cr_eleele___DY_Low = node_DY_cr_eleele.Filter("mll<70", "cut_DY_Low");
    node_DY_cr_eleele___DY_Low = SafeDefine(node_DY_cr_eleele___DY_Low, "my_sample_weight_DY_Low", "(my_sample_weight)*1.00");
    ROOT::RDF::RNode node_DY_cr_eleele___DY_High = node_DY_cr_eleele.Filter("mll>70", "cut_DY_High");
    node_DY_cr_eleele___DY_High = SafeDefine(node_DY_cr_eleele___DY_High, "my_sample_weight_DY_High", "(my_sample_weight)*1.00");
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele___DY_Low"].push_back(node_DY_cr_eleele___DY_Low.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_eleele___DY_High"].push_back(node_DY_cr_eleele___DY_High.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele___DY_Low"].push_back(node_DY_cr_eleele___DY_Low.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_eleele___DY_High"].push_back(node_DY_cr_eleele___DY_High.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele___DY_Low"].push_back(node_DY_cr_eleele___DY_Low.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_eleele___DY_High"].push_back(node_DY_cr_eleele___DY_High.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele___DY_Low"].push_back(node_DY_cr_eleele___DY_Low.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_eleele___DY_High"].push_back(node_DY_cr_eleele___DY_High.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele___DY_Low"].push_back(node_DY_cr_eleele___DY_Low.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_eleele___DY_High"].push_back(node_DY_cr_eleele___DY_High.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele___DY_Low"].push_back(node_DY_cr_eleele___DY_Low.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_eleele___DY_High"].push_back(node_DY_cr_eleele___DY_High.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_High"));
    hist_map_2D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_2D["DY_cr_eleele___DY_Low"].push_back(node_DY_cr_eleele___DY_Low.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_Low"));
    hist_map_2D["DY_cr_eleele___DY_High"].push_back(node_DY_cr_eleele___DY_High.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele___DY_Low"].push_back(node_DY_cr_eleele___DY_Low.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_eleele___DY_High"].push_back(node_DY_cr_eleele___DY_High.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele___DY_Low"].push_back(node_DY_cr_eleele___DY_Low.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_eleele___DY_High"].push_back(node_DY_cr_eleele___DY_High.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_High"));
    auto node_DY_cr_mumu = node_DY_cr.Filter("(mumu)", "DY_cr_mumu");
    ROOT::RDF::RNode node_DY_cr_mumu___DY_Low = node_DY_cr_mumu.Filter("mll<70", "cut_DY_Low");
    node_DY_cr_mumu___DY_Low = SafeDefine(node_DY_cr_mumu___DY_Low, "my_sample_weight_DY_Low", "(my_sample_weight)*1.00");
    ROOT::RDF::RNode node_DY_cr_mumu___DY_High = node_DY_cr_mumu.Filter("mll>70", "cut_DY_High");
    node_DY_cr_mumu___DY_High = SafeDefine(node_DY_cr_mumu___DY_High, "my_sample_weight_DY_High", "(my_sample_weight)*1.00");
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu___DY_Low"].push_back(node_DY_cr_mumu___DY_Low.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_mumu___DY_High"].push_back(node_DY_cr_mumu___DY_High.Histo1D<float>({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu___DY_Low"].push_back(node_DY_cr_mumu___DY_Low.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_mumu___DY_High"].push_back(node_DY_cr_mumu___DY_High.Histo1D<float>({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu___DY_Low"].push_back(node_DY_cr_mumu___DY_Low.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_mumu___DY_High"].push_back(node_DY_cr_mumu___DY_High.Histo1D<float>({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu___DY_Low"].push_back(node_DY_cr_mumu___DY_Low.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_mumu___DY_High"].push_back(node_DY_cr_mumu___DY_High.Histo1D<float>({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu___DY_Low"].push_back(node_DY_cr_mumu___DY_Low.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_mumu___DY_High"].push_back(node_DY_cr_mumu___DY_High.Histo1D<float>({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu___DY_Low"].push_back(node_DY_cr_mumu___DY_Low.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_mumu___DY_High"].push_back(node_DY_cr_mumu___DY_High.Histo1D<float>({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight_DY_High"));
    hist_map_2D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_2D["DY_cr_mumu___DY_Low"].push_back(node_DY_cr_mumu___DY_Low.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_Low"));
    hist_map_2D["DY_cr_mumu___DY_High"].push_back(node_DY_cr_mumu___DY_High.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu___DY_Low"].push_back(node_DY_cr_mumu___DY_Low.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_mumu___DY_High"].push_back(node_DY_cr_mumu___DY_High.Histo1D<float>({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight_DY_High"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu___DY_Low"].push_back(node_DY_cr_mumu___DY_Low.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_Low"));
    hist_map_1D["DY_cr_mumu___DY_High"].push_back(node_DY_cr_mumu___DY_High.Histo1D<float>({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight_DY_High"));
    
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
    std::map<std::string, std::pair<std::string, int> > map_nuisances_name_for_averaged_histograms;

    

    //
    // In root file:    <cut>/<variable>/histo_<sample>
    //

    TFile out_file("rootFile/root_file___DY_DYJetsToLL_M-10to50_NLO_2.root", "RECREATE");
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

          //
          // special treatment for nuisances based on averaged histograms
          //
          bool found_any_nuisances_for_averaged_histograms = false;
          for (auto const& [string_pattern, nuisance_name_numVariations] : map_nuisances_name_for_averaged_histograms) {

            std::string nuisance_name = nuisance_name_numVariations.first;
            int numVariations_here = nuisance_name_numVariations.second;

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
                  it->second.Add(histo.get(), 1. / numVariations_here);
                }
                else {
                  map_nuisances_average_histogram[nuisance_name + "up"] = (*histo);
                  found_any_nuisances_for_averaged_histograms = true;
                  break; // end loop over map to save time
                }
              }
              else {
                if (auto it = map_nuisances_average_histogram.find(string_pattern + "do"); it != map_nuisances_average_histogram.end()) {
                  it->second.Add(histo.get(), 1. / numVariations_here);
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

          // now write all the averaged histograms, up and down variations, if there are any!
          for (auto const& [name, temp_histo] : map_nuisances_average_histogram) {
            temp_histo.Write();
          }


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


          if (list_of_variables_fold_2D.at(ivar) != 0) FoldHistogram(histo.get(), list_of_variables_fold_2D.at(ivar));

          //UnrollHistogram(dynamic_cast<TH2D*>(histo.get()))->Write();

          auto new_histo = UnrollHistogram(dynamic_cast<TH2D*>(histo.get()));


          //
          // special treatment for nuisances based on averaged histograms
          //
          bool found_any_nuisances_for_averaged_histograms = false;
          for (auto const& [string_pattern, nuisance_name_numVariations] : map_nuisances_name_for_averaged_histograms) {

            std::string nuisance_name = nuisance_name_numVariations.first;
            int numVariations_here = nuisance_name_numVariations.second;

            std::string string_pattern_up = "histo_.*__NORM__.*_" + string_pattern + "up";
            std::string string_pattern_do = "histo_.*__NORM__.*_" + string_pattern + "do";

            std::regex pattern_up(string_pattern_up);
            std::regex pattern_do(string_pattern_do);

            if (std::regex_search(temp_name, pattern_up) || std::regex_search(temp_name, pattern_do)) {
              std::regex pattern_to_remove("__NORM__[0-9]+_");
              std::string histo_temp_name = std::regex_replace(temp_name, pattern_to_remove, "");
              std::regex pattern(string_pattern);

              histo_temp_name = std::regex_replace(histo_temp_name, pattern, nuisance_name); // replace with real nuisance name

              new_histo->SetName(histo_temp_name.c_str());

              if (std::regex_search(temp_name, pattern_up)) {
                if (auto it = map_nuisances_average_histogram.find(string_pattern + "up"); it != map_nuisances_average_histogram.end()) {
                  it->second.Add(new_histo, 1. / numVariations_here);
                }
                else {
                  map_nuisances_average_histogram[nuisance_name + "up"] = (*new_histo);
                  found_any_nuisances_for_averaged_histograms = true;
                  break; // end loop over map to save time
                }
              }
              else {
                if (auto it = map_nuisances_average_histogram.find(string_pattern + "do"); it != map_nuisances_average_histogram.end()) {
                  it->second.Add(new_histo, 1. / numVariations_here);
                }
                else {
                  map_nuisances_average_histogram[nuisance_name + "do"] = (*new_histo);
                  found_any_nuisances_for_averaged_histograms = true;
                  break; // end loop over map to save time
                }
              }
            }
          }
          // if it's NOT a histogram to be averaged, then write it directly
          if (not found_any_nuisances_for_averaged_histograms) {
            new_histo->Write();
          }

          // now write all the averaged histograms, up and down variations, if there are any!
          for (auto const& [name, temp_histo] : map_nuisances_average_histogram) {
            temp_histo.Write();
          }


        }
      }
      out_file.cd(); // Go back to root for the next directory
    }



    out_file.Close();

    return 0;
}

        