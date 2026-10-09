from search_files import SearchFiles
import os
searchFiles = SearchFiles()

useXROOTD = False
redirector = 'root://eoscms.cern.ch/'

mcProduction       = 'Summer24_150x_nAODv15_Full2024v15'
mcSteps            = 'MCl2loose2024v15__MCCorr2024v15__JERFrom23BPix__l2tight'
dataRecoMuon       = 'Run2024_ReRecoCDE_PromptFGHI_nAODv15_Full2024v15_Muon'
dataRecoEGamma     = 'Run2024_ReRecoCDE_PromptFGHI_nAODv15_Full2024v15_EGamma'
dataRecoMuonEG     = 'Run2024_ReRecoCDE_PromptFGHI_nAODv15_Full2024v15_MuonEG'
dataSteps          = 'DATAl2loose2024v15__l2loose'
fakeSteps          = 'DATAl2loose2024v15__l2loose'

##############################################
###### Tree base directory for the site ######
##############################################
treeBaseDir = '/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano'
limitFiles = -1

def makeMCDirectory(var=""):
    _treeBaseDir = treeBaseDir + ""
    if var == "":
        return "/".join([_treeBaseDir, mcProduction, mcSteps])
    else:
        return "/".join([_treeBaseDir, mcProduction, mcSteps + "__" + var])



mcDirectory   = makeMCDirectory()
print(mcDirectory)
fakeDirectoryMuon = os.path.join(treeBaseDir, dataRecoMuon, fakeSteps)
dataDirectoryMuon = os.path.join(treeBaseDir, dataRecoMuon, dataSteps)
fakeDirectoryEGamma = os.path.join(treeBaseDir, dataRecoEGamma, fakeSteps)
dataDirectoryEGamma = os.path.join(treeBaseDir, dataRecoEGamma, dataSteps)
fakeDirectoryMuonEG = os.path.join(treeBaseDir, dataRecoMuonEG, fakeSteps)
dataDirectoryMuonEG = os.path.join(treeBaseDir, dataRecoMuonEG, dataSteps)


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




################################################
############ DATA DECLARATION ##################
################################################

DataRun = [
    ['C',   'Run2024C-ReReco-v1'],
    ['D',   'Run2024D-ReReco-v1'],
    ['E',   'Run2024E-ReReco-v1'],
    ['F',   'Run2024F-Prompt-v1'],
    ['G',   'Run2024G-Prompt-v1'],
    ['H',   'Run2024H-Prompt-v1'],
    ['Iv1', 'Run2024I-Prompt-v1'],
    ['Iv2', 'Run2024I-Prompt-v2'],
]

DataSets = [
    'MuonEG',
    'Muon0',
    'Muon1',
    'EGamma0',
    'EGamma1'
]

DataTrig = {
    'MuonEG' : 'Trigger_ElMu',
    'Muon0'  : '!Trigger_ElMu && (Trigger_sngMu || Trigger_dblMu)',
    'Muon1'  : '!Trigger_ElMu && (Trigger_sngMu || Trigger_dblMu)',
    'EGamma0': '!Trigger_ElMu && !Trigger_sngMu && !Trigger_dblMu && (Trigger_sngEl || Trigger_dblEl)',
    'EGamma1': '!Trigger_ElMu && !Trigger_sngMu && !Trigger_dblMu && (Trigger_sngEl || Trigger_dblEl)',
}

#########################################
############ MC COMMON ##################
#########################################

# tomas kello
# mcCommonWeightNoMatch = 'XSWeight*METFilter_Common*SFweight'
# mcCommonWeight        = 'XSWeight*METFilter_Common*PromptGenLepMatch2l*SFweight'


mcCommonWeight =        'XSWeight * SFweight2l * LepWPCut * LepWPSF * PromptGenLepMatch2l'
mcCommonWeightNoMatch = 'XSWeight * SFweight2l * LepWPCut * LepWPSF'

# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * PromptGenLepMatch2l'
# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * METFilter_MC * PromptGenLepMatch2l'
# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * Jet_PUIDSF * METFilter_MC * PromptGenLepMatch2l'
# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * Jet_PUIDSF * btagSF * METFilter_MC * PromptGenLepMatch2l'




# ##########
# ### DY ###
# ##########
# # DYto2E-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# # DYto2Mu-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# # DYto2Tau-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# # DYto2E_Bin-MLL-10to50_TuneCP5_13p6TeV_powheg-pythia8
# # DYto2Mu_Bin-MLL-10to50_TuneCP5_13p6TeV_powheg-pythia8
# # DYto2Tau_Bin-MLL-10to50_TuneCP5_13p6TeV_powheg-pythia8

# files = nanoGetSampleFiles(mcDirectory, 'DYto2E-2Jets_MLL-50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYto2Mu-2Jets_MLL-50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYto2Tau-2Jets_MLL-50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYto2E-2Jets_MLL-10to50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYto2Mu-2Jets_MLL-10to50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYto2Tau-2Jets_MLL-10to50')
# samples['DY'] = {
#     'name': files,
#     'weight': mcCommonWeight,
#         'EventsPerJob': 240000,
# }


# ############
# ### Top   ##
# ############
# # TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8
# # TbarWplusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8
# # TWminusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8
# # TBbarQtoLNu-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8
# # TbarBQtoLNu-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8
# # TBbartoLNu-s-channel_TuneCP5_13p6TeV_powheg-pythia8
# # TbarBtoLNu-s-channel_TuneCP5_13p6TeV_powheg-pythia8

# files = nanoGetSampleFiles(mcDirectory, 'TTTo2L2Nu') | \
#         nanoGetSampleFiles(mcDirectory, 'TbarWplusto2L2Nu') | \
#         nanoGetSampleFiles(mcDirectory, 'TWminusto2L2Nu') | \
#         nanoGetSampleFiles(mcDirectory, 'ST_t-channel_top') | \
#         nanoGetSampleFiles(mcDirectory, 'ST_t-channel_antitop') | \
#         nanoGetSampleFiles(mcDirectory, 'ST_s-channel_plus') | \
#         nanoGetSampleFiles(mcDirectory, 'ST_s-channel_minus')
# samples['top'] = {
#     'name': files,
#     'weight': mcCommonWeight,
#         'EventsPerJob': 240000,
# }
# addSubSampleWeights (samples, 'top', 'TTTo2L2Nu', 'Top_pTrw')

# ##########################################
# ## WW QCD and gluon-induced background ###
# ##########################################

# # GluGluWWto2E2Nu_TuneCP5_13p6TeV_mcfm-pythia8
# # GluGluWWtoENuMuNu_TuneCP5_13p6TeV_mcfm-pythia8
# # GluGluWWtoENuTauNu_TuneCP5_13p6TeV_mcfm-pythia8
# # GluGluWWtoMuNuENu_TuneCP5_13p6TeV_mcfm-pythia8
# # GluGluWWto2Mu2Nu_TuneCP5_13p6TeV_mcfm-pythia8
# # GluGluWWtoMuNuTauNu_TuneCP5_13p6TeV_mcfm-pythia8
# # GluGluWWtoTauNuENu_TuneCP5_13p6TeV_mcfm-pythia8
# # GluGluWWtoTauNuMuNu_TuneCP5_13p6TeV_mcfm-pythia8
# # GluGluWWto2Tau2Nu_TuneCP5_13p6TeV_mcfm-pythia8

# files = nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoENuENu') | \
#     nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoENuMuNu') | \
#     nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoENuTauNu') |	\
#     nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoMuNuENu') |	\
#     nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoMuNuMuNu') |	\
#     nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoMuNuTauNu') |	\
#     nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoTauNuENu') |	\
#     nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoTauNuMuNu') |	\
#     nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoTauNuTauNu')
# samples['ggWW'] = {
#     'name': files,
#     'weight': mcCommonWeight,
#         'EventsPerJob': 240000,
# }

# ## TODO: add QCD WW once ready -> just post process existing NanoAOD

# ##########
# ### VZ ###
# ##########
# # WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8
# files = nanoGetSampleFiles(mcDirectory, 'WZTo3LNu')
# samples['WZ'] = {
#     'name': files,
#     'weight': mcCommonWeight + ' * (Gen_ZGstar_mass >= 50)',
#         'EventsPerJob': 500000,
# }

# # ZZ_TuneCP5_13p6TeV_pythia8/
# files = nanoGetSampleFiles(mcDirectory, 'ZZ')
# samples['ZZ'] = {
#     'name': files,
#     'weight': mcCommonWeight,
#         'EventsPerJob': 500000,
# }    

# ##################
# ### Vg/VgS/VZS ###
# ##################
# # DYGto2LG-1Jets_Bin-MLL-4to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# # DYGto2LG-1Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# files = nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_Bin-MLL-50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_Bin-MLL-4to50')    
# samples['Zg'] = {
#     'name': files,
#     'weight': mcCommonWeightNoMatch + '*(Gen_ZGstar_mass <= 0)',
#         'EventsPerJob': 500000,
# }

# # WGtoLNuG-1Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# files = nanoGetSampleFiles(mcDirectory, 'WGtoLNuG-1J')
# samples['Wg'] = {
#     'name': files,
#     'weight': mcCommonWeightNoMatch + '*(Gen_ZGstar_mass <= 0)',
#         'EventsPerJob': 500000,
# }

# # DYGto2LG-1Jets_Bin-MLL-4to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# # DYGto2LG-1Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# files = nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_Bin-MLL-4to50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_Bin-MLL-50')
# samples['ZgS'] = {
#     'name': files,
#     'weight': mcCommonWeight,
#         'EventsPerJob': 500000,
# }
# addSubSampleWeights(samples, 'ZgS', "DYGto2LG-1Jets_Bin-MLL-4to50", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")
# addSubSampleWeights(samples, 'ZgS', "DYGto2LG-1Jets_Bin-MLL-50", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")

# # WGtoLNuG-1Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# files =  nanoGetSampleFiles(mcDirectory, 'WGtoLNuG-1J')      
# samples['WgS'] = {
#     'name': files,
#     'weight': mcCommonWeight,
#         'EventsPerJob': 500000,
# }
# addSubSampleWeights(samples, 'WgS', "WGtoLNuG-1J", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")

# # WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8
# files =  nanoGetSampleFiles(mcDirectory, "WZTo3LNu") 
# samples['WZS'] = {
#     'name': files,
#     'weight': mcCommonWeight,
#         'EventsPerJob': 500000,
# }
# addSubSampleWeights(samples, 'WZS', "WZTo3LNu", "(Gen_ZGstar_mass >= 4 && Gen_ZGstar_mass < 50)")    

# ##################
# ### Multiboson ###
# ##################
# # WWW-4F_TuneCP5_13p6TeV_amcatnlo-pythia8
# # WWZ-4F_TuneCP5_13p6TeV_amcatnlo-pythia8
# # WZZ-5F_TuneCP5_13p6TeV_amcatnlo-pythia8
# # ZZZ-5F_TuneCP5_13p6TeV_amcatnlo-pythia8
# files = nanoGetSampleFiles(mcDirectory, 'WWW') | \
#         nanoGetSampleFiles(mcDirectory, 'WWZ') | \
#         nanoGetSampleFiles(mcDirectory, 'WZZ') | \
#         nanoGetSampleFiles(mcDirectory, 'ZZZ')  
# samples['VVV'] = {
#     'name': files,
#     'weight': mcCommonWeight,
#         'EventsPerJob': 500000,
# }

# ##################
# ###    Higgs   ###
# ##################
# # GluGluHto2Wto2L2Nu_Par-M-125_TuneCP5_13p6TeV_powheg-jhugen-pythia
# files = nanoGetSampleFiles(mcDirectory, 'GluGluHToWWTo2L2Nu_M125')
# samples['ggH_hww'] = {
#     'name': files,
#     'weight': mcCommonWeight,
#         'EventsPerJob': 500000,
# }

# # VBFHto2Wto2L2Nu_Par-M-125_TuneCP5_13p6TeV_powheg-jhugen-pythia8
# files = nanoGetSampleFiles(mcDirectory, 'VBFHToWWTo2L2Nu_M125')
# samples['qqH_hww'] = {
#     'name': files,
#     'weight': mcCommonWeight,
#         'EventsPerJob': 500000,
# }

# #TODO: add VH and ttH

# ###########################################
# #############    SIGNALS  #################
# ###########################################

# ####################
# ### WW inclusive ###
# ####################
# #TODO: Change for EWK Madgraph samples when produced  
# #   WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8
# files = nanoGetSampleFiles(mcDirectory, 'WWTo2L2Nu')
# samples['WW'] = {
#     'name': files,
#     'weight': mcCommonWeight,
#         'EventsPerJob': 500000,
# }

# #TODO: add polarized

# ###########
# ## DATA ###
# ############
# samples['DATA'] = {
#     'name': {},
#     'weight': 'LepWPCut*METFilter_DATA',
#     'weights': {},
#     'isData': ['all'],
#     'FilesPerJob': 100
# }

# for _, sd in DataRun:
#     for pd in DataSets:
#         datatag = pd + '_' + sd
#         if datatag.startswith('MuonEG'):
#             files = nanoGetSampleFiles(dataDirectoryMuonEG, datatag)
#         elif datatag.startswith('Muon'):
#             files = nanoGetSampleFiles(dataDirectoryMuon, datatag)
#         elif datatag.startswith('EGamma'):
#             files = nanoGetSampleFiles(dataDirectoryEGamma, datatag)
#         print(datatag)
#         samples['DATA']['name'].update(files)
#         samples['DATA']['weights'].update({
#             datatag: DataTrig[pd]
#         })

# #############
# ### Fakes ###
# #############
samples['Fake'] = {
    'name': {},
    'weight': 'METFilter_DATA*fakeW',
    'weights': {},
    'isData': ['all'],
    'FilesPerJob': 100
}

for _, sd in DataRun:
    for pd in DataSets:
        datatag = pd + '_' + sd
        if datatag.startswith('MuonEG'):
            files = nanoGetSampleFiles(fakeDirectoryMuonEG, datatag)
        elif datatag.startswith('Muon'):
            files = nanoGetSampleFiles(fakeDirectoryMuon, datatag)
        elif datatag.startswith('EGamma'):
            files = nanoGetSampleFiles(fakeDirectoryEGamma, datatag)
        samples['Fake']['name'].update(files)
        samples['Fake']['weights'].update({
            datatag: DataTrig[pd]
        })












# files = nanoGetSampleFiles(mcDirectory, 'DYto2E-2Jets_MLL-50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYto2Mu-2Jets_MLL-50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYto2Tau-2Jets_MLL-50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYto2E-2Jets_MLL-10to50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYto2Mu-2Jets_MLL-10to50') | \
#         nanoGetSampleFiles(mcDirectory, 'DYto2Tau-2Jets_MLL-10to50')



# DataRun = [
#     ['C','Run2024C-ReReco-v1'],
#     ['D','Run2024D-ReReco-v1'],
#     ['E','Run2024E-ReReco-v1'],
#     ['F','Run2024F-Prompt-v1'],
#     ['G','Run2024G-Prompt-v1'],
#     ['H','Run2024H-Prompt-v1'],
#     ['I','Run2024I-Prompt-v1'],
# ]


# DataSets = [
#   'MuonEG',
#   'Muon0',
#   'Muon1',
#   'EGamma0',
#   'EGamma1'
#   ]

# DataTrig = {
#     'MuonEG'  : 'Trigger_ElMu' ,
#     'Muon0'   : '!Trigger_ElMu && (Trigger_sngMu || Trigger_dblMu)',
#     'Muon1'   : '!Trigger_ElMu && (Trigger_sngMu || Trigger_dblMu)',
#     'EGamma0' : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_dblMu && (Trigger_sngEl || Trigger_dblEl)',
#     'EGamma1' : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_dblMu && (Trigger_sngEl || Trigger_dblEl)',
# }



# samples['DATA'] = {
#   'name': {},
#   'weight': 'LepWPCut',
#   # 'weight': 'LepWPCut*METFilter_DATA',
#   'weights': {},
#   'isData': ['all'],
#   'FilesPerJob': 100
# }

# for era, era_name in DataRun:
#   for pd in DataSets:
#     datatag = pd + '_' + era_name

#     # get the files
#     if datatag.startswith('MuonEG'):
#         files = nanoGetSampleFiles(dataDirectoryMuonEG, datatag)
#     elif datatag.startswith('Muon'):
#         files = nanoGetSampleFiles(dataDirectoryMuon, datatag)
#     elif datatag.startswith('EGamma'):
#         files = nanoGetSampleFiles(dataDirectoryEGamma, datatag)

#     samples['DATA']['name'].update(files)

#     # add the weight that is different pd by pd, to take into account orthogonality of triggers
#     samples['DATA']['weights'].update( {datatag : DataTrig[pd] })


#
# Useful later on, like aliases.py, nuisances.py, ...
#

