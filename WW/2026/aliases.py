#
# List of aliases to be "defined"
# This list will NOT be the actual "Alias" of RDataFrame (as useless)
# but "Define" of all this math will be performed
#
#
#

#
# LepCut2l__ele_cutBased_LooseID_tthMVA_Run3__mu_cut_TightID_pfIsoLoose_HWW_PNet
#

eleWP = 'cutBased_LooseID_tthMVA_Run3'
# eleWP = 'cutBased_MediumID_tthMVA_Run3'
# muWP  = 'cut_TightID_pfIsoTight_HWW_tthmva_67'
muWP  = 'cut_TightID_pfIsoLoose_HWW_PNet'


aliases['PromptGenLepMatch2l'] = {
    'expr': '(Lepton_promptgenmatched.size() > 0 ? Lepton_promptgenmatched[0] : 0.) * (Lepton_promptgenmatched.size() > 1 ? Lepton_promptgenmatched[0] : 0.)',
    'samples': mcALL
}




aliases['mumu'] = {
    'expr': '(Lepton_pdgId.size() > 0 ? Lepton_pdgId[0] : -99) * (Lepton_pdgId.size() > 1 ? Lepton_pdgId[1]: -99) == -13*13',
    'samples': ALL
}

aliases['ee'] = {
    'expr': '(Lepton_pdgId.size() > 0 ? Lepton_pdgId[0] : -99) * (Lepton_pdgId.size() > 1 ? Lepton_pdgId[1]: -99) == -11*11',
    'samples': ALL
}




# -------- lepton WP
aliases['LepWPCut'] = {
    'expr': 'LepCut2l__ele_'+eleWP+'__mu_'+muWP ,
    'samples': ALL
}



# ---------------------------- btagging
#
# B-Tagging WP: https://btv-wiki.docs.cern.ch/ScaleFactors/Run3Summer22/
#
#
#    "UParTAK4B" : {"loose" : "0.0246", "medium" : "0.1272", "tight" : "0.4648", "xtight" : "0.6298", "xxtight" : "0.9739"},
#

aliases['bVeto'] = {
    'expr' : 'ROOT::VecOps::Sum(Take(Jet_btagUParTAK4B,CleanJet_jetIdx)[CleanJet_pt > 20 && abs(CleanJet_eta) < 2.5] > 0.0246) == 0',
    'samples': ALL
}

aliases['bReq'] = {
    'expr' : 'ROOT::VecOps::Sum(Take(Jet_btagUParTAK4B,CleanJet_jetIdx)[CleanJet_pt > 20 && abs(CleanJet_eta) < 2.5] > 0.0246) >= 1',
    'samples': ALL
}

# aliases['bVetoSF'] = {
#     'expr' : 'ROOT::VecOps::Product(Take(Jet_btagSF_deepcsv_shape,CleanJet_jetIdx)[CleanJet_pt > 20 && abs(CleanJet_eta) < 2.5])',
#     'samples': mcALL
# }
#
# aliases['bReqSF'] = {
#     'expr' : 'ROOT::VecOps::Product(Take(Jet_btagSF_deepcsv_shape,CleanJet_jetIdx)[CleanJet_pt > 30 && abs(CleanJet_eta) < 2.5])',
#     'samples': mcALL
# }
#
# aliases['btagSF'] = {
#     'expr': 'bVeto*bVetoSF + bReq*bReqSF',
#     'samples': mcALL
# }





# --------------------------- PU weights
# aliases['Jet_PUIDSF'] = {
#   'expr' : 'ROOT::VecOps::Product(Jet_PUIDSF_loose[Jet_jetId>=2])',
#   'samples': mcALL
# }
#
# aliases['Jet_PUIDSF_up'] = {
#   'expr' : 'ROOT::VecOps::Product(Jet_PUIDSF_loose_up[Jet_jetId>=2])',
#   'samples': mcALL
# }
#
# aliases['Jet_PUIDSF_down'] = {
#   'expr' : 'ROOT::VecOps::Product(Jet_PUIDSF_loose_down[Jet_jetId>=2])',
#   'samples': mcALL
# }



aliases['LepWPSF'] = {
    'expr': 'LepSF2l__ele_'+eleWP+'__mu_'+muWP,
    'samples': mcALL
}


# see:
# https://github.com/latinos/LatinoAnalysis/blob/master/NanoGardener/python/data/formulasToAdd_MC_2017.py
#


# variations
aliases['SFweightEleUp'] = {
    'expr': 'LepSF2l__ele_'+eleWP+'__Up',
    'samples': mcALL
}
aliases['SFweightEleDown'] = {
    # 'expr': 'LepSF2l__ele_'+eleWP+'__Do',
    'expr': 'LepSF2l__ele_'+eleWP+'__Down',
    'samples': mcALL
}
aliases['SFweightMuUp'] = {
    'expr': 'LepSF2l__mu_'+muWP+'__Up',
    'samples': mcALL
}
aliases['SFweightMuDown'] = {
    # 'expr': 'LepSF2l__mu_'+muWP+'__Do',
    'expr': 'LepSF2l__mu_'+muWP+'__Down',
    'samples': mcALL
}




aliases['Top_pTrw'] = {
  'expr': '(topGenPt * antitopGenPt > 0.) * (TMath::Sqrt((0.103*TMath::Exp(-0.0118*topGenPt) - 0.000134*topGenPt + 0.973) * (0.103*TMath::Exp(-0.0118*antitopGenPt) - 0.000134*antitopGenPt + 0.973))) + (topGenPt * antitopGenPt <= 0.)',
  # 'expr': '(topGenPt * antitopGenPt > 0.) * (TMath::Sqrt(TMath::Exp(0.0615 - 0.0005 * topGenPt) * TMath::Exp(0.0615 - 0.0005 * antitopGenPt))) + (topGenPt * antitopGenPt <= 0.)',
  'samples': ['top']
}






#
# external defined variable: c++ code
#

# aliases['myVariableMll'] = {
#   'external' : "code/mymll.c",
#   'variables': ["Lepton_pt[0]", "Lepton_eta[0]", "Lepton_phi[0]", "Lepton_pt[1]", "Lepton_eta[1]", "Lepton_phi[1]"],
#   'function' : 'calculate_mass',
#   'samples': mcALL
# }



#
# if some variables are not defined but they are needed as inputs of the TMVA, define them!
#

aliases['ptj1'] = {
    'expr': 'CleanJet_pt.size() > 0 ? CleanJet_pt[0] : -9999.',
    'samples' : ALL
}

aliases['njet'] = {
    'expr': 'Sum(CleanJet_pt>30)',
    'samples' : ALL
}

# aliases['myVariableBDT'] = {
#   'variables': ["pt1", "ptj1", "mll", "njet"],
#   'function' : 'TMVA',
#   'xmlfile'  : 'code/TMVAClassification_BDTG.weights.xml',
#   'samples': ALL
# }

