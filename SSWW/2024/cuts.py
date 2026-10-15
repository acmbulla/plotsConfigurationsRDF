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
    # 'categories': {
    #     'ee'   : 'ee && !(abs(mll - 91.2) < 15)',
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
    # 'categories': {
    #     'ee'   : 'ee && !(abs(mll - 91.2) < 15)',
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
    # 'categories': {
    #     'ee'   : 'ee && !(abs(mll - 91.2) < 15)',
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
    # 'categories': {
    #     'ee'   : 'ee && !(abs(mll - 91.2) < 15)',
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
# DNN_train -- the region the training ntuple is dumped from
# (branch DNNTraining; used by snapshot.py, not by mkShapes)
#
# This is deliberately *looser* than WW_SR and a superset of it, of
# nonprompt_CR and of both WW_VR_*. Every cut that WW_SR applies and this one
# does not is dumped as a branch instead, so the selection can be retuned --
# or handed to the network as an input -- without re-reading nanoAOD. That is
# the whole point of snapshotting rather than histogramming.
#
# Dropped with respect to WW_SR, and why:
#   PuppiMET_pt > 30   -> dumped as dnn_met_*; MET is an input, and the
#                         nonprompt background lives at low MET
#   bVeto              -> dumped as dnn_nbjet / dnn_maxbtag, so the b working
#                         point stays free
#   zstar_max < 0.75   -> dumped as zstar_max and the per-object dnn_zepp_*
#   detajj > 2.5       -> dumped as detajj
#   Z veto in ee       -> dumped as mll plus the flavour flags
#
# Kept, and why:
#   nLepSel == 2       -> the 2-lepton branch is what this classifier is for;
#                         WZ/ZZ are a different network with different inputs
#   same sign          -> opposite-sign is a different analysis entirely, and
#                         keeping it would multiply the ntuple by the DY+top yield
#   Lepton_pt[1] > 20  -> below this the trigger and the fake rate are not
#                         measured, so the events could not be used anyway
#   mll > 20           -> the low-mass resonance region, never used
#   mjj > 200          -> the loosest mjj any planned region uses (WW_VR_*);
#                         without it the QCD-induced tail dominates the file size
#
# Note the Lepton_pt[1] index: the supercut only guarantees one lepton in the
# collection, so this term is safe only because nLepSel == 2 is evaluated
# first and && short-circuits left to right.
# ------------------------------------------------
cuts['DNN_train'] = {
    'expr': (
        'nLepSel == 2'
        ' && Lepton_pt[1] > 20'
        ' && (ee || mumu || emu)'
        ' && mll > 20'
        ' && mjj > 200'
    ),
}
