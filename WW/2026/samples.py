#
# Samples file
#

# import os

#
# How to get the list of files to be analysed
#

mcProduction        = 'Summer24_150x_nAODv15_Full2024v15_OLD'
mcSteps             = 'MCl2loose2024v15__MCCorr2024v15__JERFrom23BPix__l2tight'
dataReco_EGamma     = 'Run2025_PromptCDEFG_nAODv15_Full2025v15_EGamma'
dataReco_Muon       = 'Run2025_PromptCDEFG_nAODv15_Full2025v15_Muon'
dataReco_MuonEG     = 'Run2025_PromptCDEFG_nAODv15_Full2025v15_MuonEG'
dataSteps           = 'DATAl2loose2025v15__l2loose'

treeBaseDir = '/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano'



def makeMCDirectory(var=""):
    _treeBaseDir = treeBaseDir + ""
    if var == "":
        return "/".join([_treeBaseDir, mcProduction, mcSteps])
    else:
        return "/".join([_treeBaseDir, mcProduction, mcSteps + "__" + var])

mcDirectory = makeMCDirectory()
# fakeDirectory = os.path.join(treeBaseDir, dataReco, fakeSteps)
# dataDirectory = os.path.join(treeBaseDir, dataReco, dataSteps)

# fakeDirectoryMuon = os.path.join(treeBaseDir, dataRecoMuon, dataSteps)
# dataDirectoryMuon = os.path.join(treeBaseDir, dataRecoMuon, dataSteps)
# fakeDirectoryEGamma = os.path.join(treeBaseDir, dataRecoEGamma, dataSteps)
# dataDirectoryEGamma = os.path.join(treeBaseDir, dataRecoEGamma, dataSteps)
# fakeDirectoryMuonEG = os.path.join(treeBaseDir, dataRecoMuonEG, dataSteps)
# dataDirectoryMuonEG = os.path.join(treeBaseDir, dataRecoMuonEG, dataSteps)


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
    'FilesPerJob': 30,
}

addSubSampleWeights (samples, 'top', 'TTTo2L2Nu', 'Top_pTrw')


############ DY ############


files = nanoGetSampleFiles(mcDirectory, 'DYto2E-2Jets_MLL-50') | \
        nanoGetSampleFiles(mcDirectory, 'DYto2Mu-2Jets_MLL-50') | \
        nanoGetSampleFiles(mcDirectory, 'DYto2Tau-2Jets_MLL-50') | \
        nanoGetSampleFiles(mcDirectory, 'DYto2E-2Jets_MLL-10to50') | \
        nanoGetSampleFiles(mcDirectory, 'DYto2Mu-2Jets_MLL-10to50') | \
        nanoGetSampleFiles(mcDirectory, 'DYto2Tau-2Jets_MLL-10to50')

#
# files = nanoGetSampleFiles(mcDirectory, 'DYto2L-2Jets_MLL-10to50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYto2L-2Jets_MLL-50')
#

#print (" list of files DY = ", files)

samples['DY'] = {
    'name': files,
    'weight': mcCommonWeight,
    'FilesPerJob': 50,
}





#
# Data
#


DataRun = [
    ['C','Run2025C-Prompt-v1'],
    ['C','Run2025C-Prompt-v2'],
    ['D','Run2025D-Prompt-v1'],
    ['E','Run2025E-Prompt-v1'],
    ['F','Run2025F-Prompt-v1'],
    ['F','Run2025F-Prompt-v2'],
    ['G','Run2025G-Prompt-v1'],
]


DataSets = [
  'MuonEG',
  'Muon0',
  'Muon1',
  'EGamma0',
  'EGamma1',
  'EGamma2',
  'EGamma3'
  ]


DataTrig = {
    'MuonEG'          : 'Trigger_ElMu' ,
    'Muon0'           : '!Trigger_ElMu && (Trigger_sngMu || Trigger_dblMu)',
    'Muon1'           : '!Trigger_ElMu && (Trigger_sngMu || Trigger_dblMu)',
    'EGamma0'         : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_dblMu && (Trigger_sngEl || Trigger_dblEl)',
    'EGamma1'         : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_dblMu && (Trigger_sngEl || Trigger_dblEl)',
    'EGamma2'         : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_dblMu && (Trigger_sngEl || Trigger_dblEl)',
    'EGamma3'         : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_dblMu && (Trigger_sngEl || Trigger_dblEl)',
}



samples['DATA'] = {
  'name': {},
  'weight': 'LepWPCut',
  # 'weight': 'LepWPCut*METFilter_DATA',
  'weights': {},
  'isData': ['all'],
  'FilesPerJob': 100
}

for era, era_name in DataRun:
  for pd in DataSets:
    datatag = pd + '_' + era_name

    # get the files
    if "EGamma" in pd: dataReco = dataReco_EGamma
    elif "Muon" in pd and pd != "MuonEG": dataReco = dataReco_Muon
    elif pd == "MuonEG": dataReco = dataReco_MuonEG

    dataDirectory = os.path.join(treeBaseDir, dataReco, dataSteps)
    files = nanoGetSampleFiles(dataDirectory, datatag)

    samples['DATA']['name'].update(files)

    # add the weight that is different pd by pd, to take into account orthogonality of triggers
    samples['DATA']['weights'].update( {datatag : DataTrig[pd] })


#
# Useful later on, like aliases.py, nuisances.py, ...
#

mcALL     = [skey for skey in samples if skey not in ('DATA', 'Fake_lep')]
ALL       = [skey for skey in samples]


# del samples['top']
# del samples['DY']


