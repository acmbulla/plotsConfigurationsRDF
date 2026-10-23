#!/usr/bin/env python3
"""Compare measureFakeRate.py ROOT maps after integrating their counts in eta.

Per flavor/WP: one inclusive 1l/2l-lep0/2l-lep1 overlay and three
inclusive/btag/bveto overlays. 2l combines SS SF+DF by default.
No ROOT Python bindings needed: numpy, uproot and matplotlib are sufficient.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import html
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
MAP_NAME = re.compile(r'^(Ele|Muon)FR_(?:1l|ee_lep[01]|mumu_lep[01]|emu_lep[01])_(?:incl|btag|bveto)\.root$')


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


def project_pt(parts):
    """Tight/rest are disjoint. Independent channels and eta bins add in yield/variance."""
    first = parts[0]
    for other in parts[1:]:
        same_edges(first.pt, other.pt, 'pT'); same_edges(first.eta, other.eta, 'eta')
    n, vn, rest, vrest = [sum(getattr(p, field).sum(axis=1) for p in parts)
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


def needed_names(flavor, case, bcat, channels):
    tag, sf = TAGS[flavor]
    if case == '1l':
        return [f'{tag}FR_1l_{bcat}.root']
    slot = 0 if case == '2l_lep0' else 1
    return [f'{tag}FR_{sf if channel == "sf" else "emu"}_lep{slot}_{bcat}.root'
            for channel in channels]


def plain(value):
    if isinstance(value, np.ndarray):
        return [None if isinstance(v, (float, np.floating)) and not np.isfinite(v)
                else v.item() if isinstance(v, np.generic) else v for v in value]
    return value


def overlay(curves, entries, title, target, variant):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 6))
    bounds = []
    found = 0
    for (key, label), color, marker in zip(entries, ['#0072B2', '#D55E00', '#009E73'], ['o', 's', '^']):
        curve = curves.get(key)
        if curve is None:
            ax.plot([], [], color=color, marker=marker, ls='none', label=label+' [mancante]')
            continue
        valid = curve['valid']; pt = curve['pt_edges']; x = (pt[:-1]+pt[1:])/2
        rate, error = curve['rate'], curve['error']
        ax.errorbar(x, rate, yerr=error, xerr=np.diff(pt)/2, color=color, marker=marker,
                    label=label, capsize=2, lw=1.2, ms=4)
        nonphysical = valid & ~curve['physical']
        ax.scatter(x[nonphysical], rate[nonphysical], facecolors='none', edgecolors='red', s=90, zorder=5)
        bounds.extend((rate[valid]-error[valid]).tolist()+(rate[valid]+error[valid]).tolist())
        found += 1
    ax.axhline(0, lw=.7, color='#777')
    if bounds:
        lo, hi = min(0., min(bounds)), max(.05, max(bounds))
        margin = .08*max(hi-lo, .05); ax.set_ylim(lo-margin, hi+margin)
        if hi > 1: ax.axhline(1, lw=.7, color='#777', ls='--')
    labels = {'corrected': 'dati − prompt MC con SF DY', 'ewk': 'dati − prompt MC', 'raw': 'dati, senza sottrazione'}
    ax.set(title=title+f'\n{labels[variant]} · integrazione su η', xlabel=r'$p_T$ [GeV]', ylabel='Fake rate')
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
    ap.add_argument('--variant', choices=['corrected','ewk','raw'], default='corrected')
    ap.add_argument('--two-lepton-channels', nargs='+', choices=['sf','df'], default=['sf','df'])
    ap.add_argument('--allow-missing', action='store_true', help='mark incomplete curves missing; never merge only part of the requested channels')
    args = ap.parse_args()
    channels = list(dict.fromkeys(args.two_lepton_channels))
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
    prepared = []; missing = []
    for (relative,wp,flavor), files in sorted(groups.items()):
        curves = {}; axes = None
        for case in CASES:
            for bcat in BCATS:
                names = needed_names(flavor,case,bcat,channels)
                absent = [name for name in names if name not in files]
                if absent:
                    missing.append(f'{relative}/{flavor}/{case}/{bcat}: '+', '.join(absent))
                    continue
                curve = project_pt([read_counts(files[name],args.variant) for name in names])
                curve['sources'] = [files[name] for name in names]
                if axes is not None:
                    same_edges(axes[0],curve['pt_edges'],'pT');same_edges(axes[1],curve['eta_edges'],'eta')
                axes = curve['pt_edges'],curve['eta_edges']
                curves[f'{case}/{bcat}'] = curve
        prepared.append((relative,wp,flavor,curves))
    if missing and not args.allow_missing:
        ap.error('Required maps are missing:\n'+'\n'.join(missing)+'\nUse --allow-missing only for explicitly partial plots.')
    gallery = []; manifest = dict(input=args.input,variant=args.variant,two_lepton_channels=channels,
                                  eta_integration='sum tight/rest and variances before forming the ratio',
                                  missing=missing,groups=[])
    for relative,wp,flavor,curves in prepared:
        folder = args.out/relative/flavor;folder.mkdir(parents=True,exist_ok=True)
        context = wp if relative=='.' else relative
        plots = [('inclusive_1lep_vs_2lep',[(f'{case}/incl',label) for case,label in CASES.items()],
                  f'{flavor} · {context} · inclusive')]
        plots += [(f'{case}_inclusive_bjet_bveto',[(f'{case}/{bcat}',label) for bcat,label in BCATS.items()],
                   f'{flavor} · {context} · {CASES[case]}') for case in CASES]
        for name,entries,title in plots:
            overlay(curves,entries,title,folder/name,args.variant)
            rel=(folder/name).relative_to(args.out).as_posix()
            gallery.append(f'<section><h2>{html.escape(title)}</h2><a href="{html.escape(rel)}.pdf">PDF</a><img src="{html.escape(rel)}.png"></section>')
        serial = {key:{field:plain(value) for field,value in curve.items()} for key,curve in curves.items()}
        (folder/'curves.json').write_text(json.dumps(serial,indent=2,allow_nan=False))
        with (folder/'curves.csv').open('w',newline='') as stream:
            writer=csv.writer(stream);writer.writerow(['case','bcat','pt_low','pt_high','FR','stat_error','tight_subtracted','rest_subtracted','var_tight','var_rest','valid','physical'])
            for key,c in curves.items():
                case,bcat=key.split('/')
                for i in range(len(c['rate'])):
                    writer.writerow([case,bcat,c['pt_edges'][i],c['pt_edges'][i+1],
                                     c['rate'][i] if c['valid'][i] else '',c['error'][i] if c['valid'][i] else '',
                                     c['tight'][i],c['rest'][i],c['var_tight'][i],c['var_rest'][i],bool(c['valid'][i]),bool(c['physical'][i])])
        invalid=sum(int((~c['valid']).sum()) for c in curves.values())
        nonphysical=sum(int((c['valid'] & ~c['physical']).sum()) for c in curves.values())
        manifest['groups'].append(dict(directory=str(folder),wp=wp,flavor=flavor,curves=len(curves),
                                        invalid_bins=invalid,nonphysical_bins=nonphysical))
        print(f'{relative}/{flavor}: {len(curves)} curves, 4 comparisons; invalid bins={invalid}, nonphysical={nonphysical}')
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    (args.out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>FR vs pT</title>'
        '<style>body{font-family:system-ui;max-width:1100px;margin:2em auto}img{max-width:100%}section{border-top:1px solid #ccc}</style>'
        '<h1>Fake rate in pT, integrata su η</h1>'+''.join(gallery))
    print(f'Gallery: {args.out/"index.html"}')


if __name__=='__main__':
    main()
