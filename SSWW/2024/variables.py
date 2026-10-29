
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
# ------------------------------------------------
# The polarisation networks
#
# Two models, both deployed through `dnn_reader` (see the block at the end of
# aliases.py). Each produces an UNROLLED observable:
#
#     dnn2s_unrolled  in [0, 6)   6 cells: LL/TL/TT x p(stage 2) low/high
#     dnn4_unrolled   in [0, 4)   4 categories: background/LL/TL/TT
#
# The integer part is the categorical cell; the fractional part is the frozen
# CDF of the reference signal inside that cell, so it is uniform on [0, 1) by
# construction. That is the whole point: a bin boundary at `cell + k/n` is the
# k-th n-quantile of that cell, and the binning is therefore chosen HERE and
# not baked into the weight file.
#
# Two ways to bin it.
#
#   equal bins everywhere      'range': (6 * n, 0, 6)
#   a different n per cell     'range': dnn_bins([...])
#
# The second is the list form of 'range', which mkShapes turns into explicit
# double edges, so the bins may have any width -- and `dnn_bins` only ever
# places boundaries inside a cell, never across one. Spending bins where the
# signal is and not where it is not is exactly what you want here: the
# background category of the four-head model holds most of the yield and
# almost none of the information, while the LL category holds the opposite.
#
# Do NOT write a uniform range whose bin count is not a multiple of the cell
# count. A bin straddling two cells averages two different categories and the
# fit reads the average.
#
# The pieces are columns too (`dnn2s_q`, `dnn4_q`, `dnn4_cat`, ...), so one
# category can also be histogrammed on its own with a cut rather than as part
# of the unrolled variable.
# ------------------------------------------------
def dnn_bins(bins_per_cell):
    """Edges for an unrolled DNN variable, with its own bin count per cell.

    `dnn_bins([2, 6, 4, 3])` gives the four-head observable 2 bins in the
    background category, 6 in LL, 4 in TL and 3 in TT: fifteen bins in all,
    each one a quantile interval of its own category. The cell boundaries are
    always edges, so no bin can mix two categories.
    """
    edges = []
    for cell, n in enumerate(bins_per_cell):
        if n < 1:
            raise ValueError('every cell needs at least one bin')
        edges += [cell + k / float(n) for k in range(n)]
    edges.append(float(len(bins_per_cell)))
    return edges


# The published two-stage observable: 6 cells x 4 bins = 24. Equivalent to
# dnn_bins([4] * 6), written as a uniform range because it is uniform.
variables['dnn2s'] = {
    'name' : 'dnn2s_unrolled',
    'range': (24, 0, 6),
    'xaxis': 'two-stage DNN (LL/TL/TT x p_{stage 2} x signal score)',
    'fold' : 0
}

# The same observable with the bins moved to where the longitudinal signal
# is: the two LL cells get six each, the TL and TT cells four, and the
# low-probability halves fewer. Change the list, not the model.
variables['dnn2s_tuned'] = {
    'name' : 'dnn2s_unrolled',
    'range': dnn_bins([4, 6, 3, 4, 3, 4]),
    'xaxis': 'two-stage DNN (per-cell binning)',
    'fold' : 0
}

# The four-head observable, 4 categories x 6 bins = 24.
variables['dnn4'] = {
    'name' : 'dnn4_unrolled',
    'range': (24, 0, 4),
    'xaxis': 'multiclass DNN (argmax x p_{max})',
    'fold' : 0
}

# The same, with the bins spent on the signal categories instead of on the
# background one, which carries most of the yield and almost no information.
variables['dnn4_tuned'] = {
    'name' : 'dnn4_unrolled',
    'range': dnn_bins([3, 8, 5, 5]),
    'xaxis': 'multiclass DNN (per-category binning)',
    'fold' : 0
}

# ------------------------------------------------
# The pieces
#
# `*_q` is the within-cell quantile on [0, 1): the unrolled variable with its
# cell stripped off. Combined with a cut on the category it histograms one
# class on its own, at whatever binning, without touching the others.
# ------------------------------------------------
variables['dnn2s_signal'] = {
    'name' : 'dnn2s_signal',
    'range': (20, 0, 1),
    'xaxis': 'stage-1 p(signal)',
    'fold' : 0
}

variables['dnn2s_cell'] = {
    'name' : 'dnn2s_cell',
    'range': (6, 0, 6),
    'xaxis': 'stage-2 cell (LL/TL/TT x p_{1}/p_{2})',
    'fold' : 0
}

variables['dnn2s_q'] = {
    'name' : 'dnn2s_q',
    'range': (20, 0, 1),
    'xaxis': 'stage-1 score quantile within the cell',
    'fold' : 0
}

variables['dnn4_cat'] = {
    'name' : 'dnn4_cat',
    'range': (4, 0, 4),
    'xaxis': 'multiclass argmax (0 bkg, 1 LL, 2 TL, 3 TT)',
    'fold' : 0
}

variables['dnn4_q'] = {
    'name' : 'dnn4_q',
    'range': (20, 0, 1),
    'xaxis': 'p_{max} quantile within the category',
    'fold' : 0
}

variables['dnn4_pLL'] = {
    'name' : 'dnn4_p_LL',
    'range': (20, 0, 1),
    'xaxis': 'multiclass p(LL)',
    'fold' : 0
}

variables['dnn4_LL_frac'] = {
    'name' : 'dnn4_LL_frac',
    'range': (20, 0, 1),
    'xaxis': 'p_{LL} / (p_{LL} + p_{TL} + p_{TT})',
    'fold' : 0
}
