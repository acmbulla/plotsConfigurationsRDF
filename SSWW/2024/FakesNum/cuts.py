# ------------------------------------------------
# Supercut: loose preselection applied to all events
# - at least 2 leptons, fewer than 5
# - leading lepton pT > 25, subleading > 10
# - at least 2 jets with pT > 50 and |eta| < 5
# ------------------------------------------------
supercut = (
    '  Lepton_pt.size() > 1'
    ' && Lepton_pt.size() < 5'
    ' && ROOT::VecOps::All(Lepton_pt > 10.f)'  # tutti i leptoni > 10 GeV
    ' && (Lepton_pt.size() > 0 ? Lepton_pt[0] : -99) > 25'
    ' && (Lepton_pt.size() > 1 ? Lepton_pt[1] : -99) > 10'
    ' && CleanJet_pt.size() > 1'
    ' && (CleanJet_pt.size() > 0 ? CleanJet_pt[0] : -99) > 50'
    ' && (CleanJet_pt.size() > 1 ? CleanJet_pt[1] : -99) > 50'
    ' && (CleanJet_pt.size() > 0 ? abs(CleanJet_eta[0]) : 99) < 5.0'
    ' && (CleanJet_pt.size() > 1 ? abs(CleanJet_eta[1]) : 99) < 5.0'
)

cuts['ALL'] = {'expr': '1.'}