# ------------------------------------------------
# Supercut: loose preselection applied to all events
# - at least 2 leptons, fewer than 5
# - leading lepton pT > 25, subleading > 10
# - at least 2 jets with pT > 50 and |eta| < 5
# ------------------------------------------------
supercut = (
    '  Lepton_pt.size() > 1'
    ' && Lepton_pt.size() < 5'
    ' && (Lepton_pt.size() > 0 ? Lepton_pt[0] : -99) > 25'
    ' && (Lepton_pt.size() > 1 ? Lepton_pt[1] : -99) > 10'
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
        'Lepton_pt.size() == 2'
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
        'Lepton_pt.size() == 3'
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
        'Lepton_pt.size() == 2'
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
        'Lepton_pt.size() == 3'
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
        'Lepton_pt.size() == 2'
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
        'Lepton_pt.size() == 2'
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
        'Lepton_pt.size() == 3'
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
        'Lepton_pt.size() == 3'
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
# pT > 25/20, both SFOS pairs in Z window
# mjj > 500, detajj > 2.5, no MET cut, no bveto
# ------------------------------------------------
cuts['ZZ_VR'] = {
    'expr': (
        'Lepton_pt.size() == 4'
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