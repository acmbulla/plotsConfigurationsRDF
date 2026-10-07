
# ------------------------------------------------
# variables.py - VBS WW/WZ analysis
# Conservative binning - to be optimized after looking at data
# NB: if a variable is defined in aliases.py it will NOT be overwritten here!
# ------------------------------------------------

# fold: 0 = no fold (default), 1 = underflow, 2 = overflow, 3 = both

# ------------------------------------------------
# Counting
# ------------------------------------------------
variables['events'] = {
    'name' : '1',
    'range': (1, 0, 2),
    'xaxis': 'events',
    'fold' : 3
}

variables['njet'] = {
    'name' : 'Sum(CleanJet_pt > 30)',
    'range': (8, 0, 8),
    'xaxis': 'N_{jets} (p_{T} > 30 GeV)',
    'fold' : 2
}

variables['nlep'] = {
    'name' : 'Lepton_pt.size()',
    'range': (5, 0, 5),
    'xaxis': 'N_{leptons}',
    'fold' : 2
}

# ------------------------------------------------
# Lepton kinematics
# ------------------------------------------------
variables['ptl1'] = {
    'name' : 'Lepton_pt.size() > 0 ? Lepton_pt[0] : -9999.',
    'range': (10, 25, 225),
    'xaxis': 'p_{T}^{l1} [GeV]',
    'fold' : 2
}

variables['ptl2'] = {
    'name' : 'Lepton_pt.size() > 1 ? Lepton_pt[1] : -9999.',
    'range': (10, 20, 120),
    'xaxis': 'p_{T}^{l2} [GeV]',
    'fold' : 2
}

variables['etal1'] = {
    'name' : 'Lepton_pt.size() > 0 ? Lepton_eta[0] : -9999.',
    'range': (10, -2.5, 2.5),
    'xaxis': '#eta^{l1}',
    'fold' : 0
}

variables['etal2'] = {
    'name' : 'Lepton_pt.size() > 1 ? Lepton_eta[1] : -9999.',
    'range': (10, -2.5, 2.5),
    'xaxis': '#eta^{l2}',
    'fold' : 0
}

# ------------------------------------------------
# Dilepton system (WW)
# ------------------------------------------------
variables['mll'] = {
    'name' : 'mll',
    'range': (10, 20, 320),
    'xaxis': 'm_{ll} [GeV]',
    'fold' : 2
}

variables['drll'] = {
    'name' : 'dRll',
    'range': (10, 0, 5),
    'xaxis': '#Delta R(l_{1}, l_{2})',
    'fold' : 2
}

variables['dphill'] = {
    'name' : 'dphill',
    'range': (10, 0, 3.15),
    'xaxis': '#Delta#phi(l_{1}, l_{2})',
    'fold' : 2
}

# ------------------------------------------------
# MET
# ------------------------------------------------
variables['MET'] = {
    'name' : 'PuppiMET_pt',
    'range': (10, 30, 230),
    'xaxis': 'p_{T}^{miss} [GeV]',
    'fold' : 2
}

variables['MET_phi'] = {
    'name' : 'PuppiMET_phi',
    'range': (10, -3.15, 3.15),
    'xaxis': '#phi(p_{T}^{miss})',
    'fold' : 0
}

# ------------------------------------------------
# WW-specific variables
# ------------------------------------------------
variables['mT2'] = {
    'name' : 'mT2',
    'range': (10, 0, 150),
    'xaxis': 'm_{T2} [GeV]',
    'fold' : 2
}

variables['proxyW_l1'] = {
    'name' : 'proxyW_l1',
    'range': (10, 0, 300),
    'xaxis': 'm_{T}(l_{1}, p_{T}^{miss}) [GeV]',
    'fold' : 2
}

variables['proxyW_l2'] = {
    'name' : 'proxyW_l2',
    'range': (10, 0, 300),
    'xaxis': 'm_{T}(l_{2}, p_{T}^{miss}) [GeV]',
    'fold' : 2
}

# ------------------------------------------------
# Jet kinematics
# ------------------------------------------------
variables['ptj1'] = {
    'name' : 'CleanJet_pt.size() > 0 ? CleanJet_pt[0] : -9999.',
    'range': (10, 50, 350),
    'xaxis': 'p_{T}^{j1} [GeV]',
    'fold' : 2
}

variables['ptj2'] = {
    'name' : 'CleanJet_pt.size() > 1 ? CleanJet_pt[1] : -9999.',
    'range': (10, 50, 250),
    'xaxis': 'p_{T}^{j2} [GeV]',
    'fold' : 2
}

variables['etaj1'] = {
    'name' : 'CleanJet_pt.size() > 0 ? CleanJet_eta[0] : -9999.',
    'range': (10, -5, 5),
    'xaxis': '#eta^{j1}',
    'fold' : 0
}

variables['etaj2'] = {
    'name' : 'CleanJet_pt.size() > 1 ? CleanJet_eta[1] : -9999.',
    'range': (10, -5, 5),
    'xaxis': '#eta^{j2}',
    'fold' : 0
}

# ------------------------------------------------
# VBS dijet system
# ------------------------------------------------
variables['mjj'] = {
    'name' : 'mjj',
    'range': ([500, 700, 1000, 1500, 3000]),
    'xaxis': 'm_{jj} [GeV]',
    'fold' : 2
}

variables['mjj_incl'] = {
    'name' : 'mjj',
    'range': ([200, 300, 400, 500, 700, 1000, 1500, 3000]),
    'xaxis': 'm_{jj} [GeV]',
    'fold' : 2
}

variables['detajj'] = {
    'name' : 'detajj',
    'range': (8, 2.5, 8.5),
    'xaxis': '#Delta#eta(j_{1}, j_{2})',
    'fold' : 2
}

variables['zstar_max'] = {
    'name' : 'zstar_max',
    'range': (8, 0, 1.5),
    'xaxis': 'max(z*_{l})',
    'fold' : 2
}

variables['Zepp_ll'] = {
    'name' : '0.5*abs((Lepton_eta[0] + Lepton_eta[1]) - (CleanJet_eta[0] + CleanJet_eta[1]))',
    'range': (8, 0, 4),
    'xaxis': 'z*_{ll}',
    'fold' : 2
}

variables['Rpt'] = {
    'name' : 'Lepton_pt[0]*Lepton_pt[1]/(CleanJet_pt[0]*CleanJet_pt[1])',
    'range': (8, 0, 0.5),
    'xaxis': 'R_{pT}',
    'fold' : 2
}

# ------------------------------------------------
# Lepton-jet variables (nonprompt discrimination)
# ------------------------------------------------
variables['dr_l1j1'] = {
    'name' : 'dr_l1j1',
    'range': (10, 0, 5),
    'xaxis': '#Delta R(l_{1}, j_{1})',
    'fold' : 2
}

variables['dr_l2j1'] = {
    'name' : 'dr_l2j1',
    'range': (10, 0, 5),
    'xaxis': '#Delta R(l_{2}, j_{1})',
    'fold' : 2
}

variables['m_l1j1'] = {
    'name' : 'm_l1j1',
    'range': (10, 0, 400),
    'xaxis': 'm(l_{1}, j_{1}) [GeV]',
    'fold' : 2
}

variables['m_l2j1'] = {
    'name' : 'm_l2j1',
    'range': (10, 0, 400),
    'xaxis': 'm(l_{2}, j_{1}) [GeV]',
    'fold' : 2
}

# ------------------------------------------------
# WZ-specific variables
# ------------------------------------------------
variables['mll_Z'] = {
    'name' : 'mll_Z',
    'range': (10, 61, 121),
    'xaxis': 'm_{ll}^{Z} [GeV]',
    'fold' : 0
}

variables['mlll'] = {
    'name' : 'mlll',
    'range': (10, 100, 500),
    'xaxis': 'm_{lll} [GeV]',
    'fold' : 2
}

variables['pt_W'] = {
    'name' : 'pt_W',
    'range': (10, 20, 220),
    'xaxis': 'p_{T}^{l_{W}} [GeV]',
    'fold' : 2
}

variables['proxyW_W'] = {
    'name' : 'proxyW_W',
    'range': (10, 0, 300),
    'xaxis': 'm_{T}(l_{W}, p_{T}^{miss}) [GeV]',
    'fold' : 2
}

# ------------------------------------------------
# ZZ-specific variables
# ------------------------------------------------
variables['mll_Z1'] = {
    'name' : 'mll_Z1',
    'range': (10, 61, 121),
    'xaxis': 'm_{ll}^{Z1} [GeV]',
    'fold' : 0
}

variables['mll_Z2'] = {
    'name' : 'mll_Z2',
    'range': (10, 61, 121),
    'xaxis': 'm_{ll}^{Z2} [GeV]',
    'fold' : 0
}

variables['mllll'] = {
    'name' : 'mllll',
    'range': (10, 200, 600),
    'xaxis': 'm_{llll} [GeV]',
    'fold' : 2
}

# ------------------------------------------------
# 2D variables
# ------------------------------------------------
variables['mjjVSdetajj'] = {
    'name' : 'mjj:detajj',
    'range': ([500, 700, 1000, 1500, 3000], [2.5, 4, 6, 10]),
    'xaxis': 'm_{jj} : #Delta#eta_{jj}',
    'fold' : 3,
    'is2d' : 1
}

variables['mllVSmjj'] = {
    'name' : 'mll:mjj',
    'range': ([20, 60, 120, 300], [500, 700, 1000, 3000]),
    'xaxis': 'm_{ll} : m_{jj}',
    'fold' : 3,
    'is2d' : 1
}