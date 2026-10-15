# snapshot.py -- SSWW 2024, DNN polarisation-classifier training ntuple
#
# Flat tree for the VBS SSWW polarisation classifier. The measurement this
# feeds is mu_LL = sigma_LL(obs) / sigma_LL(exp), and the planned sequence of
# trainings is, in order of difficulty:
#
#   0  binary      LL vs everything else (TL + TT + all background)
#   1  multiclass  LL / TL / TT / background
#   2  INFERNO     loss = var(mu_LL) instead of cross entropy
#                  (de Castro & Dorigo, arXiv:1806.04743)
#   3  + angular   add the solved W -> l nu decay, recover the lost
#                  longitudinal information
#   4  nuisance-aware INFERNO: systematics and control regions inside the
#                  variance
#
# Stage 4 is the target, and it is what fixes the branch list: every stage
# after 1 needs things the histogram path never carries -- per-event weight
# *factors*, the control regions in the same file, and the gen truth. All of
# them are cheap to dump and expensive to add later, so they are all here.
#
# ===================================================================
#  How mkSnapshot reads this file -- four behaviours that matter
# ===================================================================
#
# 1. ONE REGION PER RUN, AND IT IS MANDATORY. cut_to_dump names a single key
#    of cuts.py. _build_cpp_cuts_and_output applies that one Filter and
#    nothing else; there is no list form and no loop over regions, so a
#    second region means a second run with a different cut_to_dump and a
#    different folder_where_to_save_trees.
#
#    That is why DNN_dump is the *union* of every region in cuts.py and the
#    regions travel with the event as is_<region> branches, generated from
#    the cuts dict at the end of aliases.py. The signal region, the control
#    regions and the validation regions are then carved out of these same
#    files offline -- which is also what stage 4 needs, since a
#    nuisance-aware likelihood has to hold the control regions that constrain
#    its nuisances, drawn from the same events as the signal region.
#
#    A cut_to_dump that is not a key of cuts.py does NOT fail here: the
#    generator prints a warning, emits no Filter, and then still writes
#    `node_<name>.Snapshot(...)`. The result is C++ that does not compile.
#    Loud, but at compile time, not at configuration time.
#
# 2. COLUMN NAMES ONLY, NOT EXPRESSIONS. Entries are matched against
#    df.GetColumnNames(). 'Lepton_pt[0]' is not a column and will never
#    appear; anything derived has to be an alias in aliases.py first.
#
# 3. A MISSING COLUMN IS DROPPED IN SILENCE. The generated C++ intersects the
#    requested list with the existing one, so a typo, a branch the skim
#    removed, or an alias restricted to other samples all produce the same
#    thing: no branch, no warning, no failure. Verify the tree after the first
#    job rather than after the training (recipe at the bottom of this file).
#
# 4. THE LIST BELOW IS A FLOOR, NOT A CEILING. mkSnapshot adds, on its own:
#      - my_sample_weight, always;
#      - my_sample_weight_<nuis>Up/Down for every shape/weight nuisance
#        (none right now -- nuisances.py is almost entirely commented out);
#      - every branch name it can tokenise out of *every* cut in cuts.py;
#      - every simple 'expr' alias in aliases.py.
#    The last one is why the tree also carries LepWPCut2l, fakeW* and friends.
#    They are listed again below where they are actually wanted, both as
#    documentation and because the auto-add is a convenience, not a contract.
#
# ===================================================================
#  The label is in the FILE NAME, not in the tree
# ===================================================================
#
# Nothing in the tree says which sample an event came from. The output file is
#     nanoLatino_snapshot____<sample>_<subname>_<i>.root
# and <sample> is the key of samples.py -- VBS_SSWW_WWCM_LL, _TL, _TT, DY,
# top, Fake, ... -- so the class label is parsed from the path at load time.
#
# Two consequences:
#   - do NOT run `mkSnapshot.py --haddBatch` across samples for training. The
#     merge is per-sample by construction, but the merged snapshot_<tag>.root
#     would still lose nothing only because it is per-sample; a hand-rolled
#     hadd over several samples destroys the label irrecoverably.
#   - the three polarisation samples (LL / TL / TT) are generated separately
#     and their sum is NOT the inclusive VBS_SSWW sample: interference between
#     polarisation states is missing. Train on LL/TL/TT, normalise against
#     VBS_SSWW, and keep the difference in mind as a modelling systematic.

# -------------------------------------------------------------------
# Region and output
# -------------------------------------------------------------------

# must be a key of cuts.py -- see DNN_dump there for what it keeps and drops
cut_to_dump = 'DNN_dump'

folder_where_to_save_trees = '/eos/user/a/abulla/latinoRDF/snapshot/DNNTraining/2024/'

# -------------------------------------------------------------------
# Event weight and its factors
#
# my_sample_weight is added automatically and is the product of everything:
# lumi * XSWeight * METFilter * PromptGenLepMatchN * SFweight. INFERNO cannot
# use only the product. Its loss evaluates the yield under a shifted nuisance,
# which means re-weighting each event by
#     w' = my_sample_weight / f_nominal * f_shifted
# and that division is impossible once the factors have been collapsed. So
# every factor that a nuisance can move is dumped on its own.
#
# The btagSF shifts come from `shifts_needed` in aliases.py. Only the shifts
# listed there exist as aliases; asking for one that is not there is a column
# that vanishes (behaviour 3 above), not an error.
# -------------------------------------------------------------------
_weights = [
    'my_sample_weight',      # redundant -- added anyway; listed so it is visible
    'dnn_w_xs',
    'dnn_w_sf',
    'dnn_w_lepsf',
    'dnn_w_lepcut',
    'dnn_w_glob',
    'dnn_w_match',
    'METFilter_Common',
    'METFilter_DATA',
    'puWeight',
    # b tagging, nominal and the four shifts in shifts_needed
    'btagSFbc',
    'btagSFbc_up_correlated',
    'btagSFbc_down_correlated',
    'btagSFbc_up_uncorrelated',
    'btagSFbc_down_uncorrelated',
    'btagSFlight',
    'btagSFlight_up_correlated',
    'btagSFlight_down_correlated',
    'btagSFlight_up_uncorrelated',
    'btagSFlight_down_uncorrelated',
    # lepton efficiency, the aliases already built at the end of aliases.py
    'SFweightEleUp',
    'SFweightEleDown',
    'SFweightMuUp',
    'SFweightMuDown',
    # the nonprompt estimate: Fake only, dropped in silence everywhere else
    'fakeW',
    'fakeWEleUp',
    'fakeWEleDown',
    'fakeWMuUp',
    'fakeWMuDown',
    'fakeWStatEleUp',
    'fakeWStatEleDown',
    'fakeWStatMuUp',
    'fakeWStatMuDown',
]

# Theory weights. Vectors, not scalars: LHEScaleWeight has the 9 (muR, muF)
# points and LHEPdfWeight the PDF replicas. They are dumped whole because the
# envelope convention (9-point vs 7-point, Hessian vs replica) is exactly the
# kind of thing that gets revised after the jobs have run.
#
# The _vec aliases exist in aliases.py for `lhesamples` only; the raw branches
# are listed too so the samples outside that set keep whatever they have.
_theory = [
    'LHEScaleWeight',
    'LHEPdfWeight',
    'LHEScaleWeight_vec',
    'LHEPdfWeight_vec',
    'PSWeight',             # ISR/FSR, 4 entries
    'LHEReweightingWeight',
    'Top_pTrw',
]

# -------------------------------------------------------------------
# The DNN inputs proper
#
# All of these are dnn_* aliases added at the end of aliases.py, so the naming
# says plainly what is an input and what is bookkeeping. They are scalars: the
# network wants a fixed-width row, and the jagged collections are dumped
# separately below for anything that needs to be rebuilt offline.
# -------------------------------------------------------------------

# leptons
_dnn_leptons = [
    'dnn_l1_pt', 'dnn_l1_eta', 'dnn_l1_phi', 'dnn_l1_pdgId',
    'dnn_l2_pt', 'dnn_l2_eta', 'dnn_l2_phi', 'dnn_l2_pdgId',
    # the 3l and 4l branches of DNN_dump; sentinel when the event has fewer,
    # which is the loader's cue to mask the column and not to read -1 as a
    # measurement
    'dnn_l3_pt', 'dnn_l3_eta', 'dnn_l3_phi', 'dnn_l3_pdgId',
    'dnn_l4_pt', 'dnn_l4_eta', 'dnn_l4_phi', 'dnn_l4_pdgId',
    'dnn_lep_charge',
    'nLepSel',
    'ee', 'mumu', 'emu',
    'eee', 'eem', 'mme', 'mmm',
    'eeee', 'eemm', 'mmmm',
]

# -------------------------------------------------------------------
# Region membership
#
# One boolean per region of cuts.py, generated from the cuts dict itself at
# the end of aliases.py -- not copied, so the two cannot drift apart. They are
# simple 'expr' aliases and so would be auto-added anyway; listed here because
# they are the reason DNN_dump is a union and not a signal region.
#
# There is deliberately no is_DNN_dump: it is true for every event in the
# file.
# -------------------------------------------------------------------
_regions = [
    'is_WW_SR',
    'is_nonprompt_CR',
    'is_WW_VR_bveto',
    'is_WW_VR_btag',
    'is_WZ_SR',
    'is_WZb_CR',
    'is_WZ_VR_bveto',
    'is_WZ_VR_btag',
    'is_ZZ_VR',
]

# -------------------------------------------------------------------
# The 3-lepton and 4-lepton systems
#
# Needed because DNN_dump covers them: WZ is both a background to the 2l
# signal region and, through WZ_SR and WZb_CR, the control region that
# constrains it. The scalars come from the WZ_vars / ZZ_vars function aliases;
# those two parents are NOT auto-added, but every scalar below is a plain
# 'expr' over them, so listing the scalars is enough.
# -------------------------------------------------------------------
_dnn_3l4l = [
    'mll_Z', 'mlll', 'pt_W', 'pt_Z1', 'pt_Z2', 'proxyW_W', 'idx_W', 'WZ_flav',
    'mll_Z1', 'mll_Z2', 'mllll', 'pt_4l_1', 'pt_4l_2', 'ZZ_flav',
]

# the pair -- dphill and detall are the classic LL handles
_dnn_pair = [
    'mll',
    'dnn_ptll',
    'dnn_dphill',
    'dnn_detall',
    'dnn_drll',
    'dnn_etall',
    'dnn_ptAsymll',
]

# MET and the transverse WW system
_dnn_met = [
    'PuppiMET_pt',
    'PuppiMET_phi',
    'dnn_met_px',
    'dnn_met_py',
    'dnn_dphi_llMET',
    'dnn_mTww',
    'dnn_mindphi_METjet',
    'proxyW_l1',       # mT(l1, MET)
    'proxyW_l2',       # mT(l2, MET)
    'mT2',             # function alias -- NOT auto-added, must be listed
]

# the VBS dijet
_dnn_jets = [
    'mjj',
    'detajj',
    'dnn_dphijj',
    'dnn_drjj',
    'dnn_ptjj',
    'dnn_etaProdjj',
    'dnn_j1_pt', 'dnn_j1_eta', 'dnn_j1_phi', 'dnn_j1_mass',
    'dnn_j2_pt', 'dnn_j2_eta', 'dnn_j2_phi', 'dnn_j2_mass',
    'dnn_j3_pt', 'dnn_j3_eta', 'dnn_j3_phi', 'dnn_j3_mass',
]

# Zeppenfeld / centrality / balance
_dnn_vbs = [
    'zstar_max',       # function alias -- NOT auto-added, must be listed
    'dnn_zepp_l1',
    'dnn_zepp_l2',
    'dnn_zepp_ll',
    'dnn_zepp_j3',
    'dnn_Rpt',
]

# hadronic activity and b tagging
_dnn_activity = [
    'dnn_njet20',
    'dnn_njet30',
    'dnn_njet50',
    'dnn_ht_jets',
    'dnn_nbjet',
    'dnn_maxbtag',
    'bVeto',
    'bReq',
]

# lepton-jet geometry -- the nonprompt handles
_dnn_lepjet = [
    'dnn_drl1j_min',
    'dnn_drl2j_min',
    'dr_lj',           # function alias, the full 4-vector of combinations
    'm_lj',            # idem
    'm_l1j1', 'm_l1j2', 'm_l2j1', 'm_l2j2',
    'dr_l1j1', 'dr_l1j2', 'dr_l2j1', 'dr_l2j2',
]

# -------------------------------------------------------------------
# Raw collections
#
# Kept whole so that any definition frozen above can be undone offline: a
# different tagging-jet pairing (leading mjj instead of leading pT), a
# different lepton pT threshold, a different b working point, a jet-by-jet
# input to a graph or set network instead of the flat row.
#
# This is the part that costs disk. If the files are too large, this is the
# block to cut first -- the flat inputs above are what the first three stages
# actually read.
# -------------------------------------------------------------------
_collections = [
    'nCleanJet',
    'CleanJet_pt',
    'CleanJet_eta',
    'CleanJet_phi',
    'CleanJet_jetIdx',
    'Jet_mass',
    'Jet_btagUParTAK4B',
    'Jet_qgl',
    'Jet_jetId',
    'Lepton_pt',
    'Lepton_eta',
    'Lepton_phi',
    'Lepton_pdgId',
    'SelLep_pt',
    'SelLep_eta',
    'SelLep_phi',
    'SelLep_pdgId',
]

# -------------------------------------------------------------------
# Gen-level truth -- stage 3 and the closure of stages 0 and 1
#
# Stages 0 and 1 need none of this: the LL/TL/TT label is the sample, i.e. the
# file name. Stage 3 reconstructs the W -> l nu decay and needs the generated
# W bosons and leptons to check the reconstruction and to define cos(theta*)
# in the W helicity frame, which is the observable the whole measurement is
# about.
#
# LHEPart_* is the hard-process final state: a handful of entries, enough to
# build both W four-momenta, and far cheaper than GenPart. GenPart is listed
# below it, commented out, because it is large and is only needed if the LHE
# record turns out not to carry the Ws explicitly (it depends on how the
# sample was generated -- the SSWW samples decay the Ws in madgraph, so the
# LHE final state is the four fermions plus the two jets, and the Ws have to
# be rebuilt by pairing l with nu by charge).
#
# UNVERIFIED: no nanoAOD file was opened to confirm the latino skim keeps
# these. Behaviour 3 applies -- if they are gone, the branches simply are not
# there. Run the check at the bottom of this file before submitting.
# -------------------------------------------------------------------
_gen = [
    'nLHEPart',
    'LHEPart_pt',
    'LHEPart_eta',
    'LHEPart_phi',
    'LHEPart_mass',
    'LHEPart_pdgId',
    'LHEPart_status',
    'Lepton_genmatched',
    'Lepton_promptgenmatched',
    'Jet_hadronFlavour',
    'Gen_ZGstar_mass',
    # Uncomment if LHEPart does not resolve the W bosons. Large.
    # 'nGenPart', 'GenPart_pt', 'GenPart_eta', 'GenPart_phi', 'GenPart_mass',
    # 'GenPart_pdgId', 'GenPart_status', 'GenPart_statusFlags',
    # 'GenPart_genPartIdxMother',
]

# -------------------------------------------------------------------
# Event identity and pileup
#
# run / luminosityBlock / event are the only way to deduplicate after a
# resubmission and the only way to make a train/test split that is stable
# across re-runs: hash the event number, do not shuffle at load time.
# -------------------------------------------------------------------
_event = [
    'run',
    'luminosityBlock',
    'event',
    'PV_npvsGood',
    'PV_npvs',
    'Pileup_nTrueInt',
    'Trigger_sngEl', 'Trigger_sngMu', 'Trigger_dblEl', 'Trigger_dblMu', 'Trigger_ElMu',
]

variables_to_dump = (
    _weights
    + _theory
    + _dnn_leptons
    + _regions
    + _dnn_3l4l
    + _dnn_pair
    + _dnn_met
    + _dnn_jets
    + _dnn_vbs
    + _dnn_activity
    + _dnn_lepjet
    + _collections
    + _gen
    + _event
)

# -------------------------------------------------------------------
# Verify the tree before trusting it
#
# Because a missing column is dropped in silence, the first job's output has
# to be read back and compared against the list above. On lxplus:
#
#   python3 - <<'EOF'
#   import ROOT, itertools
#   import importlib.util
#   spec = importlib.util.spec_from_loader('snap', loader=None)
#   ns = {'cuts': {}, 'variables_to_dump': []}
#   exec(open('snapshot.py').read(), ns)
#   want = set(ns['variables_to_dump'])
#   f = ROOT.TFile.Open('<one output file>.root')
#   have = {b.GetName() for b in f.Get('Events').GetListOfBranches()}
#   print('MISSING:', sorted(want - have))
#   print('EXTRA  :', sorted(have - want))
#   EOF
#
# MISSING is the list to act on. Expect a few entries legitimately: the gen
# and theory branches are absent for DATA and Fake, fakeW* exists only for
# Fake, and btagSF*/SFweight*/dnn_w_* exist only for MC. Anything else is a
# typo or a branch the skim removed.
#
# To check a branch's existence and type on the input nanoAOD instead, before
# any job is submitted:
#
#   t = ROOT.TFile.Open(path).Get('Events')
#   print(bool(t.GetBranch('LHEPart_pt')))
#
# -------------------------------------------------------------------
# Open points
#
# - The per-year lumi normalisation is inside my_sample_weight (mkSnapshot
#   multiplies the MC weight by lumi). Training across years therefore mixes
#   normalisations; that is correct for a yield-aware loss like INFERNO and
#   wrong for a plain reweighted cross-entropy, which wants class balance.
#   Stage 0/1 should renormalise per class at load time.
#
# - The shape nuisances (JES, JER, MET scale, lepton scale/resolution) are the
#   'suffix' kind and are produced by `mkSnapshot.py --shapeNuisances` as
#   *separate trees*, not as extra branches. They are all commented out in
#   nuisances.py today. Stage 4 needs at least JES and JER uncommented, and
#   then needs the varied trees matched to the nominal one event by event via
#   (run, luminosityBlock, event).
#
# - The 2l, 3l and 4l branches share one flat row, so the per-lepton columns
#   are ragged in meaning even though they are rectangular on disk. Select on
#   nLepSel or on the is_<region> flags before feeding anything to a network;
#   a model trained on all three at once would be learning the multiplicity,
#   not the polarisation.
#
# - DNN_dump is the union of every region in cuts.py as those regions stand
#   today. If a region is added there that reaches outside it -- an
#   opposite-sign region, a lower-mjj one, a 1-lepton one -- the flag will be
#   generated and will simply be false for every event in the file, which is
#   the one failure mode of this design and is silent. Widen DNN_dump in the
#   same commit.
