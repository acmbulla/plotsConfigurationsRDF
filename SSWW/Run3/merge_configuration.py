
# tag: used to define root file name and more
tag = 'WW'
tagger = '260928_Run3'
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
                    "tag"    : "WW_260916_test22",
                  },

                  "2022EE" : {
                    "folder" : "../2022EE",
                    "tag"    : "WW_260916_test22EE",
                  },

                  "2023" : {
                    "folder" : "../2023",
                    "tag"    : "WW_260916_test23",
                    'sampleRename': {
                        'VBS_SSWW_TT':  'VBS_SSWW_WWCM_TT', 
                        'VBS_SSWW_LL':  'VBS_SSWW_WWCM_LL',  
                        'VBS_SSWW_TL':  'VBS_SSWW_WWCM_TL', 
                    } 
                  },

                  "2023BPix" : {
                    "folder" : "../2023BPix",
                    "tag"    : "260916_test23Bpix",
                  },

                  "2024" : {
                    "folder" : "../2024",
                    "tag"    : "WW_260923_test24",
                    'sampleRename': {
                        'VBS_SSWW_TT':  'VBS_SSWW_WWCM_TT', 
                        'VBS_SSWW_LL':  'VBS_SSWW_WWCM_LL',  
                        'VBS_SSWW_TL':  'VBS_SSWW_WWCM_TL',  
                    }
                   },

                  "2025" : {
                    'folder': '../2025',
                    'tag': 'WW_260923_test25',
                    'sampleRename': {
                        'VBS_SSWW_TT':  'VBS_SSWW_WWCM_TT', 
                        'VBS_SSWW_LL':  'VBS_SSWW_WWCM_LL',  
                        'VBS_SSWW_TL':  'VBS_SSWW_WWCM_TL', 
                    } 
                  },

                  "2026" : {
                    'folder': '../2026',
                    'tag': 'WW_260923_test26',
                    'sampleRename': {
                        'VBS_SSWW_TT':  'VBS_SSWW_WWCM_TT', 
                        'VBS_SSWW_LL':  'VBS_SSWW_WWCM_LL',  
                        'VBS_SSWW_TL':  'VBS_SSWW_WWCM_TL',  
                    },
                  }
}



