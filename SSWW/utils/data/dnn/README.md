# Frozen polarisation networks

The weight files the `dnn_reader` aliases read, one per deployed model.

| file | model | what it is |
|---|---|---|
| `twostage_uparT_open_64x32.root` | two-stage UParT, open region, 64→32 | stage 1 separates signal from background, stage 2 separates LL/TL/TT. Best expected sensitivity on `mu_LX` of everything tried |
| `mc4_uparT_open_64x32.root` | four-head UParT multiclass, open region, 64→32 | one network, background/LL/TL/TT. Second best, and the only one that gives three process outputs at once |

Each holds the exported text in a `TObjString` named `weights`, so
`TFile::Open` reaches it over xrootd from a batch node. Inside are the 42-input
feature list, the fitted preprocessing and the dense layers of every fold model
of every stage, and one monotone CDF table per observable cell.

## The fold rule

The file declares how the fold models combine, and the reader obeys it.

`parity`, which both files above use, applies model `event % n_models` and
nothing else. A batch job can reproduce that from the event number alone, so
every simulated event is scored by a model that was trained without it and the
templates are honest rather than optimistically sharp.

`ensemble` averages all the fold models instead. It is what a batch job has to
do for a run whose folds came from a `StratifiedKFold` over the training table,
since nothing per event recovers which fold held an event out. It is right for
data and for anything the networks never trained on, and optimistic for the
simulation they did.

Both files were re-trained for the parity rule on 2026-10-29: two models per
stage, trained on `event % 2 != k` and applied to `event % 2 == k`. That halves
the training set against the earlier ten-fold crossfit and costs 0.003 in
signal-vs-background test AUC (0.9564 → 0.9531/0.9528), which the DNN project's
learning curve had predicted would be small. Nothing in `aliases.py` changed:
the event number is passed to the reader under either rule.

The runs behind them, in the sibling DNN project:

- `ce_small/runs/parity_sigvsbkg_uparT_open_angles_64x32_20261029` (stage 1)
- `ce_small/runs/parity_3sig_uparT_open_angles_64x32_20261029` (stage 2)
- `ce_small/runs/parity_4class_uparT_open_angles_64x32_20261029` (multiclass)

## Where they come from

Produced in the sibling DNN project, not here:

```sh
# in DNN/
P=/opt/anaconda3/envs/hep/bin/python
R=ce_small/runs

$P scripts/export_dnn_reader.py \
   --stage1 $R/parity_sigvsbkg_uparT_open_angles_64x32_20261029 \
   --stage2 $R/parity_3sig_uparT_open_angles_64x32_20261029 \
   --fold-rule parity --b-bins 2 --compare-bins 4 \
   --out deploy/weights/twostage_uparT_open_64x32.dnn \
   --dump-reference deploy/weights/reference_twostage.csv

$P scripts/export_dnn_reader.py \
   --multiclass $R/parity_4class_uparT_open_angles_64x32_20261029 \
   --fold-rule parity --compare-bins 6 \
   --out deploy/weights/mc4_uparT_open_64x32.dnn \
   --dump-reference deploy/weights/reference_mc4.csv
```

then, here:

```sh
python3 ../../scripts/pack_dnn_weights.py <file>.dnn <file>.root
```

and finally into the directory the jobs actually read, which is **not** this
one:

```sh
cp *.root ../../../2024/rootFile/dnn/
```

The files here are the tracked record of which network made which plots. The
copy under `SSWW/2024/rootFile/dnn` is what `dnnweights` in `aliases.py` points
at, and it is there because `rootFile` is gitignored on every branch: this
directory only exists on the branch that tracks it, so checking the eos clone
out onto another one deletes it under the running jobs. Forgetting this copy
after a re-export is the one way the deployment can now go quietly wrong -- the
jobs keep reading the previous network and nothing complains.

The `.dnn` text files are not kept in this repository. They are a megabyte of
fitted numbers each and they belong to a training run; the run is what is worth
citing, and `export_dnn_reader.py` rebuilds the file from it in minutes.

## Checking an export before trusting it

`--dump-reference` writes a CSV of inputs with the output the torch model
produces for them. The C++ reader is then held against it:

```sh
cd ../../macros
g++ -O2 -std=c++17 $(root-config --cflags --libs) -o test_dnn_reader test_dnn_reader.cc
./test_dnn_reader <file>.dnn <reference>.csv
```

It must print `PASS` with zero cell mismatches. On the two files above the
probabilities agree with torch to 3.7e-8, the cell exactly, and the unrolled
observable to 7.5e-7 (two-stage) and 6.5e-6 (multiclass) -- float32 rounding
and nothing else. The exporter's own numpy-against-TorchScript check, on the
same fold rule, agrees to 4.2e-7.

`--compare-bins n` makes the exporter print the quantile edges its CDF tables
imply for `n` uniform sub-bins. Those are the numbers to diff against the
binning the DNN study used (`edges_2stage.json`, `edges_signal_quantiles_*.json`
in the run directories). Note that the parity re-training moves them: they are
a property of this network, not of the earlier ten-fold one, which is exactly
why the CDF tables travel with the weights instead of being re-derived next to
the histogram.
