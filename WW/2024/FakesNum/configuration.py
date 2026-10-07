# example of configuration file
import os

tag = 'WW'
tagger = '260915_Fakes'

# used by mkShape to define output directory for root files
outputDir = './rootFile/' + tagger

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
lumi = 110.11

# used by mkPlot to define output directory for plots
# different from "outputDir" to do things more tidy
outputDirPlots = '../plots/' + tagger

# used by mkDatacards to define output directory for datacards
outputDirDatacard = '../datacards/' + tagger

scripts_run_folder    = "${MY_PATH_JOBS}/2024/"+tag+"_"+tagger+"/run_scripts"
script_batch_location = "${MY_PATH_JOBS}/2024/"+tag+"_"+tagger+"/batch_scripts"

# snapshot.py
batchScriptLocation   = "${MY_PATH_JOBS}/2024/" + tag + "_" + tagger + "/batch_scripts_snapshot"
snapshotRunFolder = "${MY_PATH_JOBS}/2024/" + tag + "_" + tagger + "/run_scripts_snapshot"

## if this is set, the outDir is overloaded
# folder_where_to_save_trees = os.path.expandvars("${MY_PATH_JOBS}/2024/") + tag + "_" + tagger + "/snapshot"