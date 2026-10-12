# example of configuration file

tag = 'WW'

# used by mkShape to define output directory for root files
# outputDir = 'rootFile'
outputDir = './'

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
lumi = 281.56

# 2022     lumi = 8.0
# 2022EE   lumi = 26.7
# 2023     lumi = 17.8
# 2023BPix lumi = 9.5
# 2024     lumi = 109.08
# 2025     lumi = 110.48
#
# 8.0 + 26.7 + 17.8 + 9.5 + 109.08 + 110.48
#

# used by mkPlot to define output directory for plots
# different from "outputDir" to do things more tidy
outputDirPlots = 'plots'


# used by mkDatacards to define output directory for datacards
outputDirDatacard = 'datacards'



