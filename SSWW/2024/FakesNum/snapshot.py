# snapshot.py

# -------------------------------------------------------------------
# Dove salvare i TTree prodotti
# -------------------------------------------------------------------
# folder_where_to_save_trees = '../rootFile/' + '260914_Fakes' + '/snapshot/'

# -------------------------------------------------------------------
# Taglio applicato prima dello snapshot
# -------------------------------------------------------------------
cut_to_dump = 'ALL'

# -------------------------------------------------------------------
# Branch da salvare
# -------------------------------------------------------------------

# Pesi base
_weights = [
    'XSWeight',
    'SFweight2l',
    'LepWPSF',
    'METFilter_DATA',
    'fakeW',
]

# Cinematica leptoni
_leptons = [
    'Lepton_pt',
    'Lepton_eta',
    'Lepton_phi',
    'Lepton_pdgId',
    'Lepton_pt_ScaleUp',
    'Lepton_pt_ScaleDo',
    'Lepton_pt_ResUp',
    'Lepton_pt_ResDo',
    'Lepton_rochesterSF',
]

# Tight WP boolean per elettroni
_tight_ele = [
    'Lepton_isTightElectron_mvaWinter22V2Iso_WP90',
    'Lepton_isTightElectron_mvaWinter22V2Iso_WP90_tthMVA_HWW',
    'Lepton_isTightElectron_mvaWinter22V2Iso_WP90_tthMVA_Run3',
    'Lepton_isTightElectron_cutBased_MediumID_tthMVA_HWW',
    'Lepton_isTightElectron_cutBased_MediumID_tthMVA_Run3',
    'Lepton_isTightElectron_wp90iso',
    'Lepton_isTightElectron_testrecipes',
]

# Tight WP boolean per muoni
_tight_mu = [
    'Lepton_isTightMuon_cut_Tight_HWW',
    'Lepton_isTightMuon_cut_TightID_pfIsoTight_HWW_tthmva_67',
    'Lepton_isTightMuon_cut_TightID_pfIsoLoose_HWW_tthmva_HWW',
    'Lepton_isTightMuon_cut_TightID_pfIsoLoose_HWW_tthmva_67',
    'Lepton_isTightMuon_cut_TightID_POG',
    'Lepton_isTightMuon_cut_TightID_pfIsoLoose_HWW_PNet',
]

# HLT trigger paths
_triggers = [
    'HLT_IsoMu24',
    'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8',
    'HLT_Ele30_WPTight_Gsf',
    'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL',
    'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL',
    'HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ',
    'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ',
]

# Variabili di selezione
_selection = [
    'PuppiMET_pt',
    'PuppiMET_phi',
    'mtw1',
    'mll',
    'bVeto',
    'bReq',
]

# Jet
_jets = [
    'CleanJet_pt',
    'CleanJet_eta',
    'CleanJet_phi',
    'CleanJet_mass',
    'CleanJet_jetIdx',
    'Jet_btagUParTAK4B',
]
# Variabili VBS di alto livello
_vbs = [
    'mjj',
    'detajj',
    'zstar_max',
    'ptll',
    'dphill',
]

# Attività adronica e vertici
_event = [
    'PV_npvsGood',
    'run',
    'luminosityBlock',
    'event',
]

# Flag di regione
_regions = [
    'isFR_QCD_CR',
    'isFR_DY_CR',
    'isFR_top_CR',
]

# Gen matching (per closure test)
_gen = [
    'Lepton_genmatched',
    'Lepton_promptgenmatched',
]

# merge di tutto
variables_to_dump = (
    _weights
    + _leptons
    + _tight_ele
    + _tight_mu
    + _triggers
    + _selection
    + _jets
    + _vbs
    + _event
    + _regions
    + _gen
)