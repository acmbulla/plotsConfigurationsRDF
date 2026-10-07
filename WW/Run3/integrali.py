import sys
import ctypes
import math
import ROOT

ROOT.gROOT.SetBatch(True)

fname = sys.argv[1] if len(sys.argv) > 1 else "histos.root"
variable = sys.argv[2] if len(sys.argv) > 2 else "events"

REGIONS = ["WW_SR", "nonprompt_CR", "WZ_SR", "WZb_CR"]
SCALE = 170.0 / 110.0      # = 1 / (307/170)
SCALE_DATA = True          # scala anche i dati
DATA_NAMES = ["DATA"]      # nome/i del sample dei dati nel file

# ---------------------------------------------------------------------------
# Valori di riferimento (tabella del draft): {processo: {regione: (val, err)}}
# ---------------------------------------------------------------------------
REF = {
    "EW WW":       {"WW_SR": (260.8, 20.3), "nonprompt_CR": (90.1, 7.5)},
    "QCD WW":      {"WW_SR": (25.2, 5.1),   "nonprompt_CR": (17.5, 3.5)},
    "EW WZ":       {"WW_SR": (18.4, 2.0),   "nonprompt_CR": (8.6, 0.8),   "WZ_SR": (115.1, 25.3), "WZb_CR": (0.7, 0.1)},
    "QCD WZ":      {"WW_SR": (45.1, 6.1),   "nonprompt_CR": (39.1, 3.7),  "WZ_SR": (269.8, 70.5), "WZb_CR": (10.5, 1.6)},
    "ZZ":          {"WW_SR": (1.5, 0.2),    "nonprompt_CR": (1.4, 0.1),   "WZ_SR": (19.3, 4.1),   "WZb_CR": (0.9, 0.1)},
    "Nonprompt":   {"WW_SR": (140.3, 40.2), "nonprompt_CR": (362.1, 43.7), "WZ_SR": (50.3, 28.1), "WZb_CR": (16.6, 8.8)},
    "VVV":         {"WW_SR": (9.6, 2.4),    "nonprompt_CR": (20.9, 4.5),  "WZ_SR": (11.1, 3.8),   "WZb_CR": (0.4, 0.1)},
    "tVx":         {"WW_SR": (3.7, 1.2),    "nonprompt_CR": (45.4, 3.8),  "WZ_SR": (41.1, 21.6),  "WZb_CR": (94.9, 6.1)},
    "Wgamma":      {"WW_SR": (21.8, 9.9),   "nonprompt_CR": (10.7, 3.8),  "WZ_SR": (4.3, 4.7),    "WZb_CR": (0.1, 0.1)},
    "Wrong-sign":  {"WW_SR": (14.6, 6.6),   "nonprompt_CR": (40.5, 12.4)},
    "Higgs":       {"WZ_SR": (2.7, 1.7),    "WZb_CR": (1.4, 0.3)},
    "Total SM":    {"WW_SR": (541.1, 23.3), "nonprompt_CR": (636.4, 25.2), "WZ_SR": (513.6, 22.7), "WZb_CR": (125.4, 11.2)},
    "Data":        {"WW_SR": (575, 0),      "nonprompt_CR": (634, 0),     "WZ_SR": (554, 0),      "WZb_CR": (137, 0)},
    # somma EW WW + QCD WW (il sample VBS_SSWW le contiene entrambe)
    "EW+QCD WW":   {"WW_SR": (286.0, 20.9), "nonprompt_CR": (107.6, 8.3)},
}

# ---------------------------------------------------------------------------
# Quali sample del file (nome dopo "histo_") compongono ogni processo della tabella.
# I polarizzati VBS_SSWW_WWCM_* sono esclusi apposta (gia' contenuti in VBS_SSWW).
# ---------------------------------------------------------------------------
MAP = {
    "EW+QCD WW":  ["WW_EWK", "WW_QCD", "WW_Int"],
    "EW WZ":      ["WZJJ_EWK", "WZSJJ_EWK"],                      # manca
    "QCD WZ":     ["WZJJ_QCD", "WZSJJ_QCD"],
    "ZZ":         ["ZZ"],
    "Nonprompt":  ["Fake"],
    "VVV":        ["VVV"],
    "tVx":        ["tVx"],                      # manca
    "Wgamma":     ["Wg", "WgS", "Zg", "ZgS"],
    "Wrong-sign": ["DY", "top", "ggWW", "OSWW"],
    "Higgs":      ["ggH_hww", "qqH_hww", "higgs"],
}


def read_region(f, region):
    """Ritorna {sample: (integrale, errore)} per region/variable (solo nominali)."""
    d = f.Get(f"{region}/{variable}")
    if not d:
        print(f"ATTENZIONE: {region}/{variable} non trovata")
        return {}
    out = {}
    for key in d.GetListOfKeys():
        obj = key.ReadObj()
        if not obj.InheritsFrom("TH1"):
            continue
        name = obj.GetName()
        if name.endswith("Up") or name.endswith("Down"):
            continue  # variazioni sistematiche
        sample = name[len("histo_"):] if name.startswith("histo_") else name
        err = ctypes.c_double(0.0)
        val = obj.IntegralAndError(1, obj.GetNbinsX(), err)
        s = SCALE if (sample not in DATA_NAMES or SCALE_DATA) else 1.0
        out[sample] = (val * s, err.value * s)
    return out


def qsum(items):
    return (sum(v for v, _ in items), math.sqrt(sum(e * e for _, e in items)))


f = ROOT.TFile.Open(fname)
if not f or f.IsZombie():
    sys.exit(f"Impossibile aprire {fname}")

data = {r: read_region(f, r) for r in REGIONS}
f.Close()

# ---- 1) tutti gli istogrammi trovati, per regione --------------------------
samples = sorted({s for r in REGIONS for s in data[r]})
w = max([len("Sample")] + [len(s) for s in samples])
cw = 20
print("\n=== Integrali dal file (tutto x 170/307) ===\n")
print(f"{'Sample':<{w}}" + "".join(f"{r:>{cw}}" for r in REGIONS))
print("-" * (w + cw * len(REGIONS)))
for s in samples:
    row = f"{s:<{w}}"
    for r in REGIONS:
        row += f"{(f'{data[r][s][0]:.1f} +- {data[r][s][1]:.1f}' if s in data[r] else '---'):>{cw}}"
    print(row)

# ---- 2) confronto con la tabella -------------------------------------------
mine = {}
for proc, sl in MAP.items():
    mine[proc] = {}
    for r in REGIONS:
        found = [data[r][s] for s in sl if s in data[r]]
        if found:
            mine[proc][r] = qsum(found)

mapped = {s for sl in MAP.values() for s in sl}
unmapped = [s for s in samples if s not in mapped and s not in DATA_NAMES]
if unmapped:
    print(f"\nATTENZIONE: sample non assegnati a nessun processo (esclusi dal Total SM): {unmapped}")

mine["Total SM"] = {r: qsum([data[r][s] for s in data[r] if s in mapped]) for r in REGIONS}
mine["Data"] = {r: qsum([data[r][s] for s in DATA_NAMES if s in data[r]]) for r in REGIONS}

print("\n=== Confronto: file / tabella (rapporto) ===\n")
pw = max(len(p) for p in REF)
cw = 32
print(f"{'Processo':<{pw}}" + "".join(f"{r:>{cw}}" for r in REGIONS))
print("-" * (pw + cw * len(REGIONS)))
for proc in REF:
    row = f"{proc:<{pw}}"
    for r in REGIONS:
        ref = REF[proc].get(r)
        me = mine.get(proc, {}).get(r)
        if ref is None and me is None:
            cell = "---"
        elif ref is None:
            cell = f"{me[0]:.1f} / ---"
        elif me is None:
            cell = f"--- / {ref[0]:.1f}"
        else:
            ratio = me[0] / ref[0] if ref[0] else float("nan")
            cell = f"{me[0]:.1f} / {ref[0]:.1f} ({ratio:.2f})"
        row += f"{cell:>{cw}}"
    print(row)