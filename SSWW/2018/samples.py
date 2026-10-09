#
# Samples file
#

# import os

#
# How to get the list of files to be analysed
#

mcProduction = 'Summer20UL18_106x_nAODv9_Full2018v9'
dataReco = 'Run2018_UL2018_nAODv9_Full2018v9'
mcSteps = 'MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9'
fakeSteps = 'DATAl1loose2018v9__l2loose__fakeW'
dataSteps = 'DATAl1loose2018v9__l2loose__l2tightOR2018v9'

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



############ DY ############

files = nanoGetSampleFiles(mcDirectory, 'DYJetsToLL_M-10to50_NLO') | \
        nanoGetSampleFiles(mcDirectory, 'DYJetsToLL_M-50')

#print (" list of files DY = ", files)

samples['DY'] = {
    'name': files,
    'weight': mcCommonWeight,
    'FilesPerJob': 3,
    'subsamples': {
      #            definition          specific weight
      'Low' : { 'cut' : 'mll<70',    'weight' :  '1.00'},
      'High': { 'cut' : 'mll>70',    'weight' :  '1.00'}
    }
}


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
    'FilesPerJob': 3,
}

addSubSampleWeights (samples, 'top', 'TTTo2L2Nu', 'Top_pTrw')




#
# Data
#

DataRun = [
    ['A','Run2018A-UL2018-v1'],
    ['B','Run2018B-UL2018-v1'],
    ['C','Run2018C-UL2018-v1'],
    ['D','Run2018D-UL2018-v1'],
]

DataSets = [
  'MuonEG',
  'SingleMuon',
  'EGamma',
  'DoubleMuon'
  ]

DataTrig = {
    'MuonEG'         : ' Trigger_ElMu' ,
    'DoubleMuon'     : '!Trigger_ElMu &&  Trigger_dblMu' ,
    'SingleMuon'     : '!Trigger_ElMu && !Trigger_dblMu &&  Trigger_sngMu' ,
    'EGamma'         : '!Trigger_ElMu && !Trigger_dblMu && !Trigger_sngMu && (Trigger_sngEl || Trigger_dblEl)' ,
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

    # fix 2018 peculiarity in versioning
    if (   ('DoubleMuon' in pd and 'Run2018B' in era_name)
        or ('DoubleMuon' in pd and 'Run2018D' in era_name)
        or ('SingleMuon' in pd and 'Run2018A' in era_name)
        or ('SingleMuon' in pd and 'Run2018B' in era_name)
        or ('SingleMuon' in pd and 'Run2018C' in era_name)):
        print("era_name = {}".format(era_name))
        print("pd       = {}".format(pd))
        print("Old datatag = {}".format(datatag))
        datatag = datatag.replace('v1','v2')
        print("New datatag = {}".format(datatag))

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





