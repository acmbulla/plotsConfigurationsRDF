from search_files import SearchFiles
import os
searchFiles = SearchFiles()

useXROOTD = False
redirector = 'root://eoscms.cern.ch/'

# ---------------------------------------------------------------------------
# Productions. BOTH OF THESE HAVE TO BE PRODUCED -- neither exists yet.
#
# The analysis productions cannot be used for this measurement:
#
#   MCl2loose2024v15__MCCorr2024v15__JERFrom23BPix__l2tight ends with the
#   l2tight step (mkShapesRDF L2TightSelection.py:33-35), a filter requiring
#   both Lepton_[0] and Lepton_[1] to pass a tight WP. The loose denominator
#   does not exist in that MC, so the denominator cannot be prompt-subtracted.
#
#   The existing l1loose MC chains all go through fakeSel, which is
#   Filter("MET_pt < 20 || PuppiMET_pt < 20") (FakeSel.py:14) and runs on MC
#   only (do4MC True, do4Data False), so data and MC would not share it.
#
# What to request, both in mkShapesRDF Steps_cfg.py and as a production:
#
#   MC   'MCl1loose2024v15__MCCorr2024v15__JERFrom23BPix'
#        = the chain at Steps_cfg.py:449 with the "fakeSel" subTarget removed.
#   DATA 'DATAl1loose2024v15'
#        = the entry at Steps_cfg.py:1449, edited in place to carry the
#          subTargets of :1468 minus "fakeSel": jetIDMaker,
#          JES_modules_reducedv15_DATA and leptonScale_data added, in that
#          order, before jetSelMask and l2Kin respectively.
#
# Both live in Steps_cfg.py, which belongs to mkShapesRDF, not here.
#
# Why not the two existing chains as they are:
#
#   fakeSel runs on data as well as MC. The do4MC / do4Data flags in
#   Steps_cfg.py are inert -- they appear nowhere else in mkShapesRDF, and
#   addDeclareLines (processor.py:156-158) emits every subTarget
#   unconditionally -- so '...__fakeSel' would apply
#   Filter("MET_pt < 20 || PuppiMET_pt < 20") (FakeSel.py:14) to both.
#
#   'DATAl1loose2024v15' as it stood had no leptonScale_data, while the MC
#   chain has leptonScale_mc, and both analysis productions have their
#   respective one. leptonScale_* is LeptonScaleSmearing, which corrects
#   Lepton_pt -- the axis the map is binned in. Measuring f(pT, eta) on
#   uncalibrated data and applying it to events with calibrated Lepton_pt
#   evaluates the map at the wrong pT. That, and not the jets, is what the
#   missing block costs: nothing in cuts.py cuts on a jet, the jet variables
#   are dumped only, so the JEC and the JER are along for the ride. They are
#   free anyway -- the chains end with finalSnapshot_{MC,DATA}, which have
#   includeVariations=False, so no variation tree is written.
#
# Both chains use the same trigData step, and TrigMaker neither filters nor
# looks at the lepton multiplicity (TrigMaker.py:385-404), so the trigger
# decisions -- dblMu / dblEl / ElMu included -- are identical to the l2loose
# production's.
#
# l1loose is a superset of l2loose in multiplicity -- its chain selection is
# "((nElectron+nMuon)>0)" against "((nElectron+nMuon)>1)" -- so one pair of
# productions covers both the 1-lepton and the 2-lepton branch of cuts.py.
# Only VV, W+jets, DY and top are needed on the MC side.
# ---------------------------------------------------------------------------
mcProduction       = 'Summer24_150x_nAODv15_Full2024v15'
mcSteps            = 'MCl1loose2024v15__MCCorr2024v15__JERFrom23BPix'
dataRecoEGamma     = 'Run2024_ReRecoCDE_PromptFGHI_nAODv15_Full2024v15_EGamma'
dataRecoMuon       = 'Run2024_ReRecoCDE_PromptFGHI_nAODv15_Full2024v15_Muon'
dataRecoMuonEG     = 'Run2024_ReRecoCDE_PromptFGHI_nAODv15_Full2024v15_MuonEG'
dataSteps          = 'DATAl1loose2024v15'

# The analysis productions, for reference. Do not point the measurement at
# these: see above.
# mcSteps   = 'MCl2loose2024v15__MCCorr2024v15__JERFrom23BPix__l2tight'
# dataSteps = 'DATAl2loose2024v15__l2loose'

##############################################
###### Tree base directory for the site ######
##############################################
treeBaseDirLat = '/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano'
treeBaseDirPVT = '/eos/cms/store/group/phys_smp/ec/Latinos/HWWNano'
limitFiles = -1

def makeMCDirectory(treeBaseDir, var=""):
    _treeBaseDir = treeBaseDir + ""
    if var == "":
        return "/".join([_treeBaseDir, mcProduction, mcSteps])
    else:
        return "/".join([_treeBaseDir, mcProduction, mcSteps + "__" + var])



mcDirectory    = makeMCDirectory(treeBaseDirLat)
mcDirectoryPVT = makeMCDirectory(treeBaseDirPVT)
print(mcDirectory)
print(mcDirectoryPVT)
dataDirectoryMuon = os.path.join(treeBaseDirPVT, dataRecoMuon, dataSteps)
dataDirectoryEGamma = os.path.join(treeBaseDirPVT, dataRecoEGamma, dataSteps)
dataDirectoryMuonEG = os.path.join(treeBaseDirPVT, dataRecoMuonEG, dataSteps)


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

# ---------------------------------------------------------------------------
# Measurement weights -- deliberately NOT the analysis ones.
#
# The analysis uses SFweight = SFweightNl * LepWPCutN * LepWPSFN * btagSF*,
# which is wrong here on two counts:
#
#   1. LepWPCutN is the *tight* requirement. The fake rate is a ratio of tight
#      over loose, so the denominator must keep the loose leptons that fail
#      tight. Folding the tight cut into the weight would make numerator and
#      denominator identical and the ratio exactly 1.
#   2. SFweightNl / LepWPSFN / LepSF{N}l exist for N = 2, 3, 4 only. The
#      measurement region has one lepton, so every term of
#      '(nLepSel == N) * ...' is false and the whole weight collapses to 0.
#      There is no SFweight1l in the nanoAOD to switch to.
#
#   3. No PromptGenLepMatch either, and this one is not an omission. The
#      nanoAOD flag is an AND over the event: PromptGenLepMatch{N}l is true
#      only if *all* N selected leptons are prompt. The subtraction here is
#      per lepton -- in a same-sign pair made of one prompt lepton and one
#      fake, lepton 0 belongs in the prompt term and lepton 1 does not -- so
#      an event-level AND would give that event weight 0 and under-subtract
#      exactly the configuration that dominates. The per-lepton flag
#      SelLep_promptgenmatched[i] is in the snapshot and is applied inside the
#      probe loop in plotFake.py, where it can distinguish the two legs.
#      (PromptGenLepMatch1l does not exist in the nanoAOD in any case: like
#      LepCut{N}l and SFweight{N}l it is defined for N = 2, 3, 4 only.)
#
# What is left is the event-level normalisation alone. The tight-lepton scale
# factor is not applied to either term: it is a tight-lepton efficiency
# correction, it does not describe a loose lepton, and it largely cancels in
# the ratio.
#
# The two names are therefore the same expression. Both are kept because the
# sample definitions below use each of them, and keeping them distinct leaves
# the Gen_ZGstar_mass stitching untouched.
mcCommonWeightNoMatch = 'XSWeight*METFilter_Common'
mcCommonWeight        = 'XSWeight*METFilter_Common'

# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * PromptGenLepMatch2l'
# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * METFilter_MC * PromptGenLepMatch2l'
# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * Jet_PUIDSF * METFilter_MC * PromptGenLepMatch2l'
# mcCommonWeight = 'XSWeight * SFweight2l * LepWPCut * LepWPSF * Jet_PUIDSF * btagSF * METFilter_MC * PromptGenLepMatch2l'



# ===========================================================================
# MC: only what the prompt subtraction needs.
#
# This is deliberately a short list. The MC enters the measurement in one way
# only -- as the prompt term that is subtracted from data, per lepton, keyed on
# SelLep_promptgenmatched[i] at fill time. So the processes that belong here are
# the ones that put a *prompt* lepton in the measurement region, not the ones
# that produce fakes: a fake is what is being measured, and it comes from data.
#
# Everything the analysis config carries and this one does not -- Higgs, ggWW,
# VVV, tVx, Wg/Zg, the whole VBS signal -- is either negligible as a prompt
# source or, for 37 of the 77 datasets the analysis samples.py asks for, not in
# the Summer24_150x_nAODv15 production at all (VBS and the VBS-shaped VV like
# WZJJ_EWK and ZZJJTo4L_*, ggZZ, and the Wg/Zg pT-binned names, which differ in
# the production).
# ===========================================================================

##########
### DY ###
##########
# Both the prompt term in the FR region and the DY region itself, where the
# prompt rate is measured. MLL-10to50 is kept: the DY region reaches below the
# peak and the FR region only cuts mll > 12.

files = nanoGetSampleFiles(mcDirectoryPVT, 'DYto2E-2Jets_MLL-50') | \
        nanoGetSampleFiles(mcDirectoryPVT, 'DYto2Mu-2Jets_MLL-50') | \
        nanoGetSampleFiles(mcDirectoryPVT, 'DYto2Tau-2Jets_MLL-50') | \
        nanoGetSampleFiles(mcDirectoryPVT, 'DYto2E-2Jets_MLL-10to50') | \
        nanoGetSampleFiles(mcDirectoryPVT, 'DYto2Mu-2Jets_MLL-10to50') | \
        nanoGetSampleFiles(mcDirectoryPVT, 'DYto2Tau-2Jets_MLL-10to50')
samples['DY'] = {
    'name': files,
    'weight': mcCommonWeight,
    'MaxEventsPerJob': 200000,
}


##############
### W+jets ###
##############
# The dominant prompt contamination, and the one the analysis config does not
# carry at all (there W+jets is a fake, handled by the data-driven fakeW). Here
# it is the opposite: the lepton from the W is prompt and passes tight with high
# efficiency, so leaving it in the denominator biases f upward.
#
# amcatnloFXFX with up to 2 jets in the matrix element: inclusive in jet
# multiplicity, no generator cut. Not the WtoLNu-4Jets_*_HT-* MLM series, whose
# lowest bin starts at HT 40 and so leaves a hole in a region that requires no
# jet. The two series are alternatives, never summed.

files = nanoGetSampleFiles(mcDirectory, 'WToENu-2Jet') | \
        nanoGetSampleFiles(mcDirectory, 'WToMuNu-2Jet') | \
        nanoGetSampleFiles(mcDirectory, 'WToTauNu-2Jet')
samples['Wjets'] = {
    'name': files,
    'weight': mcCommonWeight,
    'MaxEventsPerJob': 200000,
}


############
### Top  ###
############
# TTToSemiLeptonic matters more here than the dileptonic one: one prompt lepton
# plus jets is exactly the topology of the QCD-enriched region. s-channel single
# top is dropped as negligible.

files = nanoGetSampleFiles(mcDirectory, 'TTTo2L2Nu') | \
        nanoGetSampleFiles(mcDirectory, 'TTToSemiLeptonic') | \
        nanoGetSampleFiles(mcDirectory, 'TbarWplusto2L2Nu') | \
        nanoGetSampleFiles(mcDirectory, 'TWminusto2L2Nu') | \
        nanoGetSampleFiles(mcDirectory, 'ST_t-channel_top') | \
        nanoGetSampleFiles(mcDirectory, 'ST_t-channel_antitop')
samples['top'] = {
    'name': files,
    'weight': mcCommonWeight,
    'MaxEventsPerJob': 200000,
}
addSubSampleWeights (samples, 'top', 'TTTo2L2Nu', 'Top_pTrw')


###########
### WZ  ###
###########
# The irreducible prompt background of the same-sign branch: WZ really does
# give prompt same-sign pairs.

files = nanoGetSampleFiles(mcDirectory, 'WZTo3LNu')
samples['WZ'] = {
    'name': files,
    'weight': mcCommonWeight,
    'MaxEventsPerJob': 200000,
}


###########
### ZZ  ###
###########
files = nanoGetSampleFiles(mcDirectory, 'ZZTo4L') | \
        nanoGetSampleFiles(mcDirectory, 'ZZTo2L2Nu')
samples['ZZ'] = {
    'name': files,
    'weight': mcCommonWeight,
    'MaxEventsPerJob': 200000,
}


###########
### WW  ###
###########
# Opposite-sign prompt: it matters in the DY region, and in ee it leaks into
# the same-sign branch through charge mis-identification.

files = nanoGetSampleFiles(mcDirectory, 'WWTo2L2Nu')
samples['WW'] = {
    'name': files,
    'weight': mcCommonWeight,
    'MaxEventsPerJob': 200000,
}



###########
## DATA ###
############
samples['DATA'] = {
    'name': {},
    # no LepWPCut: same reason as mcCommonWeight above -- it is the tight
    # requirement, and the loose denominator has to survive it.
    'weight': 'METFilter_DATA',
    'weights': {},
    'isData': ['all'],
    'FilesPerJob': 100
}

for _, sd in DataRun:
    for pd in DataSets:
        datatag = pd + '_' + sd
        if datatag.startswith('MuonEG'):
            files = nanoGetSampleFiles(dataDirectoryMuonEG, datatag)
        elif datatag.startswith('Muon'):
            files = nanoGetSampleFiles(dataDirectoryMuon, datatag)
        elif datatag.startswith('EGamma'):
            files = nanoGetSampleFiles(dataDirectoryEGamma, datatag)
        print(datatag)
        samples['DATA']['name'].update(files)
        samples['DATA']['weights'].update({
            datatag: DataTrig[pd]
        })

# #############
# ### Fakes ###
# #############
# No Fake sample here. It is weighted by fakeW, i.e. by the fake rate this
# configuration exists to measure, so including it would be circular. The
# closure test that *applies* the measured rate belongs in the analysis config.
