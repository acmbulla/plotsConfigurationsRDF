from search_files import SearchFiles
import os
searchFiles = SearchFiles()

useXROOTD = False
redirector = 'root://eoscms.cern.ch/'

mcProduction = 'Summer22EE_130x_nAODv12_Full2022v12' 
mcSteps = 'MCl2loose2022EEv12__MCCorr2022EEv12JetScaling__l2tight' 
dataReco = 'Run2022EE_Prompt_nAODv12_Full2022v12'
fakeSteps = 'DATAl2loose2022EEv12__l2loose'
dataSteps = 'DATAl2loose2022EEv12__l2loose'

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
fakeDirectory = os.path.join(treeBaseDir, dataReco, fakeSteps)
dataDirectory = os.path.join(treeBaseDir, dataReco, dataSteps)



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
    ['E','Run2022E-Prompt-v1'],
    ['F','Run2022F-Prompt-v1'],
    ['G','Run2022G-Prompt-v1'],
]

DataSets = ['MuonEG','Muon','EGamma']

DataTrig = {
    'MuonEG'         : 'Trigger_ElMu' ,
    'Muon'           : '!Trigger_ElMu && (Trigger_sngMu || Trigger_dblMu)',
    'EGamma'         : '!Trigger_ElMu && !Trigger_sngMu && !Trigger_dblMu && (Trigger_sngEl || Trigger_dblEl)'
}

#########################################
############ MC COMMON ##################
#########################################

# tomas kello
# mcCommonWeightNoMatch = 'XSWeight*METFilter_Common*SFweight'
# mcCommonWeight        = 'XSWeight*METFilter_Common*PromptGenLepMatch2l*SFweight'


mcCommonWeightNoMatch = 'XSWeight*METFilter_Common*SFweight'
mcCommonWeight        = 'XSWeight*METFilter_Common*PromptGenLepMatch2l*SFweight'

# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * PromptGenLepMatch2l'
# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * METFilter_MC * PromptGenLepMatch2l'
# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * Jet_PUIDSF * METFilter_MC * PromptGenLepMatch2l'
# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * Jet_PUIDSF * btagSF * METFilter_MC * PromptGenLepMatch2l'




# ##########
# ### DY ###
# ##########

# DYto2L-2Jets_MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8

files = nanoGetSampleFiles(mcDirectory, 'DYto2L-2Jets_MLL-10to50') | \
        nanoGetSampleFiles(mcDirectory, 'DYto2L-2Jets_MLL-50')

samples['DY'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 240000,
}


# ############
# ### Top   ##
# ############

# TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8
# TbarWplusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8
# TWminusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8
# TBbarQ_t-channel_4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8
# TbarBQ_t-channel_4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8
# TBbartoLplusNuBbar-s-channel-4FS_TuneCP5_13p6TeV_amcatnlo-pythia8
# TbarBtoLminusNuB-s-channel-4FS_TuneCP5_13p6TeV_amcatnlo-pythia8

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
    'EventsPerJob': 240000,
}
addSubSampleWeights(samples,'top','TTTo2L2Nu','Top_pTrw')

# # tVx
# TTLNu-1Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# TTLL_MLL-4to50_TuneCP5_13p6TeV_amcatnlo-pythia8
# TTLL_MLL-50_TuneCP5_13p6TeV_amcatnlo-pythia8
# TZQB-Zto2L-4FS_MLL-30_TuneCP5_13p6TeV_amcatnlo-pythia8
# TTWW_TuneCP5_13p6TeV_madgraph-madspin-pythia8
# TTZZ_TuneCP5_13p6TeV_madgraph-madspin-pythia8

files = nanoGetSampleFiles(mcDirectory, 'TTLNu') | \
        nanoGetSampleFiles(mcDirectory, 'TTLL_MLL-4to50') | \
        nanoGetSampleFiles(mcDirectory, 'TTLL_MLL-50') | \
        nanoGetSampleFiles(mcDirectory, 'TZQB-ZTo2L') | \
        nanoGetSampleFiles(mcDirectory, 'TTWW') | \
        nanoGetSampleFiles(mcDirectory, 'TTZZ') 


samples['tVx'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 500000,
}

# ##########################################
# ## WW QCD and gluon-induced background ###
# ##########################################

# GluGlutoContintoWWtoENuENu_TuneCP5_13p6TeV_mcfm701-pythia8
# GluGlutoContintoWWtoENuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8
# GluGlutoContintoWWtoENuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8
# GluGlutoContintoWWtoMuNuENu_TuneCP5_13p6TeV_mcfm701-pythia8
# GluGlutoContintoWWtoMuNuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8
# GluGlutoContintoWWtoMuNuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8
# GluGlutoContintoWWtoTauNuENu_TuneCP5_13p6TeV_mcfm701-pythia8
# GluGlutoContintoWWtoTauNuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8
# GluGlutoContintoWWtoTauNuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8

files = nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoENuENu') | \
        nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoENuMuNu') | \
        nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoENuTauNu') |	\
        nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoMuNuENu') |	\
        nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoMuNuMuNu') |	\
        nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoMuNuTauNu') |	\
        nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoTauNuENu') |	\
        nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoTauNuMuNu') |	\
        nanoGetSampleFiles(mcDirectory, 'GluGlutoContintoWWtoTauNuTauNu')

samples['ggWW'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 240000,
}


# ##########
# ### VZ ###
# ##########
# WZto3LNu-2Jets_EW_TuneCP5_13p6TeV_madgraph-madspin-pythia8
# WZto3LNu-2Jets_QCD_TuneCP5_13p6TeV_madgraph-madspin-pythia8
# VBSWZ-Interference_TuneCP5_13p6TeV_madgraph-pythia8

files = nanoGetSampleFiles(mcDirectory, 'WZJJ_EWK')
samples['WZJJ_EWK'] = {
    'name': files,
    'weight': mcCommonWeight + ' * (Gen_ZGstar_mass >= 50)',
    'EventsPerJob': 500000,
}

files = nanoGetSampleFiles(mcDirectory, 'WZJJ_QCD') 

samples['WZJJ_QCD'] = {
    'name': files,
    'weight': mcCommonWeight + ' * (Gen_ZGstar_mass >= 50)',
    'EventsPerJob': 500000,
}

files = nanoGetSampleFiles(mcDirectory, 'WZJJ_Interference') 
samples['WZJJ_Int'] = {
    'name': files,
    'weight': mcCommonWeight + ' * (Gen_ZGstar_mass >= 50)',
    'EventsPerJob': 500000,
}

# ZZto2L2Nu-2Jets_QCD_TuneCP5_13p6TeV_madgraph-pythia8
# ZZto2L2Nu-2Jets_EW_TuneCP5_13p6TeV_madgraph-pythia8
# ZZto4L-2Jets_QCD_TuneCP5_13p6TeV_madgraph-pythia8
# ZZto4L-2Jets_EW_TuneCP5_13p6TeV_madgraph-pythia8
# GluGlutoContinto2Zto4Tau_TuneCP5_13p6TeV_mcfm701-pythia8

files = nanoGetSampleFiles(mcDirectory, 'ZZJJTo4L_EWK') | \
        nanoGetSampleFiles(mcDirectory, 'ZZJJTo4L_QCD') | \
        nanoGetSampleFiles(mcDirectory, 'ZZJJTo2L2Nu_EWK') | \
        nanoGetSampleFiles(mcDirectory, 'ZZJJTo2L2Nu_QCD') | \
        nanoGetSampleFiles(mcDirectory, 'GluGluToZZTo4e') | \
        nanoGetSampleFiles(mcDirectory, 'GluGluToZZTo4mu') | \
        nanoGetSampleFiles(mcDirectory, 'GluGluToZZTo4tau') | \
        nanoGetSampleFiles(mcDirectory, 'GluGluToZZTo2e2mu') | \
        nanoGetSampleFiles(mcDirectory, 'GluGluToZZTo2e2tau') | \
        nanoGetSampleFiles(mcDirectory, 'GluGluToZZTo2mu2tau')

samples['ZZ'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 500000,
}

# WW_DoubleScattering_TuneCP5_13p6TeV_pythia8
files = nanoGetSampleFiles(mcDirectory, 'WW_DPS')
samples['WW_DPS'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 500000,
}    

# ##################
# ### Vg/VgS/VZS ###
# ##################
# DYGto2LG-1Jets_MLL-4to50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-4to50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-4to50_PTG-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-50_PTG-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-50_PTG-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-50_PTG-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8

files = nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-4to50_PTG-10to100') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-4to50_PTG-100to200') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-4to50_PTG-200') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-50_PTG-10to100') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-50_PTG-100to200') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-50_PTG-200to400') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-50_PTG-400to600') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-50_PTG-600')

samples['Zg'] = {
    'name': files,
    'weight': mcCommonWeightNoMatch + '*(Gen_ZGstar_mass <= 0)',
    'EventsPerJob': 500000,
}

# /WGtoLNuG-1Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
files = nanoGetSampleFiles(mcDirectory, 'WGtoLNuG-1J_PTG10to100') | \
        nanoGetSampleFiles(mcDirectory, 'WGtoLNuG-1J_PTG100to200') | \
        nanoGetSampleFiles(mcDirectory, 'WGtoLNuG-1J_PTG200to400') | \
        nanoGetSampleFiles(mcDirectory, 'WGtoLNuG-1J_PTG400to600') | \
        nanoGetSampleFiles(mcDirectory, 'WGtoLNuG-1J_PTG600')

samples['Wg'] = {
    'name': files,
    'weight': mcCommonWeightNoMatch + '*(Gen_ZGstar_mass <= 0)',
    'EventsPerJob': 500000,
}

# DYGto2LG-1Jets_MLL-4to50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-4to50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-4to50_PTG-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-50_PTG-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-50_PTG-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8
# DYGto2LG-1Jets_MLL-50_PTG-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8

files = nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-4to50_PTG-10to100') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-4to50_PTG-100to200') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-4to50_PTG-200') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-50_PTG-10to100') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-50_PTG-100to200') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-50_PTG-200to400') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-50_PTG-400to600') | \
        nanoGetSampleFiles(mcDirectory, 'DYGto2LG-1Jets_MLL-50_PTG-600')

samples['ZgS'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 500000,
}

addSubSampleWeights(samples, 'ZgS', "DYGto2LG-1Jets_MLL-4to50_PTG-10to100", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")
addSubSampleWeights(samples, 'ZgS', "DYGto2LG-1Jets_MLL-4to50_PTG-100to200", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")
addSubSampleWeights(samples, 'ZgS', "DYGto2LG-1Jets_MLL-4to50_PTG-200", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")
addSubSampleWeights(samples, 'ZgS', "DYGto2LG-1Jets_MLL-50_PTG-10to100", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")
addSubSampleWeights(samples, 'ZgS', "DYGto2LG-1Jets_MLL-50_PTG-100to200", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")
addSubSampleWeights(samples, 'ZgS', "DYGto2LG-1Jets_MLL-50_PTG-200to400", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")
addSubSampleWeights(samples, 'ZgS', "DYGto2LG-1Jets_MLL-50_PTG-400to600", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")
addSubSampleWeights(samples, 'ZgS', "DYGto2LG-1Jets_MLL-50_PTG-600", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")

# WGtoLNuG-1Jets_PTG-*_TuneCP5_13p6TeV_amcatnloFXFX-pythia8

files = nanoGetSampleFiles(mcDirectory, 'WGtoLNuG-1J_PTG10to100') | \
        nanoGetSampleFiles(mcDirectory, 'WGtoLNuG-1J_PTG100to200') | \
        nanoGetSampleFiles(mcDirectory, 'WGtoLNuG-1J_PTG200to400') | \
        nanoGetSampleFiles(mcDirectory, 'WGtoLNuG-1J_PTG400to600') | \
        nanoGetSampleFiles(mcDirectory, 'WGtoLNuG-1J_PTG600')

samples['WgS'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 500000,
}

addSubSampleWeights(samples, 'WgS', "WGtoLNuG-1J_PTG10to100", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")
addSubSampleWeights(samples, 'WgS', "WGtoLNuG-1J_PTG100to200", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")
addSubSampleWeights(samples, 'WgS', "WGtoLNuG-1J_PTG200to400", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")
addSubSampleWeights(samples, 'WgS', "WGtoLNuG-1J_PTG400to600", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")
addSubSampleWeights(samples, 'WgS', "WGtoLNuG-1J_PTG600", "(Gen_ZGstar_mass > 0 && Gen_ZGstar_mass <= 4)")

# WZ + 2 jets, low mass Z/gamma* (4 <= m < 50 GeV)

# WZto3LNu-2Jets_EW_TuneCP5_13p6TeV_madgraph-madspin-pythia8
files =  nanoGetSampleFiles(mcDirectory, "WZJJ_EWK")
samples['WZSJJ_EWK'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 500000,
}

addSubSampleWeights(samples, 'WZSJJ_EWK', "WZJJ_EWK", "(Gen_ZGstar_mass >= 4 && Gen_ZGstar_mass < 50)")    


files =  nanoGetSampleFiles(mcDirectory, "WZJJ_QCD") | \
         nanoGetSampleFiles(mcDirectory, "WZJJ_Interference")

samples['WZSJJ_QCD'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 500000,
}

addSubSampleWeights(samples, 'WZSJJ_QCD', "WZJJ_QCD", "(Gen_ZGstar_mass >= 4 && Gen_ZGstar_mass < 50)")    
addSubSampleWeights(samples, 'WZSJJ_QCD', "WZJJ_Interference", "(Gen_ZGstar_mass >= 4 && Gen_ZGstar_mass < 50)")    

# ##################
# ### Multiboson ###
# ##################
# WWW_4F_TuneCP5_13p6TeV_amcatnlo-madspin-pythia8
# WWZ_4F_TuneCP5_13p6TeV_amcatnlo-pythia8
# WZZ_TuneCP5_13p6TeV_amcatnlo-pythia8
# ZZZ_TuneCP5_13p6TeV_amcatnlo-pythia8

files = nanoGetSampleFiles(mcDirectory, 'WWW') | \
        nanoGetSampleFiles(mcDirectory, 'WWZ') | \
        nanoGetSampleFiles(mcDirectory, 'WZZ') | \
        nanoGetSampleFiles(mcDirectory, 'ZZZ') | \
        nanoGetSampleFiles(mcDirectory, 'WZG')


samples['VVV'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 500000,
}
# ##################
# ###    Higgs   ###
# ##################
# GluGluHto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-jhugen752-pythia8
files = nanoGetSampleFiles(mcDirectory, 'GluGluHToWWTo2L2Nu_M125')

samples['ggH_hww'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 500000,
}

# VBFHto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-jhugen752-pythia8
files = nanoGetSampleFiles(mcDirectory, 'VBFHToWWTo2L2Nu_M125')

samples['qqH_hww'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 500000,
}

files = nanoGetSampleFiles(mcDirectory, 'VH-HToNon2B') | \
        nanoGetSampleFiles(mcDirectory, 'ttHToNonbb_M125') | \
        nanoGetSampleFiles(mcDirectory, 'GluGluHToZZTo4L_M125') | \
        nanoGetSampleFiles(mcDirectory, 'VBFHToTauTau_M125') | \
        nanoGetSampleFiles(mcDirectory, 'VBFHToZZTo4L_M125') | \
        nanoGetSampleFiles(mcDirectory, 'GluGluHToTauTau_M125')

samples['higgs'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 500000,
}

# # OS WW
files = nanoGetSampleFiles(mcDirectory, 'WpWmJJ_QCD_noTop') | \
        nanoGetSampleFiles(mcDirectory, 'WpWmJJ_EWK_noTop')
        
samples['OSWW'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 500000,
}




# ###########################################
# #############    SIGNALS  #################
# ###########################################

#   WpWpJJ_EWK-QCD_TuneCP5_13p6TeV_madgraph-pythia8
files = nanoGetSampleFiles(mcDirectory, 'VBS_SSWW')
samples['VBS_SSWW'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 250000,
}

#### polarized:

# VBS-SSWW_PolarizationLL_TuneCP5_13p6TeV_madgraph-pythia8
files = nanoGetSampleFiles(mcDirectory, 'VBS_SSWW_WWCM_LL')
samples['VBS_SSWW_WWCM_LL'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 250000,
}

# VBS-SSWW_PolarizationTL_TuneCP5_13p6TeV_madgraph-pythia8
files = nanoGetSampleFiles(mcDirectory, 'VBS_SSWW_WWCM_TL')
samples['VBS_SSWW_WWCM_TL'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 250000,
}

# VBS-SSWW_PolarizationTT_TuneCP5_13p6TeV_madgraph-pythia8
files = nanoGetSampleFiles(mcDirectory, 'VBS_SSWW_WWCM_TT')
samples['VBS_SSWW_WWCM_TT'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 250000,
}

# WWto2L2Nu-2Jets_SS_noTop_EW_TuneCP5_13p6TeV_madgraph-pythia8
files = nanoGetSampleFiles(mcDirectory, 'WpWpJJ_EWK_noTop')
samples['WW_EWK'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 250000,
}

# WWto2L2Nu-2Jets_SS_noTop_QCD_TuneCP5_13p6TeV_madgraph-pythia8
files = nanoGetSampleFiles(mcDirectory, 'WpWpJJ_QCD_noTop')
samples['WW_QCD'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 250000,
}

# SSWWJJ_Interference_TuneCP5_13p6TeV_madgraph-pythia8
files = nanoGetSampleFiles(mcDirectory, 'WpWpJJ_Interference')
samples['WW_Int'] = {
    'name': files,
    'weight': mcCommonWeight,
    'EventsPerJob': 250000,
}

# ###########
# ## DATA ###
# ############
samples['DATA'] = { 
    'name': {},  
    'weight': 'LepWPCut*METFilter_DATA',     
    'weights': {}, 
    'isData': ['all'], 
    'FilesPerJob': 15 
} 

for _, sd in DataRun:
    for pd in DataSets:
        datatag = pd + '_' + sd

        print(datatag)
        files = nanoGetSampleFiles(dataDirectory, datatag)
        samples['DATA']['name'].update(files)
        samples['DATA']['weights'].update({
            datatag: DataTrig[pd]
        })


# #############
# ### Fakes ###
# #############
samples['Fake'] = {
    'name': {},
    'weight': 'METFilter_DATA*fakeW',
    'weights': {},
    'isData': ['all'],
    'FilesPerJob': 15
}


for _, sd in DataRun:
    for pd in DataSets:
        datatag = pd + '_' + sd
        files = nanoGetSampleFiles(fakeDirectory, datatag)
        samples['Fake']['name'].update(files)
        samples['Fake']['weights'].update({
            datatag: DataTrig[pd]
        })