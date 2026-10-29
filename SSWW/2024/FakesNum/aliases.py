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

# Disabled for the fake-rate measurement: use per-lepton tight and prompt flags; LepCut1l/LepSF1l do not exist.
# # -------- lepton WP, per lepton multiplicity
# #
# # Every region pins nLepSel with '==' (see cuts.py):
# #     WW_SR, nonprompt_CR, WW_VR_bveto, WW_VR_btag   -> 2
# #     WZ_SR, WZb_CR, WZ_VR_bveto, WZ_VR_btag         -> 3
# #     ZZ_VR                                          -> 4
# # so switching on that count picks exactly the multiplicity the region requires.
# # A region written with '>=' instead of '==' would silently get the weight of
# # whichever multiplicity the event happens to have.
# #
# # These four always have to agree on N -- the tight requirement, the lepton SF,
# # the global SF and the prompt gen-matching. The nanoAOD provides LepCut{N}l,
# # LepSF{N}l, SFweight{N}l and Lepton_promptgenmatched for N = 2, 3, 4.
# nlep = 'nLepSel'

# for N in (1, 2, 3, 4):
#     aliases['LepWPCut%dl' % N] = {
#         'expr': 'LepCut%dl__ele_' % N + eleWP + '__mu_' + muWP,
#         'samples': ALL
#     }
#     aliases['LepWPSF%dl' % N] = {
#         'expr': 'LepSF%dl__ele_' % N + eleWP + '__mu_' + muWP,
#         'samples': mc
#     }
#     # prompt gen-matching of the first N leptons. GenLepMatch{N}l in the nanoAOD
#     # matches to *any* gen lepton, which is not what we want: a nonprompt lepton
#     # matched to a gen lepton from a b decay would pass.
#     aliases['PromptGenLepMatch%dl' % N] = {
#         'expr': ' * '.join(
#             '(Lepton_promptgenmatched.size() > %d ? Lepton_promptgenmatched[%d] : 0.)' % (i, i)
#             for i in range(N)),
#         'samples': mc
#     }

# # region-aware versions. Exactly one term survives per event, because the
# # region pinned the size; an event outside 2-4 gets 0 rather than a wrong SF.
# aliases['LepWPCutN'] = {
#     'expr': ' + '.join('(%s == %d) * LepWPCut%dl' % (nlep, N, N) for N in (2, 3, 4)),
#     'samples': ALL
# }
# aliases['LepWPSFN'] = {
#     'expr': ' + '.join('(%s == %d) * LepWPSF%dl' % (nlep, N, N) for N in (2, 3, 4)),
#     'samples': mc
# }
# aliases['SFweightNl'] = {
#     'expr': ' + '.join('(%s == %d) * SFweight%dl' % (nlep, N, N) for N in (2, 3, 4)),
#     'samples': mc
# }
# aliases['PromptGenLepMatchN'] = {
#     'expr': ' + '.join('(%s == %d) * PromptGenLepMatch%dl' % (nlep, N, N) for N in (2, 3, 4)),
#     'samples': mc
# }

# # the old names keep working, so samples.py and nuisances.py need no change
# aliases['LepWPCut'] = {'expr': 'LepWPCutN', 'samples': ALL}
# aliases['LepWPSF']  = {'expr': 'LepWPSFN',  'samples': mc}

# ------------------------------------------------
# Same-sign 2-lepton flavour aliases (WW SR)
# product is positive for same-sign pairs
# ------------------------------------------------
# On nLepSel and SelLep_pdgId, not on the raw collection: Lepton_pdgId.size()
# counts every object the skim kept, including the soft ones below the 10 GeV
# threshold that nLepSel defines the region with, so the two disagree on
# exactly the events where a third soft lepton exists. One counter, used
# everywhere.
# Disabled for the fake-rate measurement: unused analysis flavour categories.
# aliases['ee'] = {
#     'expr': 'nLepSel == 2 && SelLep_pdgId[0] * SelLep_pdgId[1] == 11*11',
#     'samples': ALL
# }

# aliases['mumu'] = {
#     'expr': 'nLepSel == 2 && SelLep_pdgId[0] * SelLep_pdgId[1] == 13*13',
#     'samples': ALL
# }

# aliases['emu'] = {
#     'expr': 'nLepSel == 2 && SelLep_pdgId[0] * SelLep_pdgId[1] == 11*13',
#     'samples': ALL
# }

# ------------------------------------------------
# Zeppenfeld variable: max over all leptons
# z*_l = |eta_l - (eta_j1+eta_j2)/2| / delta_eta_jj
# ------------------------------------------------
aliases['zstar_max'] = {
    'function' : 'computeZstar',
    'variables': ['SelLep_eta', 'CleanJet_eta'],
    'external' : '../../utils/macros/VBS_functions.cpp',
    'samples'  : ALL
}

# Disabled for the fake-rate measurement: three- and four-lepton analysis variables are outside nLepSel <= 2.
# # ------------------------------------------------
# # WZ variables (3 leptons, exactly)
# # computeWZvars returns:
# #   [0] mll_Z   [1] mlll   [2] idx_W   [3] category
# #   [4] pt_W    [5] pt_Z1  [6] pt_Z2   [7] proxyW_W
# # Returns -9999 if not exactly 3 leptons or no SFOS pair found
# # ------------------------------------------------
# aliases['WZ_vars'] = {
#     'function' : 'computeWZvars',
#     'variables': ['SelLep_pt', 'SelLep_eta', 'SelLep_phi', 'SelLep_pdgId',
#                   'PuppiMET_pt', 'PuppiMET_phi'],
#     'external' : '../../utils/macros/VBS_functions.cpp',
#     'samples'  : ALL
# }
# aliases['mll_Z']    = { 'expr': 'WZ_vars[0]', 'samples': ALL }
# aliases['mlll']     = { 'expr': 'WZ_vars[1]', 'samples': ALL }
# aliases['idx_W']    = { 'expr': 'WZ_vars[2]', 'samples': ALL }
# aliases['WZ_flav']  = { 'expr': 'WZ_vars[3]', 'samples': ALL }
# aliases['pt_W']     = { 'expr': 'WZ_vars[4]', 'samples': ALL }
# aliases['pt_Z1']    = { 'expr': 'WZ_vars[5]', 'samples': ALL }  # leading Z lepton pT
# aliases['pt_Z2']    = { 'expr': 'WZ_vars[6]', 'samples': ALL }  # trailing Z lepton pT
# aliases['proxyW_W'] = { 'expr': 'WZ_vars[7]', 'samples': ALL }  # mT(lW, MET)

# # WZ flavour categories (Z_flav*100 + W_flav, 11=e, 13=mu)
# aliases['eee'] = { 'expr': 'WZ_flav == 1111', 'samples': ALL }  # Z->ee,  W->e
# aliases['eem'] = { 'expr': 'WZ_flav == 1113', 'samples': ALL }  # Z->ee,  W->mu
# aliases['mme'] = { 'expr': 'WZ_flav == 1311', 'samples': ALL }  # Z->mumu, W->e
# aliases['mmm'] = { 'expr': 'WZ_flav == 1313', 'samples': ALL }  # Z->mumu, W->mu

# # ------------------------------------------------
# # ZZ variables (4 leptons, exactly)
# # computeZZvars returns:
# #   [0] mll_Z1  [1] mll_Z2  [2] mllll  [3] category
# #   [4] pt_4l_1 [5] pt_4l_2
# # Returns -9999 if not exactly 4 leptons or fewer than 2 SFOS pairs
# # ------------------------------------------------
# aliases['ZZ_vars'] = {
#     'function' : 'computeZZvars',
#     'variables': ['SelLep_pt', 'SelLep_eta', 'SelLep_phi', 'SelLep_pdgId'],
#     'external' : '../../utils/macros/VBS_functions.cpp',
#     'samples'  : ALL
# }
# aliases['mll_Z1']  = { 'expr': 'ZZ_vars[0]', 'samples': ALL }
# aliases['mll_Z2']  = { 'expr': 'ZZ_vars[1]', 'samples': ALL }
# aliases['mllll']   = { 'expr': 'ZZ_vars[2]', 'samples': ALL }
# aliases['ZZ_flav'] = { 'expr': 'ZZ_vars[3]', 'samples': ALL }
# aliases['pt_4l_1'] = { 'expr': 'ZZ_vars[4]', 'samples': ALL }  # leading lepton pT
# aliases['pt_4l_2'] = { 'expr': 'ZZ_vars[5]', 'samples': ALL }  # subleading lepton pT

# # ZZ flavour categories
# aliases['eeee'] = { 'expr': 'ZZ_flav == 1111', 'samples': ALL }
# aliases['eemm'] = { 'expr': 'ZZ_flav == 1113', 'samples': ALL }
# aliases['mmmm'] = { 'expr': 'ZZ_flav == 1313', 'samples': ALL }

# ------------------------------------------------
# DeltaR between leptons and jets
# dr_lj[0]=dr(l1,j1), [1]=dr(l1,j2), [2]=dr(l2,j1), [3]=dr(l2,j2)
# Returns -9999 if fewer than 2 leptons or 2 jets
# ------------------------------------------------
aliases['dr_lj'] = {
    'function' : 'dr_lj',
    'variables': ['CleanJet_eta', 'CleanJet_phi', 'Lepton_eta', 'Lepton_phi'],
    'external' : '../../utils/macros/VBS_functions.cpp',
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
    'external' : '../../utils/macros/VBS_functions.cpp',
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
    'external' : '../../utils/macros/VBS_functions.cpp',
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
    'external' : '../../utils/macros/VBS_functions.cpp',
    'samples'  : ALL
}


# Disabled for the fake-rate measurement: unused analysis jet categories.
# # Jet bins
# # using Alt(CleanJet_pt, n, 0) instead of Sum(CleanJet_pt >= 30) because jet pt ordering is not strictly followed in JES-varied samples

# # No jet with pt > 30 GeV
# aliases['zeroJet'] = {
#     'expr': 'CleanJet_pt.size() == 0 || CleanJet_pt[0] < 30.',
#     'samples': ALL
# }

# aliases['oneJet'] = {
#     'expr': 'CleanJet_pt.size() > 0 && CleanJet_pt[0] > 30.',
#     'samples': ALL
# }

# aliases['multiJet'] = {
#     'expr': 'CleanJet_pt.size() > 1 && CleanJet_pt[1] > 30.',
#     'samples': ALL
# }

# aliases['noJetInHorn'] = {
#     'expr' : 'Sum(CleanJet_pt > 30 && CleanJet_pt < 50 && abs(CleanJet_eta) > 2.5 && abs(CleanJet_eta) < 3.0) == 0',
#     'samples' : ALL
# }

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
    # ALL, not ['Fake']: the measurement needs the per-lepton tight flags on the
    # data and on the prompt MC that gets subtracted, not only on a Fake sample.
    aliases['SelLep_' + _c] = {
        'expr'   : f'Take({_e}, nLepSel)',
        'samples': ALL,
    }

# Disabled for the fake-rate measurement: no Fake sample; this job measures the maps instead of applying fakeW.
# for kind, label in [
#     ('nominal',     ''),
#     ('EleUp',       'EleUp'),
#     ('EleDown',     'EleDown'),
#     ('MuUp',        'MuUp'),
#     ('MuDown',      'MuDown'),
#     ('StatEleUp',   'StatEleUp'),
#     ('StatEleDown', 'StatEleDown'),
#     ('StatMuUp',    'StatMuUp'),
#     ('StatMuDown',  'StatMuDown'),
# ]:
#     # One instance per variation AND per multiplicity. The class handles
#     # nLeptons 2 and 3 only, and its isTight_ array holds 3, so there is
#     # deliberately no 4-lepton instance: in ZZ_VR the fake estimate is 0.
#     # Each instance returns 0 unless the event has exactly its own lepton
#     # count, so the two can simply be summed.
#     for N in (2, 3):
#         aliases['fakeW%dl' % N + label] = {
#             # the class is compiled into the generated .cpp, not declared at runtime
#             'external'     : f'{macros}fake_rate_reader_class.cc',
#             # one global instance per variation, built before main()
#             'linesToGlobal': [
#                 f'fake_rate_reader fr_reader_{N}l_{label or "nominal"}'
#                 f'("{eleWP}", "{muWP}", "{kind}", {N}, "std", '
#                 f'"{fakerates}", "2024_v15_pt");'
#             ],
#             'function'     : f'fr_reader_{N}l_{label or "nominal"}',
#             # The typed Define() matches column types exactly and never converts,
#             # unlike the JIT-compiled 'expr' this replaces, so each column is cast
#             # to exactly what operator() declares. nCleanJet is Int_t, which
#             # already matches the int parameter; pt/eta are float and Lepton_pdgId
#             # is int, as VBS_functions.cpp already relies on.
#             'variables'    : ['SelLep_pdgId', 'SelLep_pt', 'SelLep_eta',
#                               'SelLep_isTightMuon',
#                               'SelLep_isTightElectron',
#                               'SelLep_muonIdx',
#                               'CleanJet_pt', '(int)nCleanJet'],
#             'samples'      : ['Fake'],
#         }

#     aliases['fakeW' + label] = {
#         'expr'   : 'fakeW2l%s + fakeW3l%s' % (label, label),
#         'samples': ['Fake'],
#     }

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
# Disabled for the fake-rate measurement: no lepton/b-tag SF or LHE variations in the measurement weights.
# for flavour in ['bc', 'light']:
#     for shift in shifts_needed[flavour]:
#         btagsf = 'btagSF' + flavour + ('' if shift == 'central' else '_' + shift)
#         aliases[btagsf] = {
#             'external'     : f'{macros}evaluate_btagSF{flavour}.cc',
#             'linesToGlobal': [
#                 f'btagSF{flavour} {btagsf}_inst("{eff_map_path}", "{year}", '
#                 f'"{WP_eval}", "{shift}", "{tagger}", "{eff_map_year}");'
#             ],
#             'function'     : f'{btagsf}_inst',
#             # The typed Define() matches column types exactly and never converts,
#             # unlike the JIT-compiled 'expr' this replaces, so every column whose
#             # branch type differs from the operator() parameter is cast here:
#             #   nCleanJet          is Int_t, operator() takes unsigned int
#             #   Jet_hadronFlavour  is UChar_t from NanoAODv12 on, declared RVecI
#             # CleanJet_pt/eta are float and CleanJet_jetIdx really is ULong64_t,
#             # as VBS_functions.cpp already relies on.
#             'variables'    : ['CleanJet_pt', 'CleanJet_eta', 'CleanJet_jetIdx',
#                               '(unsigned int)nCleanJet',
#                               'ROOT::VecOps::RVec<int>(Jet_hadronFlavour)',
#                               f'Jet_btag{bAlgo}'],
#             'samples'      : mc,
#         }

# # B tagging selections and scale factors
# aliases['bVeto'] = {
#     'expr': f'Sum(CleanJet_pt > 20. && abs(CleanJet_eta) < 2.5 && Take(Jet_btag{bAlgo}, CleanJet_jetIdx, -999.f) > {bWP}) == 0',
#     'samples': ALL
# }

# aliases['bReq'] = {
#     'expr': f'Sum(CleanJet_pt > 30. && abs(CleanJet_eta) < 2.5 && Take(Jet_btag{bAlgo}, CleanJet_jetIdx, -999.f) > {bWP}) >= 1',
#     'samples': ALL
# }


# aliases['LHEScaleWeight_vec'] = {'expr': 'ROOT::VecOps::RVec<double>(LHEScaleWeight)', 'samples': lhesamples}
# aliases['LHEPdfWeight_vec']   = {'expr': 'ROOT::VecOps::RVec<double>(LHEPdfWeight)',   'samples': lhesamples}

# # --------------------------- PU weights
# # aliases['Jet_PUIDSF'] = {
# #   'expr' : 'ROOT::VecOps::Product(Jet_PUIDSF_loose[Jet_jetId>=2])',
# #   'samples': mcALL
# # }
# #
# # aliases['Jet_PUIDSF_up'] = {
# #   'expr' : 'ROOT::VecOps::Product(Jet_PUIDSF_loose_up[Jet_jetId>=2])',
# #   'samples': mcALL
# # }
# #
# # aliases['Jet_PUIDSF_down'] = {
# #   'expr' : 'ROOT::VecOps::Product(Jet_PUIDSF_loose_down[Jet_jetId>=2])',
# #   'samples': mcALL
# # }


# # see:
# # https://github.com/latinos/LatinoAnalysis/blob/master/NanoGardener/python/data/formulasToAdd_MC_2017.py
# #


# # variations
# # data/MC scale factors

# # Use this for the usual SF
# # Each factor switches on the same pinned size, so the product is the
# # single-multiplicity weight of whichever region the event belongs to.
# aliases['SFweight'] = {
#     'expr': ' * '.join(['SFweightNl', 'LepWPCutN', 'LepWPSFN', 'btagSFbc', 'btagSFlight']),
#     'samples': mc
# }

# # lepton SF variations, switched on the multiplicity like the nominal above.
# # NB: the nuisances using these are currently commented out in nuisances.py.
# for _tag, _flav, _wp in [('Ele', 'ele', eleWP), ('Mu', 'mu', muWP)]:
#     for _var in ('Up', 'Down'):
#         aliases['SFweight' + _tag + _var] = {
#             'expr': ' + '.join(
#                 '(%s == %d) * LepSF%dl__%s_%s__%s' % (nlep, N, N, _flav, _wp, _var)
#                 for N in (2, 3, 4)),
#             'samples': mc
#         }



# #
# # if some variables are not defined but they are needed as inputs of the TMVA, define them!
# #


# # aliases['myVariableBDT'] = {
# #   'variables': ["pt1", "ptj1", "mll", "njet"],
# #   'function' : 'TMVA',
# #   'xmlfile'  : 'code/TMVAClassification_BDTG.weights.xml',
# #   'samples': ALL
# # }

# ===========================================================================
# Fake-rate measurement
#
# One region, with the requirements that depend on how many leptons the event
# has (see cuts.py). The (pT, eta) map is filled from every selected lepton in
# turn, with the loop in plotFake.py over the SelLep_* arrays: nothing here
# picks a probe index, because picking one biases the numerator against the
# denominator.
#
# Everything that might become a cut later is an alias, hence a branch in the
# snapshot, so mjj / detajj / njet / b-tag variations are a re-run of
# plotFake.py on the same ntuple rather than new jobs.
# ===========================================================================

# prompt gen-matching per selected lepton, for the subtraction. Per lepton and
# not per event: which lepton is prompt is exactly what the loop needs.
aliases['SelLep_promptgenmatched'] = {
    'expr': 'Take(ROOT::VecOps::RVec<int>(Lepton_promptgenmatched), nLepSel)',
    'samples': mc
}

# -------- the pair, when there are two
aliases['isSS'] = {
    'expr': 'nLepSel == 2 && SelLep_pdgId[0] * SelLep_pdgId[1] > 0',
    'samples': ALL
}
aliases['isEE'] = {
    'expr': 'nLepSel == 2 && abs(SelLep_pdgId[0]) == 11 && abs(SelLep_pdgId[1]) == 11',
    'samples': ALL
}
aliases['dR_ll'] = {
    'expr': ('nLepSel == 2'
             ' ? sqrt(pow(SelLep_eta[0] - SelLep_eta[1], 2)'
             '      + pow(ROOT::VecOps::DeltaPhi(SelLep_phi[0], SelLep_phi[1]), 2))'
             ' : -1.f'),
    'samples': ALL
}

# -------- b tagging at two working points
# Kept as branches, not folded into the region, so the choice of working point
# stays open downstream. The loose WP has the *lowest* discriminant threshold,
# so it tags the most jets and gives the strongest veto; medium is the weaker
# veto and therefore the larger sample. Dumping without either applied means
# both are still reachable.
for _wpname in ('loose', 'medium'):
    _thr = btagging_WPs[bAlgo][_wpname]
    aliases['nBJet_' + _wpname] = {
        'expr': (f'Sum(CleanJet_pt > 20. && abs(CleanJet_eta) < 2.5'
                 f'    && Take(Jet_btag{bAlgo}, CleanJet_jetIdx, -999.f) > {_thr})'),
        'samples': ALL
    }
    aliases['bVeto_' + _wpname] = {
        'expr': 'nBJet_%s == 0' % _wpname,
        'samples': ALL
    }

# -------- opposite sign, same flavour: the DY region for the prompt rate
aliases['isOS'] = {
    'expr': 'nLepSel == 2 && SelLep_pdgId[0] * SelLep_pdgId[1] < 0',
    'samples': ALL
}
aliases['isSF'] = {
    'expr': 'nLepSel == 2 && abs(SelLep_pdgId[0]) == abs(SelLep_pdgId[1])',
    'samples': ALL
}

# -------- mT of the leading lepton, used only by the 1-lepton branch, where
# W -> l nu is the prompt background that dominates.
aliases['mt_l0'] = {
    'expr': ('nLepSel > 0'
             ' ? sqrt(2.f * SelLep_pt[0] * PuppiMET_pt'
             '      * (1.f - cos(ROOT::VecOps::DeltaPhi(SelLep_phi[0], PuppiMET_phi))))'
             ' : -1.f'),
    'samples': ALL
}

# -------- away jets, away from every selected lepton
# CleanJet already drops jets overlapping a lepton, but at a smaller radius
# than the 0.7 that separates a recoil jet from the fake's own parent jet.
# Three thresholds as branches and *not* as a requirement in cuts.py: the
# region is inclusive, and requiring an away jet -- or moving its threshold --
# is a selection applied downstream on this tree.
#
# FIXED: this used sqrt(pow(deta,2) + pow(dphi,2)) on RVec arguments, where
# pow(x, 2) resolves to an integer-exponent overload that truncates the base.
# The dR it computed was sqrt(int(deta)^2 + int(dphi)^2), i.e. 0 whenever both
# |deta| < 1 and |dphi| < 1, so the "> 0.7" test rejected every jet inside
# roughly dR < 1.4 instead of inside 0.7. Measured on a synthetic frame with
# one lepton at the origin and three jets at dR = 0.50, 1.27 and 1.98:
# the counter returned 1 where the answer is 2. It compiled, it ran, and it
# undercounted away jets in every file produced so far. No pow() on a vector.
#
# The index is clamped rather than guarded. `nLepSel < 2 || <RVec>` does NOT
# short-circuit -- ROOT::VecOps::operator|| takes a scalar and an RVec and
# returns an RVec, so both sides are always evaluated, and SelLep_eta[1] is
# read even when there is one lepton. The guard still gives the right answer
# (true || x is true for every element), and RVec's small-buffer optimisation
# means the read does not fault, but it is a read past the end returning
# whatever the buffer last held. `[nLepSel > 1 ? 1 : 0]` costs nothing and
# removes it.
_dr_to = ('ROOT::VecOps::DeltaR('
          '  CleanJet_eta,'
          '  ROOT::VecOps::RVec<float>(CleanJet_eta.size(), SelLep_eta[%s]),'
          '  CleanJet_phi,'
          '  ROOT::VecOps::RVec<float>(CleanJet_phi.size(), SelLep_phi[%s]))')
for _thr in (20, 30, 40):
    aliases['nAwayJet%d' % _thr] = {
        'expr': (
            'Sum(CleanJet_pt > %d.f && abs(CleanJet_eta) < 5.0'
            '    && (nLepSel < 1 || %s > 0.7)'
            '    && (nLepSel < 2 || %s > 0.7))'
            % (_thr, _dr_to % ('0', '0'),
               _dr_to % ('nLepSel > 1 ? 1 : 0', 'nLepSel > 1 ? 1 : 0'))),
        'samples': ALL
    }


# ===========================================================================
# Extra variables, dumped and not cut on.
#
# Everything below exists so that the parameterisation of the rate can be
# revisited on the ntuple instead of on nanoAOD. The reason to want them is
# that f(pT, eta) is only the first approximation: the rate depends on how the
# fake was produced, and the variables that carry that information are the
# proximity and the hardness of the parent jet, the hadronic activity and the
# pileup. If f turns out to depend on one of them, it becomes a third binning
# dimension -- or the evidence that the measurement region and the application
# region have to be reweighted to agree in it.
# ===========================================================================

# -------- per-lepton jet proximity, the two strongest variables after pT
#
# A lepton faked by a jet keeps the remnant of its parent jet nearby, so dR to
# the closest jet and pT(lepton)/pT(jet) separate fakes from prompt leptons
# more sharply than anything else available here. Aligned with SelLep_*, one
# entry per selected lepton, -1 when the event has no jet above threshold.
for _thr in (20, 30):
    aliases['SelLep_drClosestJet%d' % _thr] = {
        'function' : 'closestJetDR_%d' % _thr,
        'variables': ['SelLep_eta', 'SelLep_phi',
                      'CleanJet_pt', 'CleanJet_eta', 'CleanJet_phi'],
        'external' : '../../utils/macros/fake_rate_vars.cc',
        'linesToGlobal': ['closestJetDR closestJetDR_%d(%d.f);' % (_thr, _thr)],
        'samples'  : ALL,
    }
    aliases['SelLep_ptClosestJet%d' % _thr] = {
        'function' : 'closestJetPt_%d' % _thr,
        'variables': ['SelLep_eta', 'SelLep_phi',
                      'CleanJet_pt', 'CleanJet_eta', 'CleanJet_phi'],
        'external' : '../../utils/macros/fake_rate_vars.cc',
        'linesToGlobal': ['closestJetPt closestJetPt_%d(%d.f);' % (_thr, _thr)],
        'samples'  : ALL,
    }
    # pT(lepton) / pT(closest jet). Division by the -1 sentinel is harmless --
    # 'where' discards that branch -- but it must not be a 0.
    aliases['SelLep_ptRatioJet%d' % _thr] = {
        'expr': ('ROOT::VecOps::Where(SelLep_ptClosestJet{t} > 0.f,'
                 ' SelLep_pt / SelLep_ptClosestJet{t}, -1.f)').format(t=_thr),
        'samples': ALL
    }

# -------- per-lepton MET geometry
# mT per lepton, not only for the leading one: in the 2-lepton branch it is a
# diagnostic rather than a cut (see cuts.py), and it is cheap to keep.
aliases['SelLep_mt'] = {
    'expr': ('sqrt(2.f * SelLep_pt * PuppiMET_pt'
             ' * (1.f - cos(ROOT::VecOps::DeltaPhi(SelLep_phi, (float)PuppiMET_phi))))'),
    'samples': ALL
}
aliases['SelLep_dphiMET'] = {
    'expr': 'abs(ROOT::VecOps::DeltaPhi(SelLep_phi, (float)PuppiMET_phi))',
    'samples': ALL
}

# -------- the pair, beyond mll and dR_ll
aliases['ptll'] = {
    'expr': ('nLepSel == 2'
             ' ? (float)sqrt(pow(SelLep_pt[0] * cos(SelLep_phi[0])'
             '                 + SelLep_pt[1] * cos(SelLep_phi[1]), 2)'
             '             + pow(SelLep_pt[0] * sin(SelLep_phi[0])'
             '                 + SelLep_pt[1] * sin(SelLep_phi[1]), 2))'
             ' : -1.f'),
    'samples': ALL
}
# -------- mT of the dilepton+MET system, the "Higgs" transverse mass.
# Needed only by the same-sign closure test of AN-24-128 section 6.5, which
# asks for mT^H > 60 GeV. Defined here rather than recomputed downstream
# because it needs PuppiMET_phi, and PuppiMET_phi is not dumped: this one
# float replaces it.
#
#   mT^H = sqrt(2 * ptll * MET * (1 - cos(dphi(ll, MET))))
#
aliases['mth'] = {
    'expr': ('nLepSel == 2'
             ' ? (float)sqrt(2.f * ptll * PuppiMET_pt'
             '      * (1.f - cos(ROOT::VecOps::DeltaPhi('
             '            (float)atan2(SelLep_pt[0] * sin(SelLep_phi[0])'
             '                       + SelLep_pt[1] * sin(SelLep_phi[1]),'
             '                         SelLep_pt[0] * cos(SelLep_phi[0])'
             '                       + SelLep_pt[1] * cos(SelLep_phi[1])),'
             '            (float)PuppiMET_phi))))'
             ' : -1.f'),
    'samples': ALL
}

# -------- dR between each selected lepton and the HIGHEST-pT jet.
# AN-24-128 line 481 and 498: the fakeable object must be separated from the
# leading jet of the event by dR > 1.0 -- the leading jet specifically, not
# "every jet", and 1.0, not the 0.7 the nAwayJet* counters use. So neither
# nAwayJet* nor CleanJet_* with a 0.7 radius reproduces it, and this is the
# branch their denominator is actually cut on.
#
# NB: written with ROOT::VecOps::DeltaR and *not* with
# sqrt(pow(deta,2) + pow(dphi,2)). On an RVec, pow(x, 2) resolves to an
# integer-exponent overload that truncates the base: measured on a synthetic
# frame, a lepton at (eta 0.5, phi 0.3) against a jet at (eta 2.0, phi -1.0)
# came out 1.41421 instead of 1.98494, because -1.5 and 1.3 were squared as
# -1 and 1. It compiles, it runs, and it is silently wrong -- so no pow() on a
# vector anywhere in this file.
aliases['SelLep_drJet0'] = {
    'expr': ('nCleanJet > 0'
             ' ? ROOT::VecOps::DeltaR('
             '     SelLep_eta,'
             '     ROOT::VecOps::RVec<float>(SelLep_eta.size(), CleanJet_eta[0]),'
             '     SelLep_phi,'
             '     ROOT::VecOps::RVec<float>(SelLep_phi.size(), CleanJet_phi[0]))'
             ' : ROOT::VecOps::RVec<float>(SelLep_pt.size(), -1.f)'),
    'samples': ALL
}

aliases['dphi_ll'] = {
    'expr': ('nLepSel == 2'
             ' ? (float)abs(ROOT::VecOps::DeltaPhi(SelLep_phi[0], SelLep_phi[1]))'
             ' : -1.f'),
    'samples': ALL
}
aliases['deta_ll'] = {
    'expr': 'nLepSel == 2 ? (float)abs(SelLep_eta[0] - SelLep_eta[1]) : -1.f',
    'samples': ALL
}

# -------- hadronic activity
# njet* counts every jet above threshold, with no dR requirement, so the pair
# (njet20, nAwayJet20) says how much of the activity is the leptons' own.
for _thr in (20, 30, 40):
    aliases['njet%d' % _thr] = {
        'expr': 'Sum(CleanJet_pt > %d.f && abs(CleanJet_eta) < 5.0)' % _thr,
        'samples': ALL
    }

aliases['ht_jets'] = {
    'expr': 'Sum(CleanJet_pt[CleanJet_pt > 20.f && abs(CleanJet_eta) < 5.0])',
    'samples': ALL
}

# Leading-jet kinematics as scalars, so no array indexing is needed downstream.
for _i in (0, 1):
    aliases['jet%d_pt' % _i] = {
        'expr': 'CleanJet_pt.size() > %d ? CleanJet_pt[%d] : -1.f' % (_i, _i),
        'samples': ALL
    }
    aliases['jet%d_eta' % _i] = {
        'expr': 'CleanJet_eta.size() > %d ? CleanJet_eta[%d] : -99.f' % (_i, _i),
        'samples': ALL
    }

aliases['dphijj'] = {
    'expr': ('CleanJet_pt.size() > 1'
             ' ? (float)abs(ROOT::VecOps::DeltaPhi(CleanJet_phi[0], CleanJet_phi[1]))'
             ' : -1.f'),
    'samples': ALL
}

# Smallest dphi between the MET and any jet: the handle on MET that is really
# jet mismeasurement rather than a neutrino, which is what populates the
# low-MET tail of the QCD region.
aliases['mindphi_MET_jet'] = {
    'expr': ('Sum(CleanJet_pt > 20.f) > 0'
             ' ? (float)ROOT::VecOps::Min('
             '     abs(ROOT::VecOps::DeltaPhi('
             '       CleanJet_phi[CleanJet_pt > 20.f], (float)PuppiMET_phi)))'
             ' : -1.f'),
    'samples': ALL
}
