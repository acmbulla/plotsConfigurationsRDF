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
import traceback
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

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


def process_file(payload):
    path, cfg = payload
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
    for _ in range(cfg['retries'] + 1):
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
        return {}, [f'{path}: unreadable ({error}); skipped']
    messages = ([f'{os.path.basename(path)}: absent trigger paths {tmissing}']
                if tmissing else [])
    n = len(a['nLepSel'])
    if not n:
        return {}, messages
    nlep = ak.to_numpy(a['nLepSel']).astype(int)
    pt = pad2(a['SelLep_pt'], np.nan).astype(float)
    eta = pad2(a['SelLep_eta'], np.nan).astype(float)  # SIGNED eta
    pdg = np.abs(pad2(a['SelLep_pdgId']).astype(int))
    weight = (ak.to_numpy(a['METFilter_DATA']).astype(float) if is_data else
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
        if not is_data:
            sel &= prompt[:, i]
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
            for moment, ww in (('sumw', w[mask]), ('sumw2', w[mask]**2)):
                acc[('map', name, part, 'data' if is_data else 'mc', moment)] = hist2(
                    x[mask], y[mask], ww, xb, yb)
    # Control plots: all MC components (prompt AND nonprompt), and data.
    # Loose = tight + rest, both plotted independently; inclusive in signed eta.
    # For ss/dy/top, select each lepton by its actual flavour and position.
    for wp in cfg['all_wps']:
        for flav in ('ele', 'mu'):
            if wp not in (cfg['ele_wps'] if flav == 'ele' else cfg['mu_wps']):
                continue
            for chan in REGIONS:
                for bcat in cfg['bcats']:
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
                        x = np.clip(pt[sel, i], xb[0], np.nextafter(xb[-1], -np.inf))
                        w = weight[sel]
                        t = tight[flav, wp][sel, i]
                        # Split MC into prompt and nonprompt for composition.
                        labels = [('data', np.ones(len(x), dtype=bool))] if is_data else [
                            (sample + '_prompt', prompt[sel, i]),
                            (sample + '_nonprompt', ~prompt[sel, i])]
                        for component, component_mask in labels:
                            for part, partmask in (('loose', np.ones(len(x), dtype=bool)),
                                                   ('tight', t)):
                                mask = component_mask & partmask
                                if not mask.any():
                                    continue
                                for moment, ww in (('sumw', w[mask]),
                                                   ('sumw2', w[mask]**2)):
                                    key = ('plot', wp, chan, bcat, flav, i,
                                           part, component, moment)
                                    acc[key] = hist1(x[mask], ww, xb)
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


def make_plots(total, cfg, base):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    os.makedirs(base, exist_ok=True)
    files_written = 0
    for wp in cfg['all_wps']:
        for chan in REGIONS:
            for bcat in cfg['bcats']:
                for flav in ('ele', 'mu'):
                    if wp not in (cfg['ele_wps'] if flav == 'ele' else cfg['mu_wps']):
                        continue
                    xb = np.asarray(cfg['bins'][flav][0])
                    for i in range(1 if chan == '1l' else 2):
                        # Each PDF contains two pages: loose and tight.
                        prefix = f'{wp}_{chan}_{bcat}_{flav}_lep{i}'
                        path = os.path.join(base, wp, prefix + '.pdf')
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        any_entries = False
                        with PdfPages(path) as pdf:
                            for part in ('loose', 'tight'):
                                def grab(component, moment):
                                    return total.get(('plot', wp, chan, bcat, flav, i,
                                                      part, component, moment),
                                                     np.zeros(len(xb)-1))
                                data, data2 = grab('data', 'sumw'), grab('data', 'sumw2')
                                components = []
                                for sample in MC_SAMPLES:
                                    for origin in ('prompt', 'nonprompt'):
                                        label = f'{sample}_{origin}'
                                        y = grab(label, 'sumw')
                                        if np.any(y):
                                            components.append((label, y))
                                if not np.any(data) and not components:
                                    continue
                                any_entries = True
                                fig, (ax, ratioax) = plt.subplots(
                                    2, 1, figsize=(9, 7), sharex=True,
                                    gridspec_kw={'height_ratios': [3, 1], 'hspace': .08})
                                width = np.diff(xb)
                                bottom = np.zeros(len(width))
                                # Stacking signed MC is not mathematically meaningful for
                                # negative bins: stack only if all components nonnegative.
                                can_stack = all(np.all(y >= 0) for _, y in components)
                                if can_stack:
                                    for label, y in components:
                                        ax.bar(xb[:-1], y, width=width, bottom=bottom,
                                               align='edge', alpha=.75, label=label)
                                        bottom += y
                                else:
                                    for label, y in components:
                                        ax.stairs(y, xb, label=label)
                                        bottom += y
                                centers = (xb[:-1] + xb[1:]) / 2
                                ax.errorbar(centers, data, yerr=np.sqrt(data2),
                                            fmt='ko', label='DATA', markersize=4)
                                ax.set_ylabel('Weighted events / bin')
                                ax.set_title(f'{chan} | {bcat} | {flav} lep{i} | {wp} | {part}\n'
                                             f'Inclusive in signed eta')
                                ax.legend(fontsize=7, ncol=3)
                                ax.grid(alpha=.15)
                                ok = bottom > 0
                                vals = np.full(len(bottom), np.nan)
                                errs = np.full(len(bottom), np.nan)
                                vals[ok] = data[ok] / bottom[ok]
                                errs[ok] = np.sqrt(data2[ok]) / bottom[ok]
                                ratioax.errorbar(centers, vals, yerr=errs,
                                                 fmt='ko', markersize=4)
                                ratioax.axhline(1, color='gray', linestyle='--')
                                ratioax.set_ylabel('Data / MC')
                                ratioax.set_xlabel(r'$p_T$ [GeV]')
                                ratioax.grid(alpha=.2)
                                fig.tight_layout()
                                pdf.savefig(fig)
                                plt.close(fig)
                        if any_entries:
                            files_written += 1
                        else:
                            os.remove(path)
    return files_written


def parse_bins(text):
    vals = [float(x) for x in text.split(',')]
    if len(vals) < 2 or not np.all(np.diff(vals) > 0):
        raise argparse.ArgumentTypeError('bin edges must be strictly increasing')
    return vals


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--snapshot', required=True)
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
    ap.add_argument('--max-files', type=int, default=0)
    ap.add_argument('--top-met-min', type=float, default=30.)
    ap.add_argument('--top-mll-min', type=float, default=12.)
    ap.add_argument('--top-min-btags', type=int, default=1)
    ap.add_argument('--no-plots', action='store_true')
    args = ap.parse_args()
    files = list_snapshots(args.snapshot)
    if args.max_files:
        files = files[:args.max_files]
    if not files:
        ap.error('No per-sample snapshots found')
    ele_wps, mu_wps = args.ele_wp[:], args.mu_wp[:]
    if not ele_wps or not mu_wps:
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
    if not ele_wps and not mu_wps:
        ap.error('No tight working points found')
    bcats = args.bcat or ['bveto', 'btag']
    bins = {'ele': (args.pt_bins, args.eta_bins_ele),
            'mu': (args.pt_bins, args.eta_bins_mu)}
    maps = map_definitions(ele_wps, mu_wps, bcats)
    cfg = dict(ele_wps=ele_wps, mu_wps=mu_wps,
               all_wps=sorted(set(ele_wps + mu_wps)), bcats=bcats, bins=bins,
               maps=maps, lumi=args.lumi, loose_ele=args.loose_ele,
               loose_mu=args.loose_mu, btag_thr=BTAG_WPS[args.btag_wp],
               retries=args.retries, top_met_min=args.top_met_min,
               top_mll_min=args.top_mll_min, top_min_btags=args.top_min_btags)
    print(f'Files: {len(files)}; maps: {len(maps)}; lumi: {args.lumi}; '
          f'eta signed: {args.eta_bins_ele}; top CR: OS e-mu, '
          f'MET>{args.top_met_min}, mll>{args.top_mll_min}, '
          f'nbtag>={args.top_min_btags}', flush=True)
    total = {}
    problems = []
    payloads = [(f, cfg) for f in files]
    def merge(acc, msgs):
        problems.extend(msgs)
        for key, value in acc.items():
            if key in total:
                total[key] += value
            else:
                total[key] = value.copy()
    if args.workers > 1:
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
    for msg in problems[:30]:
        print('WARNING:', msg)
    if len(problems) > 30:
        print(f'... {len(problems)-30} more messages')
    base = os.path.join(os.path.expandvars(args.out), args.year)
    def grab(name, part, source, moment, flav):
        shape = (len(bins[flav][0])-1, len(bins[flav][1])-1)
        return total.get(('map', name, part, source, moment), np.zeros(shape))
    written = 0
    for name, flav, _, kind, _, wp, _ in maps:
        xb, yb = bins[flav]
        Td, Td2 = grab(name, 'tight', 'data', 'sumw', flav), grab(name, 'tight', 'data', 'sumw2', flav)
        Rd, Rd2 = grab(name, 'rest', 'data', 'sumw', flav), grab(name, 'rest', 'data', 'sumw2', flav)
        Tm, Tm2 = grab(name, 'tight', 'mc', 'sumw', flav), grab(name, 'tight', 'mc', 'sumw2', flav)
        Rm, Rm2 = grab(name, 'rest', 'mc', 'sumw', flav), grab(name, 'rest', 'mc', 'sumw2', flav)
        if not np.any(Td + Rd):
            continue
        f, e, ok = ratio(Td, Td2, Rd, Rd2, Tm, Tm2, Rm, Rm2, kind == 'FR')
        if kind == 'FR':
            raw, raw_e, _ = ratio(Td, Td2, Rd, Rd2, Tm, Tm2, Rm, Rm2, False)
            ingredients = {'FR_pT_eta': (raw, raw_e),
                           'h_tight_data': (Td, np.sqrt(Td2)),
                           'h_rest_data': (Rd, np.sqrt(Rd2)),
                           'h_tight_mc': (Tm, np.sqrt(Tm2)),
                           'h_rest_mc': (Rm, np.sqrt(Rm2))}
            hist_name = 'FR_pT_eta_EWKcorr'
        else:
            ingredients = {'PR_pT_eta': (f, e),
                           'h_tight_data': (Td, np.sqrt(Td2)),
                           'h_rest_data': (Rd, np.sqrt(Rd2))}
            hist_name = ('h_Ele_signal_pt_eta_bin' if flav == 'ele'
                         else 'h_Muon_signal_pt_eta_bin')
        invalid = ok & ((f < 0) | (f >= 1))
        if np.any(invalid):
            print(f'WARNING: {name} has {invalid.sum()} nonphysical bins')
        write_root(os.path.join(base, wp, name + '.root'), hist_name,
                   f, e, ingredients, xb, yb)
        written += 1
    print(f'Wrote {written} ROOT maps in {base}')
    if not args.no_plots:
        nplots = make_plots(total, cfg, os.path.join(base, 'plots'))
        print(f'Wrote {nplots} control PDFs in {base}/plots')
    print(f'Read warnings/errors: {len(problems)}')


if __name__ == '__main__':
    main()
