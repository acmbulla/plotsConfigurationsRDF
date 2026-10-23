#!/usr/bin/env python3
"""Measure signed-eta fake/prompt rates and make pT data/MC control plots.

Input: per-sample nanoLatino_snapshot____*.root files, locally or on XRootD.
The loose denominator is the FakeObjWP-filtered Lepton collection, further
restricted to the first nLepSel entries (SelLep = Take(Lepton, nLepSel)).

For FR: (tight_data-tight_promptMC)/(loose_data-loose_promptMC).
For PR: tight_data/loose_data in the DY region, without subtraction.
All histograms use sample weights: DATA METFilter_DATA; MC XSWeight * lumi *
METFilter_Common. If XSWeight does not include sample normalization, provide
proper normalization upstream before using this script.

The top CR is defined here (not inferred from cuts.py): OS e-mu, nLepSel==2,
mll>12, MET>30 and >=1 central loose-btag jet with pT>30. Adjust the
--top-* parameters to match your actual cuts.py. Top is plotted as a control
region, and is not used to measure FR or PR.

IMPORTANT: the downstream fake-rate reader must use signed eta, not abs(eta).
"""
from __future__ import annotations
import argparse
import glob
import os
import shutil
import subprocess
import time
import traceback
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

import numpy as np

TREE = 'Events'
PREFIX = 'nanoLatino_snapshot____'
MC_SAMPLES = ('DY', 'Wjets', 'top', 'WZ', 'ZZ', 'WW')
DATA_SAMPLES = ('DATA',)
BTAG_WPS = {'loose': 0.0246, 'medium': 0.1272, 'tight': 0.4648}
BTAG_BRANCH = 'Jet_btagUParTAK4B'
TRIGGERS = (
    'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL',
    'HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ',
    'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ',
    'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8',
    'HLT_IsoMu24',
    'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL',
    'HLT_Ele30_WPTight_Gsf',
)
BCATS = {'incl': None, 'bveto': ('zero', 20.), 'btag': ('one', 30.)}
DEFAULT_PT = '10,15,20,25,30,35,45,65,100'
DEFAULT_ETA = '-2.5,-2.0,-1.5,-1.0,-0.5,0,0.5,1.0,1.5,2.0,2.5'
REGIONS = ('1l', 'ss_sf', 'ss_df', 'dy', 'top')

# Control-plot variables. 'pt' and 'eta' take the measurement binning, so a
# control plot is binned exactly like the map it validates; the rest have their
# own edges here. mll is skipped in the 1-lepton region, where the branch is a
# placeholder and would pile up in the first bin.
# Legend groups of the control plots, stacked bottom to top in this order.
# Anything not listed falls into 'other', so a sample added to MC_SAMPLES shows
# up in the plots instead of disappearing from the stack.
MC_GROUPS = {
    'DY': ('DY',),
    'top': ('top',),
    'W+jets': ('Wjets',),
    'other': ('WZ', 'ZZ', 'WW'),
}
GROUP_COLOURS = {
    'DY': '#5790fc',
    'top': '#f89c20',
    'W+jets': '#64c364',
    'other': '#9c9ca1',
}
# Default control variables. pT and eta of each selected lepton is what a
# control plot is for; the rest are available through --ctrl-var.
DEFAULT_CTRL_VARS = ('pt', 'eta')
CTRL_VARS = {
    'pt':  (None, r'lepton $p_{T}$ [GeV]'),
    'eta': (None, r'lepton $\eta$'),
    'mll': ((0., 200., 40), r'$m_{\ell\ell}$ [GeV]'),
    'met': ((0., 120., 24), r'PuppiMET [GeV]'),
    'mt0': ((0., 150., 30), r'$m_{T}(\ell_{0})$ [GeV]'),
}
# Control plots are made for these regions only, and with no b-category split:
# the top CR already requires a b-tag, so crossing it with 'bveto' is empty by
# construction and crossing it with 'btag' just repeats the region. The b
# categories belong to the fake-rate maps, not here.
CTRL_REGIONS = ('1l', 'dy', 'top')


def ctrl_bcat_for(chan, requested):
    """The b-category a control region is plotted in.

    --ctrl-bcat applies to the QCD and DY regions, where asking for a b veto is
    a real choice. The top CR requires a b-tag by definition, so it is always
    plotted inclusively: 'bveto' there is empty by construction and 'btag'
    repeats the region's own cut.
    """
    return 'incl' if chan == 'top' else requested
REGION_LABELS = {
    '1l': 'QCD FR region (1 lepton)',
    'ss_sf': 'same-sign same-flavour',
    'ss_df': 'same-sign different-flavour',
    'dy': 'DY CR (OS SF, Z peak)',
    'top': 'top CR (OS DF, b-tagged)',
}


def ctrl_binning(var, flav, cfg):
    """Bin edges of a control variable, shared by the filling and the plotting
    so the two can never disagree."""
    if var == 'pt':
        return np.asarray(cfg['bins'][flav][0], dtype=float)
    if var == 'eta':
        return np.asarray(cfg['bins'][flav][1], dtype=float)
    lo, hi, nbins = CTRL_VARS[var][0]
    return np.linspace(lo, hi, nbins + 1)


def split_xrootd(url):
    host, _, path = url[len('root://'):].partition('/')
    return host, '/' + path.lstrip('/')


def list_snapshots(directory):
    if not directory.startswith('root://'):
        return sorted(glob.glob(os.path.join(directory, PREFIX + '*.root')))
    if not shutil.which('xrdfs'):
        raise RuntimeError('xrdfs is required for root:// directory listing')
    host, path = split_xrootd(directory)
    p = subprocess.run(['xrdfs', host, 'ls', path], capture_output=True,
                       text=True, timeout=600)
    if p.returncode:
        raise RuntimeError(f'xrdfs failed: {p.stderr}')
    return sorted(f'root://{host}/{line.strip()}' for line in p.stdout.splitlines()
                  if line.strip().endswith('.root') and
                  os.path.basename(line.strip()).startswith(PREFIX))


def sample_of(path):
    name = os.path.basename(path)
    if not name.startswith(PREFIX):
        return None, None
    suffix = name[len(PREFIX):]
    for s in sorted(DATA_SAMPLES + MC_SAMPLES, key=len, reverse=True):
        if suffix.startswith(s + '_'):
            return s, s in DATA_SAMPLES
    return None, None


def pad2(arr, fill=0):
    import awkward as ak
    return ak.to_numpy(ak.fill_none(ak.pad_none(arr, 2, clip=True), fill, axis=1))


def hist2(x, y, w, xb, yb):
    return np.histogram2d(x, y, bins=(xb, yb), weights=w)[0]


def hist1(x, w, bins):
    return np.histogram(x, bins=bins, weights=w)[0]


def map_definitions(ele_wps, mu_wps, bcats):
    out = []
    for flav, wps, tag, sf in (('ele', ele_wps, 'Ele', 'ee'),
                                ('mu', mu_wps, 'Muon', 'mumu')):
        for wp in wps:
            for bcat in bcats:
                out.extend([
                    (f'{tag}FR_1l_{bcat}', flav, 0, 'FR', '1l', wp, bcat),
                    (f'{tag}FR_{sf}_lep0_{bcat}', flav, 0, 'FR', 'ss_sf', wp, bcat),
                    (f'{tag}FR_{sf}_lep1_{bcat}', flav, 1, 'FR', 'ss_sf', wp, bcat),
                    (f'{tag}FR_emu_lep0_{bcat}', flav, 0, 'FR', 'ss_df', wp, bcat),
                    (f'{tag}FR_emu_lep1_{bcat}', flav, 1, 'FR', 'ss_df', wp, bcat),
                    (f'{tag}PR_{sf}_lep0_{bcat}', flav, 0, 'PR', 'dy', wp, bcat),
                    (f'{tag}PR_{sf}_lep1_{bcat}', flav, 1, 'PR', 'dy', wp, bcat),
                ])
    return out


def spread(seq, keep):
    """`keep` elements of `seq`, evenly spaced, first and last included.

    Evenly spaced and not seq[:keep]: the file list is sorted by name, so a head
    cut lands inside a single dataset (all of DATA_EGamma0, no MC at all), while
    a spread covers every dataset and era the sample is made of.
    """
    if keep >= len(seq) or keep <= 0:
        return list(seq)
    if keep == 1:
        return [seq[0]]
    step = (len(seq) - 1) / (keep - 1)
    return [seq[round(i * step)] for i in range(keep)]


def count_entries(paths, workers):
    """num_entries per file, read from the TTree header only.

    Cheap compared with reading the branches -- a few kB per file -- but not
    free over xrootd, which is why it runs only when something was subsampled.
    A file that cannot be read returns None and the caller falls back.
    """
    import uproot

    def one(path):
        try:
            with uproot.open(f'{path}:{TREE}') as t:
                return path, t.num_entries
        except Exception:
            return path, None

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        return dict(pool.map(one, paths))


def select_files(files, fraction, data_fraction, cap, workers):
    """Pick the files to read per sample and the weight scale for each.

    Returns (payload_files, report). The scale is entries(all)/entries(kept)
    when the headers are readable and the file-count ratio otherwise, computed
    per sample so a fraction applied to DY does not touch top.
    """
    by_sample = defaultdict(list)
    unknown = []
    for path in files:
        sample, is_data = sample_of(path)
        if sample is None:
            # kept, not dropped: process_file reports it, and that report is how
            # a sample missing from MC_SAMPLES gets noticed.
            unknown.append(path)
            continue
        by_sample[(sample, is_data)].append(path)
    kept, report, subsampled = {}, [], False
    for (sample, is_data), paths in sorted(by_sample.items()):
        frac = data_fraction if is_data else fraction
        keep = len(paths)
        if 0. < frac < 1.:
            keep = max(1, round(len(paths) * frac))
        if cap:
            keep = min(keep, cap)
        chosen = spread(paths, keep)
        kept[(sample, is_data)] = (paths, chosen)
        if len(chosen) < len(paths):
            subsampled = True
    if not subsampled:
        return [(p, 1.) for p in files], ['Full sample: every file, scale 1']
    for (sample, is_data), (paths, chosen) in sorted(kept.items()):
        scale, how = 1., 'all files'
        if len(chosen) < len(paths):
            entries = count_entries(paths, workers)
            total = sum(v for v in entries.values() if v is not None)
            used = sum(entries[p] for p in chosen if entries[p] is not None)
            if used > 0 and total > 0 and all(entries[p] is not None for p in paths):
                scale, how = total / used, f'{total} -> {used} entries'
            elif used > 0 and total > 0:
                scale = total / used
                how = f'{total} -> {used} entries, some headers unreadable'
            else:
                scale = len(paths) / len(chosen)
                how = f'{len(paths)} -> {len(chosen)} files (no entry counts)'
        kept[(sample, is_data)] = (chosen, scale)
        report.append(f'  {sample:6s} {len(chosen):4d}/{len(paths):4d} files  '
                      f'scale {scale:7.3f}  ({how})')
    payload_files = [(p, scale) for _, (chosen, scale) in sorted(kept.items())
                     for p in chosen]
    payload_files += [(p, 1.) for p in unknown]
    return payload_files, report


def process_file(payload):
    path, cfg, scale = payload
    import awkward as ak
    import uproot
    sample, is_data = sample_of(path)
    if sample is None:
        return {}, [f'{path}: unknown sample, skipped']
    cols = ['nLepSel', 'SelLep_pt', 'SelLep_eta', 'SelLep_pdgId',
            'isSS', 'isEE', 'isOS', 'isSF', 'mll', 'mt_l0', 'PuppiMET_pt',
            'CleanJet_pt', 'CleanJet_eta', 'CleanJet_jetIdx', BTAG_BRANCH]
    cols += [f'Lepton_isTightElectron_{wp}' for wp in cfg['ele_wps']]
    cols += [f'Lepton_isTightMuon_{wp}' for wp in cfg['mu_wps']]
    cols += [c for c in (cfg['loose_ele'], cfg['loose_mu']) if c]
    cols += ['METFilter_DATA'] if is_data else ['XSWeight', 'METFilter_Common',
                                                'SelLep_promptgenmatched']
    cols = list(dict.fromkeys(cols))
    error = None
    for attempt in range(cfg['retries'] + 1):
        if attempt:
            # EOS I/O errors are usually transient, and an immediate retry hits
            # the same unhappy disk server. Back off before trying again.
            time.sleep(2 ** attempt)
        try:
            with uproot.open(f'{path}:{TREE}') as tree:
                have = set(tree.keys())
                missing = [c for c in cols if c not in have]
                if missing:
                    return {}, [f'{path}: missing {missing}; skipped']
                thave = [c for c in TRIGGERS if c in have]
                if not thave:
                    return {}, [f'{path}: no trigger branches; skipped']
                tmissing = [c for c in TRIGGERS if c not in have]
                a = tree.arrays(cols + thave, library='ak')
            break
        except Exception as exc:
            error = exc
    else:
        return {}, [f'{UNREADABLE} {path}: {error}']
    messages = ([f'{os.path.basename(path)}: absent trigger paths {tmissing}']
                if tmissing else [])
    n = len(a['nLepSel'])
    if not n:
        return {}, messages
    nlep = ak.to_numpy(a['nLepSel']).astype(int)
    pt = pad2(a['SelLep_pt'], np.nan).astype(float)
    eta = pad2(a['SelLep_eta'], np.nan).astype(float)  # SIGNED eta
    pdg = np.abs(pad2(a['SelLep_pdgId']).astype(int))
    # scale != 1 only when this sample was subsampled: it is
    # entries(all files) / entries(files read), so the sum of weights estimates
    # the full sample.  Unbiased, but the statistical error of the subtraction
    # grows as sqrt(scale) -- see the warning main() prints.
    weight = scale * (
        ak.to_numpy(a['METFilter_DATA']).astype(float) if is_data else
        ak.to_numpy(a['XSWeight']).astype(float) *
        ak.to_numpy(a['METFilter_Common']).astype(float) * cfg['lumi'])
    fired = np.zeros(n, dtype=bool)
    for trigger in thave:
        fired |= ak.to_numpy(a[trigger]).astype(bool)
    # Safe take for CleanJet_jetIdx == -1: such jets must not be b-tagged.
    # int64 is not optional: CleanJet_jetIdx is ULong64_t, and uint64 against
    # the int64 literal of ak.where promotes to float64 -- which awkward then
    # refuses as an index.  Casting first also makes the >= 0 test mean what it
    # says instead of being vacuously true on an unsigned type.
    jet_idx = ak.values_astype(a['CleanJet_jetIdx'], np.int64)
    valid_idx = (jet_idx >= 0) & (jet_idx < ak.num(a[BTAG_BRANCH], axis=1))
    safe_idx = ak.values_astype(ak.where(valid_idx, jet_idx, 0), np.int64)
    padded_btag = ak.pad_none(a[BTAG_BRANCH], 1, axis=1)
    jet_btag = ak.fill_none(padded_btag[safe_idx], -np.inf)
    tagged = (valid_idx & (np.abs(a['CleanJet_eta']) < 2.5) &
              (jet_btag > cfg['btag_thr']))
    nbtags = {thr: ak.to_numpy(ak.sum(tagged & (a['CleanJet_pt'] > thr), axis=1))
              for thr in (20., 30.)}
    bmask = {'incl': np.ones(n, dtype=bool),
             'bveto': nbtags[20.] == 0, 'btag': nbtags[30.] >= 1}
    isss = ak.to_numpy(a['isSS']).astype(bool)
    isee = ak.to_numpy(a['isEE']).astype(bool)
    isos = ak.to_numpy(a['isOS']).astype(bool)
    issf = ak.to_numpy(a['isSF']).astype(bool)
    mll = ak.to_numpy(a['mll']).astype(float)
    met = ak.to_numpy(a['PuppiMET_pt']).astype(float)
    mt0 = ak.to_numpy(a['mt_l0']).astype(float)
    inz = np.abs(mll - 91.2) < 15.
    region = {
        '1l': (nlep == 1) & (met < 30.) & (mt0 < 30.),
        'ss_sf': (nlep == 2) & isss & issf & (mll > 12.) & ~(isee & inz),
        'ss_df': (nlep == 2) & isss & ~issf & (mll > 12.),
        'dy': (nlep == 2) & isos & issf & inz,
        'top': (nlep == 2) & isos & ~issf & (mll > cfg['top_mll_min']) &
               (met > cfg['top_met_min']) & (nbtags[30.] >= cfg['top_min_btags']),
    }
    region = {r: mask & fired for r, mask in region.items()}
    prompt = (pad2(a['SelLep_promptgenmatched']).astype(bool)
              if not is_data else None)
    loose = {}
    for flav, branch in (('ele', cfg['loose_ele']), ('mu', cfg['loose_mu'])):
        loose[flav] = (pad2(a[branch]).astype(bool) if branch else
                       np.ones_like(pt, dtype=bool))
    # The first nLepSel entries of Lepton are the SelLep prefix.  Tight IDs
    # are read from Lepton and therefore index-aligned with SelLep here.
    tight = {}
    for flav, wps, prefix in (('ele', cfg['ele_wps'], 'Lepton_isTightElectron_'),
                               ('mu', cfg['mu_wps'], 'Lepton_isTightMuon_')):
        for wp in wps:
            tight[flav, wp] = pad2(a[prefix + wp]).astype(bool)
    acc = {}
    # Histograms for maps: (mapname, tight/rest, data/mc, sumw/sumw2)
    for name, flav, i, kind, chan, wp, bcat in cfg['maps']:
        sel = (region[chan] & bmask[bcat] & (nlep > i) &
               (pdg[:, i] == (11 if flav == 'ele' else 13)) &
               loose[flav][:, i] & np.isfinite(pt[:, i]) &
               np.isfinite(eta[:, i]) & np.isfinite(weight) & (weight != 0))
        xb, yb = cfg['bins'][flav]
        sel &= (eta[:, i] >= yb[0]) & (eta[:, i] < yb[-1])
        if not np.any(sel):
            continue
        x = np.clip(pt[sel, i], xb[0], np.nextafter(xb[-1], -np.inf))
        y, w = eta[sel, i], weight[sel]
        t = tight[flav, wp][sel, i]
        # Two MC series, not one. 'mc' is the prompt component, which is what
        # the fake rate subtracts; 'mcnp' is the nonprompt one, which is the
        # contamination the prompt rate has to subtract instead. Keeping both
        # means neither measurement needs its own pass.
        if is_data:
            series = [('data', np.ones(len(w), dtype=bool))]
        else:
            series = [('mc', prompt[sel, i]), ('mcnp', ~prompt[sel, i])]
        for part, partmask in (('tight', t), ('rest', ~t)):
            for source, srcmask in series:
                mask = partmask & srcmask
                if not mask.any():
                    continue
                for moment, ww in (('sumw', w[mask]), ('sumw2', w[mask]**2)):
                    acc[('map', name, part, source, moment)] = hist2(
                        x[mask], y[mask], ww, xb, yb)
    # Control plots: all MC components (prompt AND nonprompt), and data.
    # Loose = tight + rest, both plotted independently; inclusive in signed eta.
    # For ss/dy/top, select each lepton by its actual flavour and position.
    for wp in cfg['ctrl_wps']:
        for flav in ('ele', 'mu'):
            if wp not in (cfg['ele_wps'] if flav == 'ele' else cfg['mu_wps']):
                continue
            for chan in cfg['ctrl_regions']:
                for bcat in (ctrl_bcat_for(chan, cfg['ctrl_bcat']),):
                    for i in (0, 1):
                        if chan == '1l' and i == 1:
                            continue
                        sel = (region[chan] & bmask[bcat] & (nlep > i) &
                               (pdg[:, i] == (11 if flav == 'ele' else 13)) &
                               loose[flav][:, i] & np.isfinite(pt[:, i]) &
                               np.isfinite(eta[:, i]) & np.isfinite(weight) &
                               (weight != 0))
                        xb, yb = cfg['bins'][flav]
                        sel &= (eta[:, i] >= yb[0]) & (eta[:, i] < yb[-1])
                        if not np.any(sel):
                            continue
                        w = weight[sel]
                        t = tight[flav, wp][sel, i]
                        quantity = {'pt': pt[sel, i], 'eta': eta[sel, i],
                                    'mll': mll[sel], 'met': met[sel],
                                    'mt0': mt0[sel]}
                        # Split MC into prompt and nonprompt for composition.
                        labels = [('data', np.ones(len(w), dtype=bool))] if is_data else [
                            (sample + '_prompt', prompt[sel, i]),
                            (sample + '_nonprompt', ~prompt[sel, i])]
                        # pT and eta are kept as ONE 2D histogram and
                        # projected at plot time, not as two 1D ones. A scale
                        # factor that is a function of (pT, eta) can be applied
                        # bin by bin to this and then projected; from a 1D pT
                        # projection the eta dependence is already gone and the
                        # reweighting is no longer possible.
                        xpt = np.clip(pt[sel, i], xb[0],
                                      np.nextafter(xb[-1], -np.inf))
                        yeta = eta[sel, i]
                        for component, component_mask in labels:
                            for part, partmask in (
                                    ('loose', np.ones(len(w), dtype=bool)),
                                    ('tight', t)):
                                mask = component_mask & partmask
                                if not mask.any():
                                    continue
                                for moment, ww in (('sumw', w[mask]),
                                                   ('sumw2', w[mask]**2)):
                                    acc[('plot2', wp, chan, bcat, flav, i, part,
                                         component, moment)] = hist2(
                                        xpt[mask], yeta[mask], ww, xb, yb)
                        for var in cfg['ctrl_vars']:
                            if var in ('pt', 'eta'):
                                continue          # covered by the 2D above
                            if var == 'mll' and chan == '1l':
                                continue
                            edges = ctrl_binning(var, flav, cfg)
                            # clipped, not dropped: an overflow event is a real
                            # event of the region and belongs in the last bin,
                            # or data and MC lose different events
                            x = np.clip(quantity[var], edges[0],
                                        np.nextafter(edges[-1], -np.inf))
                            finite = np.isfinite(x)
                            for component, component_mask in labels:
                                for part, partmask in (
                                        ('loose', np.ones(len(w), dtype=bool)),
                                        ('tight', t)):
                                    mask = component_mask & partmask & finite
                                    if not mask.any():
                                        continue
                                    for moment, ww in (('sumw', w[mask]),
                                                       ('sumw2', w[mask]**2)):
                                        key = ('plot', wp, chan, bcat, flav, i,
                                               var, part, component, moment)
                                        acc[key] = hist1(x[mask], ww, edges)
    # ---- ingredients of the DY scale factors -------------------------------
    # data over ALL MC, in (pT, eta), per working point, flavour and lepton
    # slot. No prompt requirement: this is a data/MC agreement correction, not
    # a fake subtraction, so every MC event of the region counts. Kept for
    # every WP, not only the plotted ones, so the same factors can later
    # reweight the MC of the fake-rate maps.
    for wp in cfg['all_wps']:
        for flav in ('ele', 'mu'):
            if wp not in (cfg['ele_wps'] if flav == 'ele' else cfg['mu_wps']):
                continue
            for i in (0, 1):
                sel = (region['dy'] & bmask[cfg['sf_bcat']] & (nlep > i) &
                       (pdg[:, i] == (11 if flav == 'ele' else 13)) &
                       loose[flav][:, i] & np.isfinite(pt[:, i]) &
                       np.isfinite(eta[:, i]) & np.isfinite(weight) &
                       (weight != 0))
                xb, yb = cfg['bins'][flav]
                sel &= (eta[:, i] >= yb[0]) & (eta[:, i] < yb[-1])
                if not np.any(sel):
                    continue
                x = np.clip(pt[sel, i], xb[0], np.nextafter(xb[-1], -np.inf))
                y, w = eta[sel, i], weight[sel]
                t = tight[flav, wp][sel, i]
                for part, mask in (('tight', t), ('rest', ~t)):
                    if not mask.any():
                        continue
                    for moment, ww in (('sumw', w[mask]),
                                       ('sumw2', w[mask]**2)):
                        acc[('sf', wp, flav, i, part,
                             'data' if is_data else 'mc', moment)] = hist2(
                            x[mask], y[mask], ww, xb, yb)
    return acc, messages


def ratio(Td, Td2, Rd, Rd2, Tm, Tm2, Rm, Rm2, subtract):
    N, vN = (Td - Tm, Td2 + Tm2) if subtract else (Td, Td2)
    R, vR = (Rd - Rm, Rd2 + Rm2) if subtract else (Rd, Rd2)
    D = N + R
    f, e = np.zeros_like(D), np.zeros_like(D)
    ok = D > 0
    f[ok] = N[ok] / D[ok]
    e[ok] = np.sqrt(np.maximum((R[ok]**2*vN[ok] + N[ok]**2*vR[ok]) /
                                D[ok]**4, 0.))
    return f, e, ok


def write_root(path, main_name, f, e, ingredients, xb, yb):
    import ROOT
    from array import array
    ROOT.gROOT.SetBatch(True)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file = ROOT.TFile.Open(path, 'RECREATE')
    if not file or file.IsZombie():
        raise RuntimeError(f'Cannot create {path}')
    for name, (values, errors) in [(main_name, (f, e))] + list(ingredients.items()):
        h = ROOT.TH2F(name, name, len(xb)-1, array('d', xb),
                      len(yb)-1, array('d', yb))
        h.GetXaxis().SetTitle('p_{T} [GeV]')
        h.GetYaxis().SetTitle('#eta')
        for ix in range(len(xb)-1):
            for iy in range(len(yb)-1):
                h.SetBinContent(ix+1, iy+1, float(values[ix, iy]))
                h.SetBinError(ix+1, iy+1, float(errors[ix, iy]))
        h.Write()
    file.Close()


def group_of(sample):
    """Legend group a sample belongs to. Anything unlisted lands in 'other'."""
    for group, members in MC_GROUPS.items():
        if sample in members:
            return group
    return 'other'


def compute_sf(total, cfg):
    """Data over MC in the DY CR, in (pT, eta), per WP, flavour, lepton slot
    and selection level.

    Returns {(wp, flav, i, part): (sf, err)} for part in tight / rest / loose.
    'rest' is loose-but-not-tight, the denominator ingredient the subtraction
    actually uses; 'loose' is tight + rest, which is what one looks at.

    A bin where either side is empty is left at 1 and counted. No MC means
    there is nothing to correct; no data means the ratio is not measured, and
    taking it as 0 would silently delete that MC instead of saying so.
    """
    out, empty = {}, defaultdict(int)
    for wp in cfg['all_wps']:
        for flav in ('ele', 'mu'):
            if wp not in (cfg['ele_wps'] if flav == 'ele' else cfg['mu_wps']):
                continue
            shape = (len(cfg['bins'][flav][0]) - 1,
                     len(cfg['bins'][flav][1]) - 1)
            for i in (0, 1):
                def get(part, source, moment):
                    return total.get(('sf', wp, flav, i, part, source, moment),
                                     np.zeros(shape))
                pieces = {}
                for part in ('tight', 'rest'):
                    pieces[part] = tuple(get(part, src, mom)
                                         for src in ('data', 'mc')
                                         for mom in ('sumw', 'sumw2'))
                tdw, tdw2, tmw, tmw2 = pieces['tight']
                rdw, rdw2, rmw, rmw2 = pieces['rest']
                for part, (dw, dw2, mw, mw2) in (
                        ('tight', (tdw, tdw2, tmw, tmw2)),
                        ('rest', (rdw, rdw2, rmw, rmw2)),
                        ('loose', (tdw + rdw, tdw2 + rdw2,
                                   tmw + rmw, tmw2 + rmw2))):
                    sf = np.ones(shape)
                    err = np.zeros(shape)
                    ok = (mw > 0) & (dw > 0)
                    sf[ok] = dw[ok] / mw[ok]
                    # ratio of two independent sums of weights
                    err[ok] = sf[ok] * np.sqrt(dw2[ok] / dw[ok] ** 2
                                               + mw2[ok] / mw[ok] ** 2)
                    empty[(wp, flav, i, part)] = int((~ok).sum())
                    out[(wp, flav, i, part)] = (sf, err)
    return out, empty


def plot_rate_map(values, xb, yb, title, path, vmax=None):
    """2D colz view of one rate map. Scale fixed from 0 to vmax so the three
    variants of the same map can be compared by eye."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    top = vmax if vmax else max(float(np.max(values)), 1e-6)
    mesh = ax.pcolormesh(np.asarray(xb), np.asarray(yb), values.T,
                         cmap='viridis', vmin=0., vmax=top)
    bar = fig.colorbar(mesh, ax=ax)
    bar.set_label('rate')
    for ix in range(values.shape[0]):
        for iy in range(values.shape[1]):
            ax.text((xb[ix] + xb[ix + 1]) / 2, (yb[iy] + yb[iy + 1]) / 2,
                    f'{values[ix, iy]:.3f}', ha='center', va='center',
                    fontsize=5.5, color='white')
    ax.set_xlabel(r'lepton $p_{T}$ [GeV]')
    ax.set_ylabel(r'lepton $\eta$')
    ax.set_title(title, fontsize=9)
    fig.subplots_adjust(left=.10, right=1.0, top=.92, bottom=.11)
    fig.savefig(path, dpi=140)
    plt.close(fig)


def compare_variants(comparisons):
    """How far apart the three versions of each map are.

    The question this answers is whether the EWK subtraction, and then the DY
    reweighting of that subtraction, move the rate by an amount worth caring
    about. Quoted as an absolute difference in the rate, because the rate is
    itself a fraction: a 0.01 shift on f = 0.15 is what matters, not a
    percentage of a percentage.
    """
    if not comparisons:
        return []
    lines = ['',
             'Effect of the subtraction and of the DY reweighting, as the '
             'largest and median |delta f| over the measured bins:',
             f'  {"map":34s} {"raw->EWK":>18s} {"EWK->EWKcorr":>18s}']
    worst = 0.
    for name, wp, ok, raw, ewk, corr in comparisons:
        if not ok.any():
            continue
        d1 = np.abs(ewk[ok] - raw[ok])
        d2 = np.abs(corr[ok] - ewk[ok])
        worst = max(worst, float(d2.max()))
        lines.append(f'  {name:34s} '
                     f'{d1.max():7.4f} ({np.median(d1):6.4f}) '
                     f'{d2.max():7.4f} ({np.median(d2):6.4f})')
    lines.append(f'  largest effect of the reweighting on any bin of any map: '
                 f'{worst:.4f} in absolute rate')
    return lines


def report_sf(scale_factors, empty, wps):
    """One line per map: how large the correction actually is."""
    lines = ['DY scale factors (data/MC), applied to every MC process:']
    for key in sorted(scale_factors):
        wp, flav, i, part = key
        if wp not in wps or part == 'rest':
            continue
        sf = scale_factors[key][0]
        measured = sf[sf != 1.]
        if not measured.size:
            lines.append(f'  {flav} lep{i + 1} {part:5s}: nothing measured')
            continue
        lines.append(
            f'  {flav} lep{i + 1} {part:5s}: median {np.median(measured):.3f}, '
            f'range [{measured.min():.3f}, {measured.max():.3f}], '
            f'{measured.size} bins measured, {empty[key]} left at 1')
    return lines


def plot_sf_map(plt, sf, err, xb, yb, title, path, empty):
    """2D colz view of one scale-factor map."""
    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    # symmetric around 1: the question is which way a bin pulls, and by how
    # much, so the colour scale must not hide the sign
    # 95th percentile and not the maximum: one wild bin must not flatten the
    # colour scale over the bins that carry the information
    measured = sf[sf != 1.]
    spread = (np.percentile(np.abs(measured - 1.), 95)
              if measured.size else 0.)
    span = max(0.05, min(spread, 1.))
    mesh = ax.pcolormesh(np.asarray(xb), np.asarray(yb), sf.T,
                         cmap='RdBu_r', vmin=1 - span, vmax=1 + span)
    bar = fig.colorbar(mesh, ax=ax)
    bar.set_label('Data / MC')
    for ix in range(sf.shape[0]):
        for iy in range(sf.shape[1]):
            ax.text((xb[ix] + xb[ix + 1]) / 2, (yb[iy] + yb[iy + 1]) / 2,
                    f'{sf[ix, iy]:.2f}\n±{err[ix, iy]:.2f}',
                    ha='center', va='center', fontsize=5.5)
    ax.set_xlabel(r'lepton $p_{T}$ [GeV]')
    ax.set_ylabel(r'lepton $\eta$')
    ax.set_title(title + (f'   [{empty} bins not measured (no data or no MC), '
                          f'left at 1]' if empty else ''), fontsize=9)
    fig.subplots_adjust(left=.10, right=1.0, top=.92, bottom=.11)
    fig.savefig(path, dpi=140)
    plt.close(fig)


def make_plots(total, cfg, base, scale_factors, empty_bins):
    """One PNG per region, lepton slot, variable and loose/tight.

    Deliberately one file per plot rather than a multi-page PDF: these are
    looked at one at a time, and a file name that says what it holds beats
    paging through a document.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    os.makedirs(base, exist_ok=True)
    written = []
    for (wp, flav, i, part), (sf, err) in sorted(scale_factors.items()):
        if wp not in cfg['ctrl_wps'] or part == 'rest':
            continue
        xb, yb = cfg['bins'][flav]
        path = os.path.join(base, wp, f'SF_dy_{flav}_lep{i}_{part}.png')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        plot_sf_map(plt, sf, err, xb, yb,
                    f'DY CR scale factor | {flav} lepton {i + 1} | {part}\n{wp}',
                    path, empty_bins[(wp, flav, i, part)])
        written.append(path)
    for wp in cfg['ctrl_wps']:
        for chan in cfg['ctrl_regions']:
            bcat = ctrl_bcat_for(chan, cfg['ctrl_bcat'])
            for flav in ('ele', 'mu'):
                if wp not in (cfg['ele_wps'] if flav == 'ele' else cfg['mu_wps']):
                    continue
                for i in range(1 if chan == '1l' else 2):
                    xb, yb = cfg['bins'][flav]
                    shape2 = (len(xb) - 1, len(yb) - 1)
                    for var in cfg['ctrl_vars']:
                        if var == 'mll' and chan == '1l':
                            continue
                        twod = var in ('pt', 'eta')
                        edges = ctrl_binning(var, flav, cfg)
                        # The (pT, eta) histogram is stored whole and projected
                        # here, which is what makes the reweighted version
                        # possible; the other variables are 1D and are drawn
                        # unweighted, since the factor is not a function of them.
                        axis = 1 if var == 'pt' else 0

                        def grab(component, part, moment, weights=None):
                            if not twod:
                                return total.get(
                                    ('plot', wp, chan, bcat, flav, i, var, part,
                                     component, moment),
                                    np.zeros(len(edges) - 1))
                            h = total.get(('plot2', wp, chan, bcat, flav, i,
                                           part, component, moment),
                                          np.zeros(shape2))
                            if weights is not None:
                                power = 2 if moment == 'sumw2' else 1
                                h = h * weights ** power
                            return h.sum(axis=axis)

                        for part in ('loose', 'tight'):
                            data = grab('data', part, 'sumw')
                            data2 = grab('data', part, 'sumw2')
                            # Pre-reweighting always; post-reweighting as well
                            # when a factor exists for this lepton and level.
                            passes = [('', None)]
                            key = (wp, flav, i, part)
                            if twod and key in scale_factors:
                                passes.append(('_sf', scale_factors[key][0]))
                            for suffix, sfmap in passes:
                                # prompt and nonprompt are summed back together:
                                # the split is for the fake-rate maps, a control
                                # plot wants the processes a reader recognises
                                stack = []
                                for group in MC_GROUPS:
                                    y = np.zeros(len(edges) - 1)
                                    y2 = np.zeros(len(edges) - 1)
                                    for sample in MC_SAMPLES:
                                        if group_of(sample) != group:
                                            continue
                                        for origin in ('prompt', 'nonprompt'):
                                            label = f'{sample}_{origin}'
                                            y = y + grab(label, part, 'sumw',
                                                         sfmap)
                                            y2 = y2 + grab(label, part, 'sumw2',
                                                           sfmap)
                                    if np.any(y):
                                        stack.append((group, y, y2))
                                if not np.any(data) and not stack:
                                    continue
                                tag = '' if bcat == 'incl' else f'_{bcat}'
                                name = (f'{chan}{tag}_{flav}_lep{i}_{var}_'
                                        f'{part}{suffix}.png')
                                path = os.path.join(base, wp, name)
                                os.makedirs(os.path.dirname(path), exist_ok=True)
                                fig = one_control_plot(
                                    plt, edges, data, data2, stack,
                                    xlabel=CTRL_VARS[var][1].replace(
                                        'lepton', f'lepton {i + 1}'),
                                    lumi=cfg['lumi'],
                                    header=f'{REGION_LABELS[chan]}'
                                           + ('' if bcat == 'incl'
                                              else f', {bcat}')
                                           + f' | lepton {i + 1} ({flav}) | '
                                           f'{part}',
                                    # on the second line, where it cannot run
                                    # under the legend
                                    wp=wp + ('    [MC x DY CR scale factors]'
                                             if suffix else ''))
                                fig.savefig(path, dpi=140)
                                plt.close(fig)
                                written.append(path)
    return len(written)


def one_control_plot(plt, edges, data, data2, stack, xlabel, lumi, header, wp):
    """CMS-style data/MC comparison with a ratio panel. Returns the figure."""
    fig, (ax, rax) = plt.subplots(
        2, 1, figsize=(7., 6.6), sharex=True,
        gridspec_kw={'height_ratios': [3, 1], 'hspace': .06})
    width = np.diff(edges)
    centers = (edges[:-1] + edges[1:]) / 2
    total_mc = np.zeros(len(width))
    total_mc2 = np.zeros(len(width))
    # Stacking signed MC is not meaningful if a component goes negative, which
    # a subsampled or badly normalised set can do: fall back to outlines.
    can_stack = all(np.all(y >= 0) for _, y, _ in stack)
    bottom = np.zeros(len(width))
    for label, y, y2 in stack:
        if can_stack:
            ax.bar(edges[:-1], y, width=width, bottom=bottom, align='edge',
                   color=GROUP_COLOURS.get(label, '#9e9e9e'),
                   edgecolor='black', linewidth=.4, label=label)
            bottom = bottom + y
        else:
            ax.stairs(y, edges, label=label,
                      color=GROUP_COLOURS.get(label, '#9e9e9e'))
        total_mc = total_mc + y
        total_mc2 = total_mc2 + y2
    if stack and can_stack:
        ax.bar(edges[:-1], 2 * np.sqrt(total_mc2), width=width,
               bottom=total_mc - np.sqrt(total_mc2), align='edge',
               facecolor='none', edgecolor='black', hatch='/////',
               linewidth=0, label='MC stat')
    shown = data > 0
    ax.errorbar(centers[shown], data[shown], yerr=np.sqrt(data2[shown]),
                fmt='ko', markersize=4.5, label='Data', zorder=5)
    ax.set_ylabel('Events / bin')
    # Zoom on the bins that hold something. The binning is global across
    # regions, so a variable would otherwise live in a fraction of the axis.
    # Nothing is hidden: bins outside the view are empty in data and in MC.
    filled = np.nonzero((data != 0) | (total_mc != 0))[0]
    if len(filled):
        ax.set_xlim(edges[max(filled[0] - 1, 0)],
                    edges[min(filled[-1] + 2, len(edges) - 1)])
    else:
        ax.set_xlim(edges[0], edges[-1])
    top = max(data.max() if len(data) else 0.,
              total_mc.max() if len(total_mc) else 0.)
    if top > 0:
        ax.set_ylim(0., 1.5 * top)
    ax.legend(fontsize=8, ncol=3, loc='upper right', framealpha=.9)
    ax.grid(alpha=.15)
    ax.text(0., 1.012, 'CMS', transform=ax.transAxes, fontweight='bold',
            fontsize=15, va='bottom')
    ax.text(.125, 1.015, 'Preliminary', transform=ax.transAxes, style='italic',
            fontsize=11, va='bottom')
    ax.text(1., 1.015, f'{lumi:.1f} fb$^{{-1}}$ (13.6 TeV)',
            transform=ax.transAxes, fontsize=10, va='bottom', ha='right')
    ax.text(.03, .955, header + f'\n{wp}', transform=ax.transAxes, fontsize=7.5,
            va='top', ha='left')
    ok = (total_mc > 0) & (data > 0)
    vals = np.full(len(width), np.nan)
    errs = np.full(len(width), np.nan)
    vals[ok] = data[ok] / total_mc[ok]
    errs[ok] = np.sqrt(data2[ok]) / total_mc[ok]
    band = np.zeros(len(width))
    good = total_mc > 0
    band[good] = np.sqrt(total_mc2[good]) / total_mc[good]
    rax.bar(edges[:-1], 2 * band, width=width, bottom=1 - band, align='edge',
            facecolor='none', edgecolor='black', hatch='/////', linewidth=0)
    rlo, rhi = 0., 2.
    inside = ok & (vals >= rlo) & (vals <= rhi)
    rax.errorbar(centers[inside], vals[inside], yerr=errs[inside],
                 fmt='ko', markersize=4.5)
    # A point off the scale is drawn as a triangle at the edge. Dropping it
    # silently would make 'data/MC is 40 here' indistinguishable from 'no data
    # in this bin', which is exactly the case worth seeing.
    for mask, ypos, marker in ((ok & (vals > rhi), rhi, '^'),
                               (ok & (vals < rlo), rlo, 'v')):
        if mask.any():
            rax.plot(centers[mask], np.full(mask.sum(), ypos), marker,
                     color='red', markersize=5.5, clip_on=False)
    rax.axhline(1., color='gray', linestyle='--', linewidth=.8)
    rax.set_ylabel('Data / MC', fontsize=9)
    rax.set_xlabel(xlabel)
    rax.set_ylim(rlo, rhi)
    rax.grid(alpha=.2)
    # explicit margins rather than tight_layout(), which warns on every figure
    # because the shared-x gridspec is not compatible with it
    fig.subplots_adjust(left=.11, right=.97, top=.93, bottom=.09)
    return fig


# ---------------------------------------------------------------------------
# HTCondor: the work is one independent pass per file, so it splits by file.
# A job reads its own list and writes a partial accumulator; --merge sums the
# partials and makes the plots and the maps exactly as a local run would.
# ---------------------------------------------------------------------------
PART_PREFIX = 'part_'
# Prefix of the message a skipped file produces, so the summary can pick those
# out from the other warnings without parsing free text.
UNREADABLE = 'UNREADABLE'


CFG_KEYS_CHECKED = ('ele_wps', 'mu_wps', 'ctrl_wps', 'bcats', 'ctrl_regions',
                    'ctrl_vars', 'ctrl_bcat', 'sf_bcat', 'bins', 'lumi')


def dump_partial(path, acc, problems, cfg, files):
    """Write one job's accumulator and the configuration that produced it.

    pickle, not npz: the keys are tuples of mixed strings and integers, which
    npz cannot represent as archive names. The configuration travels with the
    histograms so --merge needs no option repeated, and so a part produced with
    a different binning is caught instead of being summed into the rest.
    """
    import pickle
    tmp = path + '.tmp'
    with open(tmp, 'wb') as fh:
        pickle.dump({'acc': acc, 'problems': problems, 'cfg': cfg,
                     'files': files}, fh, protocol=4)
    os.replace(tmp, path)          # never leave a half-written part behind


def load_partials(directory):
    """Sum every part file in `directory`. Returns (total, problems, nparts)."""
    import pickle
    total, problems, nparts, cfg = {}, [], 0, None
    seen_files = []
    for path in sorted(glob.glob(os.path.join(directory,
                                              PART_PREFIX + '*.pkl'))):
        with open(path, 'rb') as fh:
            blob = pickle.load(fh)
        if cfg is None:
            cfg = blob['cfg']
        else:
            differ = [k for k in CFG_KEYS_CHECKED
                      if blob['cfg'].get(k) != cfg.get(k)]
            if differ:
                raise SystemExit(
                    f'{os.path.basename(path)} was produced with a different '
                    f'configuration ({", ".join(differ)}); refusing to merge. '
                    f'Resubmit the whole set.')
        nparts += 1
        problems.extend(blob['problems'])
        seen_files.extend(blob.get('files', []))
        for key, value in blob['acc'].items():
            if key in total:
                total[key] += value
            else:
                total[key] = value.copy()
    return total, problems, nparts, cfg, seen_files


def find_credentials():
    """X509 proxy and Kerberos cache to ship with the jobs, if they exist.

    Neither is required: EOS over root://eoscms.cern.ch takes Kerberos, a CMS
    redirector takes the proxy, and a job that needed the missing one fails on
    the node with xrootd's own message.
    """
    out = []
    proxy = os.environ.get('X509_USER_PROXY') or f'/tmp/x509up_u{os.getuid()}'
    if os.path.exists(proxy):
        out.append(('X509_USER_PROXY', proxy))
    cache = os.environ.get('KRB5CCNAME', f'FILE:/tmp/krb5cc_{os.getuid()}')
    if cache.startswith('FILE:'):
        cache = cache[len('FILE:'):]
    elif ':' in cache:
        cache = ''                 # KEYRING/KCM/DIR: no file to transfer
    if cache and os.path.exists(cache):
        out.append(('KRB5CCNAME', cache))
    return out


def write_batch(args, selected, cfg_args):
    """Write the job scripts and the submit file. Returns the submit path."""
    batch = os.path.abspath(os.path.expandvars(args.batch_dir))
    parts = os.path.join(batch, 'parts')
    logs = os.path.join(batch, 'logs')
    for d in (batch, parts, logs):
        os.makedirs(d, exist_ok=True)
    per_job = args.files_per_job
    chunks = [selected[k:k + per_job]
              for k in range(0, len(selected), per_job)]
    # Each line carries the file and its weight scale: the subsampling is
    # decided once here, so a job must not recompute it from what it can see.
    for j, chunk in enumerate(chunks):
        with open(os.path.join(batch, f'filelist_{j}.txt'), 'w') as fh:
            fh.write(''.join(f'{path}\t{scale!r}\n' for path, scale in chunk))
    script = os.path.abspath(__file__)
    creds = find_credentials()
    cred_lines = []
    for var, path in creds:
        base = os.path.basename(path)
        if var == 'KRB5CCNAME':
            # The export is load-bearing: the submit node's KRB5CCNAME points
            # at a path that does not exist on the execute node.
            cred_lines.append(f'export KRB5CCNAME=FILE:$(pwd)/{base}')
            cred_lines.append(f'chmod 600 $(pwd)/{base} 2>/dev/null || true')
        else:
            cred_lines.append(f'export X509_USER_PROXY=$(pwd)/{base}')
    runner = os.path.join(batch, 'run.sh')
    with open(runner, 'w') as fh:
        fh.write('#!/bin/bash\n'
                 'set -e\n'
                 'JOB=$1\n'
                 f'source {args.lcg_view}\n'
                 + ''.join(line + '\n' for line in cred_lines) +
                 f'python3 {os.path.basename(script)} \\\n'
                 f'    --file-list filelist_${{JOB}}.txt \\\n'
                 f'    --dump {PART_PREFIX}${{JOB}}.pkl \\\n'
                 f'    {cfg_args}\n')
    os.chmod(runner, 0o755)
    transfer = [script] + [p for _, p in creds]
    sub = os.path.join(batch, 'submit.sub')
    with open(sub, 'w') as fh:
        fh.write(f"""universe              = vanilla
executable            = {runner}
arguments             = $(job)
output                = {logs}/job_$(job).out
error                 = {logs}/job_$(job).err
log                   = {logs}/condor.log
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files  = {','.join(transfer + [batch + '/filelist_$(job).txt'])}
transfer_output_files = {PART_PREFIX}$(job).pkl
transfer_output_remaps = "{PART_PREFIX}$(job).pkl = {parts}/{PART_PREFIX}$(job).pkl"
+JobFlavour           = "{args.job_flavour}"
request_cpus          = {max(1, args.workers)}
queue job in ({' '.join(str(j) for j in range(len(chunks)))})
""")
    print(f'{len(chunks)} jobs of up to {per_job} files in {batch}')
    if creds:
        print('shipping: ' + ', '.join(f'{v} ({os.path.basename(p)})'
                                       for v, p in creds))
    else:
        print('no proxy and no Kerberos ticket found: shipping neither')
    return sub, len(chunks)


def unreadable_report(problems, files, out_path=None):
    """Per-sample account of the files that could not be read.

    The overall fraction is the wrong number to look at: losing 25 of 1294
    files is 2%, but if 9 of them are one sample's, that sample's
    normalisation is low by its own fraction, and the data/MC ratio moves by
    the difference between the deficits of data and of each process.
    """
    bad = [line.split(' ', 1)[1].split(':')[0] for line in problems
           if line.startswith(UNREADABLE)]
    if not bad:
        return []
    per_sample = defaultdict(int)
    for path in bad:
        sample, _ = sample_of(path)
        per_sample[sample or '(unknown)'] += 1
    totals = defaultdict(int)
    for path in files:
        sample, _ = sample_of(path)
        totals[sample or '(unknown)'] += 1
    lines = [f'{len(bad)} of {len(files)} files could not be read. '
             f'Per sample, which is what biases the normalisation:']
    for sample in sorted(per_sample, key=lambda k: -per_sample[k]):
        n, total = per_sample[sample], totals.get(sample, 0)
        share = f'{100. * n / total:.1f}%' if total else '?'
        lines.append(f'  {sample:12s} {n:4d} of {total:4d}  ({share} of that '
                     f'sample is missing from the histograms)')
    if out_path:
        with open(out_path, 'w') as fh:
            fh.write('\n'.join(sorted(bad)) + '\n')
        lines.append(f'  list written to {out_path}')
    return lines


def check_batch(batch_dir):
    """Which jobs have produced a part. Jobs are counted from the file lists
    written at submit time, so a part that was never produced is reported as
    missing rather than silently left out of the merge."""
    batch = os.path.abspath(os.path.expandvars(batch_dir))
    parts = os.path.join(batch, 'parts')
    jobs = sorted(os.path.basename(f)[len('filelist_'):-len('.txt')]
                  for f in glob.glob(os.path.join(batch, 'filelist_*.txt')))
    done, missing = [], []
    for job in jobs:
        path = os.path.join(parts, f'{PART_PREFIX}{job}.pkl')
        (done if os.path.exists(path) and os.path.getsize(path) else
         missing).append(job)
    return done, missing


def batch_args(args, cfg):
    """The options a job needs, rebuilt as a command line.

    Only what changes the histograms is passed on; the plotting and the map
    writing happen in --merge, on the submit node. The working points come
    from the resolved cfg and never from args: left to discover them, two jobs
    reading different files could end up with different WP lists, and their
    partial accumulators would not line up.
    """
    out = []
    for flag, value, default in (
            ('--lumi', args.lumi, None),
            ('--btag-wp', args.btag_wp, None),
            ('--loose-ele', args.loose_ele, ''),
            ('--loose-mu', args.loose_mu, ''),
            ('--top-met-min', args.top_met_min, None),
            ('--top-mll-min', args.top_mll_min, None),
            ('--top-min-btags', args.top_min_btags, None),
            ('--ctrl-bcat', args.ctrl_bcat, None),
            ('--workers', args.workers, None)):
        if value != default:
            out.append(f'{flag}={value}')
    for flag, values in (('--ele-wp', cfg['ele_wps']),
                         ('--mu-wp', cfg['mu_wps']),
                         ('--bcat', cfg['bcats']),
                         ('--ctrl-wp', cfg['ctrl_wps']),
                         ('--ctrl-region', cfg['ctrl_regions']),
                         ('--ctrl-var', cfg['ctrl_vars'])):
        out.extend(f'{flag}={v}' for v in values)
    for flag, value in (('--pt-bins', args.pt_bins),
                        ('--eta-bins-ele', args.eta_bins_ele),
                        ('--eta-bins-mu', args.eta_bins_mu)):
        # '=' and not a space: an eta binning starts with '-2.5', which
        # argparse would otherwise read as an option name
        out.append(f'{flag}=' + ','.join(repr(float(x)) for x in value))
    return ' \\\n    '.join(out)


def parse_bins(text):
    vals = [float(x) for x in text.split(',')]
    if len(vals) < 2 or not np.all(np.diff(vals) > 0):
        raise argparse.ArgumentTypeError('bin edges must be strictly increasing')
    return vals


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--snapshot')
    ap.add_argument('--out', default='FakeRateMeasured')
    ap.add_argument('--year', default='2024_v15_pt_measured')
    ap.add_argument('--lumi', type=float, default=110.11)
    ap.add_argument('--ele-wp', action='append', default=[])
    ap.add_argument('--mu-wp', action='append', default=[])
    ap.add_argument('--bcat', action='append', choices=sorted(BCATS), default=[])
    ap.add_argument('--btag-wp', choices=sorted(BTAG_WPS), default='loose')
    ap.add_argument('--loose-ele', default='')
    ap.add_argument('--loose-mu', default='')
    ap.add_argument('--pt-bins', type=parse_bins, default=parse_bins(DEFAULT_PT))
    ap.add_argument('--eta-bins-ele', type=parse_bins, default=parse_bins(DEFAULT_ETA))
    ap.add_argument('--eta-bins-mu', type=parse_bins, default=parse_bins(DEFAULT_ETA))
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--retries', type=int, default=2)
    ap.add_argument('--max-files', type=int, default=0,
                    help='blunt global head cut on the sorted list; for a test '
                         'prefer --max-files-per-sample, which keeps every '
                         'sample alive')
    ap.add_argument('--fraction', type=float, default=1.,
                    help='read this fraction of the MC files of each sample '
                         'and scale the weights back up by the exact entry '
                         'ratio (0.25 = a quarter, weight x4)')
    ap.add_argument('--data-fraction', type=float, default=1.,
                    help='same for DATA. Default 1: subsampling data only adds '
                         'noise to a measurement. Use it for a smoke test')
    ap.add_argument('--max-files-per-sample', type=int, default=0,
                    help='cap per sample, evenly spread over its datasets, '
                         'applied on top of the fractions')
    ap.add_argument('--top-met-min', type=float, default=30.)
    ap.add_argument('--top-mll-min', type=float, default=12.)
    ap.add_argument('--top-min-btags', type=int, default=1)
    ap.add_argument('--ctrl-wp', action='append', default=[],
                    help='working points to make control plots for. Default: '
                         'the first electron and muon WP. The maps are always '
                         'made for every WP; this only bounds the plots, which '
                         'cost one set of histograms per WP')
    ap.add_argument('--ctrl-region', action='append', choices=list(REGIONS),
                    default=[],
                    help=f'regions to make control plots for '
                         f'(default: {" ".join(CTRL_REGIONS)})')
    ap.add_argument('--sf-bcat', choices=sorted(BCATS), default='incl',
                    help='b-category the DY scale factors are derived in')
    ap.add_argument('--ctrl-bcat', choices=sorted(BCATS), default='incl',
                    help='b-category of the QCD and DY control plots '
                         '(default incl). The top CR ignores it: it requires '
                         'a b-tag by definition')
    ap.add_argument('--ctrl-var', action='append', choices=list(CTRL_VARS),
                    default=[],
                    help=f'control-plot variables '
                         f'(default: {" ".join(DEFAULT_CTRL_VARS)})')
    ap.add_argument('--no-plots', action='store_true')
    ap.add_argument('--submitBatch', action='store_true',
                    help='split the files into HTCondor jobs and submit them')
    ap.add_argument('--prepareBatch', action='store_true',
                    help='write the job scripts but do not submit')
    ap.add_argument('--checkBatch', action='store_true',
                    help='report which jobs have not produced their part yet')
    ap.add_argument('--merge', action='store_true',
                    help='sum the partial accumulators and make the plots and '
                         'the maps')
    ap.add_argument('--batch-dir', default='condor',
                    help='where job scripts, logs and partial results live')
    ap.add_argument('--files-per-job', type=int, default=20)
    ap.add_argument('--job-flavour', default='workday',
                    help='HTCondor +JobFlavour (espresso microcentury longlunch '
                         'workday tomorrow testmatch nextweek)')
    ap.add_argument('--lcg-view',
                    default='/cvmfs/sft.cern.ch/lcg/views/LCG_109a/'
                            'x86_64-el9-gcc13-opt/setup.sh',
                    help='setup.sh the job sources before running')
    ap.add_argument('--file-list',
                    help='internal: read these files (one path and weight '
                         'scale per line) instead of listing the snapshot')
    ap.add_argument('--dump',
                    help='internal: write the accumulator here and stop')
    ap.add_argument('--problem-list',
                    help='write the paths of the unreadable files here, one '
                         'per line, ready to be deleted and regenerated')
    ap.add_argument('--plots-only', action='store_true',
                    help='make the control plots and skip the fake/prompt rate '
                         'maps entirely. Does not need ROOT')
    args = ap.parse_args()
    if args.checkBatch:
        done, missing = check_batch(args.batch_dir)
        print(f'{len(done)} of {len(done) + len(missing)} jobs have a part')
        if missing:
            print('missing:', ' '.join(missing[:40]),
                  '...' if len(missing) > 40 else '')
        return
    for name, value in (('--fraction', args.fraction),
                        ('--data-fraction', args.data_fraction)):
        if not 0. < value <= 1.:
            ap.error(f'{name} must be in (0, 1]')
    needs_input = not (args.merge or args.checkBatch)
    if needs_input and not args.snapshot and not args.file_list:
        ap.error('--snapshot is required unless --merge or --checkBatch')
    if args.file_list:
        files = [line.split('\t')[0] for line in
                 open(args.file_list).read().splitlines() if line.strip()]
    elif needs_input:
        files = list_snapshots(args.snapshot)
    else:
        files = []
    if args.max_files:
        files = files[:args.max_files]
    if needs_input and not files:
        ap.error('No per-sample snapshots found')
    ele_wps, mu_wps = args.ele_wp[:], args.mu_wp[:]
    if files and (not ele_wps or not mu_wps):
        import uproot
        keys = None
        for path in files:
            try:
                with uproot.open(f'{path}:{TREE}') as t:
                    keys = list(t.keys())
                break
            except Exception:
                continue
        if keys is None:
            ap.error('No readable ROOT file for automatic WP discovery')
        if not ele_wps:
            ele_wps = sorted(k.removeprefix('Lepton_isTightElectron_') for k in keys
                             if k.startswith('Lepton_isTightElectron_'))
        if not mu_wps:
            mu_wps = sorted(k.removeprefix('Lepton_isTightMuon_') for k in keys
                            if k.startswith('Lepton_isTightMuon_'))
    if not args.merge and not ele_wps and not mu_wps:
        ap.error('No tight working points found')
    bcats = args.bcat or ['bveto', 'btag']
    bins = {'ele': (args.pt_bins, args.eta_bins_ele),
            'mu': (args.pt_bins, args.eta_bins_mu)}
    maps = map_definitions(ele_wps, mu_wps, bcats)
    ctrl_wps = args.ctrl_wp or ele_wps[:1] + mu_wps[:1]
    unknown_ctrl = [w for w in ctrl_wps if w not in set(ele_wps + mu_wps)]
    if unknown_ctrl:
        ap.error(f'--ctrl-wp not among the measured working points: '
                 f'{unknown_ctrl}')
    cfg = dict(ele_wps=ele_wps, mu_wps=mu_wps, ctrl_wps=ctrl_wps,
               ctrl_regions=args.ctrl_region or list(CTRL_REGIONS),
               ctrl_vars=args.ctrl_var or list(DEFAULT_CTRL_VARS),
               ctrl_bcat=args.ctrl_bcat, sf_bcat=args.sf_bcat,
               all_wps=sorted(set(ele_wps + mu_wps)), bcats=bcats, bins=bins,
               maps=maps, lumi=args.lumi, loose_ele=args.loose_ele,
               loose_mu=args.loose_mu, btag_thr=BTAG_WPS[args.btag_wp],
               retries=args.retries, top_met_min=args.top_met_min,
               top_mll_min=args.top_mll_min, top_min_btags=args.top_min_btags)
    print(f'Control plots: regions {args.ctrl_region or list(CTRL_REGIONS)}, '
          f'variables {args.ctrl_var or list(DEFAULT_CTRL_VARS)}, '
          f'b-category {args.ctrl_bcat}, WPs {ctrl_wps}', flush=True)
    print(f'Files: {len(files)}; maps: {len(maps)}; lumi: {args.lumi}; '
          f'eta signed: {args.eta_bins_ele}; top CR: OS e-mu, '
          f'MET>{args.top_met_min}, mll>{args.top_mll_min}, '
          f'nbtag>={args.top_min_btags}', flush=True)
    total = {}
    problems = []
    if args.file_list:
        # the scale was decided once, at submit time
        selected = [(line.split('\t')[0], float(line.split('\t')[1]))
                    for line in open(args.file_list).read().splitlines()
                    if line.strip()]
        report = [f'From {args.file_list}: {len(selected)} files']
    elif needs_input:
        selected, report = select_files(files, args.fraction,
                                        args.data_fraction,
                                        args.max_files_per_sample, args.workers)
    else:
        selected, report = [], []
    for line in report:
        print(line, flush=True)
    if len(selected) < len(files):
        print(f'SUBSAMPLED: reading {len(selected)} of {len(files)} files. '
              'The weights are scaled back up, so the central values are '
              'unbiased, but the subtracted MC carries sqrt(scale) more '
              'statistical error and the uncertainties written out are '
              'correspondingly larger. Not a result to publish.', flush=True)
    files = [p for p, _ in selected]
    if args.submitBatch or args.prepareBatch:
        sub, njobs = write_batch(args, selected, batch_args(args, cfg))
        if args.prepareBatch:
            print(f'Written {sub}. Submit with: condor_submit {sub}')
            return
        proc = subprocess.run(['condor_submit', os.path.basename(sub)],
                              cwd=os.path.dirname(sub), text=True,
                              capture_output=True)
        print(proc.stdout or '', proc.stderr or '')
        if proc.returncode:
            raise SystemExit(f'condor_submit failed ({proc.returncode})')
        print(f'Submitted {njobs} jobs. When they are done:\n'
              f'  {os.path.basename(__file__)} --merge '
              f'--batch-dir {args.batch_dir} --out {args.out} '
              f'--year {args.year}')
        return
    payloads = [(p, cfg, scale) for p, scale in selected]
    def merge(acc, msgs):
        problems.extend(msgs)
        for key, value in acc.items():
            if key in total:
                total[key] += value
            else:
                total[key] = value.copy()
    if args.merge:
        parts_dir = os.path.join(os.path.abspath(
            os.path.expandvars(args.batch_dir)), 'parts')
        (total, part_problems, nparts, job_cfg,
         files) = load_partials(parts_dir)
        problems.extend(part_problems)
        if not nparts:
            raise SystemExit(f'No {PART_PREFIX}*.pkl in {parts_dir}')
        # The jobs' configuration wins: the histograms were filled with it, and
        # re-deriving it here would mean repeating every option on the merge.
        cfg.update(job_cfg)
        ele_wps, mu_wps = cfg['ele_wps'], cfg['mu_wps']
        bcats, bins, maps = cfg['bcats'], cfg['bins'], cfg['maps']
        done, missing = check_batch(args.batch_dir)
        print(f'Merged {nparts} partial results from {parts_dir}')
        if missing:
            print(f'WARNING: {len(missing)} jobs have no part and are NOT in '
                  f'this merge: {" ".join(missing[:20])}'
                  f'{" ..." if len(missing) > 20 else ""}')
    elif args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(process_file, payload): payload[0]
                       for payload in payloads}
            for i, future in enumerate(as_completed(futures), 1):
                try:
                    merge(*future.result())
                except Exception:
                    problems.append(f'{futures[future]}: {traceback.format_exc(limit=2)}')
                if i % 50 == 0:
                    print(f'Processed {i}/{len(files)}', flush=True)
    else:
        for i, payload in enumerate(payloads, 1):
            try:
                merge(*process_file(payload))
            except Exception:
                problems.append(f'{payload[0]}: {traceback.format_exc(limit=2)}')
            if i % 50 == 0:
                print(f'Processed {i}/{len(files)}', flush=True)
    if args.dump:
        dump_partial(args.dump, total, problems, cfg, files)
        print(f'Wrote {args.dump}: {len(total)} histograms, '
              f'{len(problems)} warnings')
        return
    for line in unreadable_report(problems, files, args.problem_list):
        print(line)
    for msg in problems[:30]:
        print('WARNING:', msg)
    if len(problems) > 30:
        print(f'... {len(problems)-30} more messages')
    base = os.path.join(os.path.expandvars(args.out), args.year)
    scale_factors, empty_bins = compute_sf(total, cfg)
    for line in report_sf(scale_factors, empty_bins, cfg['ctrl_wps']):
        print(line, flush=True)
    def grab(name, part, source, moment, flav):
        shape = (len(bins[flav][0])-1, len(bins[flav][1])-1)
        return total.get(('map', name, part, source, moment), np.zeros(shape))
    written = 0
    comparisons = []
    for name, flav, i, kind, _, wp, _ in maps:
        if args.plots_only:
            break
        xb, yb = bins[flav]
        Td, Td2 = grab(name, 'tight', 'data', 'sumw', flav), grab(name, 'tight', 'data', 'sumw2', flav)
        Rd, Rd2 = grab(name, 'rest', 'data', 'sumw', flav), grab(name, 'rest', 'data', 'sumw2', flav)
        # The fake rate subtracts the prompt MC; the prompt rate subtracts the
        # nonprompt contamination of the DY CR. Same arithmetic, other series.
        source = 'mc' if kind == 'FR' else 'mcnp'
        Tm, Tm2 = grab(name, 'tight', source, 'sumw', flav), grab(name, 'tight', source, 'sumw2', flav)
        Rm, Rm2 = grab(name, 'rest', source, 'sumw', flav), grab(name, 'rest', source, 'sumw2', flav)
        if not np.any(Td + Rd):
            continue
        # The DY factors reweight the subtracted MC, each level by its own map.
        sf_t = scale_factors.get((wp, flav, i, 'tight'), (np.ones_like(Tm),))[0]
        sf_r = scale_factors.get((wp, flav, i, 'rest'), (np.ones_like(Rm),))[0]
        raw, raw_e, ok = ratio(Td, Td2, Rd, Rd2, Tm, Tm2, Rm, Rm2, False)
        ewk, ewk_e, _ = ratio(Td, Td2, Rd, Rd2, Tm, Tm2, Rm, Rm2, True)
        corr, corr_e, _ = ratio(Td, Td2, Rd, Rd2,
                                Tm * sf_t, Tm2 * sf_t ** 2,
                                Rm * sf_r, Rm2 * sf_r ** 2, True)
        f, e = corr, corr_e
        tag = 'FR' if kind == 'FR' else 'PR'
        ingredients = {f'{tag}_pT_eta': (raw, raw_e),
                       f'{tag}_pT_eta_EWK': (ewk, ewk_e),
                       'h_tight_data': (Td, np.sqrt(Td2)),
                       'h_rest_data': (Rd, np.sqrt(Rd2)),
                       'h_tight_mc': (Tm, np.sqrt(Tm2)),
                       'h_rest_mc': (Rm, np.sqrt(Rm2)),
                       'h_tight_mc_SF': (Tm * sf_t, np.sqrt(Tm2) * sf_t),
                       'h_rest_mc_SF': (Rm * sf_r, np.sqrt(Rm2) * sf_r)}
        if kind == 'FR':
            hist_name = 'FR_pT_eta_EWKcorr'
        else:
            hist_name = ('h_Ele_signal_pt_eta_bin' if flav == 'ele'
                         else 'h_Muon_signal_pt_eta_bin')
        comparisons.append((name, wp, ok, raw, ewk, corr))
        if wp in cfg['ctrl_wps'] and not args.no_plots:
            # one scale for the three, so the comparison is the picture and
            # not an exercise in reading two colour bars
            top = max(float(np.max(v[ok])) if ok.any() else 0.
                      for v in (raw, ewk, corr))
            top = min(max(top, 1e-3), 1.)
            for suffix, values in (('', raw), ('_EWK', ewk),
                                   ('_EWKcorr', corr)):
                out = os.path.join(base, wp, 'maps',
                                   f'{name}{suffix}.png')
                os.makedirs(os.path.dirname(out), exist_ok=True)
                plot_rate_map(values, xb, yb,
                              f'{name}{suffix or "  (no subtraction)"}\n{wp}',
                              out, vmax=top)
        invalid = ok & ((f < 0) | (f >= 1))
        if np.any(invalid):
            print(f'WARNING: {name} has {invalid.sum()} nonphysical bins')
        write_root(os.path.join(base, wp, name + '.root'), hist_name,
                   f, e, ingredients, xb, yb)
        written += 1
    print(f'Wrote {written} ROOT maps in {base}')
    for line in compare_variants(comparisons):
        print(line)
    if not args.no_plots:
        nplots = make_plots(total, cfg, os.path.join(base, 'plots'),
                            scale_factors, empty_bins)
        print(f'Wrote {nplots} control PNGs in {base}/plots')
    print(f'Read warnings/errors: {len(problems)}')


if __name__ == '__main__':
    main()
