#!/usr/bin/env python3
"""Wrap an exported DNN weight file in a ROOT file so xrootd can serve it.

`dnn_reader` reads a plain text file directly, which is what a local run or an
eosfuse mount wants. A batch node is different: the b-tag and fake-rate maps
reach it as `root://eosuser.cern.ch//eos/...` because that is the one transport
the job is guaranteed to have, and a bare POSIX path to /eos is not. So the
text goes inside a TObjString called `weights` and the reader opens it with
TFile::Open, which handles the URL.

    python3 pack_dnn_weights.py twostage_uparT_open_64x32.dnn \
            ../data/dnn/twostage_uparT_open_64x32.root

The .root under ../data/dnn is the tracked record. The jobs read a copy of it
in SSWW/2024/rootFile/dnn, which is gitignored and therefore survives a branch
switch, so the last step is

    cp ../data/dnn/*.root ../../2024/rootFile/dnn/

The .dnn text files themselves are produced by `scripts/export_dnn_reader.py`
in the sibling DNN project and are not kept in this repository: they are a
megabyte of fitted numbers each, they belong to a training run, and the run
that produced them is the thing worth citing.
"""
import sys
from pathlib import Path

import ROOT


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    source, target = Path(argv[1]), Path(argv[2])
    text = source.read_text()
    if not text.startswith("DNNREADER "):
        raise ValueError(f"{source} is not an exported weight file")
    if not text.rstrip().endswith("END"):
        raise ValueError(f"{source} is truncated: it does not end with END")
    target.parent.mkdir(parents=True, exist_ok=True)
    out = ROOT.TFile.Open(str(target), "RECREATE")
    ROOT.TObjString(text).Write("weights")
    out.Close()

    # Read it back the way the reader will, so a packing mistake is found here
    # and not in a batch job that has already burned its slot.
    check = ROOT.TFile.Open(str(target))
    stored = str(check.Get("weights").GetString())
    check.Close()
    if stored != text:
        raise ValueError(f"{target} does not hold what {source} holds")
    print(f"{target}: {len(text) / 1e6:.2f} MB, round trip verified")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
