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
lhesamples = [skey for skey in mc if skey not in ('ggWW', 'ZZ', 'WW_DPS')]

btagmaps = 'root://eosuser.cern.ch//eos/user/a/abulla/latinoRDF/plotsConfigurationsRDF/SSWW/utils/data/btag'
macros = '/eos/user/a/abulla/latinoRDF/plotsConfigurationsRDF/SSWW/utils/macros/'
fakerates = 'root://eosuser.cern.ch//eos/user/a/abulla/latinoRDF/plotsConfigurationsRDF/SSWW/utils/data/FakeRate'


#tomas kello
# eleWP = 'cutBased_LooseID_tthMVA_Run3'
eleWP = 'cutBased_MediumID_tthMVA_Run3'
muWP  = 'cut_TightID_pfIsoTight_HWW_tthmva_67'

Tag = 'ele_'+eleWP+'_mu_'+muWP

# -------- lepton multiplicity, counted above threshold
#
# AN2025_031 Sec. 4 counts leptons with pT > 10 GeV ("two, three, or four
# isolated charged leptons with pT > 10 GeV [...] Candidate events with five or
# more charged leptons satisfying the loose identification criteria are
# rejected"), while Lepton_pt.size() counts the whole collection, which reaches
# down to ~3 GeV. An event with three good leptons plus one soft spurious one is
# a 3-lepton event, not a 4-lepton one, and must not migrate out of the WZ
# regions.
#
# This works -- and switching the weights on it is safe -- only because the
# Lepton collection is pT-ordered, so the leptons above threshold are always the
# *first* nLepSel ones (verified: 0 violations in 77k events, thresholds 10, 15
# and 20 GeV). That prefix is exactly what LepCut{N}l, LepSF{N}l, SFweight{N}l
# and Lepton_promptgenmatched[0..N-1] refer to, so the tight requirement, the
# lepton SF, the global SF and the prompt gen-matching all keep pointing at the
# selected leptons and at nothing else.
ptMinLep = 10.

aliases['nLepSel'] = {
    'expr': 'Sum(Lepton_pt > %ff)' % ptMinLep,
    'samples': ALL
}

# the selected leptons themselves, for the helpers that take the collection.
# Take(v, n) with n > 0 returns the first n entries, i.e. the prefix above.
for _c in ('pt', 'eta', 'phi', 'pdgId'):
    aliases['SelLep_' + _c] = {
        'expr': 'Take(Lepton_%s, nLepSel)' % _c,
        'samples': ALL
    }

# -------- lepton WP, per lepton multiplicity
#
# Every region pins nLepSel with '==' (see cuts.py):
#     WW_SR, nonprompt_CR, WW_VR_bveto, WW_VR_btag   -> 2
#     WZ_SR, WZb_CR, WZ_VR_bveto, WZ_VR_btag         -> 3
#     ZZ_VR                                          -> 4
# so switching on that count picks exactly the multiplicity the region requires.
# A region written with '>=' instead of '==' would silently get the weight of
# whichever multiplicity the event happens to have.
#
# These four always have to agree on N -- the tight requirement, the lepton SF,
# the global SF and the prompt gen-matching. The nanoAOD provides LepCut{N}l,
# LepSF{N}l, SFweight{N}l and Lepton_promptgenmatched for N = 2, 3, 4.
nlep = 'nLepSel'

for N in (2, 3, 4):
    aliases['LepWPCut%dl' % N] = {
        'expr': 'LepCut%dl__ele_' % N + eleWP + '__mu_' + muWP,
        'samples': ALL
    }
    aliases['LepWPSF%dl' % N] = {
        'expr': 'LepSF%dl__ele_' % N + eleWP + '__mu_' + muWP,
        'samples': mc
    }
    # prompt gen-matching of the first N leptons. GenLepMatch{N}l in the nanoAOD
    # matches to *any* gen lepton, which is not what we want: a nonprompt lepton
    # matched to a gen lepton from a b decay would pass.
    aliases['PromptGenLepMatch%dl' % N] = {
        'expr': ' * '.join(
            '(Lepton_promptgenmatched.size() > %d ? Lepton_promptgenmatched[%d] : 0.)' % (i, i)
            for i in range(N)),
        'samples': mc
    }

# region-aware versions. Exactly one term survives per event, because the
# region pinned the size; an event outside 2-4 gets 0 rather than a wrong SF.
aliases['LepWPCutN'] = {
    'expr': ' + '.join('(%s == %d) * LepWPCut%dl' % (nlep, N, N) for N in (2, 3, 4)),
    'samples': ALL
}
aliases['LepWPSFN'] = {
    'expr': ' + '.join('(%s == %d) * LepWPSF%dl' % (nlep, N, N) for N in (2, 3, 4)),
    'samples': mc
}
aliases['SFweightNl'] = {
    'expr': ' + '.join('(%s == %d) * SFweight%dl' % (nlep, N, N) for N in (2, 3, 4)),
    'samples': mc
}
aliases['PromptGenLepMatchN'] = {
    'expr': ' + '.join('(%s == %d) * PromptGenLepMatch%dl' % (nlep, N, N) for N in (2, 3, 4)),
    'samples': mc
}

# the old names keep working, so samples.py and nuisances.py need no change
aliases['LepWPCut'] = {'expr': 'LepWPCutN', 'samples': ALL}
aliases['LepWPSF']  = {'expr': 'LepWPSFN',  'samples': mc}

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
    'variables': ['SelLep_eta', 'CleanJet_eta'],
    'external' : '../utils/macros/VBS_functions.cpp',
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
    'variables': ['SelLep_pt', 'SelLep_eta', 'SelLep_phi', 'SelLep_pdgId',
                  'PuppiMET_pt', 'PuppiMET_phi'],
    'external' : '../utils/macros/VBS_functions.cpp',
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
    'variables': ['SelLep_pt', 'SelLep_eta', 'SelLep_phi', 'SelLep_pdgId'],
    'external' : '../utils/macros/VBS_functions.cpp',
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
    'external' : '../utils/macros/VBS_functions.cpp',
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
    'external' : '../utils/macros/VBS_functions.cpp',
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
    'external' : '../utils/macros/VBS_functions.cpp',
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
    'external' : '../utils/macros/VBS_functions.cpp',
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

# The fake-rate reader guards on Lepton_pt.size() == nLeptons_, so it has to be
# fed the selected leptons too. Fed the full collection while the regions pin
# nLepSel, the instances stop being mutually exclusive: in a 2-lepton region an
# event whose third lepton is below threshold has size() == 3, so the 3l
# instance fires and looks the fake rate up below the lowest pT bin of the map,
# which comes back NaN and poisons the whole histogram.
for _c, _e in (
        ('isTightMuon',     f'ROOT::VecOps::RVec<int>(Lepton_isTightMuon_{muWP})'),
        ('isTightElectron', f'ROOT::VecOps::RVec<int>(Lepton_isTightElectron_{eleWP})'),
        ('muonIdx',         'ROOT::VecOps::RVec<int>(Lepton_muonIdx)')):
    aliases['SelLep_' + _c] = {
        'expr'   : f'Take({_e}, nLepSel)',
        'samples': ['Fake'],
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
    # One instance per variation AND per multiplicity. The class handles
    # nLeptons 2 and 3 only, and its isTight_ array holds 3, so there is
    # deliberately no 4-lepton instance: in ZZ_VR the fake estimate is 0.
    # Each instance returns 0 unless the event has exactly its own lepton
    # count, so the two can simply be summed.
    for N in (2, 3):
        aliases['fakeW%dl' % N + label] = {
            # the class is compiled into the generated .cpp, not declared at runtime
            'external'     : f'{macros}fake_rate_reader_class.cc',
            # one global instance per variation, built before main()
            'linesToGlobal': [
                f'fake_rate_reader fr_reader_{N}l_{label or "nominal"}'
                f'("{eleWP}", "{muWP}", "{kind}", {N}, "std", '
                f'"{fakerates}", "2024_v15_pt");'
            ],
            'function'     : f'fr_reader_{N}l_{label or "nominal"}',
            # The typed Define() matches column types exactly and never converts,
            # unlike the JIT-compiled 'expr' this replaces, so each column is cast
            # to exactly what operator() declares. nCleanJet is Int_t, which
            # already matches the int parameter; pt/eta are float and Lepton_pdgId
            # is int, as VBS_functions.cpp already relies on.
            'variables'    : ['SelLep_pdgId', 'SelLep_pt', 'SelLep_eta',
                              'SelLep_isTightMuon',
                              'SelLep_isTightElectron',
                              'SelLep_muonIdx',
                              'CleanJet_pt', '(int)nCleanJet'],
            'samples'      : ['Fake'],
        }

    aliases['fakeW' + label] = {
        'expr'   : 'fakeW2l%s + fakeW3l%s' % (label, label),
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

# Algo / SF name
btagging_SFs = {
    "UParTAK4B"      : "upart",
}

# Algorithm and WP selection
bAlgo = 'UParTAK4B'
WP    = 'loose'     # ['loose','medium','tight','xtight','xxtight']

WP_eval = 'L'# ['L', 'M', 'T', 'XT', 'XXT']
tagger = 'UParTAK4'

# Access information from dictionaries
bWP   = btagging_WPs[bAlgo][WP]

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

eff_map_year = '2024' #['2022', '2022EE', '2023', '2023BPix', '2024]
year = 'Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15' # ['Run3-22CDSep23-Summer22-NanoAODv12', 'Run3-22EFGSep23-Summer22EE-NanoAODv12, 'Run3-23CSep23-Summer23-NanoAODv12', 'Run3-23DSep23-Summer23BPix-NanoAODv12', 'Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15']
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

# One instance per (flavour, shift): the configuration lives in the constructor,
# so operator() takes only columns and can be used by the typed Define().
for flavour in ['bc', 'light']:
    for shift in shifts_needed[flavour]:
        btagsf = 'btagSF' + flavour + ('' if shift == 'central' else '_' + shift)
        aliases[btagsf] = {
            'external'     : f'{macros}evaluate_btagSF{flavour}.cc',
            'linesToGlobal': [
                f'btagSF{flavour} {btagsf}_inst("{eff_map_path}", "{year}", '
                f'"{WP_eval}", "{shift}", "{tagger}", "{eff_map_year}");'
            ],
            'function'     : f'{btagsf}_inst',
            # The typed Define() matches column types exactly and never converts,
            # unlike the JIT-compiled 'expr' this replaces, so every column whose
            # branch type differs from the operator() parameter is cast here:
            #   nCleanJet          is Int_t, operator() takes unsigned int
            #   Jet_hadronFlavour  is UChar_t from NanoAODv12 on, declared RVecI
            # CleanJet_pt/eta are float and CleanJet_jetIdx really is ULong64_t,
            # as VBS_functions.cpp already relies on.
            'variables'    : ['CleanJet_pt', 'CleanJet_eta', 'CleanJet_jetIdx',
                              '(unsigned int)nCleanJet',
                              'ROOT::VecOps::RVec<int>(Jet_hadronFlavour)',
                              f'Jet_btag{bAlgo}'],
            'samples'      : mc,
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
# aliases['LHEPdfWeight_vec']   = {'expr': 'ROOT::VecOps::RVec<double>(LHEPdfWeight)',   'samples': lhesamples}

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
# Each factor switches on the same pinned size, so the product is the
# single-multiplicity weight of whichever region the event belongs to.
aliases['SFweight'] = {
    'expr': ' * '.join(['SFweightNl', 'LepWPCutN', 'LepWPSFN', 'btagSFbc', 'btagSFlight']),
    'samples': mc
}

# lepton SF variations, switched on the multiplicity like the nominal above.
# NB: the nuisances using these are currently commented out in nuisances.py.
for _tag, _flav, _wp in [('Ele', 'ele', eleWP), ('Mu', 'mu', muWP)]:
    for _var in ('Up', 'Down'):
        aliases['SFweight' + _tag + _var] = {
            'expr': ' + '.join(
                '(%s == %d) * LepSF%dl__%s_%s__%s' % (nlep, N, N, _flav, _wp, _var)
                for N in (2, 3, 4)),
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

###############################################################################
#                                                                             #
#  The polarisation networks                                                   #
#                                                                             #
#  Two frozen models from the sibling DNN project, deployed as columns:         #
#                                                                             #
#    dnn2s_*  the two-stage UParT model -- stage 1 separates signal from        #
#             background, stage 2 separates LL/TL/TT. Best expected            #
#             sensitivity on mu_LX of everything that was tried.                #
#    dnn4_*   the four-head multiclass UParT model (background/LL/TL/TT),       #
#             second best, and the one that gives three process outputs in      #
#             one network.                                                      #
#                                                                             #
#  Both read the SAME 42 inputs, so there is one input vector and two reader    #
#  instances over it. The weights -- the fitted preprocessing, the dense        #
#  layers of all ten cross-fit folds and the binning tables -- are frozen into  #
#  a file by `scripts/export_dnn_reader.py` in the DNN project. No torch, no    #
#  onnxruntime, no SOFIE: the reader is a matrix-vector loop, so nothing is     #
#  added to the link line.                                                      #
#                                                                             #
#  WHAT TO HISTOGRAM: `dnn2s_unrolled` and `dnn4_unrolled`. variables.py has    #
#  the binning, including how to give each class its own bin count.             #
#                                                                             #
#  TWO THINGS TO KNOW BEFORE QUOTING A NUMBER FROM THESE TEMPLATES.             #
#                                                                             #
#  1. Every event is scored by the ten-fold ENSEMBLE, because the training      #
#     fold assignment is a StratifiedKFold over a table a batch job cannot      #
#     see. So simulation the networks trained on is scored partly in sample     #
#     and its templates are optimistically sharp. The reader also supports a    #
#     `parity` rule -- model `event % n` -- which IS reproducible here; using    #
#     it needs a training that held its folds out that way.                     #
#                                                                             #
#  2. The networks were trained on a LOOSER region than WW_SR: two jets above   #
#     30 GeV, mjj > 200, no detajj cut and no b veto. Inside WW_SR that is an   #
#     interpolation and is fine. In the 3- and 4-lepton regions the inputs are  #
#     sentinel and the output is whatever the imputation says.                  #
#                                                                             #
###############################################################################

# The weights. Read once per job at construction, through TFile::Open when the
# path is a .root wrapper, so xrootd reaches them from a batch node the way it
# already reaches the b-tag and fake-rate maps.
#
# They are served from SSWW/2024/rootFile/dnn. That directory sits under
# mkShapes' output folder, which .gitignore lists on every branch, so git never
# adds or removes anything in it at a checkout -- which is the whole point. The
# jobs read this path on eos, and a checkout of a branch that does not track
# SSWW/utils/data/dnn deletes that directory: switching the eos clone to
# FakeRate did exactly that and every job died with
# "dnn_reader: cannot open ...". Being under rootFile also puts the weights
# beside the per-tagger subdirectories rather than inside one, so cleaning a
# tagger does not take them.
#
# The copies under SSWW/utils/data/dnn stay tracked, because they are the record
# of which network produced a given set of plots and they are half a megabyte.
# After re-exporting a model, copy them across or the jobs go on reading the old
# network without saying anything:
#
#   cp SSWW/utils/data/dnn/*.root SSWW/2024/rootFile/dnn/
#
dnnweights = 'root://eosuser.cern.ch//eos/user/a/abulla/latinoRDF/plotsConfigurationsRDF/SSWW/2024/rootFile/dnn'

###############################################################################
#  The inputs                                                                  #
#                                                                             #
#  MOST OF THEM ALREADY EXIST. The training ntuple (branch DNNTraining) dumped  #
#  its own `dnn_*` copies because mkSnapshot needed flat columns, but in the    #
#  nanoAOD the same numbers are already there, from mkShapesRDF's               #
#  l2KinProducerFilter. Redefining them here would be two spellings of one      #
#  quantity drifting apart, so they are NOT redefined -- the feature list below #
#  names the existing branch.                                                   #
#                                                                             #
#  This was checked and not assumed. Recomputing each candidate from            #
#  Lepton_*/CleanJet_* on 604945 snapshot events with nLepSel > 1 and           #
#  comparing against the stored `dnn_*` column:                                 #
#                                                                             #
#    pt1 eta1 pt2 eta2        identical, 0 events differ                        #
#    ptll detall drll          max |diff| 1e-4 or below, 0 events above 1e-3     #
#    dphilmet1 drjj            max |diff| 5e-7                                   #
#    dphilep1jet1/2            max |diff| 2e-7                                   #
#    mth vs dnn_mTww           max |diff| 0.05 GeV on 304 of 604945 events,      #
#                              i.e. float32 rounding in a near-cancellation      #
#                                                                             #
#  Two do NOT match and must not be substituted: nanoAOD's `dphill` and         #
#  `dphijj` are SIGNED, the networks were trained on |dphi|. Hence the two      #
#  `abs*` aliases below -- new quantities, not duplicates.                       #
#                                                                             #
#  Also checked: SelLep_* (leptons above 10 GeV) and Lepton_* have the same     #
#  leading two entries in 604945 of 604945 events, so a quantity built on       #
#  Lepton_[0,1] is the one the networks were trained on.                        #
#                                                                             #
#  SENTINELS. A sentinel is not a defect to be patched: it means "this          #
#  quantity does not exist for this event", and the reader imputes the          #
#  training-fold median and raises an absence indicator. It recognises the      #
#  three the training used -- -9999, -1, -99 -- and nanoAOD uses -9999 for      #
#  most of these but -999.9 for a few, which the reader would take as a real    #
#  value. `_absent` below maps anything below -90 onto -9999, which is exactly  #
#  equivalent on the training data (no input of this list is legitimately       #
#  below -90) and safe on everything else.                                      #
###############################################################################

def _absent(expr):
    """Normalise a branch's own sentinel onto one the reader recognises."""
    return '(float)((%s) > -90.f ? (%s) : -9999.f)' % (expr, expr)


def _jet(i, var, sentinel):
    """A pT-ordered CleanJet scalar; CleanJet_* has no flat nanoAOD copy."""
    return '(float)(CleanJet_pt.size() > %d ? CleanJet_%s[%d] : %s)' % (i, var, i, sentinel)


def _jet_mass(i):
    return ('(float)(CleanJet_pt.size() > %d'
            ' ? Take(Jet_mass, CleanJet_jetIdx, -1.f)[%d] : -1.f)' % (i, i))


# -- the two that differ from the nanoAOD branch of the same name -------------
#
# |dphi|, which is what the networks saw. The guard matters: abs(-9999) is
# +9999, which is a perfectly good-looking number and would be fed to the
# network as one.
aliases['absdphill'] = {
    'expr': '(float)(dphill > -90.f ? abs(dphill) : -9999.f)',
    'samples': ALL
}
aliases['absdphijj'] = {
    'expr': '(float)(dphijj > -90.f ? abs(dphijj) : -9999.f)',
    'samples': ALL
}

# -- quantities the nanoAOD does not have -------------------------------------

# Zeppenfeld per object. zstar_max above is these two collapsed by a max();
# the networks get both separately.
aliases['zepp_l1'] = {
    'expr': ('nLepSel > 0 && CleanJet_pt.size() > 1 && abs(CleanJet_eta[0] - CleanJet_eta[1]) > 0.f'
             ' ? (float)abs(SelLep_eta[0] - 0.5f*(CleanJet_eta[0] + CleanJet_eta[1]))'
             '   / (float)abs(CleanJet_eta[0] - CleanJet_eta[1])'
             ' : -1.f'),
    'samples': ALL
}
aliases['zepp_l2'] = {
    'expr': ('nLepSel > 1 && CleanJet_pt.size() > 1 && abs(CleanJet_eta[0] - CleanJet_eta[1]) > 0.f'
             ' ? (float)abs(SelLep_eta[1] - 0.5f*(CleanJet_eta[0] + CleanJet_eta[1]))'
             '   / (float)abs(CleanJet_eta[0] - CleanJet_eta[1])'
             ' : -1.f'),
    'samples': ALL
}

# R_pT, the standard VBS balance variable.
aliases['Rpt'] = {
    'expr': ('nLepSel > 1 && CleanJet_pt.size() > 1'
             ' ? (float)(SelLep_pt[0]*SelLep_pt[1]) / (float)(CleanJet_pt[0]*CleanJet_pt[1])'
             ' : -1.f'),
    'samples': ALL
}

# pT asymmetry of the pair: a longitudinal pair shares the energy more evenly.
aliases['ptAsymll'] = {
    'expr': ('nLepSel > 1 && (SelLep_pt[0] + SelLep_pt[1]) > 0.f'
             ' ? (float)(SelLep_pt[0] - SelLep_pt[1]) / (SelLep_pt[0] + SelLep_pt[1])'
             ' : -9.f'),
    'samples': ALL
}

# ATLAS Table 2's projected transverse mass. Distinct from `mth`, which treats
# the dilepton as one visible object; this keeps the two leptons separate in
# the scalar term, so it responds differently when they are back to back.
aliases['vsum_px'] = {
    'expr': ('nLepSel > 1'
             ' ? (float)(SelLep_pt[0]*cos(SelLep_phi[0]) + SelLep_pt[1]*cos(SelLep_phi[1])'
             '           + PuppiMET_pt*cos(PuppiMET_phi))'
             ' : -9999.f'),
    'samples': ALL
}
aliases['vsum_py'] = {
    'expr': ('nLepSel > 1'
             ' ? (float)(SelLep_pt[0]*sin(SelLep_phi[0]) + SelLep_pt[1]*sin(SelLep_phi[1])'
             '           + PuppiMET_pt*sin(PuppiMET_phi))'
             ' : -9999.f'),
    'samples': ALL
}
aliases['mTo'] = {
    'expr': ('nLepSel > 1'
             ' ? (float)sqrt(std::max(0.,'
             '     pow((double)(SelLep_pt[0] + SelLep_pt[1] + PuppiMET_pt), 2)'
             '   - pow((double)vsum_px, 2) - pow((double)vsum_py, 2)))'
             ' : -1.f'),
    'samples': ALL
}

# RAPIDITY gap of the tagging jets. detajj (pseudorapidity) is what the
# regions cut on and it stays; this is what the ATLAS DNN uses, and for a
# massive jet the two are not the same.
aliases['dyjj'] = {
    'function' : 'deltaYjj',
    'variables': ['CleanJet_pt', 'CleanJet_eta',
                  'Take(Jet_mass, CleanJet_jetIdx, 0.f)'],
    'external' : f'{macros}VBS_functions.cpp',
    'samples'  : ALL
}

# Smallest dR between any selected lepton and any jet above 30 GeV: what
# catches a lepton sitting inside a soft jet, the nonprompt signature.
aliases['drlj_min'] = {
    'function' : 'minDeltaRLepJet',
    'variables': ['SelLep_eta', 'SelLep_phi',
                  'CleanJet_pt', 'CleanJet_eta', 'CleanJet_phi'],
    'external' : f'{macros}VBS_functions.cpp',
    'samples'  : ALL
}

# The continuous UParT inputs: the two tagging jets' own scores, and the
# largest score among central jets -- the b veto as a variable rather than a
# cut. No central jet gives -9999, and that absence is itself the VBS
# signature, so it travels in the indicator instead of being patched.
aliases['btag_jets'] = {
    'function' : 'dnnJetBtag',
    # Types are pinned here and not in the C++: the branch type belongs to the
    # input data (CleanJet_jetIdx is genuinely unsigned 64-bit in these
    # nanoAODs) while the helper signature is shared by every year, and the
    # typed Define compares types rather than converting silently.
    'variables': ['ROOT::VecOps::RVec<unsigned long long>(CleanJet_jetIdx)',
                  f'ROOT::VecOps::RVec<float>(Jet_btag{bAlgo})',
                  'ROOT::VecOps::RVec<float>(CleanJet_pt)',
                  'ROOT::VecOps::RVec<float>(CleanJet_eta)'],
    'external' : f'{macros}VBS_functions.cpp',
    'samples'  : ALL
}
aliases['btag_j1']    = {'expr': 'btag_jets[0]', 'samples': ALL}
aliases['btag_j2']    = {'expr': 'btag_jets[1]', 'samples': ALL}
aliases['btag_max20'] = {'expr': 'btag_jets[2]', 'samples': ALL}

# The two angles of the lepton pair that need no neutrino. ONE number each,
# for the pair: in the rest frame of (l1 + l2) the momenta are exactly back to
# back, so the subleading lepton would give exactly minus the leading one.
aliases['lep_angles'] = {
    'function' : 'computeLeptonAngles',
    'variables': ['SelLep_pt', 'SelLep_eta', 'SelLep_phi', 'SelLep_pdgId'],
    'external' : f'{macros}VBS_functions.cpp',
    'samples'  : ALL
}
aliases['cosThetaCS']  = {'expr': 'lep_angles[0]', 'samples': ALL}
aliases['cosThetaHel'] = {'expr': 'lep_angles[1]', 'samples': ALL}

# The angle between the leading lepton and each tagging jet in the dilepton
# rest frame: dimensionless, so it survives an energy-scale shift, and the
# only engineered input of the two models that is not a branch or a one-line
# expression. NaN where any input is sentinel, which the reader imputes.
aliases['llrest_angles'] = {
    'function' : 'dnnLeptonJetRestAngles',
    'variables': [_absent('pt1'), _absent('eta1'), _absent('phi1'),
                  _absent('pt2'), _absent('eta2'), _absent('phi2'),
                  _jet(0, 'pt', '-1.f'), _jet(0, 'eta', '-99.f'),
                  _jet(0, 'phi', '-99.f'), _jet_mass(0),
                  _jet(1, 'pt', '-1.f'), _jet(1, 'eta', '-99.f'),
                  _jet(1, 'phi', '-99.f'), _jet_mass(1)],
    'external' : f'{macros}VBS_functions.cpp',
    'samples'  : ALL
}
aliases['cos_l1j1_llrest'] = {'expr': 'llrest_angles[0]', 'samples': ALL}
aliases['cos_l1j2_llrest'] = {'expr': 'llrest_angles[1]', 'samples': ALL}

# ------------------------------------------------
# The input vector
#
# ORDER IS THE INTERFACE. The reader indexes positionally and checks only the
# length, so a permutation here feeds every network the wrong numbers with no
# error anywhere. The second column is the name the training table used, i.e.
# `features.json` of both runs, which the exporter also writes into the weight
# file: diff the two before trusting a new export.
# ------------------------------------------------
dnn_features = [
    # expression here                      # name in features.json
    (_absent('pt1'),                        'dnn_l1_pt'),
    (_absent('eta1'),                       'dnn_l1_eta'),
    (_absent('pt2'),                        'dnn_l2_pt'),
    (_absent('eta2'),                       'dnn_l2_eta'),
    ('(float)(nLepSel > 0 ? Lepton_pdgId[0] : 0)', 'dnn_l1_pdgId'),
    ('(float)(nLepSel > 1 ? Lepton_pdgId[1] : 0)', 'dnn_l2_pdgId'),
    (_absent('mll'),                        'mll'),
    (_absent('ptll'),                       'dnn_ptll'),
    (_absent('drll'),                       'dnn_drll'),
    (_absent('detall'),                     'dnn_detall'),
    ('absdphill',                           'dnn_dphill'),
    ('(float)PuppiMET_pt',                  'PuppiMET_pt'),
    (_absent('proxyW_l1'),                  'proxyW_l1'),
    (_absent('proxyW_l2'),                  'proxyW_l2'),
    (_absent('mth'),                        'dnn_mTww'),
    ('mTo',                                 'dnn_mTo'),
    (_absent('dphilmet1'),                  'dnn_dphi_METl1'),
    ('zepp_l1',                             'dnn_zepp_l1'),
    ('zepp_l2',                             'dnn_zepp_l2'),
    (_jet(0, 'pt', '-1.f'),                 'dnn_j1_pt'),
    (_jet(0, 'eta', '-99.f'),               'dnn_j1_eta'),
    (_jet(1, 'pt', '-1.f'),                 'dnn_j2_pt'),
    (_jet(1, 'eta', '-99.f'),               'dnn_j2_eta'),
    (_absent('mjj'),                        'mjj'),
    ('dyjj',                                'dnn_dyjj'),
    (_absent('drjj'),                       'dnn_drjj'),
    ('absdphijj',                           'dnn_dphijj'),
    (_absent('dphilep1jet1'),               'dnn_dphi_j1l1'),
    (_absent('dphilep1jet2'),               'dnn_dphi_j2l1'),
    ('Rpt',                                 'dnn_Rpt'),
    ('drlj_min',                            'dnn_drlj_min'),
    (_absent('detajj'),                     'detajj'),
    ('btag_j1',                             'dnn_j1_btagUParTAK4B'),
    ('btag_j2',                             'dnn_j2_btagUParTAK4B'),
    ('btag_max20',                          'dnn_btag_max20'),
    ('cosThetaCS',                          'dnn_cosThetaCS'),
    ('cosThetaHel',                         'dnn_cosThetaHel'),
    ('cos_l1j1_llrest',                     'n_cos_l1_j1_llrest'),
    ('cos_l1j2_llrest',                     'n_cos_l1_j2_llrest'),
    ('ptAsymll',                            'dnn_ptAsymll'),
    (_absent('mT2'),                        'mT2'),
    (_absent('zstar_max'),                  'zstar_max'),
]
aliases['dnn_inputs'] = {
    'expr': ('ROOT::VecOps::RVec<float>{'
             + ', '.join('(float)(%s)' % _e for _e, _n in dnn_features) + '}'),
    'samples': ALL
}

# ------------------------------------------------
# The models
#
# One global instance each, constructed once per job: the constructor reads
# and validates the weight file, so a wrong path or a truncated file stops the
# job instead of producing a column of zeros.
#
# Each call returns one RVec<float> per event, ending in three columns that
# are the ones the analysis actually uses:
#
#   axis      the continuous discriminant being binned -- the stage-1 signal
#             probability for the two-stage model, the winning class
#             probability for the four-head one.
#   cell      an INTEGER, the categorical part of the observable: the discrete
#             choice the network made. No bin ever crosses it.
#   unrolled  `cell + F_cell(axis)`, the integer cell plus a fraction in
#             [0, 1) -- the axis mapped through the empirical CDF of the
#             reference signal INSIDE THAT CELL, frozen into the weight file
#             at export time. This is the one column to histogram.
#
# Why unrolled and not the raw score: F_cell is a CDF, so that fraction is
# uniform on [0, 1) by construction, and `n` equal-width bins inside one cell
# are exactly that cell's `n` quantile bins. The quantile rule therefore
# travels inside the weight file, where it belongs -- the edges are a property
# of this network and moved when it was retrained -- while the NUMBER of bins
# stays a free choice in variables.py. Only multiples of the cell count are
# meaningful: a bin straddling two cells averages two categories and the fit
# reads the average.
#
# The cells, as the two deployed weight files define them:
#
#   twostage_uparT_open_64x32  6 cells = argmax(stage 2) in {LL, TL, TT},
#              times the stage-2 winning probability cut in two at 0.569 (LL),
#              0.450 (TL), 0.472 (TT). So the cell says which polarisation the
#              second stage picked and how sure it was, and the axis inside it
#              is the stage-1 signal-vs-background score. dnn2s_unrolled is
#              therefore in [0, 6).
#   mc4_uparT_open_64x32       4 cells = argmax in {background, LL, TL, TT},
#              with no sub-split, and the axis is that winning probability.
#              dnn4_unrolled is in [0, 4).
#
# How many bins is NOT decided here: variables.py does it, today 24 for each
# observable (6 cells x 4 and 4 cells x 6), with `dnn_bins` there to spend a
# different number per cell. Its comment block is the place to read next.
#
# Index by index, which is what the [i] below are:
#   two-stage  [0,1] stage-1 background/signal, [2..4] stage-2 LL/TL/TT,
#              [5] axis = stage-1 signal score, [6] cell, [7] unrolled
#   multiclass [0..3] background/LL/TL/TT, [4] axis = winning probability,
#              [5] cell, [6] unrolled
#
# **Only `dnn2s_unrolled` and `dnn4_unrolled` are needed to fit.** Every other
# alias below is for control plots and for debugging, and none of them costs
# anything: RDF evaluates a Define only when a booked action asks for it, so
# an unused alias is compile time and no event loop.
# ------------------------------------------------
aliases['dnn2s'] = {
    'external'     : f'{macros}dnn_reader_class.cc',
    'linesToGlobal': [
        f'dnn_reader dnn2s_inst("{dnnweights}/twostage_uparT_open_64x32.root");'
    ],
    'function'     : 'dnn2s_inst',
    # The event number selects the fold model when the weight file says
    # `parity`; under `ensemble` the reader ignores it. It travels either way
    # so that changing the rule is a re-export and not an edit here.
    'variables'    : ['dnn_inputs', '(unsigned long long)event'],
    'samples'      : ALL
}
# The stage-2 probabilities are CONDITIONAL on the event being signal: the
# three sum to one whatever the stage-1 score says, so read them together with
# dnn2s_signal and never as a yield.
aliases['dnn2s_p_LL']     = {'expr': 'dnn2s[2]', 'samples': ALL}
aliases['dnn2s_p_TL']     = {'expr': 'dnn2s[3]', 'samples': ALL}
aliases['dnn2s_p_TT']     = {'expr': 'dnn2s[4]', 'samples': ALL}
# The axis: p(signal) of the first stage, the LL+TL+TT-vs-background score.
aliases['dnn2s_signal']   = {'expr': 'dnn2s[5]', 'samples': ALL}
# 0..5, as 2 * argmax(LL/TL/TT) + (stage-2 winning probability above its cell
# edge). Cut on it to select one cell, or plot it to see the populations.
aliases['dnn2s_cell']     = {'expr': 'dnn2s[6]', 'samples': ALL}
# The observable to fit.
aliases['dnn2s_unrolled'] = {'expr': 'dnn2s[7]', 'samples': ALL}
# The unrolled variable with its cell stripped off: the stage-1 score mapped
# through the frozen CDF of its own cell, uniform on [0, 1). Histogramming
# this under a cut on dnn2s_cell bins one cell alone.
aliases['dnn2s_q'] = {'expr': '(float)(dnn2s[7] - dnn2s[6])', 'samples': ALL}

aliases['dnn4'] = {
    'external'     : f'{macros}dnn_reader_class.cc',
    'linesToGlobal': [
        f'dnn_reader dnn4_inst("{dnnweights}/mc4_uparT_open_64x32.root");'
    ],
    'function'     : 'dnn4_inst',
    'variables'    : ['dnn_inputs', '(unsigned long long)event'],
    'samples'      : ALL
}
aliases['dnn4_p_bkg']    = {'expr': 'dnn4[0]', 'samples': ALL}
aliases['dnn4_p_LL']     = {'expr': 'dnn4[1]', 'samples': ALL}
aliases['dnn4_p_TL']     = {'expr': 'dnn4[2]', 'samples': ALL}
aliases['dnn4_p_TT']     = {'expr': 'dnn4[3]', 'samples': ALL}
# The axis: the probability of the winning class, so always >= 0.25.
aliases['dnn4_pmax']     = {'expr': 'dnn4[4]', 'samples': ALL}
# The cell, 0..3: 0 background, 1 LL, 2 TL, 3 TT -- the argmax, nothing else.
aliases['dnn4_cat']      = {'expr': 'dnn4[5]', 'samples': ALL}
# The observable to fit.
aliases['dnn4_unrolled'] = {'expr': 'dnn4[6]', 'samples': ALL}
aliases['dnn4_q']        = {'expr': '(float)(dnn4[6] - dnn4[5])', 'samples': ALL}

# Two continuous combinations the four-head model can define and the two-stage
# one cannot, kept because they are the axes the DNN project's grid studies
# used and they need no new export.
aliases['dnn4_signal'] = {'expr': '(float)(1.f - dnn4[0])', 'samples': ALL}
aliases['dnn4_LL_frac'] = {
    'expr': '(float)(dnn4[1] / std::max(dnn4[1] + dnn4[2] + dnn4[3], 1e-15f))',
    'samples': ALL
}
