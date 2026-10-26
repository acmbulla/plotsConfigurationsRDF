#!/usr/bin/env python3
"""Compare measureFakeRate.py ROOT maps after integrating their counts in eta.

Per flavor/WP and subtraction variant: one inclusive 1l/2l-lep0/2l-lep1
overlay and three inclusive/btag/bveto overlays. Default: separate EWK and
EWKcorr files, points with error bars only. 2l combines SS SF+DF.

When the input also holds the jet-binned maps (measureFakeRate.py --jetcat,
file names suffixed _j0/_j1/_j2), each b category additionally gets an
overlay of its jet-multiplicity bins against its jet-inclusive curve. Those
maps are optional: absent, nothing is reported, because the split is opt-in
at measurement time.

With --legacy-input, the old recoil-jet-pT maps (EleFR_jet<thr>.root and
ElePR.root, the ones fake_rate_reader_class.cc reads) are overlaid as well:
one plot scanning the jet threshold, one comparing the threshold the weight
actually uses against the new region maps, and, per legacy |eta| band, the
old prompt rate against the new one.

No ROOT Python bindings needed: numpy, uproot and matplotlib are sufficient.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import html
from itertools import cycle
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import urlsplit

import numpy as np
import uproot


TAGS = {'ele': ('Ele', 'ee'), 'mu': ('Muon', 'mumu')}
CASES = {'1l': '1 lep', '2l_lep0': '2 lep — primo lep', '2l_lep1': '2 lep — secondo lep'}
BCATS = {'incl': 'inclusive', 'btag': 'bjet', 'bveto': 'bveto'}
# Jet-multiplicity categories as measureFakeRate.py names them, with the label
# each one carries in the plots. Insertion order is the order they are drawn.
JETCATS = {'j0': '0 jet', 'j1': '1 jet', 'j2': '≥2 jet',
           'j2excl': '2 jet esatti', 'j3': '≥3 jet'}
# Longest first: ordered alternation, so 'j2' must not shadow 'j2excl' and
# leave 'excl' to be matched by '\.root$'.
_JETPAT = '|'.join(sorted(JETCATS, key=len, reverse=True))
MAP_NAME = re.compile(r'^(Ele|Muon)(?:FR_(?:1l|ee_lep[01]|mumu_lep[01]|emu_lep[01])_(?:incl|btag|bveto)'
                      r'(?:_(?:' + _JETPAT + r'))?'
                      r'|PR_(?:ee|mumu)_lep[01])\.root$')
# The old maps: one per recoil-jet pT threshold, plus a single prompt rate.
LEGACY_FR = re.compile(r'^(Ele|Muon)FR_jet(\d+)\.root$')
LEGACY_PR = {'ele': 'ElePR.root', 'mu': 'MuonPR.root'}
PR_HIST = {'ele': 'h_Ele_signal_pt_eta_bin', 'mu': 'h_Muon_signal_pt_eta_bin'}
SUBTRACTION = {'corrected': 'dati − prompt MC con SF DY', 'ewk': 'dati − prompt MC',
               'raw': 'dati, senza sottrazione'}
# Ten of each: the jet-threshold scan puts nine curves on one axis, and a
# shorter cycle would hand the measured reference the same colour and marker
# as the first legacy threshold.
COLORS = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00', '#56B4E9',
          '#994F00', '#555555', '#000000', '#7F3FBF']
MARKERS = ['o', 's', '^', 'v', 'D', 'P', 'X', '*', 'h', '<']


@dataclass
class Counts:
    pt: np.ndarray
    eta: np.ndarray
    tight: np.ndarray
    var_tight: np.ndarray
    rest: np.ndarray
    var_rest: np.ndarray


def inventory(directory):
    """Return (relative name, readable local path/XRootD URL)."""
    if directory.startswith('root://'):
        url = urlsplit(directory)
        result = subprocess.run(['xrdfs', url.netloc, 'ls', '-R', url.path],
                                capture_output=True, text=True, timeout=600, check=True)
        base = PurePosixPath('/' + url.path.lstrip('/'))
        files = []
        for line in result.stdout.splitlines():
            full = PurePosixPath('/' + line.strip().lstrip('/'))
            if full.suffix != '.root':
                continue
            files.append((full.relative_to(base), f'root://{url.netloc}//{str(full).lstrip("/")}'))
        return files
    base = Path(directory).expanduser().resolve()
    if not base.is_dir():
        raise ValueError(f'Input directory does not exist: {base}')
    return [(PurePosixPath(p.relative_to(base).as_posix()), str(p))
            for p in sorted(base.rglob('*.root'))]


def same_edges(left, right, description):
    if left.shape != right.shape or not np.allclose(left, right, rtol=0, atol=1e-9):
        raise ValueError(f'Incompatible {description} bin edges; rebin the counts before comparing')


def read_hist(root, name, source):
    if name not in root:
        raise ValueError(f'{source}: missing {name}; cannot integrate a precomputed FR map correctly')
    hist = root[name]
    values, pt, eta = hist.to_numpy(flow=False)
    if len(hist.member('fSumw2')) == 0:
        raise ValueError(f'{source}/{name}: weighted variances (Sumw2) are missing')
    variances = hist.variances(flow=False)
    if variances is None or not np.isfinite(values).all() or not np.isfinite(variances).all():
        raise ValueError(f'{source}/{name}: missing/nonfinite counts or variances')
    if np.any(variances < 0):
        raise ValueError(f'{source}/{name}: negative variance')
    return np.asarray(values, float), np.asarray(variances, float), np.asarray(pt), np.asarray(eta)


def read_plain(root, name, source):
    """Counts with no Sumw2 requirement: the legacy numerator and denominator
    carry none, and they are used only as eta weights."""
    if name not in root:
        raise ValueError(f'{source}: missing {name}')
    values, pt, eta = root[name].to_numpy(flow=False)
    if not np.isfinite(values).all():
        raise ValueError(f'{source}/{name}: nonfinite counts')
    return np.asarray(values, float), np.asarray(pt), np.asarray(eta)


def read_counts(source, variant):
    """Subtract in 2D before summing: corrected SF can depend on eta."""
    with uproot.open(source) as root:
        td, vt, pt, eta = read_hist(root, 'h_tight_data', source)
        rd, vr, xp, yp = read_hist(root, 'h_rest_data', source)
        same_edges(pt, xp, 'pT'); same_edges(eta, yp, 'eta')
        if variant != 'raw':
            suffix = '_SF' if variant == 'corrected' else ''
            for part, data, variance in [('tight', td, vt), ('rest', rd, vr)]:
                mc, vmc, xp, yp = read_hist(root, f'h_{part}_mc{suffix}', source)
                same_edges(pt, xp, 'pT'); same_edges(eta, yp, 'eta')
                data -= mc
                variance += vmc
    return Counts(pt, eta, td, vt, rd, vr)


def project_pt(parts, eta_mask=None):
    """Tight/rest are disjoint. Independent channels and eta bins add in yield/variance."""
    first = parts[0]
    for other in parts[1:]:
        same_edges(first.pt, other.pt, 'pT'); same_edges(first.eta, other.eta, 'eta')
    def selected(part, field):
        # Index only when a band was asked for: a full boolean mask copies the
        # array and reorders the summation, which moves the last digit.
        values = getattr(part, field)
        return values if eta_mask is None else values[:, eta_mask]
    n, vn, rest, vrest = [sum(selected(p, field).sum(axis=1) for p in parts)
                          for field in ['tight', 'var_tight', 'rest', 'var_rest']]
    denominator = n + rest
    valid = denominator > 0
    rate = np.full_like(n, np.nan); error = np.full_like(n, np.nan)
    rate[valid] = n[valid] / denominator[valid]
    error[valid] = np.sqrt((rest[valid]**2 * vn[valid] + n[valid]**2 * vrest[valid])
                           / denominator[valid]**4)
    return dict(pt_edges=first.pt, eta_edges=first.eta, rate=rate, error=error,
                tight=n, var_tight=vn, rest=rest, var_rest=vrest, denominator=denominator,
                valid=valid, physical=valid & (rate >= 0) & (rate <= 1))


def legacy_fr_curve(source, variant):
    """The legacy map stores the rate with its Sumw2 and, separately, unweighted
    numerator and denominator counts. The counts give the eta weights; the error
    comes from the stored per-bin rate errors, with the denominators held fixed.
    The legacy production has a single subtracted version, so ewk and corrected
    read the same histogram."""
    name = 'FR_pT_eta' if variant == 'raw' else 'FR_pT_eta_EWKcorr'
    with uproot.open(source) as root:
        rate2d, var2d, pt, eta = read_hist(root, name, source)
        num, xp, yp = read_plain(root, f'{name}_numerator', source)
        den, xq, yq = read_plain(root, f'{name}_denominator', source)
    for edges, axis in [(xp, 'pT'), (xq, 'pT')]:
        same_edges(pt, edges, axis)
    for edges in [yp, yq]:
        same_edges(eta, edges, 'eta')
    tight = num.sum(axis=1)
    denominator = den.sum(axis=1)
    valid = denominator > 0
    weight = np.divide(den, denominator[:, None], out=np.zeros_like(den),
                       where=denominator[:, None] > 0)
    rate = np.full(tight.shape, np.nan)
    error = np.full(tight.shape, np.nan)
    rate[valid] = tight[valid] / denominator[valid]
    error[valid] = np.sqrt((weight**2 * var2d).sum(axis=1))[valid]
    blank = np.full(tight.shape, np.nan)
    return dict(pt_edges=pt, eta_edges=eta, rate=rate, error=error,
                tight=tight, var_tight=blank, rest=denominator - tight, var_rest=blank,
                denominator=denominator, valid=valid,
                physical=valid & (rate >= 0) & (rate <= 1))


def legacy_pr_curve(source, flavor, column):
    """The legacy prompt rate ships only the rate map, so one |eta| bin is read
    as it stands; there is nothing to integrate and no subtraction variant."""
    with uproot.open(source) as root:
        rate2d, var2d, pt, eta = read_hist(root, PR_HIST[flavor], source)
    rate = rate2d[:, column].copy()
    error = np.sqrt(var2d[:, column])
    valid = rate > 0
    rate[~valid] = np.nan
    error[~valid] = np.nan
    blank = np.full(rate.shape, np.nan)
    return dict(pt_edges=pt, eta_edges=eta[column:column + 2], rate=rate, error=error,
                tight=blank, var_tight=blank, rest=blank, var_rest=blank, denominator=blank,
                valid=valid, physical=valid & (rate <= 1),
                eta_band=[float(eta[column]), float(eta[column + 1])])


def snap_bands(legacy_eta, measured_eta):
    """The legacy maps are binned in |eta|, the measured ones in signed eta.
    Each legacy boundary is snapped to the nearest |measured| edge: 1.479 has no
    counterpart in the measured binning, so the band edges are reported with the
    plot rather than silently assumed equal."""
    available = np.unique(np.abs(measured_eta))
    centres = np.abs((measured_eta[:-1] + measured_eta[1:]) / 2)
    bands = []
    for k in range(len(legacy_eta) - 1):
        lo, hi = [float(available[np.argmin(np.abs(available - edge))])
                  for edge in legacy_eta[k:k + 2]]
        bands.append((float(legacy_eta[k]), float(legacy_eta[k + 1]), lo, hi,
                      (centres >= lo) & (centres < hi)))
    return bands


def legacy_maps(legacy, wp, flavor):
    """Jet threshold -> file, for one WP and flavor."""
    tag = TAGS[flavor][0]
    found = {}
    for (directory, name), source in legacy.items():
        match = LEGACY_FR.match(name)
        if directory == wp and match and match.group(1) == tag:
            found[int(match.group(2))] = source
    return found


def needed_names(flavor, case, cat, channels):
    """`cat` is the category suffix of the file name: a b category on its own
    ('incl', 'bveto', 'btag') or one crossed with a jet bin ('bveto_j1')."""
    tag, sf = TAGS[flavor]
    if case == '1l':
        return [f'{tag}FR_1l_{cat}.root']
    slot = 0 if case == '2l_lep0' else 1
    return [f'{tag}FR_{sf if channel == "sf" else "emu"}_lep{slot}_{cat}.root'
            for channel in channels]


def plain(value):
    if isinstance(value, np.ndarray):
        return [None if isinstance(v, (float, np.floating)) and not np.isfinite(v)
                else v.item() if isinstance(v, np.generic) else v for v in value]
    return value


def cell(value):
    """Blank rather than 'nan' in the CSV: the legacy curves have no variances."""
    if isinstance(value, (float, np.floating)) and not np.isfinite(value):
        return ''
    return value


def overlay(curves, entries, title, subtitle, target, ylabel='Fake rate'):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 6))
    bounds = []
    found = 0
    for (key, label), color, marker in zip(entries, cycle(COLORS), cycle(MARKERS)):
        curve = curves.get(key)
        if curve is None:
            ax.plot([], [], color=color, marker=marker, ls='none', label=label+' [mancante]')
            continue
        valid = curve['valid']; pt = curve['pt_edges']; x = (pt[:-1]+pt[1:])/2
        rate, error = curve['rate'], curve['error']
        ax.errorbar(x, rate, yerr=error, xerr=np.diff(pt)/2, color=color, marker=marker,
                    label=label, capsize=2, lw=1.2, ms=4, linestyle='none')
        nonphysical = valid & ~curve['physical']
        ax.scatter(x[nonphysical], rate[nonphysical], facecolors='none', edgecolors='red', s=90, zorder=5)
        bounds.extend((rate[valid]-error[valid]).tolist()+(rate[valid]+error[valid]).tolist())
        found += 1
    ax.axhline(0, lw=.7, color='#777')
    if bounds:
        lo, hi = min(0., min(bounds)), max(.05, max(bounds))
        margin = .08*max(hi-lo, .05); ax.set_ylim(lo-margin, hi+margin)
        if hi > 1: ax.axhline(1, lw=.7, color='#777', ls='--')
    ax.set(xlabel=r'$p_T$ [GeV]', ylabel=ylabel)
    # The band titles run long; shrink rather than let tight_layout clip them.
    ax.set_title(f'{title}\n{subtitle}', fontsize=11 if len(title) < 70 else 9)
    ax.grid(alpha=.2); ax.legend(fontsize=9)
    if found < len(entries): ax.text(.98,.98,'CONFRONTO PARZIALE',transform=ax.transAxes,ha='right',va='top',color='red')
    fig.tight_layout()
    for suffix in ['png','pdf']: fig.savefig(target.with_suffix('.'+suffix), dpi=180)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', required=True, help='FakeRateMeasured, year directory, or a single WP directory; local or root://')
    ap.add_argument('--out', type=Path, default=Path('FR_comparisons_pt'))
    ap.add_argument('--flavor', nargs='+', choices=list(TAGS), default=list(TAGS))
    ap.add_argument('--wp', action='append', help='exact WP directory name; repeat to select multiple WPs')
    ap.add_argument('--variant', choices=['both','corrected','ewk','raw'], default='both',
                    help='both (default): separate EWK and EWKcorr outputs; corrected selects EWKcorr only')
    ap.add_argument('--two-lepton-channels', nargs='+', choices=['sf','df'], default=['sf','df'])
    ap.add_argument('--jet-cat', nargs='+', choices=list(JETCATS), default=list(JETCATS),
                    help='jet-multiplicity categories to pick up when the input has them (default: all)')
    ap.add_argument('--allow-missing', action='store_true', help='mark incomplete curves missing; never merge only part of the requested channels')
    ap.add_argument('--legacy-input', help='old recoil-jet maps, e.g. .../FakeRate/2024_v15_pt; adds the jet-threshold scan, the old-vs-new overlay and the prompt-rate comparison')
    ap.add_argument('--legacy-jet', nargs='+', type=int, help='jet pT thresholds to overlay (default: every one found)')
    ap.add_argument('--legacy-nominal-jet', type=int, default=30, help='threshold the analysis weight reads (default 30)')
    args = ap.parse_args()
    variants = ['ewk','corrected'] if args.variant == 'both' else [args.variant]
    channels = list(dict.fromkeys(args.two_lepton_channels))
    jetcats = [jcat for jcat in JETCATS if jcat in args.jet_cat]
    args.out.mkdir(parents=True,exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR',str((args.out/'.matplotlib').resolve()))
    import matplotlib
    matplotlib.use('Agg')
    groups = {}
    for relative, source in inventory(args.input):
        match = MAP_NAME.match(relative.name)
        if not match: continue
        flavor = 'ele' if match.group(1)=='Ele' else 'mu'
        wp = relative.parent.name if str(relative.parent)!='.' else args.input.rstrip('/').split('/')[-1]
        if flavor not in args.flavor or (args.wp and wp not in args.wp): continue
        groups.setdefault((str(relative.parent),wp,flavor),{})[relative.name] = source
    if not groups: ap.error('No measurement ROOT maps found (expected EleFR_1l_incl.root / MuonFR_1l_incl.root and related maps)')
    legacy = {}
    if args.legacy_input:
        for relative, source in inventory(args.legacy_input):
            directory = (relative.parent.name if str(relative.parent) != '.'
                         else args.legacy_input.rstrip('/').split('/')[-1])
            legacy[(directory, relative.name)] = source
        if not legacy:
            ap.error(f'No legacy ROOT maps found under {args.legacy_input}')
    prepared = []; missing = []; legacy_missing = []
    for (relative,wp,flavor), files in sorted(groups.items()):
        for variant in variants:
            curves = {}; axes = None
            for case in CASES:
                # A b category is expected and its absence is reported. A jet
                # category is opt-in at measurement time, so absent means it
                # was not measured and nothing is said -- but a *partly*
                # present one is still a gap, by the same rule the channels
                # follow: never merge only some of the requested maps.
                for bcat in BCATS:
                    for cat, required in ([(bcat, True)] +
                                          [(f'{bcat}_{jcat}', False) for jcat in jetcats]):
                        names = needed_names(flavor,case,cat,channels)
                        absent = [name for name in names if name not in files]
                        if absent:
                            if required or len(absent) < len(names):
                                missing.append(f'{relative}/{flavor}/{case}/{cat}: '+', '.join(absent))
                            continue
                        curve = project_pt([read_counts(files[name],variant) for name in names])
                        curve['sources'] = [files[name] for name in names]
                        if axes is not None:
                            same_edges(axes[0],curve['pt_edges'],'pT');same_edges(axes[1],curve['eta_edges'],'eta')
                        axes = curve['pt_edges'],curve['eta_edges']
                        curves[f'{case}/{cat}'] = curve
            # Legacy curves keep their own pT binning (up to 50 GeV, 2 |eta|
            # bins), so they are added after the axis-consistency check above.
            pr_curves = {}; bands = []
            if legacy:
                tag, sf = TAGS[flavor]
                jets = legacy_maps(legacy, wp, flavor)
                if args.legacy_jet:
                    jets = {jet: source for jet, source in jets.items() if jet in args.legacy_jet}
                if not jets:
                    legacy_missing.append(f'{relative}/{flavor}: no {tag}FR_jet*.root for WP {wp}')
                for jet, source in sorted(jets.items()):
                    curve = legacy_fr_curve(source, variant)
                    curve['sources'] = [source]
                    curves[f'legacy/jet{jet}'] = curve
                pr_sources = {slot: files.get(f'{tag}PR_{sf}_lep{slot}.root') for slot in (0, 1)}
                pr_legacy = legacy.get((wp, LEGACY_PR[flavor]))
                if pr_legacy is None or not all(pr_sources.values()):
                    legacy_missing.append(f'{relative}/{flavor}: the prompt-rate comparison needs '
                                          f'{LEGACY_PR[flavor]} under the legacy input and '
                                          f'{tag}PR_{sf}_lep0/1.root among the measured maps')
                else:
                    with uproot.open(pr_legacy) as root:
                        legacy_eta = read_hist(root, PR_HIST[flavor], pr_legacy)[3]
                    counts = {slot: read_counts(source, variant) for slot, source in pr_sources.items()}
                    # The reader macro takes h_*_signal_pt_eta_bin, which is the
                    # unsubtracted rate, so it is drawn alongside the variant.
                    raw = ({slot: read_counts(source, 'raw') for slot, source in pr_sources.items()}
                           if variant != 'raw' else {})
                    bands = snap_bands(legacy_eta, counts[0].eta)
                    for index, (_, _, low, high, mask) in enumerate(bands):
                        pr_curves[f'legacy/eta{index}'] = legacy_pr_curve(pr_legacy, flavor, index)
                        for slot in (0, 1):
                            for key, source_counts in [(f'lep{slot}', counts), (f'lep{slot}_raw', raw)]:
                                if slot not in source_counts:
                                    continue
                                curve = project_pt([source_counts[slot]], mask)
                                curve['eta_band'] = [low, high]
                                curve['sources'] = [pr_sources[slot]]
                                pr_curves[f'{key}/eta{index}'] = curve
            prepared.append((relative,wp,flavor,variant,curves,pr_curves,bands))
    if missing and not args.allow_missing:
        ap.error('Required maps are missing:\n'+'\n'.join(missing)+'\nUse --allow-missing only for explicitly partial plots.')
    gallery = []; manifest = dict(input=args.input,variant=args.variant,variants=variants,two_lepton_channels=channels,
                                  eta_integration='sum tight/rest and variances before forming the ratio',
                                  legacy_input=args.legacy_input,legacy_nominal_jet=args.legacy_nominal_jet,
                                  legacy_eta_integration='legacy denominators as fixed weights on the stored per-bin rate errors',
                                  legacy_missing=legacy_missing,
                                  missing=missing,groups=[])
    for relative,wp,flavor,variant,curves,pr_curves,bands in prepared:
        variant_tag = {'ewk':'EWK','corrected':'EWKcorr','raw':'raw'}[variant]
        folder = args.out/relative/flavor;folder.mkdir(parents=True,exist_ok=True)
        context = wp if relative=='.' else relative
        plots = [('inclusive_1lep_vs_2lep',[(f'{case}/incl',label) for case,label in CASES.items()],
                  f'{flavor} · {context} · inclusive')]
        plots += [(f'{case}_inclusive_bjet_bveto',[(f'{case}/{bcat}',label) for bcat,label in BCATS.items()],
                   f'{flavor} · {context} · {CASES[case]}') for case in CASES]
        # One per case and b category, only where jet-binned maps were found.
        # The jet-inclusive curve of the same b category leads, so the plot
        # shows what the split does to the number the analysis uses today.
        for case in CASES:
            for bcat, blabel in BCATS.items():
                entries = [(f'{case}/{bcat}_{jcat}', JETCATS[jcat]) for jcat in jetcats
                           if f'{case}/{bcat}_{jcat}' in curves]
                if not entries:
                    continue
                plots.append((f'{case}_{bcat}_jetbins',
                              [(f'{case}/{bcat}', f'{blabel} · tutti i jet')] + entries,
                              f'{flavor} · {context} · {CASES[case]} · {blabel} · bin di jet'))
        jet_keys = sorted((key for key in curves if key.startswith('legacy/jet')),
                          key=lambda key: int(key.split('jet')[1]))
        if jet_keys:
            plots.append(('legacy_jet_scan',
                          [(key, f'vecchio · jet > {key.split("jet")[1]} GeV') for key in jet_keys]
                          + [('2l_lep0/bveto', 'nuovo · 2 lep, primo lep · bveto')],
                          f'{flavor} · {context} · soglia del jet di rinculo'))
            plots.append(('legacy_vs_measured',
                          [(f'legacy/jet{args.legacy_nominal_jet}',
                            f'vecchio · jet > {args.legacy_nominal_jet} GeV (quello del peso)'),
                           ('1l/bveto', 'nuovo · 1 lep · bveto'),
                           ('2l_lep0/bveto', 'nuovo · 2 lep, primo lep · bveto'),
                           ('2l_lep1/bveto', 'nuovo · 2 lep, secondo lep · bveto')],
                          f'{flavor} · {context} · mappe vecchie vs nuove'))
        for name,entries,title in plots:
            name = f'{name}_{variant_tag}'
            title = f'{title} · {variant_tag}'
            overlay(curves,entries,title,f'{SUBTRACTION[variant]} · integrazione su η',folder/name)
            rel=(folder/name).relative_to(args.out).as_posix()
            gallery.append(f'<section><h2>{html.escape(title)}</h2><a href="{html.escape(rel)}.pdf">PDF</a><img src="{html.escape(rel)}.png"></section>')
        for index,(legacy_low,legacy_high,low,high,_) in enumerate(bands):
            entries = [(f'legacy/eta{index}', 'vecchio (file PR unico)'),
                       (f'lep0/eta{index}', 'nuovo · primo lep'),
                       (f'lep1/eta{index}', 'nuovo · secondo lep')]
            if variant != 'raw':
                entries += [(f'lep0_raw/eta{index}', 'nuovo · primo lep, senza sottrazione (quello del peso)'),
                            (f'lep1_raw/eta{index}', 'nuovo · secondo lep, senza sottrazione (quello del peso)')]
            band = (f'|η| ∈ [{legacy_low:g}, {legacy_high:g}]' if (low, high) == (legacy_low, legacy_high)
                    else f'|η| ∈ [{legacy_low:g}, {legacy_high:g}] vecchio, [{low:g}, {high:g}] nuovo')
            name = f'prompt_rate_eta{index}_{variant_tag}'
            title = f'{flavor} · {context} · prompt rate · {band} · {variant_tag}'
            overlay(pr_curves,entries,title,
                    f'{SUBTRACTION[variant]} per le mappe nuove; il PR vecchio non ha varianti',
                    folder/name,ylabel='Prompt rate')
            rel=(folder/name).relative_to(args.out).as_posix()
            gallery.append(f'<section><h2>{html.escape(title)}</h2><a href="{html.escape(rel)}.pdf">PDF</a><img src="{html.escape(rel)}.png"></section>')
        def dump(table, stem, first_column):
            serial = {key:{field:plain(value) for field,value in curve.items()} for key,curve in table.items()}
            (folder/f'{stem}_{variant_tag}.json').write_text(json.dumps(serial,indent=2,allow_nan=False))
            with (folder/f'{stem}_{variant_tag}.csv').open('w',newline='') as stream:
                writer=csv.writer(stream);writer.writerow(['case',first_column,'pt_low','pt_high','rate','stat_error','tight_subtracted','rest_subtracted','var_tight','var_rest','valid','physical'])
                for key,c in table.items():
                    case,bcat=key.split('/')      # 'bcat' may carry a jet suffix
                    for i in range(len(c['rate'])):
                        writer.writerow([case,bcat,c['pt_edges'][i],c['pt_edges'][i+1],
                                         cell(c['rate'][i]) if c['valid'][i] else '',cell(c['error'][i]) if c['valid'][i] else '',
                                         cell(c['tight'][i]),cell(c['rest'][i]),cell(c['var_tight'][i]),cell(c['var_rest'][i]),
                                         bool(c['valid'][i]),bool(c['physical'][i])])
        dump(curves,'curves','cat')
        if pr_curves:
            dump(pr_curves,'prompt_rate','eta_band')
        invalid=sum(int((~c['valid']).sum()) for c in curves.values())
        nonphysical=sum(int((c['valid'] & ~c['physical']).sum()) for c in curves.values())
        manifest['groups'].append(dict(directory=str(folder),wp=wp,flavor=flavor,variant=variant,curves=len(curves),
                                        legacy_curves=len(jet_keys),prompt_rate_curves=len(pr_curves),
                                        prompt_rate_bands=[dict(legacy=[low,high],measured=[snapped_low,snapped_high])
                                                           for low,high,snapped_low,snapped_high,_ in bands],
                                        invalid_bins=invalid,nonphysical_bins=nonphysical))
        print(f'{relative}/{flavor}/{variant_tag}: {len(curves)} curves, {len(plots)} comparisons, '
              f'{len(bands)} prompt-rate bands; invalid bins={invalid}, nonphysical={nonphysical}')
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    if legacy_missing:
        # One line per gap, not one per subtraction variant.
        legacy_missing = list(dict.fromkeys(legacy_missing))
        print('Legacy comparison skipped where the old maps are absent:\n  ' + '\n  '.join(legacy_missing))
    (args.out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>FR vs pT</title>'
        '<style>body{font-family:system-ui;max-width:1100px;margin:2em auto}img{max-width:100%}section{border-top:1px solid #ccc}</style>'
        '<h1>Fake rate in pT, integrata su η</h1>'+''.join(gallery))
    print(f'Gallery: {args.out/"index.html"}')


if __name__=='__main__':
    main()
