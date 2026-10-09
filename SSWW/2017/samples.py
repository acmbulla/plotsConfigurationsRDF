#
# Samples file
#

# import os

#
# How to get the list of files to be analysed
#

mcProduction = 'Summer20UL17_106x_nAODv9_Full2017v9'
dataReco     = 'Run2017_UL2017_nAODv9_Full2017v9'
mcSteps      = 'MCl1loose2017v9__MCCorr2017v9NoJERInHorn__l2tightOR2017v9'
fakeSteps    = 'DATAl1loose2017v9__l2loose__fakeW'
dataSteps    = 'DATAl1loose2017v9__l2loose__l2tightOR2017v9'

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

mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * Jet_PUIDSF * btagSF * METFilter_MC * PromptGenLepMatch2l'






#
# The actual list of samples
#

############ Top ############


files = nanoGetSampleFiles(mcDirectory, 'TTTo2L2Nu') | \
        nanoGetSampleFiles(mcDirectory, 'ST_s-channel') | \
        nanoGetSampleFiles(mcDirectory, 'ST_t-channel_top') | \
        nanoGetSampleFiles(mcDirectory, 'ST_t-channel_antitop') | \
        nanoGetSampleFiles(mcDirectory, 'ST_tW_antitop') | \
        nanoGetSampleFiles(mcDirectory, 'ST_tW_top')

samples['top'] = {
    'name': files,
    'weight': mcCommonWeight,
    # 'weight': mcCommonWeight + " * Top_pTrw ",
    'FilesPerJob': 3,
}


############ DY ############

files = nanoGetSampleFiles(mcDirectory, 'DYJetsToLL_M-10to50_NLO') | \
        nanoGetSampleFiles(mcDirectory, 'DYJetsToLL_M-50')

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
    ['B','Run2017B-UL2017-v1'],
    ['C','Run2017C-UL2017-v1'],
    ['D','Run2017D-UL2017-v1'],
    ['E','Run2017E-UL2017-v1'],
    ['F','Run2017F-UL2017-v1'],
]

DataSets = [
  'MuonEG',
  'SingleMuon',
  'SingleElectron',
  'DoubleMuon',
  'DoubleEG'
  ]


DataTrig = {
    'MuonEG'         : ' Trigger_ElMu' ,
    'SingleMuon'     : '!Trigger_ElMu && Trigger_sngMu' ,
    'SingleElectron' : '!Trigger_ElMu && !Trigger_sngMu && Trigger_sngEl',
    'DoubleMuon'     : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_sngEl && Trigger_dblMu',
    'DoubleEG'       : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_sngEl && !Trigger_dblMu && Trigger_dblEl'
}


samples['DATA'] = {
  'name': {},
  'weight': 'LepWPCut*METFilter_DATA',
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





