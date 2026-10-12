#!/usr/bin/env python3
"""
Scala gli istogrammi MC di un file mkShapes.

Non usa UPDATE: legge il file (copiato in locale) e scrive un file NUOVO in
tmpdir con gli istogrammi MC scalati, poi sovrascrive l'originale.
Scrivere da zero e' lineare; l'overwrite in UPDATE e' quadratico nel numero
di chiavi (ogni delete aggiorna la lista dei segmenti liberi).

Esempio:
  python3 scale_mc.py ../2024/rootFile/WW_260923_test24/mkShapes__WW_260923_test24.root 2.5
"""
import argparse
import logging
import os
import shutil
import subprocess
import sys
import time

import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.TH1.AddDirectory(False)   # niente oggetti agganciati alle directory in memoria

MARKER = "mc_rescaled_factor"

parser = argparse.ArgumentParser()
parser.add_argument("--file", help="file root di origine (anche su /eos)")
parser.add_argument("--factor", type=float, help="fattore di scala per il MC")
parser.add_argument("--tmpdir", default="/tmp/abulla")
parser.add_argument("--skip", nargs="+", default=["DATA", "Fake"],
                    help="campioni da NON scalare (match esatto o prefisso + '_')")
parser.add_argument("--keep-backup", action="store_true",
                    help="conserva in tmpdir la copia originale non scalata")
parser.add_argument("--xrdcp", action="store_true",
                    help="copia con xrdcp invece che via mount (spesso molto piu' veloce su EOS)")
parser.add_argument("--log-every", type=int, default=2000,
                    help="stampa il progresso ogni N istogrammi")
parser.add_argument("--dry-run", action="store_true",
                    help="fa tutto in locale ma NON sovrascrive l'originale")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger()


def human(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def to_xrootd(path):
    # /eos/user/a/abulla/... -> root://eosuser.cern.ch//eos/user/a/abulla/...
    if path.startswith("/eos/user"):
        return "root://eosuser.cern.ch/" + path
    if path.startswith("/eos/cms"):
        return "root://eoscms.cern.ch/" + path
    return path


def copy(a, b, label):
    t0 = time.time()
    if args.xrdcp and (a.startswith("/eos") or b.startswith("/eos")):
        subprocess.run(["xrdcp", "-f", "-s", to_xrootd(a), to_xrootd(b)], check=True)
    else:
        shutil.copyfile(a, b)
    dt = time.time() - t0
    size = os.path.getsize(b) if os.path.exists(b) else os.path.getsize(a)
    log.info(f"{label}: {human(size)} in {dt:.1f} s ({human(size / max(dt, 1e-6))}/s)")


src = os.path.abspath(args.file)
os.makedirs(args.tmpdir, exist_ok=True)
base = os.path.basename(src)
local_in = os.path.join(args.tmpdir, base + ".orig")
local_out = os.path.join(args.tmpdir, base)

T0 = time.time()

# 1) copia locale dell'originale
log.info(f"[1/4] Copio in locale: {src}")
copy(src, local_in, "      copia EOS -> tmp")

# 2) scrivo un file nuovo con il MC scalato
fin = ROOT.TFile.Open(local_in, "READ")
if not fin or fin.IsZombie():
    sys.exit(f"Impossibile aprire {local_in}")
if fin.Get(MARKER):
    prev = fin.Get(MARKER).GetTitle()
    fin.Close()
    sys.exit(f"ERRORE: file gia' scalato (fattore {prev}). Non faccio nulla.")

fout = ROOT.TFile.Open(local_out, "RECREATE")
fout.SetCompressionSettings(fin.GetCompressionSettings())

stats = {"scaled": 0, "skipped": 0, "other": 0, "dirs": 0}
skipped_prefixes = set()
t_scan = time.time()
t_last = t_scan


def is_skipped(sample):
    return any(sample == s or sample.startswith(s + "_") for s in args.skip)


def progress():
    global t_last
    n = stats["scaled"] + stats["skipped"]
    if n and n % args.log_every == 0:
        now = time.time()
        rate = args.log_every / max(now - t_last, 1e-6)
        log.info(f"      {n} istogrammi processati  ({rate:.0f} histo/s, "
                 f"{stats['dirs']} directory, {now - t_scan:.1f} s)")
        t_last = now


def process(din, dout):
    stats["dirs"] += 1
    seen = set()
    # lista statica delle chiavi: niente modifiche alla lista durante l'iterazione
    keys = list(din.GetListOfKeys())
    for key in keys:
        name = key.GetName()
        if name in seen:          # tiene solo il cycle piu' alto (il primo in lista)
            continue
        seen.add(name)

        cls = ROOT.TClass.GetClass(key.GetClassName())

        if cls.InheritsFrom("TDirectory"):
            sub_in = din.Get(name)
            sub_out = dout.mkdir(name)
            process(sub_in, sub_out)
            continue

        obj = key.ReadObj()

        if cls.InheritsFrom("TH1") and name.startswith("histo_"):
            sample = name[len("histo_"):]
            if is_skipped(sample):
                stats["skipped"] += 1
                skipped_prefixes.add(sample.split("_")[0])
            else:
                obj.Scale(args.factor)
                stats["scaled"] += 1
            dout.WriteTObject(obj, name)
            progress()
        elif cls.InheritsFrom("TTree"):
            dout.cd()
            obj.CloneTree(-1, "fast").Write(name)
            stats["other"] += 1
        else:
            dout.WriteTObject(obj, name)
            stats["other"] += 1


log.info(f"[2/4] Scalo il MC di un fattore {args.factor} e scrivo {local_out}")
process(fin, fout)
fout.cd()
ROOT.TNamed(MARKER, str(args.factor)).Write()
fout.Close()
fin.Close()

log.info(f"      scalati: {stats['scaled']}, saltati: {stats['skipped']}, "
         f"altri oggetti: {stats['other']}, directory: {stats['dirs']}")
log.info(f"      prefissi saltati: {sorted(skipped_prefixes)}")
log.info(f"      scansione completata in {time.time() - t_scan:.1f} s "
         f"(in: {human(os.path.getsize(local_in))}, out: {human(os.path.getsize(local_out))})")

# 3) sovrascrivo l'originale
if args.dry_run:
    log.info("[3/4] --dry-run: NON sovrascrivo l'originale. Output in " + local_out)
else:
    log.info(f"[3/4] Sovrascrivo {src}")
    copy(local_out, src, "      copia tmp -> EOS")
    if os.path.getsize(local_out) != os.path.getsize(src):
        sys.exit("ERRORE: dimensione su origine diversa da quella locale!")
    os.remove(local_out)

# 4) pulizia
if not args.keep_backup and not args.dry_run:
    os.remove(local_in)
else:
    log.info(f"      originale non scalato conservato in {local_in}")

log.info(f"[4/4] Fatto in {time.time() - T0:.1f} s totali.")