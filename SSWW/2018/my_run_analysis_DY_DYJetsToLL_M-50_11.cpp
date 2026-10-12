
#include "ROOT/RDataFrame.hxx"
#include "ROOT/RDFHelpers.hxx"
#include "ROOT/RVec.hxx"

#include "TFile.h"
#include "TH1D.h"
#include "TDirectory.h"
#include "TChain.h"
#include <map>
#include <vector>
#include <iostream>
#include <string>
#include <typeinfo>

//
// doFold
//   0 = no
//   1 = overflow
//   2 = underflow
//   3 = overflow and underflow
//

//                 TH1 works for TH1F, TH2F, ...
void FoldHistogram(TH1* h, int doFold) {

  // 1D historgram
  if (h->GetDimension() == 1) {

    // Get the number of visible bins
    int nBins = h->GetNbinsX();

    // overflow
    if (doFold == 1 || doFold == 3) {
      double content_last     = h->GetBinContent(nBins);
      double error_last       = h->GetBinError(nBins);
      double content_overflow = h->GetBinContent(nBins+1);
      double error_overflow   = h->GetBinError(nBins+1);

      h->SetBinContent(nBins, content_last + content_overflow);
      h->SetBinError(nBins, std::sqrt(error_last*error_last + error_overflow*error_overflow));

      h->SetBinContent(nBins + 1, 0);
      h->SetBinError(nBins + 1, 0);

    }

    // underflow
    if (doFold == 2 || doFold == 3) {

      double content_first     = h->GetBinContent(1);
      double error_first       = h->GetBinError(1);
      double content_underflow = h->GetBinContent(0);
      double error_underflow   = h->GetBinError(0);

      h->SetBinContent(1, content_first + content_underflow);
      h->SetBinError(1, std::sqrt(error_first*error_first + error_underflow*error_underflow));

      h->SetBinContent(0, 0);
      h->SetBinError(0, 0);

    }

  }
  // 2D histogram (com'on you don't need a 3D version ...)
  else {

    int nX = h->GetNbinsX();
    int nY = h->GetNbinsY();

    // overflow
    if (doFold == 1 || doFold == 3) {
      for (int iy = 0; iy <= nY + 1; ++iy) {
        h->SetBinContent(nX, iy, h->GetBinContent(nX, iy) + h->GetBinContent(nX + 1, iy));
        h->SetBinError(nX, iy, std::hypot(h->GetBinError(nX, iy), h->GetBinError(nX + 1, iy)));
        h->SetBinContent(nX + 1, iy, 0);
        h->SetBinError(nX + 1, iy, 0);
      }
      for (int ix = 0; ix <= nX + 1; ++ix) {
        h->SetBinContent(ix, nY, h->GetBinContent(ix, nY) + h->GetBinContent(ix, nY + 1));
        h->SetBinError(ix, nY, std::hypot(h->GetBinError(ix, nY), h->GetBinError(ix, nY + 1)));
        h->SetBinContent(ix, nY + 1, 0);
        h->SetBinError(ix, nY + 1, 0);
      }
    }

    // underflow
    if (doFold == 2 || doFold == 3) {
      for (int iy = 0; iy <= nY + 1; ++iy) {
        h->SetBinContent(1, iy, h->GetBinContent(1, iy) + h->GetBinContent(0, iy));
        h->SetBinError(1, iy, std::hypot(h->GetBinError(1, iy), h->GetBinError(0, iy)));
        h->SetBinContent(0, iy, 0);
        h->SetBinError(0, iy, 0);
      }
      for (int ix = 0; ix <= nX + 1; ++ix) {
        h->SetBinContent(ix, 1, h->GetBinContent(ix, 1) + h->GetBinContent(ix, 0));
        h->SetBinError(ix, 1, std::hypot(h->GetBinError(ix, 1), h->GetBinError(ix, 0)));
        h->SetBinContent(ix, 0, 0);
        h->SetBinError(ix, 0, 0);
      }
    }

  }


}


// --- transform 2D into 1D: unrolling
//
//      3    6    9
//      2    5    8
//      1    4    7
//


TH1D* UnrollHistogram(TH2D* h2) {

  int nBinsX = h2->GetNbinsX();
  int nBinsY = h2->GetNbinsY();
  int totalBins = nBinsX * nBinsY;

  // Create a 1D histogram with the same name (plus a suffix)
  TString name = h2->GetName();
  TString title = h2->GetTitle();
  h2->SetName(name + "_old"); // Rename original to avoid conflict

  TH1D* h1 = new TH1D(name, title, totalBins, 0.5, totalBins + 0.5);
  h1->Sumw2();

  int i1D = 1;
  for (int iy = 1; iy <= nBinsY; ++iy) {
      for (int ix = 1; ix <= nBinsX; ++ix) {
          h1->SetBinContent(i1D, h2->GetBinContent(ix, iy));
          h1->SetBinError(i1D, h2->GetBinError(ix, iy));
          i1D++;
      }
  }

  return h1;
}




#include "TMVA/RReader.hxx"
#include "TMVA/RInferenceUtils.hxx"



ROOT::RDF::RNode SafeDefine(ROOT::RDF::RNode df, std::string name, std::string expr) {
    auto colNames = df.GetColumnNames();
    if (std::find(colNames.begin(), colNames.end(), name) == colNames.end()) {
        return df.Define(name, expr);
    }
    return df;
}


std::vector<std::string> getBranchNames(TTree* tree) {
  std::vector<std::string> names;
  TObjArray* branches = tree->GetListOfBranches();
  for (int i = 0; i < branches->GetEntries(); ++i)
    names.push_back(branches->At(i)->GetName());
  return names;
}



// --- Automatically generated: code to be added for additional functions ---


#include <cmath>
float calculate_mass(float pt1, float eta1, float phi1, float pt2, float eta2, float phi2) {
  return std::sqrt(2 * pt1 * pt2 * (std::cosh(eta1 - eta2) - std::cos(phi1-phi2)));
}






// ----------------------------------------




int main() {
    ROOT::EnableImplicitMT();

    // --- Automatically generated input root files ---

    //  Nominal input files
    auto* nominal = new TChain("Events");
    nominal->Add("root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9/nanoLatino_DYJetsToLL_M-50__part55.root");
    nominal->Add("root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9/nanoLatino_DYJetsToLL_M-50__part56.root");
    nominal->Add("root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9/nanoLatino_DYJetsToLL_M-50__part57.root");
    nominal->Add("root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9/nanoLatino_DYJetsToLL_M-50__part58.root");
    nominal->Add("root://eoscms.cern.ch//eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9/nanoLatino_DYJetsToLL_M-50__part59.root");
//  Variations input files (if any)
    auto* friend_ElepTup = new TChain("Events");
    auto* friend_ElepTdo = new TChain("Events");
    friend_ElepTup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTup_suffix/nanoLatino_DYJetsToLL_M-50__part55.root");
    friend_ElepTdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTdo_suffix/nanoLatino_DYJetsToLL_M-50__part55.root");
    friend_ElepTup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTup_suffix/nanoLatino_DYJetsToLL_M-50__part56.root");
    friend_ElepTdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTdo_suffix/nanoLatino_DYJetsToLL_M-50__part56.root");
    friend_ElepTup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTup_suffix/nanoLatino_DYJetsToLL_M-50__part57.root");
    friend_ElepTdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTdo_suffix/nanoLatino_DYJetsToLL_M-50__part57.root");
    friend_ElepTup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTup_suffix/nanoLatino_DYJetsToLL_M-50__part58.root");
    friend_ElepTdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTdo_suffix/nanoLatino_DYJetsToLL_M-50__part58.root");
    friend_ElepTup->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTup_suffix/nanoLatino_DYJetsToLL_M-50__part59.root");
    friend_ElepTdo->Add("/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/Summer20UL18_106x_nAODv9_Full2018v9/MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9__ElepTdo_suffix/nanoLatino_DYJetsToLL_M-50__part59.root");
    nominal->AddFriend(friend_ElepTup, "ElepTup");
    nominal->AddFriend(friend_ElepTdo, "ElepTdo");
    auto varBranches_ElepTup = getBranchNames(friend_ElepTup);
    auto varBranches_ElepTdo = getBranchNames(friend_ElepTdo);
    ROOT::RDataFrame base_df(*nominal);
    auto varied_df = ROOT::RDF::RNode(base_df);


    // ----------------------------------------

    std::map<std::string, std::vector<ROOT::RDF::RResultPtr<TH1D>>> hist_map_1D;
    std::map<std::string, std::vector<ROOT::RDF::RResultPtr<TH2D>>> hist_map_2D;

    // --- Automatically generated define aliases ---

    //  aliases/define needed
    varied_df = SafeDefine(varied_df, "PromptGenLepMatch2l", "(Lepton_promptgenmatched.size() > 0 ? Lepton_promptgenmatched[0] : 0.) * (Lepton_promptgenmatched.size() > 1 ? Lepton_promptgenmatched[0] : 0.)");
    varied_df = SafeDefine(varied_df, "SFweightEle", "1");
    varied_df = SafeDefine(varied_df, "SFweightMu", "1");
    varied_df = SafeDefine(varied_df, "SFweightMuUp", "LepSF2l__mu_cut_Tight_HWWW_tthmva_80__Up");
    varied_df = SafeDefine(varied_df, "SFweightMuDown", "LepSF2l__mu_cut_Tight_HWWW_tthmva_80__Do");
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
    varied_df = SafeDefine(varied_df, "SFweight", "SFweight2l * LepWPCut");
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
    varied_df = SafeDefine(varied_df, "my_sample_weight", "(XSWeight * SFweight * METFilter_MC * PromptGenLepMatch2l * (mumu ? SFweightMu : 1) * (ee ? SFweightEle : 1)) * 59.83");


    // ----------------------------------------


    // --- Automatically generated register nuisances variations ---

    //  Register the variations
    int suffix_size = 0;
    suffix_size = 8;
    for (const auto& branch : varBranches_ElepTup) {
      if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "ElepTup") == 0 ) {
        std::string nomCol = branch.substr(0, branch.size() - suffix_size);
        std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{" + branch + "}";
        varied_df = varied_df.Vary(
                                  nomCol,
                                  expression,
                                  {"up"},
                                  "scale_e_2018_UL"
                                  );
      };
    };
    
    suffix_size = 8;
    for (const auto& branch : varBranches_ElepTdo) {
      if (int(branch.size()) >= (suffix_size-1) && branch.compare(branch.size() - (suffix_size-1), (suffix_size-1), "ElepTdo") == 0 ) {
        std::string nomCol = branch.substr(0, branch.size() - suffix_size);
        std::string expression = "ROOT::RVec<" + varied_df.GetColumnType(nomCol) + ">{" + branch + "}";
        varied_df = varied_df.Vary(
                                  nomCol,
                                  expression,
                                  {"do"},
                                  "scale_e_2018_UL"
                                  );
      };
    };
    varied_df = varied_df.Vary(
      "my_sample_weight",
      "ROOT::RVecD{(XSWeight * SFweight * METFilter_MC * PromptGenLepMatch2l * (mumu ? SFweightMuUp : 1) * (ee ? SFweightEle : 1)) * 59.83,(XSWeight * SFweight * METFilter_MC * PromptGenLepMatch2l * (mumu ? SFweightMuDown : 1) * (ee ? SFweightEle : 1)) * 59.83}",
      {"up", "do"},
      "eff_m_2018_UL"
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
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_2D["lowmll_ee"].push_back(node_lowmll_ee.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["lowmll_ee"].push_back(node_lowmll_ee.Histo1D({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    auto node_highmll_ee = current_node.Filter("mll>120 && ee", "highmll_ee");
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_2D["highmll_ee"].push_back(node_highmll_ee.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["highmll_ee"].push_back(node_highmll_ee.Histo1D({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    auto node_lowmll_mumu = current_node.Filter("mll>40 && mll<120  && mumu", "lowmll_mumu");
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_2D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["lowmll_mumu"].push_back(node_lowmll_mumu.Histo1D({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    auto node_highmll_mumu = current_node.Filter("mll>120 && mumu", "highmll_mumu");
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_2D["highmll_mumu"].push_back(node_highmll_mumu.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["highmll_mumu"].push_back(node_highmll_mumu.Histo1D({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    auto node_DY_cr = current_node.Filter("(mll>70 && mll<120)", "DY_cr");
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_2D["DY_cr"].push_back(node_DY_cr.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["DY_cr"].push_back(node_DY_cr.Histo1D({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    auto node_DY_cr_eleele = node_DY_cr.Filter("(ee)", "DY_cr_eleele");
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_2D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["DY_cr_eleele"].push_back(node_DY_cr_eleele.Histo1D({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    auto node_DY_cr_mumu = node_DY_cr.Filter("(mumu)", "DY_cr_mumu");
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D({"h_events", "events", 1, 0, 2}, "events", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D({"h_ptj1", "ptj1", 15, 0.0, 200}, "ptj1", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D({"h_ptj2", "ptj2", 15, 0.0, 150}, "ptj2", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D({"h_ptl1", "ptl1", 15, 0.0, 200}, "ptl1", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D({"h_mll", "mll", 200, 10, 500}, "mll", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D({"h_mll_mybins", "mll_mybins", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}}, "mll_mybins", "my_sample_weight"));
    hist_map_2D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo2D({"h_mllVSmth", "mllVSmth", 8, (const double[]){12, 17, 25, 30, 35, 40, 45, 65, 200}, 4, (const double[]){60, 95, 110, 135, 200}}, "mll", "mth", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D({"h_njet", "njet", 8, 0, 8}, "njet", "my_sample_weight"));
    hist_map_1D["DY_cr_mumu"].push_back(node_DY_cr_mumu.Histo1D({"h_BDT", "BDT", 200, 0, 1}, "BDT", "my_sample_weight"));
    
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
    // In root file:    <cut>/<variable>/histo_<sample>
    //

    TFile out_file("rootFile/root_file___DY_DYJetsToLL_M-50_11.root", "RECREATE");
    for (auto& [cut_label, h_list] : hist_map_1D) {
        // Create a folder for this cut
        TDirectory *dir = out_file.mkdir(cut_label.c_str());
        int ivar = 0;
        for (auto& h : h_list) {
          dir->cd();
          TDirectory *subdir = out_file.mkdir( (cut_label+"/"+list_of_variables_1D.at(ivar)).c_str() );
          subdir->cd();

          // get the nominal and the variations too
          auto all_histos = ROOT::RDF::Experimental::VariationsFor(h);

          for (auto& [name, histo] : all_histos) {
            std::string temp_name;
            if (name == "nominal") {
                temp_name = "histo_DY";
            }
            else {
              temp_name = name.c_str();
              // scale_e_2018_UL:up --> scale_e_2018_ULup
              temp_name.erase(std::remove(temp_name.begin(), temp_name.end(), ':'), temp_name.end());
              //size_t pos = temp_name.find(':');
              //if (pos != std::string::npos) {
              //  temp_name = temp_name.substr(0, pos);
              //}
              temp_name = ("histo_DY_" + temp_name);
            }
            gDirectory = subdir;
            histo->SetName(temp_name.c_str());

            if (list_of_variables_fold_1D.at(ivar) != 0) FoldHistogram(histo.get(), list_of_variables_fold_1D.at(ivar));

            histo->Write();

          }
          ivar++;
        }
        out_file.cd(); // Go back to root for the next directory
    }


    for (auto& [cut_label, h_list] : hist_map_2D) {
        // Create a folder for this cut
        TDirectory *dir = out_file.GetDirectory(cut_label.c_str());
        if (!dir) {
          // If it doesn't exist, create it
          dir = out_file.mkdir(cut_label.c_str());
        }
        int ivar = 0;
        for (auto& h : h_list) {
          dir->cd();
          TDirectory *subdir = out_file.GetDirectory( (cut_label+"/"+list_of_variables_2D.at(ivar)).c_str() );
          if (!subdir) {
            // If it doesn't exist, create it
            subdir = out_file.mkdir( (cut_label+"/"+list_of_variables_2D.at(ivar)).c_str() );
          }
          subdir->cd();

          // get the nominal and the variations too
          auto all_histos = ROOT::RDF::Experimental::VariationsFor(h);

          for (auto& [name, histo] : all_histos) {
            std::string temp_name;
            if (name == "nominal") {
                temp_name = "histo_DY";
            }
            else {
              temp_name = name.c_str();
              // scale_e_2018_UL:up --> scale_e_2018_ULup
              temp_name.erase(std::remove(temp_name.begin(), temp_name.end(), ':'), temp_name.end());
              //size_t pos = temp_name.find(':');
              //if (pos != std::string::npos) {
              //  temp_name = temp_name.substr(0, pos);
              //}
              temp_name = ("histo_DY_" + temp_name);
            }
            gDirectory = subdir;
            histo->SetName(temp_name.c_str());


            if (list_of_variables_fold_2D.at(ivar) != 0) FoldHistogram(histo.get(), list_of_variables_fold_2D.at(ivar));

            UnrollHistogram(dynamic_cast<TH2D*>(histo.get()))->Write();

          }
          ivar++;
        }
        out_file.cd(); // Go back to root for the next directory
    }



    out_file.Close();

    return 0;
}

        