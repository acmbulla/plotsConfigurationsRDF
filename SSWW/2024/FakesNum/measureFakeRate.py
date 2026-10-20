#!/usr/bin/env python3
"""Measure the fake rate and the prompt rate from the FakesNum snapshot.

    ./measureFakeRate.py --snapshot root://eosuser.cern.ch//eos/user/a/abulla/... \
                         --out ../../utils/data/FakeRate --year 2024_v15_pt_measured

What it computes, per (pT, |eta|) bin:

    f = N / (N + R)        N = tight_data - tight_promptMC
                           R = rest_data  - rest_promptMC      rest = loose && !tight

so the denominator is the inclusive loose sample (tight is a subset of loose),
which is the convention fake_rate_reader_class.cc applies with f/(1-f). The
ratio is written as N/(N+R) rather than T/L because N and R are *disjoint*
samples and therefore uncorrelated, which is what makes the uncertainty

    var(f) = ( R^2 var(N) + N^2 var(R) ) / (N + R)^4

correct. Dividing two histograms where one contains the other would need the
covariance instead, and `TH2::Divide(..., "B")` does not have it once the
entries are weighted and prompt-subtracted.

The prompt rate is the same ratio in the DY region with **no** subtraction:
there the leptons are prompt by construction, so what the ratio measures is
the tight efficiency of a real lepton.

Every event has to pass the combined trigger: the OR of the five paths the
analysis uses, the same set on data and on MC (see the HLT block in
../samples.py). It is a requirement and not an option, so data and the prompt
MC that gets subtracted from it are selected the same way -- subtracting an MC
that was not trigger-selected from data that was would leave the difference
wherever the efficiency is not one. TRIGGER_OR below is the one place it is
written down.

No requirement on the jets. The rate is measured on whatever the region holds.

**Loose is FakeObjWP, and it is already applied.** The denominator requires
nothing per lepton on purpose. In mkShapesRDF, LeptonSel("Loose", 1, era)
resolves "Loose" -> "isLoose" -> "FakeObjWP" (LeptonSel_cfg.LepFilter_dict) and
then *redefines the collection itself*:

    Lepton_{pt,eta,phi,pdgId,electronIdx,muonIdx}
        = Lepton_{...}[LeptonMaskHyg_Ele && LeptonMaskHyg_Mu]

with both masks built from ElectronWP[era]["FakeObjWP"] and
MuonWP[era]["FakeObjWP"] (LeptonSel.py:211-217). So every entry of Lepton_* in
an l1loose tree passes FakeObjWP by construction, and the loose denominator
here is

    FakeObjWP  &&  pT > 10 (nLepSel)  &&  |eta| < 2.5 (the supercut)

Do NOT reach for the `isLoose` branch to express it. It is defined before that
redefinition, so it is aligned with the *unfiltered* collection and is a
different length from Lepton_pt; and in a Loose skim it is
`LeptonMaskHyg_Mu || LeptonMaskHyg_Ele` with propagateMask defaulting to true,
so it is true for everything that survives anyway.

`--loose-ele` / `--loose-mu` are therefore not how FakeObjWP is applied; they
exist for the different measurement where the denominator is itself a tight WP,
i.e. the rate from WP_A to WP_B rather than from FakeObjWP to WP_B.

Reading is over xrootd with uproot, one basket set per file, the way
DNN/dnn/dataset.py does it: only the branches needed are fetched, a directory
that starts with root:// is listed with `xrdfs ls`, and a file that cannot be
read is counted and listed rather than fatal, because files arrive while this
runs.

Output, under <out>/<year>/<WP>/, one file per map so the reader can be
pointed straight at it:

    EleFR_1l_<bcat>.root            MuonFR_1l_<bcat>.root
    EleFR_ee_lep0_<bcat>.root       MuonFR_mumu_lep0_<bcat>.root
    EleFR_ee_lep1_<bcat>.root       MuonFR_mumu_lep1_<bcat>.root
    EleFR_emu_lep0_<bcat>.root      MuonFR_emu_lep0_<bcat>.root
    EleFR_emu_lep1_<bcat>.root      MuonFR_emu_lep1_<bcat>.root
    ElePR_ee_lep0_<bcat>.root       MuonPR_mumu_lep0_<bcat>.root
    ElePR_ee_lep1_<bcat>.root       MuonPR_mumu_lep1_<bcat>.root

Each holds the map under the name the reader looks for -- FR_pT_eta_EWKcorr for
a fake rate, h_{Ele,Muon}_signal_pt_eta_bin for a prompt rate -- plus
FR_pT_eta / PR_pT_eta without the subtraction and the four ingredient
histograms (tight/rest x data/MC), because a ratio alone cannot be debugged.
"""

from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
import traceback
from collections import defaultdict

import numpy as np

TREE = "Events"
SNAPSHOT_PREFIX = "nanoLatino_snapshot____"

#: The samples the configuration declares, longest first so the prefix match in
#: `sample_of` is unambiguous (DATA_... vs DY_... is fine, but a sample whose
#: name is a prefix of another is not).
MC_SAMPLES = ("DY", "Wjets", "top", "WZ", "ZZ", "WW")
DATA_SAMPLES = ("DATA",)

#: UParTAK4B discriminant thresholds, copied from aliases.py:355. Kept here and
#: not imported because aliases.py is exec()'d with the framework's namespace.
BTAG_WPS = {"loose": 0.0246, "medium": 0.1272, "tight": 0.4648}
BTAG_BRANCH = "Jet_btagUParTAK4B"

#: The combined trigger, as ../samples.py declares it for 2024: the same five
#: groups of paths for DATA and for MC, OR'd together. A file whose tree is
#: missing one of them -- mkSnapshot drops a column it cannot find in silence,
#: and a primary dataset need not carry every path -- counts that path as false
#: and is reported, rather than being thrown away.
TRIGGER_OR = (
    # EleMu
    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
    "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
    "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
    # DoubleMu
    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
    # SingleMu
    "HLT_IsoMu24",
    # DoubleEle
    "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
    # SingleEle
    "HLT_Ele30_WPTight_Gsf",
)

#: The b-tag regions. See the block in cuts.py: mutually exclusive, and
#: deliberately not exhaustive, because these are the analysis' own thresholds.
BCATS = {
    "incl":  None,
    "bveto": ("==0", 20.),
    "btag":  (">=1", 30.),
}

DEFAULT_PT_BINS  = "10,15,20,25,30,35,45,65,100"
DEFAULT_ETA_ELE  = "0,0.8,1.479,2.0,2.5"
DEFAULT_ETA_MU   = "0,0.9,1.2,2.1,2.4"


# ---------------------------------------------------------------------------
#  Input
# ---------------------------------------------------------------------------

def _split_xrootd(url):
    rest = url[len("root://"):]
    host, _, path = rest.partition("/")
    return host, "/" + path.lstrip("/")


def list_snapshots(directory):
    """Every per-job snapshot file in `directory`, local or on xrootd.

    The merged snapshot_<tag>.root is left out: it has thrown the sample name
    away, and the sample is what says whether a file is data or MC.
    """
    if not directory.startswith("root://"):
        return sorted(glob.glob(os.path.join(directory, SNAPSHOT_PREFIX + "*.root")))

    if shutil.which("xrdfs") is None:
        raise RuntimeError(
            "listing a root:// directory needs the xrootd client (`xrdfs`) on PATH"
        )
    host, path = _split_xrootd(directory)
    proc = subprocess.run(["xrdfs", host, "ls", path],
                          capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        raise RuntimeError(
            f"xrdfs ls {host} {path} failed ({proc.returncode}). "
            f"Is there a Kerberos ticket? `klist`.\n{proc.stderr.strip()}")
    out = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.endswith(".root") and os.path.basename(line).startswith(SNAPSHOT_PREFIX):
            out.append(f"root://{host}/{line}")
    return sorted(out)


def sample_of(path):
    """(sample, is_data) from the file name, or (None, None).

    The name is <prefix><sample>_<subname>_<i>.root and both fields contain
    underscores, so the sample cannot be split out positionally: it is matched
    against what the configuration declares, which is the authority on what
    exists (see the stale-file section of latinoRDF/CLAUDE.md).
    """
    base = os.path.basename(path)[len(SNAPSHOT_PREFIX):]
    for s in sorted(DATA_SAMPLES + MC_SAMPLES, key=len, reverse=True):
        if base.startswith(s + "_"):
            return s, s in DATA_SAMPLES
    return None, None


# ---------------------------------------------------------------------------
#  The maps
# ---------------------------------------------------------------------------

def map_definitions(ele_wps, mu_wps, bcats):
    """Every (name, flavour, index, kind, channel) map to fill.

    kind is 'FR' or 'PR'; channel is the region the lepton is counted in.
    """
    maps = []
    for flav in ("ele", "mu"):
        wps = ele_wps if flav == "ele" else mu_wps
        tag = "Ele" if flav == "ele" else "Muon"
        sf  = "ee" if flav == "ele" else "mumu"
        for wp in wps:
            for bcat in bcats:
                maps.append((f"{tag}FR_1l_{bcat}",        flav, 0, "FR", "1l",    wp, bcat))
                maps.append((f"{tag}FR_{sf}_lep0_{bcat}", flav, 0, "FR", "ss_sf", wp, bcat))
                maps.append((f"{tag}FR_{sf}_lep1_{bcat}", flav, 1, "FR", "ss_sf", wp, bcat))
                maps.append((f"{tag}FR_emu_lep0_{bcat}",  flav, 0, "FR", "ss_df", wp, bcat))
                maps.append((f"{tag}FR_emu_lep1_{bcat}",  flav, 1, "FR", "ss_df", wp, bcat))
                maps.append((f"{tag}PR_{sf}_lep0_{bcat}", flav, 0, "PR", "dy",    wp, bcat))
                maps.append((f"{tag}PR_{sf}_lep1_{bcat}", flav, 1, "PR", "dy",    wp, bcat))
    return maps


# ---------------------------------------------------------------------------
#  One file
# ---------------------------------------------------------------------------

def branches_needed(ele_wps, mu_wps, loose_ele, loose_mu, is_data):
    cols = [
        "nLepSel", "SelLep_pt", "SelLep_eta", "SelLep_pdgId",
        "isSS", "isEE", "isOS", "isSF", "mll", "mt_l0", "PuppiMET_pt",
        "CleanJet_pt", "CleanJet_eta", "CleanJet_jetIdx", BTAG_BRANCH,
    ]
    cols += [f"Lepton_isTightElectron_{w}" for w in ele_wps]
    cols += [f"Lepton_isTightMuon_{w}" for w in mu_wps]
    for b in (loose_ele, loose_mu):
        if b:
            cols.append(b)
    if is_data:
        cols.append("METFilter_DATA")
    else:
        cols += ["XSWeight", "METFilter_Common", "SelLep_promptgenmatched"]
    return list(dict.fromkeys(cols))


def _pad2(arr, fill):
    """A jagged per-lepton array as a regular (n, 2) numpy array."""
    import awkward as ak
    return ak.to_numpy(
        ak.fill_none(ak.pad_none(arr, 2, clip=True), fill, axis=1)
    ).astype(np.float64)


def process_file(args):
    """Fill every map from one file. Returns (accumulators, [messages])."""
    (path, opts) = args
    import awkward as ak
    import uproot

    msgs = []
    sample, is_data = sample_of(path)
    if sample is None:
        return {}, [f"{path}: sample not in the configuration, not used"]

    cols = branches_needed(opts["ele_wps"], opts["mu_wps"],
                           opts["loose_ele"], opts["loose_mu"], is_data)

    last = None
    for attempt in range(opts["retries"] + 1):
        try:
            with uproot.open(f"{path}:{TREE}") as t:
                have = set(t.keys())
                missing = [c for c in cols if c not in have]
                if missing:
                    return {}, [f"{path}: missing branches {missing}, not used"]
                trig_have = [b for b in TRIGGER_OR if b in have]
                trig_miss = [b for b in TRIGGER_OR if b not in have]
                if not trig_have:
                    return {}, [f"{path}: none of the trigger paths is in the "
                                f"tree, not used"]
                a = t.arrays(cols + trig_have, library="ak")
            break
        except Exception as exc:                      # truncated / unreachable
            last = exc
    else:
        return {}, [f"{path}: unreadable after {opts['retries'] + 1} attempts: {last}"]

    if trig_miss:
        msgs.append(f"{os.path.basename(path)}: trigger path(s) absent from the "
                    f"tree, counted as false: {trig_miss}")

    n = len(a["nLepSel"])
    if n == 0:
        return {}, msgs

    nlep = ak.to_numpy(a["nLepSel"]).astype(np.int64)
    pt   = _pad2(a["SelLep_pt"],    np.nan)
    eta  = np.abs(_pad2(a["SelLep_eta"], np.nan))
    pdg  = _pad2(a["SelLep_pdgId"], 0.)
    absp = np.abs(pdg)

    # ---- event weight
    if is_data:
        w = ak.to_numpy(a["METFilter_DATA"]).astype(np.float64)
    else:
        w = (ak.to_numpy(a["XSWeight"]).astype(np.float64)
             * ak.to_numpy(a["METFilter_Common"]).astype(np.float64)
             * opts["lumi"])

    # ---- trigger: required, on data and on MC alike
    fired = np.zeros(n, dtype=bool)
    for b in trig_have:
        fired |= ak.to_numpy(a[b]).astype(bool)

    # ---- b-tag counts, at both thresholds, from the jet collection itself
    idx    = ak.values_astype(a["CleanJet_jetIdx"], np.int64)
    jbtag  = a[BTAG_BRANCH][idx]
    central = np.abs(a["CleanJet_eta"]) < 2.5
    tagged  = jbtag > opts["btag_thr"]
    nb = {}
    for thr in (20., 30.):
        nb[thr] = ak.to_numpy(
            ak.sum((a["CleanJet_pt"] > thr) & central & tagged, axis=1)
        ).astype(np.int64)

    bmask = {}
    for name, spec in BCATS.items():
        if spec is None:
            bmask[name] = np.ones(n, dtype=bool)
        else:
            op, thr = spec
            bmask[name] = (nb[thr] == 0) if op == "==0" else (nb[thr] >= 1)

    # ---- regions, mirroring cuts.py. They must agree with it: the snapshot
    #      holds the union of FR and DY, so re-applying them here is what
    #      separates the two, and a change there needs a change here.
    isSS = ak.to_numpy(a["isSS"]).astype(bool)
    isEE = ak.to_numpy(a["isEE"]).astype(bool)
    isOS = ak.to_numpy(a["isOS"]).astype(bool)
    isSF = ak.to_numpy(a["isSF"]).astype(bool)
    mll  = ak.to_numpy(a["mll"]).astype(np.float64)
    met  = ak.to_numpy(a["PuppiMET_pt"]).astype(np.float64)
    mt0  = ak.to_numpy(a["mt_l0"]).astype(np.float64)

    in_z = np.abs(mll - 91.2) < 15.
    region = {
        "1l":    (nlep == 1) & (met < 30.) & (mt0 < 30.),
        "ss_sf": (nlep == 2) & isSS & isSF & (mll > 12.) & ~(isEE & in_z),
        "ss_df": (nlep == 2) & isSS & ~isSF & (mll > 12.),
        "dy":    (nlep == 2) & isOS & isSF & in_z,
    }
    region = {k: v & fired for k, v in region.items()}

    # ---- per-lepton prompt flag, for the subtraction
    prompt = (_pad2(a["SelLep_promptgenmatched"], 0.) > 0.5
              if not is_data else None)

    # ---- loose, per lepton: the skim's loose ID unless a branch was named
    loose = {}
    for flav, branch in (("ele", opts["loose_ele"]), ("mu", opts["loose_mu"])):
        if branch:
            loose[flav] = _pad2(a[branch], 0.) > 0.5
        else:
            loose[flav] = np.ones_like(pt, dtype=bool)

    acc = defaultdict(lambda: np.zeros(0))
    for (name, flav, i, kind, chan, wp, bcat) in opts["maps"]:
        if i >= 2:
            continue
        want_pdg = 11 if flav == "ele" else 13
        tight_branch = (f"Lepton_isTightElectron_{wp}" if flav == "ele"
                        else f"Lepton_isTightMuon_{wp}")
        tight = _pad2(a[tight_branch], 0.) > 0.5

        sel = (region[chan] & bmask[bcat] & (nlep > i)
               & (absp[:, i] == want_pdg) & loose[flav][:, i]
               & np.isfinite(pt[:, i]) & (w != 0.))
        if is_data:
            wsel = w
        else:
            # only prompt leptons are subtracted: the fake ones in MC are the
            # very thing being measured
            sel = sel & prompt[:, i]
            wsel = w
        if not sel.any():
            continue

        x, y, ww = pt[sel, i], eta[sel, i], wsel[sel]
        t = tight[sel, i]

        xb, yb = opts["bins"][flav]
        # pT above the last edge is CLIPPED into the last bin, because that is
        # what the reader does when it applies the map
        # (GetRate: FindBin(min(pt, lepton_pt_max), |eta|)), so the last bin
        # has to describe those leptons.
        #
        # |eta| outside the binning is DROPPED, not clipped: there the reader
        # lands in the overflow bin and reads 0, so such leptons are not
        # described by the map at all and folding them into the last bin would
        # contaminate the bin that is used.
        inrange = (y >= yb[0]) & (y < yb[-1])
        x, y, ww, t = x[inrange], y[inrange], ww[inrange], t[inrange]
        if x.size == 0:
            continue
        x = np.clip(x, xb[0], xb[-1] - 1e-6)
        for part, m in (("tight", t), ("rest", ~t)):
            if not m.any():
                continue
            h, _, _  = np.histogram2d(x[m], y[m], bins=[xb, yb], weights=ww[m])
            h2, _, _ = np.histogram2d(x[m], y[m], bins=[xb, yb], weights=ww[m] ** 2)
            key_w  = (name, part, "data" if is_data else "mc", "sumw")
            key_w2 = (name, part, "data" if is_data else "mc", "sumw2")
            for key, val in ((key_w, h), (key_w2, h2)):
                if acc[key].size == 0:
                    acc[key] = val
                else:
                    acc[key] = acc[key] + val

    return dict(acc), msgs


# ---------------------------------------------------------------------------
#  Ratio and output
# ---------------------------------------------------------------------------

def ratio_with_errors(Td, Td2, Rd, Rd2, Tm, Tm2, Rm, Rm2, subtract):
    """f = N/(N+R) and its uncertainty, N and R disjoint and uncorrelated."""
    if subtract:
        N, varN = Td - Tm, Td2 + Tm2
        R, varR = Rd - Rm, Rd2 + Rm2
    else:
        N, varN = Td, Td2
        R, varR = Rd, Rd2

    D = N + R
    f = np.zeros_like(D)
    e = np.zeros_like(D)
    ok = D > 0.
    f[ok] = N[ok] / D[ok]
    e[ok] = np.sqrt(np.maximum(
        (R[ok] ** 2 * varN[ok] + N[ok] ** 2 * varR[ok]) / D[ok] ** 4, 0.))
    return f, e, ok


def write_map(path, hist_name, f, e, ingredients, xb, yb, title):
    import ROOT
    ROOT.gROOT.SetBatch(True)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fh = ROOT.TFile.Open(path, "RECREATE")

    def _mk(name, values, errors=None):
        h = ROOT.TH2F(name, title, len(xb) - 1, np.asarray(xb, dtype=np.float64),
                      len(yb) - 1, np.asarray(yb, dtype=np.float64))
        h.GetXaxis().SetTitle("p_{T} [GeV]")
        h.GetYaxis().SetTitle("|#eta|")
        for ix in range(values.shape[0]):
            for iy in range(values.shape[1]):
                h.SetBinContent(ix + 1, iy + 1, float(values[ix, iy]))
                if errors is not None:
                    h.SetBinError(ix + 1, iy + 1, float(errors[ix, iy]))
        h.Write()
        return h

    _mk(hist_name, f, e)
    for name, (vals, errs) in ingredients.items():
        _mk(name, vals, errs)
    fh.Close()


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--snapshot", required=True,
                    help="snapshot directory, local or root://host//path")
    ap.add_argument("--out", default="FakeRateMeasured",
                    help="output base; files land in <out>/<year>/<WP>/")
    ap.add_argument("--year", default="2024_v15_pt_measured",
                    help="the directory fake_rate_reader is given as its year")
    ap.add_argument("--lumi", type=float, default=110.11)
    ap.add_argument("--ele-wp", action="append", default=[],
                    help="electron tight WP, repeatable; default: all in the tree")
    ap.add_argument("--mu-wp", action="append", default=[])
    ap.add_argument("--bcat", action="append", default=[],
                    choices=sorted(BCATS), help="default: bveto and btag")
    ap.add_argument("--btag-wp", default="loose", choices=sorted(BTAG_WPS),
                    help="the b-tag WP the regions are built with (analysis: loose)")
    ap.add_argument("--loose-ele", default="", help="branch defining loose electrons")
    ap.add_argument("--loose-mu", default="", help="branch defining loose muons")
    ap.add_argument("--pt-bins", default=DEFAULT_PT_BINS)
    ap.add_argument("--eta-bins-ele", default=DEFAULT_ETA_ELE)
    ap.add_argument("--eta-bins-mu", default=DEFAULT_ETA_MU)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--max-files", type=int, default=0)
    opt = ap.parse_args()

    files = list_snapshots(opt.snapshot)
    if opt.max_files:
        files = files[:opt.max_files]
    if not files:
        sys.exit(f"no {SNAPSHOT_PREFIX}*.root under {opt.snapshot}")

    # WPs: whatever the first readable file carries, unless asked
    ele_wps, mu_wps = opt.ele_wp, opt.mu_wp
    if not ele_wps or not mu_wps:
        import uproot
        with uproot.open(f"{files[0]}:{TREE}") as t:
            keys = list(t.keys())
        if not ele_wps:
            ele_wps = sorted(k[len("Lepton_isTightElectron_"):] for k in keys
                             if k.startswith("Lepton_isTightElectron_"))
        if not mu_wps:
            mu_wps = sorted(k[len("Lepton_isTightMuon_"):] for k in keys
                            if k.startswith("Lepton_isTightMuon_"))

    bcats = opt.bcat or ["bveto", "btag"]
    bins = {
        "ele": ([float(x) for x in opt.pt_bins.split(",")],
                [float(x) for x in opt.eta_bins_ele.split(",")]),
        "mu":  ([float(x) for x in opt.pt_bins.split(",")],
                [float(x) for x in opt.eta_bins_mu.split(",")]),
    }
    maps = map_definitions(ele_wps, mu_wps, bcats)

    print(f"  files        : {len(files)}")
    print(f"  electron WPs : {len(ele_wps)}  {ele_wps}")
    print(f"  muon WPs     : {len(mu_wps)}  {mu_wps}")
    print(f"  b-tag regions: {bcats}  (WP {opt.btag_wp} = {BTAG_WPS[opt.btag_wp]})")
    print(f"  jets         : no requirement")
    print(f"  loose        : FakeObjWP, applied by the skim"
          + (f" + {opt.loose_ele or ''} {opt.loose_mu or ''}".rstrip()
             if (opt.loose_ele or opt.loose_mu) else ""))
    print(f"  trigger      : OR of {len(TRIGGER_OR)} paths, required")
    print(f"  maps         : {len(maps)}")

    opts = {
        "ele_wps": ele_wps, "mu_wps": mu_wps, "maps": maps, "bins": bins,
        "lumi": opt.lumi,
        "loose_ele": opt.loose_ele, "loose_mu": opt.loose_mu,
        "btag_thr": BTAG_WPS[opt.btag_wp], "retries": opt.retries,
    }

    total = defaultdict(lambda: None)
    problems = []
    payload = [(f, opts) for f in files]

    if opt.workers > 1:
        import multiprocessing as mp
        with mp.Pool(opt.workers) as pool:
            results = pool.imap_unordered(process_file, payload)
            for i, (acc, msgs) in enumerate(results, 1):
                problems.extend(msgs)
                for k, v in acc.items():
                    total[k] = v if total[k] is None else total[k] + v
                if i % 50 == 0:
                    print(f"    {i}/{len(files)} files")
    else:
        for i, item in enumerate(payload, 1):
            try:
                acc, msgs = process_file(item)
            except Exception:
                problems.append(f"{item[0]}: {traceback.format_exc(limit=1)}")
                continue
            problems.extend(msgs)
            for k, v in acc.items():
                total[k] = v if total[k] is None else total[k] + v
            if i % 50 == 0:
                print(f"    {i}/{len(files)} files")

    if problems:
        print(f"\n  {len(problems)} message(s) from the read:")
        for p in problems[:20]:
            print(f"    {p}")
        if len(problems) > 20:
            print(f"    ... and {len(problems) - 20} more")

    # ---- ratios and output
    def grab(name, part, src, moment, flav):
        s = (len(bins[flav][0]) - 1, len(bins[flav][1]) - 1)
        v = total.get((name, part, src, moment))
        return np.zeros(s) if v is None else v

    written, empty, outofrange = 0, [], []
    for (name, flav, i, kind, chan, wp, bcat) in maps:
        xb, yb = bins[flav]
        Td, Td2 = grab(name, "tight", "data", "sumw", flav), grab(name, "tight", "data", "sumw2", flav)
        Rd, Rd2 = grab(name, "rest",  "data", "sumw", flav), grab(name, "rest",  "data", "sumw2", flav)
        Tm, Tm2 = grab(name, "tight", "mc",   "sumw", flav), grab(name, "tight", "mc",   "sumw2", flav)
        Rm, Rm2 = grab(name, "rest",  "mc",   "sumw", flav), grab(name, "rest",  "mc",   "sumw2", flav)

        if (Td + Rd).sum() == 0.:
            empty.append(name)
            continue

        subtract = (kind == "FR")
        f, e, ok = ratio_with_errors(Td, Td2, Rd, Rd2, Tm, Tm2, Rm, Rm2, subtract)
        bad = int(((f < 0.) | (f >= 1.)).sum())
        if bad:
            outofrange.append((name, bad))

        if kind == "FR":
            hist_name = "FR_pT_eta_EWKcorr"
            raw, raw_e, _ = ratio_with_errors(Td, Td2, Rd, Rd2, Tm, Tm2, Rm, Rm2, False)
            ingredients = {
                "FR_pT_eta":    (raw, raw_e),
                "h_tight_data": (Td, np.sqrt(Td2)),
                "h_rest_data":  (Rd, np.sqrt(Rd2)),
                "h_tight_mc":   (Tm, np.sqrt(Tm2)),
                "h_rest_mc":    (Rm, np.sqrt(Rm2)),
            }
        else:
            hist_name = ("h_Ele_signal_pt_eta_bin" if flav == "ele"
                         else "h_Muon_signal_pt_eta_bin")
            ingredients = {
                "PR_pT_eta":    (f, e),
                "h_tight_data": (Td, np.sqrt(Td2)),
                "h_rest_data":  (Rd, np.sqrt(Rd2)),
            }

        wp_dir = wp
        path = os.path.join(os.path.expandvars(opt.out), opt.year, wp_dir, name + ".root")
        write_map(path, hist_name, f, e, ingredients, xb, yb,
                  f"{name};p_{{T}} [GeV];|#eta|")
        written += 1

    print(f"\n  {written} map(s) written under "
          f"{os.path.join(os.path.expandvars(opt.out), opt.year)}")
    if empty:
        print(f"  {len(empty)} map(s) had no data entries and were skipped: "
              f"{', '.join(empty[:8])}" + (" ..." if len(empty) > 8 else ""))
    if outofrange:
        print(f"  {len(outofrange)} map(s) have bins outside [0,1) after the "
              f"subtraction -- not clipped, look at them:")
        for name, nbad in outofrange[:10]:
            print(f"    {name}: {nbad} bin(s)")


if __name__ == "__main__":
    main()
