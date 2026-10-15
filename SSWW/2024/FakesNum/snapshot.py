# snapshot.py
#
# Flat tree for the fake-rate measurement. The ratio itself is built downstream
# (plotFake.py) from these branches, so the tight/loose split, the pT-eta
# binning, the away-jet threshold and the b requirement are all still free
# after the jobs have run. That is the point of dumping rather than
# histogramming: re-binning the fake rate must not mean re-reading nanoAOD.

# -------------------------------------------------------------------
# Region the snapshot is taken from: the inclusive denominator, superset of
# every measurement region in cuts.py (see the comment there).
# -------------------------------------------------------------------
cut_to_dump = 'dump'

# -------------------------------------------------------------------
# Branches
# -------------------------------------------------------------------

# Event weight. No lepton scale factor on purpose: it is a tight-lepton
# efficiency correction, it does not describe a loose lepton, and it largely
# cancels in the ratio. PromptGenLepMatch1l is what the prompt subtraction
# keys on, and it is 1l here because the region has one lepton.
_weights = [
    'XSWeight',
    'METFilter_Common',
    'METFilter_DATA',
]

# Event-level quantities of the region. Kept as branches and not as cuts: the
# tight/loose split is the per-lepton flag in the SelLep_* arrays below, and
# everything that could become a selection is here so that changing it is a
# re-run of plotFake.py rather than new jobs.
_region = [
    'isSS',
    'isEE',
    'isOS',
    'isSF',
    'mll',
    'ptll',
    'dR_ll',
    'dphi_ll',
    'deta_ll',
    'mt_l0',
    'mjj',
    'detajj',
    'dphijj',
    'zstar_max',
]

# The selected-lepton collection. Everything per lepton is an array aligned
# with SelLep_pt, so the probe loop in plotFake.py indexes them together.
#
# drClosestJet / ptClosestJet / ptRatioJet are the variables to look at first if
# f(pT, eta) does not close: a lepton faked by a jet sits close to the remnant
# of its parent jet and carries a small fraction of its pT, while a prompt
# lepton does not. If the rate depends on them, either they become a third
# binning dimension or the measurement and application regions have to be
# reweighted to agree in them.
_leptons = [
    'nLepSel',
    'SelLep_pt',
    'SelLep_eta',
    'SelLep_phi',
    'SelLep_pdgId',
    'SelLep_isTightElectron',
    'SelLep_isTightMuon',
    'SelLep_muonIdx',
    'SelLep_promptgenmatched',
    'SelLep_mt',
    'SelLep_dphiMET',
    'SelLep_drClosestJet20',
    'SelLep_drClosestJet30',
    'SelLep_ptClosestJet20',
    'SelLep_ptClosestJet30',
    'SelLep_ptRatioJet20',
    'SelLep_ptRatioJet30',
    # the full collection too, so the 10 GeV threshold itself can be moved
    'Lepton_pt',
    'Lepton_eta',
    'Lepton_phi',
    'Lepton_pdgId',
]

# Every tight WP, not only the analysis one: the fake rate has to be remeasured
# for each WP it will be applied at, and the WP is the one thing that cannot be
# changed downstream unless the flag is in the tree.
_tight_ele = [
    'Lepton_isTightElectron_mvaWinter22V2Iso_WP90',
    'Lepton_isTightElectron_mvaWinter22V2Iso_WP90_tthMVA_HWW',
    'Lepton_isTightElectron_mvaWinter22V2Iso_WP90_tthMVA_Run3',
    'Lepton_isTightElectron_cutBased_MediumID_tthMVA_HWW',
    'Lepton_isTightElectron_cutBased_MediumID_tthMVA_Run3',
    'Lepton_isTightElectron_wp90iso',
    'Lepton_isTightElectron_testrecipes',
]

_tight_mu = [
    'Lepton_isTightMuon_cut_Tight_HWW',
    'Lepton_isTightMuon_cut_TightID_pfIsoTight_HWW_tthmva_67',
    'Lepton_isTightMuon_cut_TightID_pfIsoLoose_HWW_tthmva_HWW',
    'Lepton_isTightMuon_cut_TightID_pfIsoLoose_HWW_tthmva_67',
    'Lepton_isTightMuon_cut_TightID_POG',
    'Lepton_isTightMuon_cut_TightID_pfIsoLoose_HWW_PNet',
]

# Analysis triggers. NB: these are the wrong triggers for a 20 GeV probe --
# see the note at the bottom of this file.
_triggers = [
    'HLT_IsoMu24',
    'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8',
    'HLT_Ele30_WPTight_Gsf',
    'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL',
    'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL',
    'HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ',
    'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ',
]

# MET and the jet counting. nAwayJet* requires dR > 0.7 from every selected
# lepton, njet* does not, so the two together say how much of the hadronic
# activity is the leptons' own. mindphi_MET_jet is the handle on MET that is
# really jet mismeasurement rather than a neutrino.
_selection = [
    'PuppiMET_pt',
    'PuppiMET_phi',
    'mindphi_MET_jet',
    'nAwayJet20',
    'nAwayJet30',
    'nAwayJet40',
    'njet20',
    'njet30',
    'njet40',
    'ht_jets',
    'jet0_pt',
    'jet0_eta',
    'jet1_pt',
    'jet1_eta',
    'bVeto_loose',
    'bVeto_medium',
    'nBJet_loose',
    'nBJet_medium',
]

# Jets: the away-jet kinematics, for the recoil-dependence checks and as the
# inputs of any multivariate parameterisation later on.
_jets = [
    'nCleanJet',
    'CleanJet_pt',
    'CleanJet_eta',
    'CleanJet_phi',
    'CleanJet_mass',
    'CleanJet_jetIdx',
    'Jet_btagUParTAK4B',
]

# Pileup and event id.
_event = [
    'PV_npvsGood',
    'PV_npvs',
    'run',
    'luminosityBlock',
    'event',
]

# Gen matching, per lepton, for the closure test and for the prompt
# subtraction. MC only -- these do not exist in DATA, same as the two Lepton_*
# branches already here, so the per-sample branch set is not uniform and
# haddnano zero-fills the difference.
#
# Jet_hadronFlavour separates the two kinds of fake: a lepton from a b or c
# decay is nonprompt but it is *not* a light-jet fake, and the two have
# different rates and different relative weights in the measurement region
# (which has no b veto) and in the application region (which does). Without it
# a disagreement between the two shows up only as a failed closure.
_gen = [
    'Lepton_genmatched',
    'Lepton_promptgenmatched',
    'Jet_hadronFlavour',
]

variables_to_dump = (
    _weights
    + _region
    + _leptons
    + _tight_ele
    + _tight_mu
    + _triggers
    + _selection
    + _jets
    + _event
    + _gen
)

# -------------------------------------------------------------------
# Open point: the trigger.
#
# The paths above are the analysis ones (IsoMu24, Ele30_WPTight, and the
# dilepton legs). None of them can measure a fake rate down to 20 GeV:
#   - the single-lepton thresholds are 24 and 30 GeV, above the probe range;
#   - every one of them requires isolation on the leg it fires on, which biases
#     the loose denominator towards tight and pulls the measured ratio up;
#   - the dilepton paths need a second lepton, which the region vetoes.
#
# What this measurement wants are the dedicated prescaled fake-rate paths,
# which trigger on a jet or on a loose-ID lepton and leave the probe unbiased,
# e.g. HLT_Mu8/Mu17_TrkIsoVVL and HLT_Ele8/Ele17/Ele23_CaloIdM_TrackIdM_PFJet30.
# Whether they are kept in this nanoAOD has to be checked on a file before
# anything is submitted.
# -------------------------------------------------------------------
