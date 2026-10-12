


// Path to your JSON on CVMFS
// std::string json_path = "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/XXXX_UL/jet_jerc.json.gz";
std::string json_path = "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/2018_UL/jet_jerc.json.gz";
std::string jet_algo  = "AK4PFchs";

// Initialize our helper
static JERSmearer jer(json_path, jet_algo);

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


//
// define the variables that will change
//

int Nvariation_myJER = 3;

for (int ivariation = 0; ivariation<Nvariation_myJER; ivariation++) {
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

//
// define the variations
//

for (int ivariation = 0; ivariation<Nvariation_myJER; ivariation++) {
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








