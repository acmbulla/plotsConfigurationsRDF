
# tag: used to define root file name and more
tag = 'SSWW'
tagger = '261012_Run3'
tag = tag + "_" + tagger

# File with dict of variables
variablesFile = "variables.py"

# File with dict of cuts
cutsFile = "cuts.py"

# file with list of samples
samplesFile = "samples.py"


# structure file for datacard
structureFile = "structure.py"

# nuisances file for mkDatacards and for mkShape
nuisancesFile = "nuisances.py"

outputDir = "./rootFile/"+tag

plotDir   = "./plots/"+tag


# Folders to merge
foldersToMerge = {

                  "2022" : {
                    "folder" : "../2022",
                    "tag"    : "261012_22",
                  },

                  "2022EE" : {
                    "folder" : "../2022EE",
                    "tag"    : "261012_22EE",
                  },

                  "2023" : {
                    "folder" : "../2023",
                    "tag"    : "261012_23",
                  },

                  "2023BPix" : {
                    "folder" : "../2023BPix",
                    "tag"    : "261012_23Bpix",
                  },

                  "2024" : {
                    "folder" : "../2024",
                    "tag"    : "261012_24",
                   },

                  "2025" : {
                    'folder': '../2025',
                    'tag': '261012_25',
                  },

                  "2026" : {
                    'folder': '../2026',
                    'tag': '261012_26',
                  }
}



