#
# Samples file
#

# import os

#
# How to get the list of files to be analysed
#

mcProduction = 'Summer22EE_130x_nAODv12_Full2022v12'
mcSteps = 'MCl2loose2022EEv12__MCCorr2022EEv12JetScaling__l2tight'
dataReco = 'Run2022EE_Prompt_nAODv12_Full2022v12'
fakeSteps = 'DATAl2loose2022EEv12__l2loose'
dataSteps = 'DATAl2loose2022EEv12__l2loose'

treeBaseDir = '/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano'


def makeMCDirectory(var=""):
    _treeBaseDir = treeBaseDir + ""
    if var == "":
        return "/".join([_treeBaseDir, mcProduction, mcSteps])
    else:
        return "/".join([_treeBaseDir, mcProduction, mcSteps + "__" + var])

mcDirectory = makeMCDirectory()
fakeDirectory = os.path.join(treeBaseDir, dataReco, fakeSteps)
dataDirectory = os.path.join(treeBaseDir, dataReco, dataSteps)


from search_files import SearchFiles
searchFiles = SearchFiles()

useXROOTD = False
redirector = 'root://eoscms.cern.ch/'

def nanoGetSampleFiles(path, name):
  _files = searchFiles.searchFiles(path, name, redirector=redirector)
  return  {name : _files}


def addSubSampleWeights(samples, sampleName, subSampleName, weight):
  if 'weights' not in samples[sampleName].keys():
    samples[sampleName]['weights'] = {}
  if subSampleName in samples[sampleName]['weights'].keys():
    samples[sampleName]['weights'][subSampleName] = "(" + samples[sampleName]['weights'][subSampleName] + ") * " +  weight
  else :
    samples[sampleName]['weights'][subSampleName] = weight




#
# The weights
#

mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * PromptGenLepMatch2l'
# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * METFilter_MC * PromptGenLepMatch2l'
# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * Jet_PUIDSF * METFilter_MC * PromptGenLepMatch2l'
# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * Jet_PUIDSF * btagSF * METFilter_MC * PromptGenLepMatch2l'






#
# The actual list of samples
#

############ Top ############


files = nanoGetSampleFiles(mcDirectory, 'TTTo2L2Nu') | \
        nanoGetSampleFiles(mcDirectory, 'TbarWplusto2L2Nu') | \
        nanoGetSampleFiles(mcDirectory, 'TWminusto2L2Nu') | \
        nanoGetSampleFiles(mcDirectory, 'ST_t-channel_top') | \
        nanoGetSampleFiles(mcDirectory, 'ST_t-channel_antitop') | \
        nanoGetSampleFiles(mcDirectory, 'ST_s-channel_plus') | \
        nanoGetSampleFiles(mcDirectory, 'ST_s-channel_minus')

samples['top'] = {
    'name': files,
    'weight': mcCommonWeight,
    # 'weight': mcCommonWeight + " * Top_pTrw ",
    'FilesPerJob': 3,
}

addSubSampleWeights (samples, 'top', 'TTTo2L2Nu', 'Top_pTrw')


############ DY ############

files = nanoGetSampleFiles(mcDirectory, 'DYto2L-2Jets_MLL-10to50') | \
        nanoGetSampleFiles(mcDirectory, 'DYto2L-2Jets_MLL-50')

#print (" list of files DY = ", files)

samples['DY'] = {
    'name': files,
    'weight': mcCommonWeight,
    'FilesPerJob': 5,
}





#
# Data
#

DataRun = [
    ['E','Run2022E-Prompt-v1'],
    ['F','Run2022F-Prompt-v1'],
    ['G','Run2022G-Prompt-v1'],
]


DataSets = [
  'MuonEG',
  'Muon',
  'EGamma'
  ]


DataTrig = {
    'MuonEG'         : ' Trigger_ElMu' ,
    'Muon'           : '!Trigger_ElMu && (Trigger_sngMu || Trigger_dblMu)',
    'EGamma'         : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_dblMu && (Trigger_sngEl || Trigger_dblEl)'
}


samples['DATA'] = {
  'name': {},
  'weight': 'LepWPCut',
  # 'weight': 'LepWPCut*METFilter_DATA',
  'weights': {},
  'isData': ['all'],
  'FilesPerJob': 10
}

for era, era_name in DataRun:
  for pd in DataSets:
    datatag = pd + '_' + era_name

    # get the files
    files = nanoGetSampleFiles(dataDirectory, datatag)
    samples['DATA']['name'].update(files)

    # add the weight that is different pd by pd, to take into account orthogonality of triggers
    samples['DATA']['weights'].update( {datatag : DataTrig[pd] })


#
# Useful later on, like aliases.py, nuisances.py, ...
#

mcALL     = [skey for skey in samples if skey not in ('DATA', 'Fake_lep')]
ALL       = [skey for skey in samples]





