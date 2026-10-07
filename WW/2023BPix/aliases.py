#
# List of aliases to be "defined"
# This list will NOT be the actual "Alias" of RDataFrame (as useless)
# but "Define" of all this math will be performed
#
#
import re
import inspect

ALL = [skey for skey in samples]
mc = [skey for skey in samples if skey not in ('DATA', 'Fake')]
lhesamples = [skey for skey in mc if skey not in ('ggWW', 'ZZ')]

btagmaps = 'root://eosuser.cern.ch//eos/user/a/abulla/latinoRDF/plotsConfigurationsRDF/WW/utils/data/btag'
macros = '/eos/user/a/abulla/latinoRDF/plotsConfigurationsRDF/WW/macros/'
fakerates = 'root://eosuser.cern.ch//eos/user/a/abulla/latinoRDF/plotsConfigurationsRDF/WW/utils/data/FakeRate'


#tomas kello
# eleWP = 'cutBased_LooseID_tthMVA_Run3'
eleWP = 'cutBased_MediumID_tthMVA_Run3'
muWP  = 'cut_TightID_pfIsoTight_HWW_tthmva_67'

Tag = 'ele_'+eleWP+'_mu_'+muWP

# -------- lepton WP
aliases['LepWPCut'] = {
    'expr': 'LepCut2l__ele_'+eleWP+'__mu_'+muWP ,
    'samples': ALL
}

aliases['LepWPSF'] = {
    'expr': 'LepSF2l__ele_'+eleWP+'__mu_'+muWP,
    'samples': mc
}

# gen-matching to prompt only (GenLepMatch2l matches to *any* gen lepton)
aliases['PromptGenLepMatch2l'] = {
    'expr': '(Lepton_promptgenmatched.size() > 0 ? Lepton_promptgenmatched[0] : 0.) * (Lepton_promptgenmatched.size() > 1 ? Lepton_promptgenmatched[0] : 0.)',
    'samples': mc
}

# ------------------------------------------------
# Same-sign 2-lepton flavour aliases (WW SR)
# product is positive for same-sign pairs
# ------------------------------------------------
aliases['ee'] = {
    'expr': '(Lepton_pdgId.size() > 0 ? Lepton_pdgId[0] : -99) * (Lepton_pdgId.size() > 1 ? Lepton_pdgId[1]: -99) == 11*11',
    'samples': ALL
}
 
aliases['mumu'] = {
    'expr': '(Lepton_pdgId.size() > 0 ? Lepton_pdgId[0] : -99) * (Lepton_pdgId.size() > 1 ? Lepton_pdgId[1]: -99) == 13*13',
    'samples': ALL
}
 
aliases['emu'] = {
    'expr': '(Lepton_pdgId.size() > 0 ? Lepton_pdgId[0] : -99) * (Lepton_pdgId.size() > 1 ? Lepton_pdgId[1]: -99) == 11*13',
    'samples': ALL
}

# ------------------------------------------------
# Zeppenfeld variable: max over all leptons
# z*_l = |eta_l - (eta_j1+eta_j2)/2| / delta_eta_jj
# ------------------------------------------------
aliases['zstar_max'] = {
    'function' : 'computeZstar',
    'variables': ['Lepton_eta', 'CleanJet_eta'],
    'external' : '../macros/VBS_functions.cpp',
    'samples'  : ALL
}

# ------------------------------------------------
# WZ variables (3 leptons, exactly)
# computeWZvars returns:
#   [0] mll_Z   [1] mlll   [2] idx_W   [3] category
#   [4] pt_W    [5] pt_Z1  [6] pt_Z2   [7] proxyW_W
# Returns -9999 if not exactly 3 leptons or no SFOS pair found
# ------------------------------------------------
aliases['WZ_vars'] = {
    'function' : 'computeWZvars',
    'variables': ['Lepton_pt', 'Lepton_eta', 'Lepton_phi', 'Lepton_pdgId',
                  'PuppiMET_pt', 'PuppiMET_phi'],
    'external' : '../macros/VBS_functions.cpp',
    'samples'  : ALL
}
aliases['mll_Z']    = { 'expr': 'WZ_vars[0]', 'samples': ALL }
aliases['mlll']     = { 'expr': 'WZ_vars[1]', 'samples': ALL }
aliases['idx_W']    = { 'expr': 'WZ_vars[2]', 'samples': ALL }
aliases['WZ_flav']  = { 'expr': 'WZ_vars[3]', 'samples': ALL }
aliases['pt_W']     = { 'expr': 'WZ_vars[4]', 'samples': ALL }
aliases['pt_Z1']    = { 'expr': 'WZ_vars[5]', 'samples': ALL }  # leading Z lepton pT
aliases['pt_Z2']    = { 'expr': 'WZ_vars[6]', 'samples': ALL }  # trailing Z lepton pT
aliases['proxyW_W'] = { 'expr': 'WZ_vars[7]', 'samples': ALL }  # mT(lW, MET)

# WZ flavour categories (Z_flav*100 + W_flav, 11=e, 13=mu)
aliases['eee'] = { 'expr': 'WZ_flav == 1111', 'samples': ALL }  # Z->ee,  W->e
aliases['eem'] = { 'expr': 'WZ_flav == 1113', 'samples': ALL }  # Z->ee,  W->mu
aliases['mme'] = { 'expr': 'WZ_flav == 1311', 'samples': ALL }  # Z->mumu, W->e
aliases['mmm'] = { 'expr': 'WZ_flav == 1313', 'samples': ALL }  # Z->mumu, W->mu

# ------------------------------------------------
# ZZ variables (4 leptons, exactly)
# computeZZvars returns:
#   [0] mll_Z1  [1] mll_Z2  [2] mllll  [3] category
#   [4] pt_4l_1 [5] pt_4l_2
# Returns -9999 if not exactly 4 leptons or fewer than 2 SFOS pairs
# ------------------------------------------------
aliases['ZZ_vars'] = {
    'function' : 'computeZZvars',
    'variables': ['Lepton_pt', 'Lepton_eta', 'Lepton_phi', 'Lepton_pdgId'],
    'external' : '../macros/VBS_functions.cpp',
    'samples'  : ALL
}
aliases['mll_Z1']  = { 'expr': 'ZZ_vars[0]', 'samples': ALL }
aliases['mll_Z2']  = { 'expr': 'ZZ_vars[1]', 'samples': ALL }
aliases['mllll']   = { 'expr': 'ZZ_vars[2]', 'samples': ALL }
aliases['ZZ_flav'] = { 'expr': 'ZZ_vars[3]', 'samples': ALL }
aliases['pt_4l_1'] = { 'expr': 'ZZ_vars[4]', 'samples': ALL }  # leading lepton pT
aliases['pt_4l_2'] = { 'expr': 'ZZ_vars[5]', 'samples': ALL }  # subleading lepton pT

# ZZ flavour categories
aliases['eeee'] = { 'expr': 'ZZ_flav == 1111', 'samples': ALL }
aliases['eemm'] = { 'expr': 'ZZ_flav == 1113', 'samples': ALL }
aliases['mmmm'] = { 'expr': 'ZZ_flav == 1313', 'samples': ALL }

# ------------------------------------------------
# DeltaR between leptons and jets
# dr_lj[0]=dr(l1,j1), [1]=dr(l1,j2), [2]=dr(l2,j1), [3]=dr(l2,j2)
# Returns -9999 if fewer than 2 leptons or 2 jets
# ------------------------------------------------
aliases['dr_lj'] = {
    'function' : 'dr_lj',
    'variables': ['CleanJet_eta', 'CleanJet_phi', 'Lepton_eta', 'Lepton_phi'],
    'external' : '../macros/VBS_functions.cpp',
    'samples'  : ALL
}
aliases['dr_l1j1'] = { 'expr': 'dr_lj[0]', 'samples': ALL }
aliases['dr_l1j2'] = { 'expr': 'dr_lj[1]', 'samples': ALL }
aliases['dr_l2j1'] = { 'expr': 'dr_lj[2]', 'samples': ALL }
aliases['dr_l2j2'] = { 'expr': 'dr_lj[3]', 'samples': ALL }

# ------------------------------------------------
# Invariant mass between leptons and jets
# m_lj[0]=m(l1,j1), [1]=m(l1,j2), [2]=m(l2,j1), [3]=m(l2,j2)
# Returns -9999 if fewer than 2 leptons or 2 jets
# ------------------------------------------------
aliases['m_lj'] = {
    'function' : 'm_lj',
    'variables': ['CleanJet_pt', 'CleanJet_eta', 'CleanJet_phi', 'CleanJet_jetIdx',
                  'Jet_mass', 'Lepton_pt', 'Lepton_eta', 'Lepton_phi'],
    'external' : '../macros/VBS_functions.cpp',
    'samples'  : ALL
}
aliases['m_l1j1'] = { 'expr': 'm_lj[0]', 'samples': ALL }
aliases['m_l1j2'] = { 'expr': 'm_lj[1]', 'samples': ALL }
aliases['m_l2j1'] = { 'expr': 'm_lj[2]', 'samples': ALL }
aliases['m_l2j2'] = { 'expr': 'm_lj[3]', 'samples': ALL }

# ------------------------------------------------
# proxyW: mT(lepton + MET) for each lepton
# Only meaningful for exactly 2 leptons (WW), returns -9999 otherwise
# ------------------------------------------------
aliases['proxyW'] = {
    'function' : 'proxyW',
    'variables': ['Lepton_pt', 'Lepton_eta', 'Lepton_phi', 'PuppiMET_pt', 'PuppiMET_phi'],
    'external' : '../macros/VBS_functions.cpp',
    'samples'  : ALL
}
aliases['proxyW_l1'] = { 'expr': 'proxyW[0]', 'samples': ALL }
aliases['proxyW_l2'] = { 'expr': 'proxyW[1]', 'samples': ALL }

# ------------------------------------------------
# mT2: analytic Cheng-Han mT2 (massless invisible)
# Only meaningful for exactly 2 leptons (WW), returns -9999 otherwise
# ------------------------------------------------
aliases['mT2'] = {
    'function' : 'mT2',
    'variables': ['Lepton_pt', 'Lepton_eta', 'Lepton_phi', 'PuppiMET_pt', 'PuppiMET_phi'],
    'external' : '../macros/VBS_functions.cpp',
    'samples'  : ALL
}


# Jet bins
# using Alt(CleanJet_pt, n, 0) instead of Sum(CleanJet_pt >= 30) because jet pt ordering is not strictly followed in JES-varied samples

# No jet with pt > 30 GeV
aliases['zeroJet'] = {
    'expr': 'CleanJet_pt.size() == 0 || CleanJet_pt[0] < 30.',
    'samples': ALL
}

aliases['oneJet'] = {
    'expr': 'CleanJet_pt.size() > 0 && CleanJet_pt[0] > 30.',
    'samples': ALL
}

aliases['multiJet'] = {
    'expr': 'CleanJet_pt.size() > 1 && CleanJet_pt[1] > 30.',
    'samples': ALL
}

aliases['noJetInHorn'] = {
    'expr' : 'Sum(CleanJet_pt > 30 && CleanJet_pt < 50 && abs(CleanJet_eta) > 2.5 && abs(CleanJet_eta) < 3.0) == 0',
    'samples' : ALL
}

fake_rate_macro = open(f'{macros}fake_rate_reader_class.cc').read()

aliases['_fakeRateDecl'] = {
    'linesToAdd'    : ['#include "TInterpreter.h"'],
    'linesToProcess': [f'gInterpreter->Declare(R"FAKE({fake_rate_macro})FAKE");'],
    'expr'          : '1.',
    'samples'       : ['Fake'],
}

for kind, label in [
    ('nominal',     ''),
    ('EleUp',       'EleUp'),
    ('EleDown',     'EleDown'),
    ('MuUp',        'MuUp'),
    ('MuDown',      'MuDown'),
    ('StatEleUp',   'StatEleUp'),
    ('StatEleDown', 'StatEleDown'),
    ('StatMuUp',    'StatMuUp'),
    ('StatMuDown',  'StatMuDown'),
]:
    alias_name = 'fakeW' + label
    inst_name  = 'fr_reader_' + (label if label else 'nominal')
    aliases[alias_name] = {
        'linesToAdd'    : ['#include "TInterpreter.h"'],
        'linesToProcess': [
            f'gInterpreter->Declare("fake_rate_reader {inst_name}('
            f'\\\"{eleWP}\\\", \\\"{muWP}\\\", \\\"{kind}\\\", 2, \\\"std\\\", '
            f'\\\"{fakerates}\\\", \\\"2023BPix_v12_pt\\\");");',
        ],
        'expr': (
            f'{inst_name}('
            f'Lepton_pdgId, Lepton_pt, Lepton_eta, '
            f'Lepton_isTightMuon_{muWP}, Lepton_isTightElectron_{eleWP}, '
            f'Lepton_muonIdx, CleanJet_pt, nCleanJet)'
        ),
        'samples': ['Fake'],
    }

#Top pT reweighting
aliases['Top_pTrw'] = {
    'expr': '(topGenPt * antitopGenPt > 0.) * (TMath::Sqrt((0.103*TMath::Exp(-0.0118*topGenPt) - 0.000134*topGenPt + 0.973) * (0.103*TMath::Exp(-0.0118*antitopGenPt) - 0.000134*antitopGenPt + 0.973))) + (topGenPt * antitopGenPt <= 0.)',
    'samples': ['top']
}


##########################################################################
# B-Tagging WP: https://btv-wiki.docs.cern.ch/ScaleFactors/Run3Summer23/
##########################################################################

# Algo / WP / WP cut
btagging_WPs = {
    "UParTAK4B" : {"loose" : "0.0246", "medium" : "0.1272", "tight" : "0.4648", "xtight" : "0.6298", "xxtight" : "0.9739"},
}
# Algo / WP / WP cut 
btagging_WPs = {
    "DeepFlavB" : {"loose" : "0.048", "medium" : "0.2435", "tight" : "0.6563", "xtight" : "0.7671", "xxtight" : "0.9483"},
    "RobustParTAK4B" : {"loose" : "0.0683", "medium" : "0.3494", "tight" : "0.7994", "xtight" : "0.8877", "xxtight" : "0.9883"},
    "PNetB" : {"loose" : "0.0359", "medium" : "0.1919", "tight" : "0.6133", "xtight" : "0.7544", "xxtight" : "0.9688"}
}

# Algo / SF name
btagging_SFs = {
    "DeepFlavB"      : "deepjet",
    "RobustParTAK4B" : "partTransformer",
    "PNetB"          : "partNet",
}

# Algorithm and WP selection
bAlgo = 'DeepFlavB' # ['DeepFlavB','RobustParTAK4B','PNetB'] 
WP    = 'loose'     # ['loose','medium','tight','xtight','xxtight']

# Access information from dictionaries
bWP   = btagging_WPs[bAlgo][WP]
bSF   = btagging_SFs[bAlgo]


WP_eval = 'L' # ['L', 'M', 'T', 'XT', 'XXT']
tagger = 'deepJet' # ['deepJet', 'particleNet', 'robustParticleTransformer']

#################
### B-tagging ###
#################

# Fixed BTV wp

# btagging MC efficiencies and SFs are read through the btagSF{flavour} object:
# - the first argument is the MC btagging efficiency root file
# - the second argument is the year from which SFs are retrieved from the POG/BTV json-pog correctionlib directory; 
#   allowed options are = ['Run3-22CDSep23-Summer22-NanoAODv12', 'Run3-22EFGSep23-Summer22EE-NanoAODv12, 'Run3-23CSep23-Summer23-NanoAODv12', 'Run3-23DSep23-Summer23BPix-NanoAODv12', 'Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15']
# The btagSF{flavour}_{shift} constructor executes the actual computation
# In this you specify the WP for the computation and the tagger using the WP_eval and tagger strings.

# We assume that you heve the efficiency maps root files in your configuration, as well as the evaluation macros
# If this is not the case, swap configurations with the proper path

# path = "your/path"

eff_map_year = '2023BPix' #['2022', '2022EE', '2023', '2023BPix', '2024]
year = 'Run3-23DSep23-Summer23BPix-NanoAODv12' # ['Run3-22CDSep23-Summer22-NanoAODv12', 'Run3-22EFGSep23-Summer22EE-NanoAODv12, 'Run3-23CSep23-Summer23-NanoAODv12', 'Run3-23DSep23-Summer23BPix-NanoAODv12', 'Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15']
eff_map_path = f"{btagmaps}/{eff_map_year}/bTagEff_{eff_map_year}_ttbar_{bAlgo}_{WP}.root"
# shifts_per_flavour = {
#     'bc'   : ['central', 'down', 'down_bfragmentation', 'down_correlated', 'down_fsrdef', 'down_hdamp', 'down_isrdef', 'down_jer', 'down_jes', 'down_muf', 'down_mur', 'down_pdfas', 'down_pileup', 'down_statistic', 'down_topmass', 'down_type3', 'down_uncorrelated', 'up', 'up_bfragmentation', 'up_correlated', 'up_fsrdef', 'up_hdamp', 'up_isrdef', 'up_jer', 'up_jes', 'up_muf', 'up_mur', 'up_pdfas', 'up_pileup', 'up_statistic', 'up_topmass', 'up_type3', 'up_uncorrelated'],    
#     'light': ['central', 'down', 'down_correlated', 'down_uncorrelated', 'up', 'up_correlated', 'up_uncorrelated'],
# }

# only the shifts actually used in nuisances
shifts_needed = {
    'bc'   : ['central', 'up_correlated', 'down_correlated', 'up_uncorrelated', 'down_uncorrelated'],
    'light': ['central', 'up_correlated', 'down_correlated', 'up_uncorrelated', 'down_uncorrelated'],
}

# Dichiara la classe una volta sola
for flavour in ['bc', 'light']:
    macro_content = open(f'{macros}evaluate_btagSF{flavour}.cc').read()
    
    aliases[f'_btagSF{flavour}Decl'] = {
        'linesToAdd'    : ['#include "TInterpreter.h"'],
        'linesToProcess': [f'gInterpreter->Declare(R"BTAG({macro_content})BTAG");'],
        'expr'          : '1.',
        'samples'       : mc,
    }
    
    # Poi per ogni variante solo ProcessLine + expr
    for shift in shifts_needed[flavour]:
        btagsf = 'btagSF' + flavour + ('' if shift == 'central' else '_' + shift)
        aliases[btagsf] = {
            'linesToAdd'    : ['#include "TInterpreter.h"'],
            'linesToProcess': [
                f'gInterpreter->ProcessLine("btagSF{flavour} {btagsf}_inst('
                f'\\"{eff_map_path}\\", \\"{year}\\");");',
            ],
            'expr': (
                f"{btagsf}_inst(CleanJet_pt, CleanJet_eta, CleanJet_jetIdx, nCleanJet, "
                f"Jet_hadronFlavour, Jet_btag{bAlgo}, '{WP_eval}', '{shift}', '{tagger}', '{eff_map_year}')"
            ),
            'samples': mc,
        }

# B tagging selections and scale factors
aliases['bVeto'] = {
    'expr': f'Sum(CleanJet_pt > 20. && abs(CleanJet_eta) < 2.5 && Take(Jet_btag{bAlgo}, CleanJet_jetIdx, -999.f) > {bWP}) == 0',
    'samples': ALL
}

aliases['bReq'] = { 
    'expr': f'Sum(CleanJet_pt > 30. && abs(CleanJet_eta) < 2.5 && Take(Jet_btag{bAlgo}, CleanJet_jetIdx, -999.f) > {bWP}) >= 1',
    'samples': ALL
}


aliases['LHEScaleWeight_vec'] = {'expr': 'ROOT::VecOps::RVec<double>(LHEScaleWeight)', 'samples': lhesamples}
aliases['LHEPdfWeight_vec']   = {'expr': 'ROOT::VecOps::RVec<double>(LHEPdfWeight)',   'samples': lhesamples}

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


# see:
# https://github.com/latinos/LatinoAnalysis/blob/master/NanoGardener/python/data/formulasToAdd_MC_2017.py
#


# variations
# data/MC scale factors

# Use this for the usual SF
aliases['SFweight'] = {
    'expr': ' * '.join(['SFweight2l', 'LepWPCut', 'LepWPSF', 'btagSFbc', 'btagSFlight']),
    'samples': mc
}

aliases['SFweightEleUp'] = {
    'expr': 'LepSF2l__ele_'+eleWP+'__Up',
    'samples': mc
}
aliases['SFweightEleDown'] = {
    'expr': 'LepSF2l__ele_'+eleWP+'__Down',
    'samples': mc
}
aliases['SFweightMuUp'] = {
    'expr': 'LepSF2l__mu_'+muWP+'__Up',
    'samples': mc
}
aliases['SFweightMuDown'] = {
    'expr': 'LepSF2l__mu_'+muWP+'__Down',
    'samples': mc
}



#
# if some variables are not defined but they are needed as inputs of the TMVA, define them!
#


# aliases['myVariableBDT'] = {
#   'variables': ["pt1", "ptj1", "mll", "njet"],
#   'function' : 'TMVA',
#   'xmlfile'  : 'code/TMVAClassification_BDTG.weights.xml',
#   'samples': ALL
# }

