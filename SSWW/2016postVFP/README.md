WW analysis 2016 postVFP / noHIPM
====

Setup:

    source setup.sh
    source ../../../latinoRDF/setup.sh

Histogram production


Prepare the scripts:

    mkShapes.py  --pycfg=configuration.py

NB: the preparation of the scripts will clean all the compiled code.

Compile the scripts locally:

    mkShapes.py  --pycfg=configuration.py     --localCompile

Compile the scripts on cluster:

    mkShapes.py  --pycfg=configuration.py     --parallelCompile

Submit on batch system:

    mkShapes.py  --pycfg=configuration.py --submitBatch
    mkShapes.py  --pycfg=configuration.py --submit

Check if done:

    mkShapes.py  --pycfg=configuration.py --checkBatch

Hadd the root files:

    mkShapes.py  --pycfg=configuration.py --hadd


Plot:

    mkPlot.py  --pycfg=configuration.py
    mkPlot.py  --pycfg=configuration.py  --showIntegralLegend 1

    mkPlot.py  --pycfg=configuration.py  --showIntegralLegend 1 --skipMissingNuisance

    mkPlot.py  --pycfg=configuration.py  --showIntegralLegend 1 --skipMissingNuisance   --plotNormalizedDistributions
    mkPlot.py  --pycfg=configuration.py  --showIntegralLegend 1 --skipMissingNuisance   --plotNormalizedDistributions  --silentMode




Datacards:

    mkDatacards.py  --pycfg=configuration.py

Dump the trees:

    mkSnapshot.py   --pycfg=configuration.py
    mkSnapshot.py   --pycfg=configuration.py  --submitBatch
    mkSnapshot.py   --pycfg=configuration.py  --checkBatch


Readable:

    easyDescription.py --inputFileSamples      samples.py     --outputFileSamples      extended_samples.py
    easyDescription.py --inputFileCuts         cuts.py        --outputFileCuts         extended_cuts.py
    easyDescription.py --inputFileNuisances    nuisances.py   --outputFileNuisances    extended_nuisances.py   --inputFileSamples      samples.py



