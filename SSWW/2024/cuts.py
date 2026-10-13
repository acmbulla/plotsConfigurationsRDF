# ------------------------------------------------
# Supercut: loose preselection applied to all events. Leptons only.
# - at least 2 leptons above 10 GeV (nLepSel), fewer than 5 in the collection
#   (the >= 5 veto stays on the full collection: it stands in for the AN's veto
#   on five or more *loose* leptons)
# - leading lepton pT > 25; the subleading > 10 is implied by nLepSel > 1
#
# The jet requirement is NOT here any more: it moved into the regions, so that
# a region can be defined inclusively in jet multiplicity (see WZ_CR_incl).
# ------------------------------------------------
supercut = (
    '  nLepSel > 1'
    ' && Lepton_pt.size() < 5'
    ' && (Lepton_pt.size() > 0 ? Lepton_pt[0] : -99) > 25'
)

# ------------------------------------------------
# The two VBS tagging jets, previously part of the supercut.
#
# Every region that uses mjj, detajj or zstar_max has to keep this: all three
# are built from CleanJet[0] and CleanJet[1] and are meaningless with fewer
# than two jets. zstar_max in particular returns -1 when there are fewer, and
# -1 < 1.0 is true, so a region that dropped the requirement but kept the cut
# would silently accept every event with 0 or 1 jet.
#
# The size() check comes first and && short-circuits, so the indexing below is
# safe without ternaries.
# ------------------------------------------------
vbsjets = (
    ' && CleanJet_pt.size() > 1'
    ' && CleanJet_pt[0] > 50'
    ' && CleanJet_pt[1] > 50'
    ' && abs(CleanJet_eta[0]) < 5.0'
    ' && abs(CleanJet_eta[1]) < 5.0'
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
    ) + vbsjets,
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
# ------------------------------------------------
# WZ Control Region, inclusive in jet multiplicity
#
# The WZ leg of the selection and nothing else: three leptons at 25/10/20 by
# role, the Z pair in the mass window, mlll > 100, MET > 30. No jet
# requirement, and therefore deliberately no mjj, no detajj and no zstar_max,
# since all three need CleanJet[0] and CleanJet[1].
#
# The b veto is kept: it is well defined with zero jets (Sum(...) == 0 is
# trivially true) and without it tZq and ttZ take over the three-lepton phase
# space. Drop `&& bVeto` for the fully inclusive version.
#
# Purpose: a high-statistics WZ sample to pin the normalization. The VBS jet
# requirement costs a large factor, so this region has many more events than
# WZ_SR and measures data/MC for WZ with a far smaller statistical error --
# which is the thing the signal regions cannot do.
# ------------------------------------------------
cuts['WZ_CR_incl'] = {
    'expr': (
        'nLepSel == 3'
        ' && pt_Z1 > 25'
        ' && pt_Z2 > 10'
        ' && pt_W > 20'
        ' && abs(mll_Z - 91.2) < 15'
        ' && mlll > 100'
        ' && PuppiMET_pt > 30'
        ' && bVeto'
        ' && (eee || eem || mme || mmm)'
    ),
}

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
    ) + vbsjets,
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
    ) + vbsjets,
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
    ) + vbsjets,
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
    ) + vbsjets,
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
    ) + vbsjets,
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
    ) + vbsjets,
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
    ) + vbsjets,
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
    ) + vbsjets,
    # 'categories': {
    #     'eeee' : 'eeee',
    #     'eemm' : 'eemm',
    #     'mmmm' : 'mmmm',
    # }
}