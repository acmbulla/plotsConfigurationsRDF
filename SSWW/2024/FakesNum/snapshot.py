# snapshot.py
#
# Flat tree for the fake-rate measurement. The ratio itself is built downstream
# (measureFakeRate.py / plotFake.py) from these branches, so the tight/loose
# split, the pT-eta binning, the away-jet threshold and the b requirement are
# all still free after the jobs have run. That is the point of dumping rather
# than histogramming: re-binning the fake rate must not mean re-reading
# nanoAOD.
#
# The branch set is deliberately narrow. Everything here is either read by a
# consumer or is a handle that cannot be rebuilt from what is read; everything
# that was merely convenient has been dropped, because it is not free -- see
# "What was removed, and why" at the bottom for the measured cost of each
# block. A quantity that is a function of the jets, the leptons or the MET is
# not kept: CleanJet_pt/eta and the lepton arrays are here, so it can be
# recomputed in the analysis script in microseconds, where the file pays for it
# on every event of every sample.

# -------------------------------------------------------------------
# Region the snapshot is taken from: the inclusive denominator, superset of
# every measurement region in cuts.py (see the comment there).
# -------------------------------------------------------------------
cut_to_dump = 'dump'

# folder_where_to_save_trees = '/eos/user/a/abulla/latinoRDF/plotsConfigurationsRDF/SSWW/2024/rootFile/snapshot/Fakes/'
# NB the trailing directory. The branch set changed (84 branches, 24 triggers,
# nAwayJet* recomputed after the pow()-on-RVec fix), and this path carries no
# tag, so writing into the old 'Fakes/' would leave the two productions in one
# directory. haddnano zero-fills a branch a file does not have, so the merge
# would not fail -- it would quietly mix the old, undercounted nAwayJet* with
# the new ones. Hence a new directory per branch set.
folder_where_to_save_trees = '/eos/cms/store/group/phys_smp/ec/Latinos/HWWNano/Summer24_150x_nAODv15_Full2024v15/snapshot/Fakes_an128/'

# -------------------------------------------------------------------
# Branches
# -------------------------------------------------------------------

# Event weight. No lepton scale factor on purpose: it is a tight-lepton
# efficiency correction, it does not describe a loose lepton, and it largely
# cancels in the ratio. Prompt subtraction uses SelLep_promptgenmatched
# separately for each selected lepton.
_weights = [
    'XSWeight',
    'METFilter_Common',
    'METFilter_DATA',
]

# Event-level quantities of the region. Kept as branches and not as cuts: the
# tight/loose split is the per-lepton flag in the SelLep_* arrays below, and
# everything that could become a selection is here so that changing it is a
# re-run of the analysis script rather than new jobs.
#
# The four pair flags, mll and mt_l0 are what the region definitions in
# measureFakeRate.py are written in. mjj and detajj are not used by any
# consumer today and are kept anyway, because cuts.py says so: the
# orthogonality of the tight-tight same-sign part of FR to WW_SR and to the
# VRs is an open decision there ('mjj < 200'), and it "does have to be decided
# before the map is used". A branch that a pending decision needs is not spare.
#
# ptll and mth are the two cuts of the same-sign closure test of AN-24-128
# section 6.5 (pTll > 30, mT^H > 60) that are not functions of anything else
# here: mth needs PuppiMET_phi, which is not dumped, so the one float stands in
# for the whole angle. mT^W2 of that list is SelLep_mt[1].
#
# The rest of the dilepton kinematics -- dR_ll, dphi_ll, deta_ll, dphijj,
# zstar_max -- is arithmetic on the leptons and on CleanJet_*, both dumped, so
# it is recomputed downstream instead of stored.
_region = [
    'isSS',
    'isEE',
    'isOS',
    'isSF',
    'mll',
    'mt_l0',
    'mjj',
    'detajj',
    'ptll',
    'mth',
]

# The selected-lepton collection. Everything per lepton is an array aligned
# with SelLep_pt, so the probe loop indexes them together.
#
# SelLep_drJet0 is the legacy away-jet requirement, and it is not the one the
# nAwayJet* counters implement. AN-24-128 lines 481 and 498 ask for dR > 1.0
# from the *highest-pT jet of the event*; nAwayJet* asks for dR > 0.7 from
# *every* selected lepton. Different radius, different jet, different quantifier
# -- so their denominator cannot be rebuilt from the counters, and this array
# is what it is cut on. SelLep_phi stays anyway: it is what makes any other
# radius, any other jet and the closest-jet variables recomputable downstream.
#
# SelLep_mt is the per-probe transverse mass, and AN-24-128 Eq. 17 cuts on it
# at 20 GeV (mT^W1). mt_l0 is the leading lepton only; in the legacy region
# there is exactly one lepton so the two coincide, but the 2-lepton branch and
# the closure test (mT^W2 > 30) need the array.
#
# Lepton_pt / Lepton_pdgId are the *full* collection, before the nLepSel cut:
# they are what says whether an event holds a harder lepton that lepSel
# rejected, which is the object a dilepton path fired on (fr_study_v3/
# trigger_audit.py). That question cannot be asked from SelLep_* alone, so the
# two arrays stay. Lepton_eta / Lepton_phi do not: nothing asks where that
# object was, only that it existed and how hard it was.
_leptons = [
    'nLepSel',
    'SelLep_pt',
    'SelLep_eta',
    'SelLep_phi',
    'SelLep_pdgId',
    'SelLep_mt',
    'SelLep_drJet0',
    'SelLep_promptgenmatched',
    'Lepton_pt',
    'Lepton_pdgId',
]

# Every tight WP, not only the analysis one: the fake rate has to be remeasured
# for each WP it will be applied at, and the WP is the one thing that cannot be
# changed downstream unless the flag is in the tree. These are bool arrays and
# compress to ~0.6 B/event each, so carrying all thirteen costs less than one
# float branch.
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

# -------------------------------------------------------------------
# Triggers.
#
# Three groups, and the distinction between them is the whole point of keeping
# all of them in one tree: the analysis OR is what the rate will be applied
# under, the prescaled paths are what the rate should be measured under, and
# having both per event is what lets one be validated against the other on the
# same events rather than across two productions.
#
# Every path below was checked to exist in the nanoAODv15 menu
# (716 HLT branches survive into nanoLatino). Even so, nothing here is load
# bearing if a path is absent: mkSnapshot.py:386-393 intersects
# variables_to_dump with GetColumnNames() and silently drops what the file does
# not have, haddnano zero-fills the difference, and measureFakeRate.py keeps
# only the trigger branches it finds (`thave`). A path missing in one era
# therefore costs that era's events for that path, not the job.
#
# Cost: a bool branch is 0.02-0.11 B/event compressed. The 24 paths below
# together are under 1 B/event -- about a seventh of CleanJet_pt alone.
#
# Nothing here is *required*. cuts.py asks for no trigger at any level: the
# supercut is a lepton multiplicity and an eta acceptance, cuts['FR'] and
# cuts['DY'] are kinematic, and cuts['dump'] is their union. So the tree holds
# every event of the skim regardless of what fired, the trigger decision is a
# column, and every trigger requirement -- the analysis OR, one prescaled path,
# the exclusive-OR over a prescaled family, the primary-dataset de-overlap --
# is applied offline where it can be changed without resubmitting. That is
# deliberate and it is what makes one tree serve the comparison: the same
# events, selected two ways, rather than two productions.
#
# It also means the trigger list below can grow without invalidating anything
# already produced: a path added here appears in the next production and is
# simply absent from the older files, which the consumers tolerate (see above).
# -------------------------------------------------------------------

# The analysis OR, as mkShapesRDF actually defines it. This is the authority,
# not TrigMaker_cfg.py: SFweight2l/3l/4l
# (formulasToAdd_MC_RunIII.py:38-45) OR *eight* paths, while
# TrigMaker_cfg.py:1337-1341 lists seven. The eighth is
# HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL, the non-DZ partner of the
# Mu12/Ele23 leg, and it was the one missing from this snapshot. An event that
# fires only that path is in the analysis trigger OR and was invisible here, so
# both the de-overlap in PD_GROUPS and the 2-lepton trigger requirement were
# reconstructed from an incomplete set.
_triggers_analysis = [
    'HLT_IsoMu24',
    'HLT_Ele30_WPTight_Gsf',
    'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8',
    'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL',
    'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL',
    'HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL',     # <-- was missing
    'HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ',
    'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ',
]

# The prescaled fake-rate paths of AN-24-128 Table 15 -- the ones the legacy
# measurement is actually made with, and the reason this snapshot exists.
#
# Why the analysis paths cannot do it (AN-24-128 line 482-484: "To select
# single lepton events with such low pT thresholds, prescaled trigger paths are
# used"):
#   - the single-lepton thresholds are 24 and 30 GeV, above the probe range,
#     which starts at 10 GeV for muons and 13 for electrons;
#   - each one requires isolation, or the full tight HLT ID, on the leg it
#     fired on, which removes loose-not-tight leptons from the denominator and
#     pulls the measured ratio up;
#   - the dilepton paths need a second lepton, which the legacy region vetoes
#     ("exactly one lepton"), so there they can only have fired on something
#     that is not the probe.
#
# THE FOUR PATHS OF TABLE 15, with the 2024 effective luminosities. The split
# point is on the *offline probe pT*, and the two paths of a flavour are used
# exclusively, not OR'd:
#
#   flavour  probe pT        path                                  L_eff [pb-1]
#   -------------------------------------------------------------------------
#   ele      <= 25 GeV   HLT_Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30      70.526
#   ele       > 25 GeV   HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30      70.526
#   mu       <= 20 GeV   HLT_Mu8_TrkIsoVVL                             12.424
#   mu        > 20 GeV   HLT_Mu17_TrkIsoVVL                           336.399
#
# Two things about that table, both of which have to be settled with them:
#
#   1. The two electron paths are quoted at the *same* effective luminosity,
#      70.526 pb-1, in every era. A prescaled Ele12 and a prescaled Ele23
#      essentially never share a prescale, and the muon pair in the same table
#      differs by a factor 27. Either the two electron paths genuinely sit in
#      one prescale column in 2024, or the entry is a copy. It matters
#      directly: it is the denominator of the EWK subtraction.
#   2. L_eff is in *picobarns*, against the analysis' 110.11 fb-1. See the
#      note on the MC normalisation at the bottom of this file -- it is not a
#      detail, it is a factor of 300 to 9000 and it is pT dependent.
#
# ADDITIONALLY, the CaloIdM_TrackIdM family. This is *not* theirs, it is a
# cross-check of ours, and the distinction matters: Table 15 uses the
# CaloIdL_TrackIdL_**IsoVL** paths, which require isolation at HLT on the
# object that is about to become the loose denominator. The CaloIdM_TrackIdM
# paths are the same idea without the isolation requirement -- loose
# calorimetric and tracker ID, no isolation, event taken because of the 30 GeV
# jet -- so the difference between the two families measures how much the HLT
# isolation moves the denominator. That is the one bias the legacy measurement
# carries and cannot quantify from inside its own trigger choice. Keeping both
# costs ~0.3 B/event in total.
_triggers_fr_ele = [
    # AN-24-128 Table 15
    'HLT_Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30',
    'HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30',
    # our cross-check: same thing without the HLT isolation
    'HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30',
    'HLT_Ele8_CaloIdM_TrackIdM_PFJet30',
    'HLT_Ele17_CaloIdM_TrackIdM_PFJet30',
    'HLT_Ele23_CaloIdM_TrackIdM_PFJet30',
]

# Same on the muon side. Mu8/Mu17_TrkIsoVVL are Table 15; the bare
# HLT_Mu8/17/20/27/50 are ID only, no isolation and no jet, so a muon probe is
# unbiased in exactly the variable the tight WP cuts on (PFrelIso04 < 0.15 for
# the numerator against < 0.4 for the denominator, AN-24-128 lines 475-476).
# The pair therefore brackets the isolation bias the way the two electron
# families do.
_triggers_fr_mu = [
    # AN-24-128 Table 15
    'HLT_Mu8_TrkIsoVVL',
    'HLT_Mu17_TrkIsoVVL',
    # our cross-check: no HLT isolation
    'HLT_Mu8',
    'HLT_Mu17',
    'HLT_Mu20',
    'HLT_Mu27',
    'HLT_Mu50',
    'HLT_Mu19_TrkIsoVVL',
    'HLT_Mu12eta2p3',
    'HLT_Mu12eta2p3_PFJet40',
]

_triggers = _triggers_analysis + _triggers_fr_ele + _triggers_fr_mu

# MET, the jet counting and the b categories.
#
# The counters are pre-baked at three thresholds and are kept even though
# CleanJet_pt makes them recomputable, because they are the axes of the
# additional studies: njet* does not require separation from the leptons,
# nAwayJet* requires dR > 0.7 from every selected lepton, so the two together
# say how much of the hadronic activity is the leptons' own -- which is the
# first thing to look at when a fake rate measured in one jet environment is
# applied in another. The threshold scan between 20, 30 and 40 is free this
# way; a threshold that is none of the three is rebuilt from CleanJet_* and
# SelLep_phi, which is why both are still in the file.
#
# bVeto_{loose,medium} and nBJet_{loose,medium} define the three b categories
# of cuts.py (bveto / btag / incl) at the analysis thresholds. measureFakeRate
# recomputes them from CleanJet_pt and the discriminant today; keeping the
# nanoAOD-side versions is what lets the two be compared rather than trusted.
#
# jet0_pt / jet0_eta: the leading jet, as the legacy parameterisation uses it.
# jet1_* is not here -- nothing in a fake-rate measurement is a function of the
# second jet, and CleanJet_* has it if that changes.
#
# PuppiMET_phi is dropped: mindphi_MET_jet and SelLep_mt, the two things it was
# there to build, are stored directly and are cheaper than the angle.
_selection = [
    'PuppiMET_pt',
    'mindphi_MET_jet',
    'nAwayJet20',
    'nAwayJet30',
    'nAwayJet40',
    'njet20',
    'njet30',
    'njet40',
    'jet0_pt',
    'jet0_eta',
    'bVeto_loose',
    'bVeto_medium',
    'nBJet_loose',
    'nBJet_medium',
]

# Jets: pT, eta, phi and the b-tag discriminant. phi is the expensive one
# (4.70 B/event) and it is here for one reason: the away-jet dR. Without it the
# jet environment can only be asked about at the three pre-baked thresholds of
# _selection, and the legacy away-jet threshold is not one of them.
# CleanJet_mass stays out -- no fake-rate question is a function of it.
#
# Jet_btagUParTAK4B is the full Jet collection, indexed through
# CleanJet_jetIdx. It is the single most expensive branch in the file
# (7.9 B/event). Defining CleanJet_btag = Take(Jet_btagUParTAK4B,
# CleanJet_jetIdx) in aliases.py and dumping that instead would halve it and
# also retire CleanJet_jetIdx, at the price of an edit in process_file(); not
# done here because it changes the reader, and the reader is what the
# measurement is being validated against.
_jets = [
    'nCleanJet',
    'CleanJet_pt',
    'CleanJet_eta',
    'CleanJet_phi',
    'CleanJet_jetIdx',
    'Jet_btagUParTAK4B',
]

# Pileup and run id. PV_npvsGood is the pileup handle; run and luminosityBlock
# are 0.02 and 0.04 B/event and are the only way to ask a question about one
# era, one fill or one golden-JSON range after the fact.
_event = [
    'PV_npvsGood',
    'run',
    'luminosityBlock',
]

# Gen matching. The per-lepton prompt flag lives in _leptons, where the probe
# loop reads it; what is left here is the one piece of gen information that is
# not per lepton.
#
# Jet_hadronFlavour separates the two kinds of fake: a lepton from a b or c
# decay is nonprompt but it is *not* a light-jet fake, and the two have
# different rates and different relative weights in the measurement region
# (which has no b veto) and in the application region (which does). Without it
# a disagreement between the two shows up only as a failed closure.
#
# MC only -- it does not exist in DATA, same as SelLep_promptgenmatched, so the
# per-sample branch set is not uniform and haddnano zero-fills the difference.
_gen = [
    'Jet_hadronFlavour',
]

# -------------------------------------------------------------------
# The 85th branch, which is not in the list below and is not ours to choose.
#
# mkSnapshot.py:249-251 prepends 'my_sample_weight' to variables_to_dump
# unconditionally, and analysisFactory.py:583 defines it as
# samples[...]['weight'] times the per-subname entry of samples[...]['weights']
# (mkSnapshot.py:549-550). For DATA in samples.py that is
#
#     my_sample_weight = (METFilter_DATA) * (DataTrig[pd])
#
# i.e. METFilter_DATA times the analysis trigger OR *and* the primary-dataset
# de-overlap, as a 0/1 multiplier.
#
# IT IS NOT A FILTER -- every event of the skim is in the tree, which is what
# makes the prescaled measurement possible at all. But it is a trap: an event
# taken by a prescaled Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30 that fires no
# analysis path has my_sample_weight == 0, so weighting by the branch named
# "the sample weight" -- the obvious thing to do -- silently zeroes most of
# the AN-24-128 measurement. measureFakeRate.py:525 reads METFilter_DATA
# directly and is therefore correct today; nothing enforces that it stays so.
#
# Do NOT drop samples['DATA']['weights'] to defuse it. DataTrig[pd] is the
# only path by which the primary dataset's identity enters the tree: samples.py
# knows which PD a file came from, the tree does not. Keeping it leaves the
# de-overlap recoverable per event, since METFilter_DATA is dumped as well:
#
#     DataTrig[pd] = my_sample_weight / METFilter_DATA     (METFilter_DATA != 0)
#
# So: our measurement may use it, the legacy one must ignore it. And the legacy
# one needs no de-overlap anyway -- the Table 15 paths are flavour-specific and
# each lives in a single PD (Ele*_PFJet30 in EGamma, Mu*_TrkIsoVVL in Muon),
# so there is no cross-PD double counting to undo. Worth confirming on the
# produced tree: a path firing in two PDs would show up immediately.
# -------------------------------------------------------------------

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
# What was removed, and why.
#
# Measured on nanoLatino_DYto2E-2Jets_MLL-50__part1891.root, 67502 entries,
# compressed bytes per event per branch. A two-lepton MC file, so the array
# branches are if anything cheaper here than in the one-lepton region.
#
# Over the branch set as a whole, counting only the branches that exist in that
# file (the latinoRDF-derived aliases are built later in the chain and cannot
# be weighed there):
#
#     before   91 branches, 49 of them weighable,   79.6 B/event
#     after    81 branches, 56 of them weighable,   54.1 B/event
#                                                   -32%
#
# That figure is a lower bound on the gain, not the gain: 17 of the 27 dropped
# branches are derived aliases absent from the test file, so none of their cost
# is in the 79.6, while +1 B/event of new triggers *is* in the 54.1.
#
# What went, and what it cost:
#
#   CleanJet_mass              6.86   no fake-rate question is a function of it
#   Lepton_eta, Lepton_phi     8.83   the rejected-lepton audit needs pt and
#                                     pdgId, not where the object was
#   PuppiMET_phi               3.70   mindphi_MET_jet and SelLep_mt, the two
#                                     things it built, are stored directly
#   ptll 2.56, dphijj 1.67     4.23   arithmetic on kept branches
#   event 1.17, PV_npvs 0.67   1.84   bookkeeping; PD de-overlap is by trigger
#   Lepton_{,prompt}genmatched 1.09   SelLep_promptgenmatched covers the probes
#
#   not weighable here: dR_ll, dphi_ll, deta_ll, zstar_max, ht_jets,
#   jet1_{pt,eta}, SelLep_isTight{Electron,Muon}, SelLep_muonIdx,
#   SelLep_dphiMET, SelLep_{dr,pt}ClosestJet{20,30},
#   SelLep_ptRatioJet{20,30}  -- seventeen branches, twelve of them float
#   arrays, which is where most of the real saving is.
#
# For scale, in the same file the three most expensive branches that *stay* are
# Jet_btagUParTAK4B 7.90, CleanJet_pt 6.81 and Lepton_pt 6.28, and all 24
# trigger bools together are under 1.
#
# Two rules decided it, and neither of them is "we do not use it today":
#
#   1. A function of what is kept is not kept -- but only once the inputs of
#      that function are all here. That is the condition the first pass got
#      wrong: the dilepton angles and the six closest-jet variables are
#      arithmetic on SelLep_pt/eta/phi, CleanJet_pt/eta/phi and PuppiMET_pt,
#      and dropping SelLep_phi and CleanJet_phi alongside them made them
#      unrecoverable rather than recomputable. Both phi arrays are back, so
#      the away-jet count at any threshold, the dR to the closest jet and the
#      pT ratio to it are all one line downstream. The closest-jet variables
#      are the first thing to look at if f(pT, eta) does not close, so this is
#      not a hypothetical.
#   2. A duplicate of a kept branch is not kept. SelLep_isTightElectron /
#      SelLep_isTightMuon are the analysis WP alone, and all thirteen per-WP
#      arrays are dumped. Lepton_promptgenmatched over the whole collection is
#      SelLep_promptgenmatched for the entries anything reads.
#   3. A branch whose only use is bookkeeping is not kept. `event` is 1.2
#      B/event of incompressible 64-bit id; cross-PD de-duplication is done by
#      trigger in PD_GROUPS, not by event number.
#
# Costs, stated plainly, and they are now the only ones:
#
#   - the 10 GeV lepSel floor cannot be moved *down* by promoting rejected
#     leptons to probes: only Lepton_pt and Lepton_pdgId survive of the full
#     collection, enough to count and threshold them, not to use them;
#   - no jet-mass or substructure question (CleanJet_mass);
#   - no MET direction beyond mindphi_MET_jet and SelLep_mt (PuppiMET_phi);
#   - no per-event cross-PD de-duplication by id (`event`).
#
# Everything the legacy measurement is parameterised in -- probe pT and eta,
# MET, the probe's mT, the away-jet count at its own threshold, the jet
# multiplicity, the b category -- is in the file, at the thresholds the
# analysis uses and as the raw collections needed to rebuild any other.
# -------------------------------------------------------------------

# ===================================================================
# Replicating AN-24-128 section 6.2 with this tree: what still differs.
#
# Every branch the legacy selection needs is now here. What is not here is the
# selection itself -- it lives in cuts.py and measureFakeRate.py, and on five
# points those do something else. Listed so the comparison is a comparison and
# not a coincidence.
#
# 1. THE MC NORMALISATION, and this one is not a cut.
#
#    AN-24-128 lines 505-507: the EWK contamination is subtracted "using the
#    expected cross section and the *effective luminosity of the lepton
#    triggers* listed in Table 15". Those are prescaled paths, so their
#    integrated luminosity is not the analysis'. In 2024:
#
#      analysis                   110.11 fb-1  =  110110 pb-1
#      ele, both paths                              70.526 pb-1   / 1561
#      mu,  probe pT <= 20 GeV                      12.424 pb-1   / 8863
#      mu,  probe pT >  20 GeV                     336.399 pb-1   /  327
#
#    measureFakeRate.py scales MC by one scalar, cfg['lumi'] = 110.11 (fb).
#    Under the prescaled paths that over-subtracts the EWK term by between two
#    and four orders of magnitude, which would drive the measured rate negative
#    long before it drove it wrong. So this is not a correction to apply after
#    the fact: the normalisation has to become a function of (flavour, probe pT
#    bin), because the muon factor changes by 27 across the 20 GeV switch
#    point. One scalar cannot express it.
#
#    Note which way the bias goes if it is got wrong, because it is the sign of
#    the discrepancy we are chasing: prompt leptons are nearly all tight, so
#    they sit in the numerator far more than in the denominator.
#    UNDER-subtracting EWK therefore pushes the fake rate UP, over-subtracting
#    pushes it DOWN.
#
#    Our own measurement is not affected: it uses the unprescaled analysis
#    paths, for which 110.11 fb-1 is the right number. The factor only appears
#    the moment the Table 15 paths are used.
#
# 2. THE AWAY JET. Legacy: at least one jet with pT > 30 GeV, and
#    dR(probe, *leading* jet) > 1.0. Ours: no jet requirement at all, and the
#    nAwayJet* counters implement dR > 0.7 from every selected lepton. Use
#    njet30 >= 1 together with SelLep_drJet0 > 1.0; the counters are for the
#    threshold scan, which is the legacy shape systematic.
#
# 3. THE W REJECTION. Legacy: PuppiMET < 20 and mT^W1 < 20.
#    cuts.py:FR: PuppiMET_pt < 30 and mt_l0 < 30. Both branches are here, so
#    this is a number in the analysis script.
#
# 4. THE MULTIPLICITY AND THE PROBE FLOOR. Legacy: exactly one lepton, muon
#    pT > 10, electron pT > 13. cuts.py: nLepSel between 1 and 2, with a
#    2-lepton same-sign branch that has no legacy counterpart -- it exists to
#    reach low pT without prescaled paths, which is exactly what the Table 15
#    paths make unnecessary. Note the electron floor: 13, not 10.
#
# 5. THE BINNING AND THE PLATEAU. Legacy: two eta bins, barrel and endcap
#    (|eta| = 1.479), and for pT > 35 GeV the value measured at 35 GeV is used
#    rather than the one measured in the bin, because the EWK subtraction takes
#    over above that. Ours: ten signed-eta bins and every pT bin on its own.
#    Both are downstream choices, but the frozen plateau is not cosmetic -- it
#    is why the legacy curve is flat above 35 and ours is not.
#
# And one thing that is now settled rather than different: the fakeable object.
# AN-24-128 Table 7 is the loose, HLT-safe electron ID -- the FakeObjWP we had
# never seen written down. It cuts in both barrel and endcap, with different
# values:
#
#                        EB (|eta| <= 1.479)     EE (|eta| > 1.479)
#     sigmaIetaIeta <          0.0103                 0.0272
#     |1/E - 1/p|  <           0.0966                 0.111
#     |dEtaInSeed| <           0.00481                0.00951
#     |dPhiInSeed| <           0.127                  0.221
#     missing inner hits <=    1                      1
#     conversion veto          pass                   pass
#     |dxy| < 0.05 / |dz| < 0.1          |dxy| < 0.1 / |dz| < 0.2
#     plus H/E and relIsoWithEA, both rho- and ESC-dependent
#
# The muon denominator is PFrelIso04 < 0.4 and the numerator < 0.15, which is
# exactly Muon_pfIsoId >= 1 and >= 4 -- verified against
# muon::makeSelectorBitset in MuonSelectors.cc, and measured: of 9176 muons,
# zero pass pfIsoId >= 4 while failing pfRelIso04_all < 0.4.
# ===================================================================
