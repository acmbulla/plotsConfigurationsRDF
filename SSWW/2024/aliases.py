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
#  DNN training block (branch DNNTraining)                                    #
#                                                                             #
#  Everything below exists only to be dumped by snapshot.py into the flat      #
#  ntuple the polarisation classifier is trained on. Nothing here is used by    #
#  cuts.py, variables.py or nuisances.py, so mkShapes is unaffected: the        #
#  aliases are Define()d and never read.                                        #
#                                                                             #
#  Two rules the rest of this file already follows, repeated because they bite  #
#  hardest here:                                                                #
#                                                                             #
#  1. Aliases are emitted in *insertion order* with no topological sort         #
#     (analysisFactory._build_aliases_ordered). This block is appended last, so  #
#     it may use anything above it; inside it, order matters.                    #
#                                                                             #
#  2. An alias whose 'expr' touches a branch the sample does not have fails at   #
#     Define() time and kills the job -- it is NOT silently dropped the way a    #
#     missing *dump* column is. So every gen-level alias is restricted to `mc`   #
#     and every LHE one to `lhesamples`.                                         #
#                                                                             #
###############################################################################

# ------------------------------------------------
# Scalar lepton kinematics
#
# SelLep_* are the pT-ordered leptons above 10 GeV (see the top of this file).
# The DNN wants a fixed-width flat row, not a jagged array, so each of the two
# same-sign leptons is unrolled into scalars. The guards return a sentinel
# rather than reading out of range: the DNN_train region pins nLepSel == 2, but
# these aliases are defined for every event the supercut lets through.
# ------------------------------------------------
for _i, _l in ((0, 'l1'), (1, 'l2')):
    aliases['dnn_%s_pt' % _l] = {
        'expr': 'nLepSel > %d ? SelLep_pt[%d] : -1.f' % (_i, _i),
        'samples': ALL
    }
    aliases['dnn_%s_eta' % _l] = {
        'expr': 'nLepSel > %d ? SelLep_eta[%d] : -99.f' % (_i, _i),
        'samples': ALL
    }
    aliases['dnn_%s_phi' % _l] = {
        'expr': 'nLepSel > %d ? SelLep_phi[%d] : -99.f' % (_i, _i),
        'samples': ALL
    }
    aliases['dnn_%s_pdgId' % _l] = {
        'expr': 'nLepSel > %d ? SelLep_pdgId[%d] : 0' % (_i, _i),
        'samples': ALL
    }

# Charge of the same-sign pair. The LL fraction is not charge symmetric at the
# LHC (W+W+ and W-W- have different parton luminosities and different
# longitudinal fractions), so this is a genuine input, not bookkeeping.
aliases['dnn_lep_charge'] = {
    'expr': 'nLepSel > 0 ? (SelLep_pdgId[0] > 0 ? -1 : 1) : 0',
    'samples': ALL
}

# ------------------------------------------------
# The dilepton system
#
# dphill and detall are the classic LL discriminants in SSWW: the longitudinal
# W pair gives leptons that are closer in the transverse plane and more
# central, because the decay of a longitudinal W pushes the charged lepton
# along the W direction rather than against it.
# ------------------------------------------------
aliases['dnn_ptll'] = {
    'expr': ('nLepSel > 1'
             ' ? (float)sqrt(pow(SelLep_pt[0]*cos(SelLep_phi[0]) + SelLep_pt[1]*cos(SelLep_phi[1]), 2)'
             '             + pow(SelLep_pt[0]*sin(SelLep_phi[0]) + SelLep_pt[1]*sin(SelLep_phi[1]), 2))'
             ' : -1.f'),
    'samples': ALL
}
aliases['dnn_dphill'] = {
    'expr': 'nLepSel > 1 ? (float)abs(ROOT::VecOps::DeltaPhi(SelLep_phi[0], SelLep_phi[1])) : -1.f',
    'samples': ALL
}
aliases['dnn_detall'] = {
    'expr': 'nLepSel > 1 ? (float)abs(SelLep_eta[0] - SelLep_eta[1]) : -1.f',
    'samples': ALL
}
aliases['dnn_drll'] = {
    'expr': 'nLepSel > 1 ? (float)sqrt(pow(dnn_detall, 2) + pow(dnn_dphill, 2)) : -1.f',
    'samples': ALL
}
aliases['dnn_etall'] = {
    'expr': 'nLepSel > 1 ? (float)(SelLep_eta[0] + SelLep_eta[1]) / 2.f : -99.f',
    'samples': ALL
}
# pT asymmetry of the pair. For a longitudinal pair the two leptons share the
# energy more evenly than for a transverse one.
aliases['dnn_ptAsymll'] = {
    'expr': ('nLepSel > 1 && (SelLep_pt[0] + SelLep_pt[1]) > 0.f'
             ' ? (float)(SelLep_pt[0] - SelLep_pt[1]) / (SelLep_pt[0] + SelLep_pt[1])'
             ' : -9.f'),
    'samples': ALL
}

# ------------------------------------------------
# MET and the transverse WW system
#
# The two neutrinos are not separable from PuppiMET alone; the DNN gets the
# transverse projections and the full lepton kinematics and may learn whatever
# of the longitudinal information survives. Stage 3 (the neutrino solving) is
# done offline in python from exactly these branches plus dnn_l{1,2}_*, which
# is why MET is dumped as px/py as well as pt/phi -- no trigonometry needed on
# the python side and no ambiguity about the phi convention.
# ------------------------------------------------
aliases['dnn_met_px'] = {'expr': '(float)(PuppiMET_pt * cos(PuppiMET_phi))', 'samples': ALL}
aliases['dnn_met_py'] = {'expr': '(float)(PuppiMET_pt * sin(PuppiMET_phi))', 'samples': ALL}

aliases['dnn_dphi_llMET'] = {
    'expr': ('nLepSel > 1'
             ' ? (float)abs(ROOT::VecOps::DeltaPhi('
             '     (float)atan2(SelLep_pt[0]*sin(SelLep_phi[0]) + SelLep_pt[1]*sin(SelLep_phi[1]),'
             '                  SelLep_pt[0]*cos(SelLep_phi[0]) + SelLep_pt[1]*cos(SelLep_phi[1])),'
             '     (float)PuppiMET_phi))'
             ' : -1.f'),
    'samples': ALL
}

# mT of the whole WW system, treating the dilepton as one visible object.
aliases['dnn_mTww'] = {
    'expr': ('nLepSel > 1'
             ' ? (float)sqrt(2.f * dnn_ptll * PuppiMET_pt * (1.f - cos(dnn_dphi_llMET)))'
             ' : -1.f'),
    'samples': ALL
}

# Smallest dphi between MET and any jet above 20 GeV: separates a real
# neutrino from jet mismeasurement, which is what the nonprompt background
# looks like at low MET.
aliases['dnn_mindphi_METjet'] = {
    'expr': ('Sum(CleanJet_pt > 20.f) > 0'
             ' ? (float)ROOT::VecOps::Min('
             '     abs(ROOT::VecOps::DeltaPhi(CleanJet_phi[CleanJet_pt > 20.f], (float)PuppiMET_phi)))'
             ' : -1.f'),
    'samples': ALL
}

# ------------------------------------------------
# The VBS tagging jets
#
# CleanJet_* is pT ordered, and the supercut already requires two jets above
# 50 GeV, so j1/j2 are the tagging pair by the analysis definition. The
# *leading-mjj* pair would be a different choice; it is not made here, because
# changing it must not mean re-running the jobs -- CleanJet_* is dumped whole
# below so the alternative pairing can be built offline.
# ------------------------------------------------
for _i, _j in ((0, 'j1'), (1, 'j2'), (2, 'j3')):
    aliases['dnn_%s_pt' % _j] = {
        'expr': 'CleanJet_pt.size() > %d ? CleanJet_pt[%d] : -1.f' % (_i, _i),
        'samples': ALL
    }
    aliases['dnn_%s_eta' % _j] = {
        'expr': 'CleanJet_eta.size() > %d ? CleanJet_eta[%d] : -99.f' % (_i, _i),
        'samples': ALL
    }
    aliases['dnn_%s_phi' % _j] = {
        'expr': 'CleanJet_phi.size() > %d ? CleanJet_phi[%d] : -99.f' % (_i, _i),
        'samples': ALL
    }
    aliases['dnn_%s_mass' % _j] = {
        'expr': ('CleanJet_pt.size() > %d'
                 ' ? Take(Jet_mass, CleanJet_jetIdx, -1.f)[%d] : -1.f' % (_i, _i)),
        'samples': ALL
    }

aliases['dnn_dphijj'] = {
    'expr': ('CleanJet_pt.size() > 1'
             ' ? (float)abs(ROOT::VecOps::DeltaPhi(CleanJet_phi[0], CleanJet_phi[1])) : -1.f'),
    'samples': ALL
}
aliases['dnn_drjj'] = {
    'expr': ('CleanJet_pt.size() > 1'
             ' ? (float)sqrt(pow(CleanJet_eta[0] - CleanJet_eta[1], 2) + pow(dnn_dphijj, 2)) : -1.f'),
    'samples': ALL
}
aliases['dnn_ptjj'] = {
    'expr': ('CleanJet_pt.size() > 1'
             ' ? (float)sqrt(pow(CleanJet_pt[0]*cos(CleanJet_phi[0]) + CleanJet_pt[1]*cos(CleanJet_phi[1]), 2)'
             '             + pow(CleanJet_pt[0]*sin(CleanJet_phi[0]) + CleanJet_pt[1]*sin(CleanJet_phi[1]), 2))'
             ' : -1.f'),
    'samples': ALL
}
# Sign of eta_j1 * eta_j2: VBS puts the two tagging jets in opposite
# hemispheres, QCD-induced production does not.
aliases['dnn_etaProdjj'] = {
    'expr': 'CleanJet_pt.size() > 1 ? (float)(CleanJet_eta[0] * CleanJet_eta[1]) : -99.f',
    'samples': ALL
}

# ------------------------------------------------
# Zeppenfeld / centrality
#
# zstar_max is already defined above (the analysis cut variable). These are the
# per-object versions the DNN can use without the max() collapsing them, plus
# the Zeppenfeld of a third jet, which is the central-jet-veto information in
# continuous form.
# ------------------------------------------------
aliases['dnn_zepp_l1'] = {
    'expr': ('nLepSel > 0 && CleanJet_pt.size() > 1 && abs(CleanJet_eta[0] - CleanJet_eta[1]) > 0.f'
             ' ? (float)abs(SelLep_eta[0] - 0.5f*(CleanJet_eta[0] + CleanJet_eta[1]))'
             '   / (float)abs(CleanJet_eta[0] - CleanJet_eta[1])'
             ' : -1.f'),
    'samples': ALL
}
aliases['dnn_zepp_l2'] = {
    'expr': ('nLepSel > 1 && CleanJet_pt.size() > 1 && abs(CleanJet_eta[0] - CleanJet_eta[1]) > 0.f'
             ' ? (float)abs(SelLep_eta[1] - 0.5f*(CleanJet_eta[0] + CleanJet_eta[1]))'
             '   / (float)abs(CleanJet_eta[0] - CleanJet_eta[1])'
             ' : -1.f'),
    'samples': ALL
}
aliases['dnn_zepp_ll'] = {
    'expr': ('nLepSel > 1 && CleanJet_pt.size() > 1 && abs(CleanJet_eta[0] - CleanJet_eta[1]) > 0.f'
             ' ? (float)abs(dnn_etall - 0.5f*(CleanJet_eta[0] + CleanJet_eta[1]))'
             '   / (float)abs(CleanJet_eta[0] - CleanJet_eta[1])'
             ' : -1.f'),
    'samples': ALL
}
aliases['dnn_zepp_j3'] = {
    'expr': ('CleanJet_pt.size() > 2 && abs(CleanJet_eta[0] - CleanJet_eta[1]) > 0.f'
             ' ? (float)abs(CleanJet_eta[2] - 0.5f*(CleanJet_eta[0] + CleanJet_eta[1]))'
             '   / (float)abs(CleanJet_eta[0] - CleanJet_eta[1])'
             ' : -1.f'),
    'samples': ALL
}
# R_pT: the standard VBS balance variable.
aliases['dnn_Rpt'] = {
    'expr': ('nLepSel > 1 && CleanJet_pt.size() > 1'
             ' ? (float)(SelLep_pt[0]*SelLep_pt[1]) / (float)(CleanJet_pt[0]*CleanJet_pt[1])'
             ' : -1.f'),
    'samples': ALL
}

# ------------------------------------------------
# Hadronic activity and b tagging
#
# bVeto / bReq are booleans above; the DNN gets the counts instead, so the
# working point stays changeable downstream.
# ------------------------------------------------
for _thr in (20, 30, 50):
    aliases['dnn_njet%d' % _thr] = {
        'expr': 'Sum(CleanJet_pt > %d.f && abs(CleanJet_eta) < 5.0)' % _thr,
        'samples': ALL
    }
aliases['dnn_ht_jets'] = {
    'expr': 'Sum(CleanJet_pt[CleanJet_pt > 20.f && abs(CleanJet_eta) < 5.0])',
    'samples': ALL
}
aliases['dnn_nbjet'] = {
    'expr': (f'Sum(CleanJet_pt > 20. && abs(CleanJet_eta) < 2.5'
             f' && Take(Jet_btag{bAlgo}, CleanJet_jetIdx, -999.f) > {bWP})'),
    'samples': ALL
}
# The largest b-tag discriminant among the central jets, so the WP itself can
# be moved offline rather than being frozen into the ntuple.
aliases['dnn_maxbtag'] = {
    'expr': (f'Sum(CleanJet_pt > 20. && abs(CleanJet_eta) < 2.5) > 0'
             f' ? (float)ROOT::VecOps::Max('
             f'     Take(Jet_btag{bAlgo}, CleanJet_jetIdx, -999.f)'
             f'     [CleanJet_pt > 20. && abs(CleanJet_eta) < 2.5])'
             f' : -1.f'),
    'samples': ALL
}

# ------------------------------------------------
# Lepton-jet geometry
#
# dr_lj / m_lj above give the four (lepton, jet) combinations as arrays; these
# are the two that matter for the nonprompt background, as scalars.
# ------------------------------------------------
aliases['dnn_drl1j_min'] = {
    'expr': 'nLepSel > 0 && CleanJet_pt.size() > 1 ? (float)std::min(dr_lj[0], dr_lj[1]) : -1.f',
    'samples': ALL
}
aliases['dnn_drl2j_min'] = {
    'expr': 'nLepSel > 1 && CleanJet_pt.size() > 1 ? (float)std::min(dr_lj[2], dr_lj[3]) : -1.f',
    'samples': ALL
}

# ------------------------------------------------
# Weight decomposition -- the INFERNO ingredients
#
# my_sample_weight (added automatically by mkSnapshot) is the product of
# everything. INFERNO needs the *factors* separately, because the loss has to
# re-weight an event under a shifted nuisance without re-running the jobs: a
# single collapsed number cannot be un-multiplied. Each factor below is dumped
# as its own branch so the varied weight is
#     w_shifted = my_sample_weight / f_nominal * f_shifted
# computed in python.
#
# The btagSF*_{up,down}_{correlated,uncorrelated} aliases already exist above,
# built from `shifts_needed`; they are simply listed in snapshot.py. If a
# nuisance is wanted that is not in `shifts_needed`, add the shift there first
# or the alias will not exist and the column will be silently dropped from the
# dump (see snapshot.py).
# ------------------------------------------------
aliases['dnn_w_xs']     = {'expr': 'XSWeight',    'samples': mc}
aliases['dnn_w_sf']     = {'expr': 'SFweight',    'samples': mc}
aliases['dnn_w_lepsf']  = {'expr': 'LepWPSFN',    'samples': mc}
aliases['dnn_w_lepcut'] = {'expr': 'LepWPCutN',   'samples': ALL}
aliases['dnn_w_glob']   = {'expr': 'SFweightNl',  'samples': mc}
aliases['dnn_w_match']  = {'expr': 'PromptGenLepMatchN', 'samples': mc}

# ------------------------------------------------
# Gen-level truth for the polarisation target
#
# Stages 0 and 1 do not need any of this: the LL / TL / TT label is the *sample*
# the event came from (VBS_SSWW_WWCM_LL / _TL / _TT), and the sample name is in
# the output file name, not in the tree -- see snapshot.py.
#
# Stage 3 does need it: reconstructing the W decay and checking the
# reconstruction against truth requires the gen W bosons and the gen leptons.
# LHEPart_* is the cheapest handle (a handful of entries, the hard-process
# final state) and is enough to build both W four-momenta and cos(theta*).
#
# UNVERIFIED: no file was opened to confirm these branches survive the latino
# skim. Check before submitting -- see the recipe at the bottom of snapshot.py.
# A missing branch here is harmless (the dump drops unknown columns silently)
# but it means stage 3 has no truth, which you would only find out much later.
# ------------------------------------------------
# No alias is defined over LHEPart_*: an alias touching a branch that is not
# there is a crash, while a *dump column* that is not there is silently
# dropped. So the LHE block is listed as raw branch names in snapshot.py,
# which fails soft, and the four-vector algebra is done offline in python.
