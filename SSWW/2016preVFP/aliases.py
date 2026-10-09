#
# List of aliases to be "defined"
# This list will NOT be the actual "Alias" of RDataFrame (as useless)
# but "Define" of all this math will be performed
#
#

eleWP='mvaFall17V2Iso_WP90_tthmva_70'
muWP='cut_Tight80x_tthmva_80'




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
# b tagging WPs: https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation106XUL16preVFP
#
#
# bWP_medium_deepB = '0.6001'
#

aliases['bVeto'] = {
    'expr' : 'ROOT::VecOps::Sum(Take(Jet_btagDeepB,CleanJet_jetIdx)[CleanJet_pt > 20 && abs(CleanJet_eta) < 2.5] > 0.6001) == 0',
    'samples': ALL
}

aliases['bReq'] = {
    'expr' : 'ROOT::VecOps::Sum(Take(Jet_btagDeepB,CleanJet_jetIdx)[CleanJet_pt > 20 && abs(CleanJet_eta) < 2.5] > 0.6001) >= 1',
    'samples': ALL
}

aliases['bVetoSF'] = {
    'expr' : 'ROOT::VecOps::Product(Take(Jet_btagSF_deepcsv_shape,CleanJet_jetIdx)[CleanJet_pt > 20 && abs(CleanJet_eta) < 2.5])',
    'samples': mcALL
}

aliases['bReqSF'] = {
    'expr' : 'ROOT::VecOps::Product(Take(Jet_btagSF_deepcsv_shape,CleanJet_jetIdx)[CleanJet_pt > 30 && abs(CleanJet_eta) < 2.5])',
    'samples': mcALL
}

aliases['btagSF'] = {
    'expr': 'bVeto*bVetoSF + bReq*bReqSF',
    'samples': mcALL
}





# --------------------------- PU weights
aliases['Jet_PUIDSF'] = {
  'expr' : 'ROOT::VecOps::Product(Jet_PUIDSF_loose[Jet_jetId>=2])',
  'samples': mcALL
}

aliases['Jet_PUIDSF_up'] = {
  'expr' : 'ROOT::VecOps::Product(Jet_PUIDSF_loose_up[Jet_jetId>=2])',
  'samples': mcALL
}

aliases['Jet_PUIDSF_down'] = {
  'expr' : 'ROOT::VecOps::Product(Jet_PUIDSF_loose_down[Jet_jetId>=2])',
  'samples': mcALL
}



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
    'expr': 'LepSF2l__ele_'+eleWP+'__Do',
    'samples': mcALL
}
aliases['SFweightMuUp'] = {
    'expr': 'LepSF2l__mu_'+muWP+'__Up',
    'samples': mcALL
}
aliases['SFweightMuDown'] = {
    'expr': 'LepSF2l__mu_'+muWP+'__Do',
    'samples': mcALL
}




aliases['Top_pTrw'] = {
  'expr': '(topGenPt * antitopGenPt > 0.) * (TMath::Sqrt(TMath::Exp(0.0615 - 0.0005 * topGenPt) * TMath::Exp(0.0615 - 0.0005 * antitopGenPt))) + (topGenPt * antitopGenPt <= 0.)',
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

