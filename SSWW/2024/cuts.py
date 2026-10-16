# ------------------------------------------------
# Supercut: loose preselection applied to all events
# - at least 2 leptons above 10 GeV (nLepSel), fewer than 5 in the collection
#   (the >= 5 veto stays on the full collection: it stands in for the AN's veto
#   on five or more *loose* leptons)
# - leading lepton pT > 25; the subleading > 10 is implied by nLepSel > 1
# - at least 2 jets with pT > 50 and |eta| < 5
# ------------------------------------------------
supercut = (
    '  nLepSel > 1'
    ' && Lepton_pt.size() < 5'
    ' && (Lepton_pt.size() > 0 ? Lepton_pt[0] : -99) > 25'
    ' && CleanJet_pt.size() > 1'
    ' && (CleanJet_pt.size() > 0 ? CleanJet_pt[0] : -99) > 50'
    ' && (CleanJet_pt.size() > 1 ? CleanJet_pt[1] : -99) > 50'
    ' && (CleanJet_pt.size() > 0 ? abs(CleanJet_eta[0]) : 99) < 5.0'
    ' && (CleanJet_pt.size() > 1 ? abs(CleanJet_eta[1]) : 99) < 5.0'
)



# # ------------------------------------------------
# # FR QCD Enriched Region
# # bVeto, MET < 30, mtw1 < 20
# # ortogonale alla DY CR (escluso picco Z OS SF)
# # ------------------------------------------------
# cuts['FR_QCD_CR'] = {
#     'expr': (
#         'bVeto'
#         ' && PuppiMET_pt < 30'
#         ' && mtw1 < 20'
#         ' && !('
#         '    Lepton_pt.size() == 2'
#         '    && (Lepton_pdgId[0] + Lepton_pdgId[1]) == 0'
#         '    && mll > 60 && mll < 120'
#         ' )'
#     ),
#     # 'categories': {
#     #     'mu' : 'abs(Lepton_pdgId[0]) == 13',
#     #     'ele': 'abs(Lepton_pdgId[0]) == 11',
#     # }
# }

# # ------------------------------------------------
# # FR DY CR
# # bVeto, MET < 30, mtw1 < 20
# # esattamente 2 leptoni OS SF nel picco Z
# # ------------------------------------------------
# cuts['FR_DY_CR'] = {
#     'expr': (
#         'bVeto'
#         ' && PuppiMET_pt < 30'
#         ' && mtw1 < 20'
#         ' && Lepton_pt.size() == 2'
#         ' && (Lepton_pdgId[0] + Lepton_pdgId[1]) == 0'
#         ' && mll > 60 && mll < 120'
#     ),
#     # 'categories': {
#     #     'mumu': 'abs(Lepton_pdgId[0]) == 13',
#     #     'ee'  : 'abs(Lepton_pdgId[0]) == 11',
#     # }
# }

# # ------------------------------------------------
# # FR Top CR
# # bReq, MET < 30, mtw1 < 20
# # veto Z peak OS SF
# # ------------------------------------------------
# cuts['FR_top_CR'] = {
#     'expr': (
#         'bReq'
#         ' && PuppiMET_pt < 30'
#         ' && mtw1 < 20'
#         ' && !('
#         '    Lepton_pt.size() == 2'
#         '    && (Lepton_pdgId[0] + Lepton_pdgId[1]) == 0'
#         '    && mll > 60 && mll < 120'
#         ' )'
#     ),
#     # 'categories': {
#     #     'mu' : 'abs(Lepton_pdgId[0]) == 13',
#     #     'ele': 'abs(Lepton_pdgId[0]) == 11',
#     # }
# }

# ------------------------------------------------
# WW Signal Region
# 2 leptons, same-sign, pT > 25/20
# ------------------------------------------------
cuts['WW_SR'] = {
    'expr': (
        'nLepSel == 2'
        ' && Lepton_pt[1] > 20'
        ' && (ee && !(abs(mll - 91.2) < 15) || mumu || emu)'          # same-sign in base region
        ' && mll > 20'
        ' && PuppiMET_pt > 30'
        ' && bVeto'
        ' && zstar_max < 0.75'
        ' && mjj > 500'
        ' && detajj > 2.5'
    ),
    # Same-flavour / different-flavour split.
    #
    # The Z veto for ee is already in 'expr' above, so 'ee || mumu' needs no
    # repetition of it -- a category is ANDed with the parent expression.
    #
    # Why SF vs DF and not ee / mumu / emu: emu is ~half the same-sign WW yield
    # and has no Drell-Yan charge-flip contamination at all (the flip rate for
    # muons is negligible, so an e-mu pair cannot fake a same-sign pair the way
    # ee can), while ee carries nearly all of it. Splitting that way separates
    # regions with genuinely different backgrounds; splitting ee from mumu
    # separates two regions with the same background composition and just
    # halves the statistics of each.
    #
    # The finer 3-way split is kept below in case the charge-flip measurement
    # ends up needing ee on its own.
    'categories': {
        'SF' : 'ee || mumu',
        'DF' : 'emu',
    }
    # 'categories': {
    #     'ee'   : 'ee',
    #     'mumu' : 'mumu',
    #     'emu'  : 'emu',
    # }
}

# ------------------------------------------------
# WZ Signal Region
# 3 leptons, pT > 25/10 (Z pair) + pT > 20 (W lepton)
# ------------------------------------------------
cuts['WZ_SR'] = {
    'expr': (
        'nLepSel == 3'
        ' && pt_Z1 > 25'
        ' && pt_Z2 > 10'
        ' && pt_W > 20'
        ' && abs(mll_Z - 91.2) < 15'
        ' && mlll > 100'
        ' && PuppiMET_pt > 30'
        ' && bVeto'
        ' && zstar_max < 1.0'
        ' && mjj > 500'
        ' && detajj > 2.5'
        ' && (eee || eem || mme || mmm)'
    ),
    # 'categories': {
    #     'eee' : 'eee',
    #     'eem' : 'eem',
    #     'mme' : 'mme',
    #     'mmm' : 'mmm',
    # }
}

# ------------------------------------------------
# Nonprompt CR (WW SR with b-tag required)
# ------------------------------------------------
cuts['nonprompt_CR'] = {
    'expr': (
        'nLepSel == 2'
        ' && Lepton_pt[1] > 20'
        ' && (ee && !(abs(mll - 91.2) < 15) || mumu || emu)'
        ' && mll > 20'
        ' && PuppiMET_pt > 30'
        ' && bReq'
        ' && zstar_max < 0.75'
        ' && mjj > 500'
        ' && detajj > 2.5'
    ),
    # Same-flavour / different-flavour split.
    #
    # The Z veto for ee is already in 'expr' above, so 'ee || mumu' needs no
    # repetition of it -- a category is ANDed with the parent expression.
    #
    # Why SF vs DF and not ee / mumu / emu: emu is ~half the same-sign WW yield
    # and has no Drell-Yan charge-flip contamination at all (the flip rate for
    # muons is negligible, so an e-mu pair cannot fake a same-sign pair the way
    # ee can), while ee carries nearly all of it. Splitting that way separates
    # regions with genuinely different backgrounds; splitting ee from mumu
    # separates two regions with the same background composition and just
    # halves the statistics of each.
    #
    # The finer 3-way split is kept below in case the charge-flip measurement
    # ends up needing ee on its own.
    'categories': {
        'SF' : 'ee || mumu',
        'DF' : 'emu',
    }
    # 'categories': {
    #     'ee'   : 'ee',
    #     'mumu' : 'mumu',
    #     'emu'  : 'emu',
    # }
}

# ------------------------------------------------
# WZb CR (WZ SR with b-tag required)
# ------------------------------------------------
cuts['WZb_CR'] = {
    'expr': (
        'nLepSel == 3'
        ' && pt_Z1 > 25'
        ' && pt_Z2 > 10'
        ' && pt_W > 20'
        ' && abs(mll_Z - 91.2) < 15'
        ' && mlll > 100'
        ' && PuppiMET_pt > 30'
        ' && bReq'
        ' && zstar_max < 1.0'
        ' && mjj > 500'
        ' && detajj > 2.5'
        ' && (eee || eem || mme || mmm)'
    ),
    # 'categories': {
    #     'eee' : 'eee',
    #     'eem' : 'eem',
    #     'mme' : 'mme',
    #     'mmm' : 'mmm',
    # }
}

# ------------------------------------------------
# QCD WW Validation Regions (200 < mjj < 500, no detajj cut)
# ------------------------------------------------
cuts['WW_VR_bveto'] = {
    'expr': (
        'nLepSel == 2'
        ' && Lepton_pt[1] > 20'
        ' && (ee && !(abs(mll - 91.2) < 15) || mumu || emu)'
        ' && mll > 20'
        ' && PuppiMET_pt > 30'
        ' && bVeto'
        ' && zstar_max < 0.75'
        ' && mjj > 200 && mjj < 500'
    ),
    # Same-flavour / different-flavour split.
    #
    # The Z veto for ee is already in 'expr' above, so 'ee || mumu' needs no
    # repetition of it -- a category is ANDed with the parent expression.
    #
    # Why SF vs DF and not ee / mumu / emu: emu is ~half the same-sign WW yield
    # and has no Drell-Yan charge-flip contamination at all (the flip rate for
    # muons is negligible, so an e-mu pair cannot fake a same-sign pair the way
    # ee can), while ee carries nearly all of it. Splitting that way separates
    # regions with genuinely different backgrounds; splitting ee from mumu
    # separates two regions with the same background composition and just
    # halves the statistics of each.
    #
    # The finer 3-way split is kept below in case the charge-flip measurement
    # ends up needing ee on its own.
    'categories': {
        'SF' : 'ee || mumu',
        'DF' : 'emu',
    }
    # 'categories': {
    #     'ee'   : 'ee',
    #     'mumu' : 'mumu',
    #     'emu'  : 'emu',
    # }
}

cuts['WW_VR_btag'] = {
    'expr': (
        'nLepSel == 2'
        ' && Lepton_pt[1] > 20'
        ' && (ee && !(abs(mll - 91.2) < 15) || mumu || emu)'
        ' && mll > 20'
        ' && PuppiMET_pt > 30'
        ' && bReq'
        ' && zstar_max < 0.75'
        ' && mjj > 200 && mjj < 500'
    ),
    # Same-flavour / different-flavour split.
    #
    # The Z veto for ee is already in 'expr' above, so 'ee || mumu' needs no
    # repetition of it -- a category is ANDed with the parent expression.
    #
    # Why SF vs DF and not ee / mumu / emu: emu is ~half the same-sign WW yield
    # and has no Drell-Yan charge-flip contamination at all (the flip rate for
    # muons is negligible, so an e-mu pair cannot fake a same-sign pair the way
    # ee can), while ee carries nearly all of it. Splitting that way separates
    # regions with genuinely different backgrounds; splitting ee from mumu
    # separates two regions with the same background composition and just
    # halves the statistics of each.
    #
    # The finer 3-way split is kept below in case the charge-flip measurement
    # ends up needing ee on its own.
    'categories': {
        'SF' : 'ee || mumu',
        'DF' : 'emu',
    }
    # 'categories': {
    #     'ee'   : 'ee',
    #     'mumu' : 'mumu',
    #     'emu'  : 'emu',
    # }
}

# ------------------------------------------------
# QCD WZ Validation Regions (200 < mjj < 500, no detajj cut)
# ------------------------------------------------
cuts['WZ_VR_bveto'] = {
    'expr': (
        'nLepSel == 3'
        ' && pt_Z1 > 25'
        ' && pt_Z2 > 10'
        ' && pt_W > 20'
        ' && abs(mll_Z - 91.2) < 15'
        ' && mlll > 100'
        ' && PuppiMET_pt > 30'
        ' && bVeto'
        ' && zstar_max < 1.0'
        ' && mjj > 200 && mjj < 500'
        ' && (eee || eem || mme || mmm)'
    ),
    # 'categories': {
    #     'eee' : 'eee',
    #     'eem' : 'eem',
    #     'mme' : 'mme',
    #     'mmm' : 'mmm',
    # }
}

cuts['WZ_VR_btag'] = {
    'expr': (
        'nLepSel == 3'
        ' && pt_Z1 > 25'
        ' && pt_Z2 > 10'
        ' && pt_W > 20'
        ' && abs(mll_Z - 91.2) < 15'
        ' && mlll > 100'
        ' && PuppiMET_pt > 30'
        ' && bReq'
        ' && zstar_max < 1.0'
        ' && mjj > 200 && mjj < 500'
        ' && (eee || eem || mme || mmm)'
    ),
    # 'categories': {
    #     'eee' : 'eee',
    #     'eem' : 'eem',
    #     'mme' : 'mme',
    #     'mmm' : 'mmm',
    # }
}

# ------------------------------------------------
# ZZ Validation Region (4 leptons)
# AN Table 14 asks pT > 25/20/10/10. The 25 and the 20 are explicit below; the
# two 10s need no cut, because nLepSel == 4 already means four leptons above
# 10 GeV (and the supercut caps the collection at 4, so there are no others).
# Both SFOS pairs in the Z window, mjj > 500, detajj > 2.5, no MET cut, no bveto
# ------------------------------------------------
cuts['ZZ_VR'] = {
    'expr': (
        'nLepSel == 4'
        ' && pt_4l_1 > 25'
        ' && pt_4l_2 > 20'
        ' && abs(mll_Z1 - 91.2) < 15'
        ' && abs(mll_Z2 - 91.2) < 15'
        ' && mjj > 500'
        ' && detajj > 2.5'
        ' && zstar_max < 0.75'
        ' && (eeee || eemm || mmmm)'
    ),
    # 'categories': {
    #     'eeee' : 'eeee',
    #     'eemm' : 'eemm',
    #     'mmmm' : 'mmmm',
    # }
}

# ------------------------------------------------
# DNN_dump -- the single region the training ntuple is dumped from
# (branch DNNTraining; used by snapshot.py, not by mkShapes)
#
# mkSnapshot dumps EXACTLY ONE region per run. cut_to_dump names one key of
# this dict, _build_cpp_cuts_and_output applies that one Filter, and the
# Snapshot is taken on that node. There is no list form and no loop: a second
# region means a second run, with a different cut_to_dump and a different
# folder_where_to_save_trees.
#
# So this region is the UNION of everything in this file, loosened, and the
# membership of each analysis region travels with the event as an is_<region>
# branch (generated from this dict at the end of aliases.py -- the cuts dict
# is injected into the aliases namespace, so there is no second copy of these
# expressions to keep in sync).
#
# Three branches, one per lepton multiplicity:
#
#   nLepSel == 2, same sign   covers WW_SR, nonprompt_CR, WW_VR_bveto,
#                             WW_VR_btag
#   nLepSel == 3              covers WZ_SR, WZb_CR, WZ_VR_bveto, WZ_VR_btag
#   nLepSel == 4              covers ZZ_VR
#
# Kept here rather than dumped as a branch, and why:
#
#   mjj > 200          the loosest mjj any region uses (WW_VR_*, WZ_VR_*).
#                      Without it the QCD-induced tail dominates the file size
#                      and nothing downstream would ever look at it.
#   same sign in 2l    opposite-sign is a different analysis, and keeping it
#                      would add the whole DY and top yield to the ntuple
#   Lepton_pt[1] > 20  below this the trigger and the fake rate are not
#                      measured, so the events are unusable anyway
#   mll > 20           the low-mass resonance region, never used
#   mlll > 100         as in every 3-lepton region here
#
# Dropped with respect to the signal regions, and therefore dumped as a
# branch instead -- this is the point of snapshotting rather than
# histogramming, since each of these is either a knob to retune or an input
# to hand the network:
#
#   PuppiMET_pt > 30   -> dnn_met_*; the nonprompt background lives at low MET
#   bVeto / bReq       -> dnn_nbjet, dnn_maxbtag, so the b working point and
#                         the bveto/btag split stay free
#   zstar_max < 0.75   -> zstar_max and the per-object dnn_zepp_*
#   detajj > 2.5       -> detajj
#   the Z veto in ee   -> mll plus the flavour flags
#   the Z window in 3l -> mll_Z
#   the flavour split  -> ee/mumu/emu, eee/eem/mme/mmm, eeee/eemm/mmmm
#
# Note the Lepton_pt[1] index: the supercut only guarantees one lepton in the
# collection, so that term is safe only because nLepSel == 2 is evaluated
# first and && short-circuits left to right. Same for the 3l and 4l branches,
# which rely on mlll / the ZZ aliases returning -9999 off their multiplicity.
# ------------------------------------------------
cuts['DNN_dump'] = {
    'expr': (
        'mjj > 200'
        ' && ('
        '      (nLepSel == 2 && Lepton_pt[1] > 20 && (ee || mumu || emu) && mll > 20)'
        '   || (nLepSel == 3 && mlll > 100)'
        '   ||  nLepSel == 4'
        ' )'
    ),
}
