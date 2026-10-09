# example of configuration file

tag = 'WW'

# used by mkShape to define output directory for root files
outputDir = 'rootFile'

# file with list of aliases
aliasesFile = 'aliases.py'

# file with list of variables
variablesFile = 'variables.py'

# file with list of cuts
cutsFile = 'cuts.py'

# file with list of samples
samplesFile = 'samples.py'

# file with list of plots configuration, e.g. colours, grouping, ...
plotFile = 'plot.py'

# structure file for datacard
structureFile = 'structure.py'

# nuisances file for mkDatacards and for mkShape
nuisancesFile = 'nuisances.py'

# snapshot configuration file (if needed)
snapshotFile = 'snapshot.py'

# luminosity to normalize to (in 1/fb)
# https://github.com/latinos/LatinoAnalysis/blob/UL_production/NanoGardener/python/data/TrigMaker_cfg.py#L868 (874)
lumi = 41.48

# used by mkPlot to define output directory for plots
# different from "outputDir" to do things more tidy
outputDirPlots = 'plots'


# used by mkDatacards to define output directory for datacards
outputDirDatacard = 'datacards'



