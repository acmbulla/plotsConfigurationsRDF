mcProduction       = 'Summer24_150x_nAODv15_Full2024v15'
mcSteps            = 'MCl2loose2024v15__MCCorr2024v15__JERFrom23BPix__l2tight'
dataRecoMuon       = 'Run2024_ReRecoCDE_PromptFGHI_nAODv15_Full2024v15_Muon'
dataRecoEGamma     = 'Run2024_ReRecoCDE_PromptFGHI_nAODv15_Full2024v15_EGamma'
dataRecoMuonEG     = 'Run2024_ReRecoCDE_PromptFGHI_nAODv15_Full2024v15_MuonEG'
dataSteps          = 'DATAl2loose2024v15__l2loose'
fakeSteps          = 'DATAl2loose2024v15__l2loose'

treeBaseDir = '/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano'
limitFiles = -1

ALL = [skey for skey in samples]
mc = [skey for skey in samples if skey not in ('DATA', 'Fake')]
# The samples with an LHE record, i.e. the ones whose datasets come from
# madgraph or powheg and so carry LHEScaleWeight and LHEPdfWeight. The three
# left out, with the generator that puts them there:
#   ggWW    GluGluWWto*          mcfm-pythia8
#   ZZ      the ZZJJ* parts are madgraph, but GluGluToZZTo* is mcfm701, and a
#           sample is usable here only if EVERY dataset in it has the branch
#   WW_DPS  WW_DoubleScattering  pythia8 alone
# Keep this identical to the list in aliases.py, which is what DEFINES
# LHEScaleWeight_vec and LHEPdfWeight_vec: nuisances.py is exec'd before
# aliases.py and in its own namespace, so it cannot read it from there, and a
# nuisance naming a sample that has no such column is a crash, not a warning.
# WW_DPS was missing here while aliases.py excluded it, so every scale and pdf
# nuisance was asking for a column that sample does not have.
lhesamples = [skey for skey in mc if skey not in ('ggWW', 'ZZ', 'WW_DPS')]


redirector = 'root://eoscms.cern.ch/'
useXROOTD = True

def makeMCDirectory(var=''):
    _treeBaseDir = treeBaseDir + ''
    if useXROOTD:
        _treeBaseDir = redirector + treeBaseDir
    if var== '':
        return '/'.join([_treeBaseDir, mcProduction, mcSteps])
    else:
        return '/'.join([_treeBaseDir, mcProduction, mcSteps + '__' + var])



mcDirectory = makeMCDirectory()
fakeDirectoryMuon = os.path.join(treeBaseDir, dataRecoMuon, fakeSteps)
dataDirectoryMuon = os.path.join(treeBaseDir, dataRecoMuon, dataSteps)
fakeDirectoryEGamma = os.path.join(treeBaseDir, dataRecoEGamma, fakeSteps)
dataDirectoryEGamma = os.path.join(treeBaseDir, dataRecoEGamma, dataSteps)
fakeDirectoryMuonEG = os.path.join(treeBaseDir, dataRecoMuonEG, fakeSteps)
dataDirectoryMuonEG = os.path.join(treeBaseDir, dataRecoMuonEG, dataSteps)
print(treeBaseDir)

# # merge cuts
# _mergedCuts = []
# for cut in list(cuts.keys()):
#     __cutExpr = ''
#     if type(cuts[cut]) == dict:
#         __cutExpr = cuts[cut]['expr']
#         for cat in list(cuts[cut]['categories'].keys()):
#             _mergedCuts.append(cut + '_' + cat)
#     elif type(cuts[cut]) == str:
#         _mergedCuts.append(cut)

# cuts2j = _mergedCuts

# nuisances = {}

################################ EXPERIMENTAL UNCERTAINTIES  #################################

# https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun3
# 2022: 34.75 fb⁻¹ (±1.4%)
# 2023: 28.40 fb⁻¹ (±1.3%)
# 2024: 110.11 fb⁻¹ (±1.6%)
# 2025: 125.07 fb⁻¹ (±5%) — preliminare
# 2026: nessuna incertezza disponibile ancora


nuisances['lumi_1'] = {
    'name': 'lumi_1',
    'type': 'lnN',
    'samples': dict((skey, '1.0020') for skey in mc)
}

nuisances['lumi_2'] = {
    'name': 'lumi_2',
    'type': 'lnN',
    'samples': dict((skey, '1.0068') for skey in mc)
}

nuisances['lumi_3'] = {
    'name': 'lumi_3',
    'type': 'lnN',
    'samples': dict((skey, '1.0144') for skey in mc)
}


# nuisances['JER'] = {
#     'name': 'CMS_res_j_2024',
#     'skipCMS' : 1,
#     'kind': 'suffix',
#     'type': 'shape',
#     'mapUp': 'jerup',
#     'mapDown': 'jerdo',
#     #'separator': '__',
#     'samples': dict((skey, ['1', '1']) for skey in mc),
#     'folderUp': makeMCDirectory('jerup_suffix'),
#     'folderDown': makeMCDirectory('jerdo_suffix'),
#     'AsLnN': '0'
# }


# jes_sources = ['Absolute_2024','Absolute','BBEC1_2024','BBEC1','EC2_2024','EC2','FlavorQCD','HF_2024','HF','RelativeBal','RelativeSample_2024']
# jes_sources = ["jesRegroed_"+ _ for _ in jes_sources] 
# for js in jes_sources:
#     nuisances[js] = {
#         'name': f'CMS_scale_{js}',
#         'skipCMS' : 1,
#         'kind': 'suffix',
#         'type': 'shape',
#         'mapUp': f'{js}up',
#         'mapDown': f'{js}do',
#         #'separator': '__',
#         'samples': dict((skey, ['1', '1']) for skey in mc),
#         'folderUp': makeMCDirectory(f'{js}up_suffix'),
#         'folderDown': makeMCDirectory(f'{js}do_suffix'),
#         'AsLnN': '0'
#     }

# #BUGGED FIXME TODO
# '''
# nuisances['MET'] = {
#     'name': 'CMS_scale_met_2024',
#     'skipCMS' : 1,
#     'kind': 'suffix',
#     'type': 'shape',
#     'mapUp': 'unclustEnup',
#     'mapDown': 'unclustEndo',
#     #'separator': '__',
#     'samples': dict((skey, ['1', '1']) for skey in mc),
#     'folderUp': makeMCDirectory('unclustEnup_suffix'),
#     'folderDown': makeMCDirectory('unclustEndo_suffix'),
#     'AsLnN': '0'
# }
# '''

# ##### Lepton scale
# nuisances['lepscale'] = {
#     'name': 'CMS_lepscale_2024',
#     'skipCMS' : 1,
#     'kind': 'suffix',
#     'type': 'shape',
#     'mapUp': 'leptonScaleup',
#     'mapDown': 'leptonScaledo',
#     #'separator': '__',
#     'samples': dict((skey, ['1', '1']) for skey in mc),
#     'folderUp': makeMCDirectory('leptonScaleup_suffix'),
#     'folderDown': makeMCDirectory('leptonScaledo_suffix'),
#     'AsLnN': '0'
# }

# ##### Lepton resolution
# nuisances['lepres'] = {
#     'name': 'CMS_lepres_2024',
#     'skipCMS' : 1,
#     'kind': 'suffix',
#     'type': 'shape',
#     'mapUp': 'leptonResolutionup',
#     'mapDown': 'leptonResolutiondo',
#     #'separator': '__',
#     'samples': dict((skey, ['1', '1']) for skey in mc),
#     'folderUp': makeMCDirectory('leptonResolutionup_suffix'),
#     'folderDown': makeMCDirectory('leptonResolutiondo_suffix'),
#     'AsLnN': '0'
# }

# # ## B-tagger
# # Fixed BTV SF variations
nuisance_sources = {
    'bc': ['bfragmentation', 'fsrdef', 'hdamp', 'isrdef', 'jer', 'jes', 'muf', 'mur', 'pdfas', 'pileup', 'statistic', 'topmass', 'type3'],   
    'light': [ 'correlated', 'uncorrelated'],
}

for flavour in ['bc', 'light']:
    for corr in ['uncorrelated', 'correlated']:
        btag_syst = [f'btagSF{flavour}_up_{corr}/btagSF{flavour}', f'btagSF{flavour}_down_{corr}/btagSF{flavour}']
        if corr == 'correlated':
            name = f'CMS_btagSF{flavour}_{corr}'
        else:
            name = f'CMS_btagSF{flavour}_2024'
        nuisances[f'btagSF{flavour}{corr}'] = {
            'name': name,
            'skipCMS' : 1,
            'kind': 'weight',
            'type': 'shape',
            'samples': dict((skey, btag_syst) for skey in mc),
        }

'''
for source in nuisance_sources['bc']:
    btag_syst = [f'btagSFbc_up_{source}/btagSFbc', f'btagSFbc_down_{source}/btagSFbc']
    if source == 'statistic':
        name = f'CMS_btagSFbc_{source}_2024'
    else :
        name = f'CMS_btagSFbc_{source}'
    nuisances[f'btagSFbc_{source}'] = {
        'name': name,
        'skipCMS': 1,
        'kind': 'weight',
        'type': 'shape',
        'samples': dict((skey, btag_syst) for skey in mc),
    }

for corr in nuisance_sources['light']:
    btag_syst = [ f'btagSFlight_up_{corr}/btagSFlight', f'btagSFlight_down_{corr}/btagSFlight']
    name = (f'CMS_btagSFlight_{corr}' if corr == 'correlated' else f'CMS_btagSFlight_2024')
    nuisances[f'btagSFlight_{corr}'] = {
        'name': name,
        'skipCMS': 1,
        'kind': 'weight',
        'type': 'shape',
        'samples': dict((skey, btag_syst) for skey in mc),
    }
'''

##### Standard B-tagger

#for shift in ['jes', 'lf', 'hf', 'hfstats1', 'hfstats2', 'lfstats1', 'lfstats2', 'cferr1', 'cferr2']:
#    btag_syst = ['(btagSF%sup)/(btagSF)' % shift, '(btagSF%sdown)/(btagSF)' % shift]
#
#    name = 'CMS_btag_%s' % shift
#    if 'stats' in shift:
#        name += '_2024'
#
#    nuisances['btag_shape_%s' % shift] = {
#        'name': name,
#        'kind': 'weight',
#        'type': 'shape',
#        'samples': dict((skey, btag_syst) for skey in mc),
#    }

##### Trigger Scale Factors                                                                                                                                                                                

trig_syst = ['TriggerSFWeight_2l_u/TriggerSFWeight_2l', 'TriggerSFWeight_2l_d/TriggerSFWeight_2l']

nuisances['trigg'] = {
    'name': 'CMS_eff_hwwtrigger_2024',
    'kind': 'weight',
    'type': 'shape',
    'samples': dict((skey, trig_syst) for skey in mc)
}

##### Electron Efficiency 

nuisances['eff_e'] = {
    'name': 'CMS_eff_e_2024',
    'kind': 'weight',
    'type': 'shape',
    'samples': dict((skey, ['SFweightEleUp', 'SFweightEleDown']) for skey in mc), #TODO: IN THIS SAMPLES THERE'S AN ERROR AND SFUP AND SFDO ARE THE SAME, NEEDS TO BE FIXED
}

##### Muon Efficiency 

nuisances['eff_m'] = {
    'name': 'CMS_eff_m_2024',
    'kind': 'weight',
    'type': 'shape',
    'samples': dict((skey, ['SFweightMuUp', 'SFweightMuDown']) for skey in mc),
}


nuisances['PU'] = {
    'name'    : 'CMS_pileup_2024',
    'type'    : 'lnN',
    'samples' : dict((skey, '1.05') for skey in mc),
}

##### PS

nuisances['PS_ISR']  = {
    'name'    : 'ps_isr',
    'kind'    : 'weight',
    'type'    : 'shape',
    'samples' : dict((skey, ['PSWeight[2]', 'PSWeight[0]']) for skey in mc),
    'AsLnN'   : '0',
}

nuisances['PS_FSR']  = {
    'name'    : 'ps_fsr',
    'kind'    : 'weight',
    'type'    : 'shape',
    'samples' : dict((skey, ['PSWeight[3]', 'PSWeight[1]']) for skey in mc),
    'AsLnN'   : '0',
}

nuisances['UE_CP5']  = {
    'name'    : 'UEPS',
    'skipCMS' : 1,
    'type'    : 'lnN',
    'samples' : dict((skey, '1.015') for skey in mc),
}


## QCD scale uncertainties - RDataFrame syntax (no Alt())
## Works for samples with either 8 or 9 LHE scale weights
##
## LHEScaleWeight holds the per-event ratio to the nominal for the
## renormalisation and factorisation scales varied by a factor two. Index 0 is
## the (0.5, 0.5) variation and the last entry the (2, 2) one, in the 9-weight
## ordering (nominal kept, at index 4) as well as in the 8-weight one (nominal
## dropped) -- which is why the two ends are taken by position with the size
## read at run time. The guard leaves a sample with an empty vector at weight 1
## instead of reading past the end.

_lhe_up   = 'LHEScaleWeight_vec.size() > 0 ? LHEScaleWeight_vec[0] : 1.'
_lhe_down = 'LHEScaleWeight_vec.size() > 0 ? LHEScaleWeight_vec[LHEScaleWeight_vec.size()-1] : 1.'

## One nuisance per process: correlated across the samples that are the same
## process at the same order, independent between processes. Three of the
## groupings are a physics choice rather than bookkeeping, so they are spelt
## out here:
##
##   Vg         Wg/Zg and WgS/ZgS are one amcatnlo sample each, split by the
##              generator-level Z* mass window -- not two processes.
##   WZ_EWK     the EWK WZ and its interference with the QCD one come from the
##              same madgraph setup; the QCD WZ is powheg at another order in
##              alpha_s and keeps its own.
##   SSWW_EWK   the three polarised samples are the longitudinal decomposition
##              of WW_EWK out of one madgraph setup, so a scale variation moves
##              them together. Note this is a normalisation as much as a shape,
##              and on the signals that part is partly degenerate with mu_LX;
##              if the degeneracy bites, make it shape-only in the fit rather
##              than splitting the nuisance here.
_qcdscale = {
    'DY'       : ['DY'],
    'top'      : ['top'],
    'tVx'      : ['tVx'],
    'WZ'       : ['WZJJ_QCD', 'WZSJJ_QCD'],
    'WZ_EWK'   : ['WZJJ_EWK', 'WZSJJ_EWK', 'WZJJ_Int'],
    'Vg'       : ['Wg', 'Zg', 'WgS', 'ZgS'],
    'VVV'      : ['VVV'],
    'ggH'      : ['ggH_hww'],
    'qqH'      : ['qqH_hww'],
    'higgs'    : ['higgs'],
    'OSWW'     : ['OSWW'],
    'WW_QCD'   : ['WW_QCD'],
    'WW_Int'   : ['WW_Int'],
    'VBS_SSWW' : ['VBS_SSWW'],
    'SSWW_EWK' : ['WW_EWK', 'VBS_SSWW_WWCM_LL', 'VBS_SSWW_WWCM_TL',
                  'VBS_SSWW_WWCM_TT'],
}

## The check that stops this drifting away from samples.py again: every LHE
## sample gets exactly one scale nuisance, and nothing names a sample that does
## not exist. The previous version asked for 'WW', 'WZ' and 'WZS', none of them
## a key of samples.py, and left fourteen samples with no scale uncertainty at
## all -- silently, because a key matching no sample is simply never applied.
## Add a sample to samples.py and this now fails loudly until it has a group.
_covered = [s for _group in _qcdscale.values() for s in _group]
assert sorted(_covered) == sorted(lhesamples), (
    'QCDscale does not cover the LHE samples: missing %s, not a sample %s, '
    'repeated %s' % (sorted(set(lhesamples) - set(_covered)),
                     sorted(set(_covered) - set(lhesamples)),
                     sorted({s for s in _covered if _covered.count(s) > 1})))

for _proc, _skeys in _qcdscale.items():
    nuisances['QCDscale_' + _proc] = {
        'name'    : 'QCDscale_' + _proc,
        'kind'    : 'weight',
        'type'    : 'shape',
        'samples' : {s: [_lhe_up, _lhe_down] for s in _skeys},
    }

# ## PDF uncertainties - RDataFrame syntax (no Alt())
# for i in range(103):
#     _pdf_w = f'LHEPdfWeight_vec.size() > {i} ? LHEPdfWeight_vec[{i}] : 1.'
#     nuisances[f'pdf_ev{i}'] = {
#         'name'    : f'pdf_ev{i}',
#         'kind'    : 'weight',
#         'type'    : 'shape',
#         'samples' : {s: [_pdf_w, _pdf_w] for s in lhesamples}
#     }


nuisances['fake_syst'] = {
    'name': 'CMS_fake_syst',
    'type': 'lnN',
    'samples': {
        'Fake': '1.3'
    },
}

nuisances['fake_ele'] = {
    'name': 'CMS_fake_e_2024',
    'skipCMS' : 1,
    'kind': 'weight',
    'type': 'shape',
    'samples': {
        'Fake': ['fakeWEleUp', 'fakeWEleDown'],
    }
}

nuisances['fake_ele_stat'] = {
    'name': 'CMS_fake_stat_e_2024',
    'skipCMS' : 1,
    'kind': 'weight',
    'type': 'shape',
    'samples': {
        'Fake': ['fakeWStatEleUp', 'fakeWStatEleDown'],
    }
}

nuisances['fake_mu'] = {
    'name': 'CMS_fake_m_2024',
    'skipCMS' : 1,
    'kind': 'weight',
    'type': 'shape',
    'samples': {
        'Fake': ['fakeWMuUp', 'fakeWMuDown'],
    }
}

nuisances['fake_mu_stat'] = {
    'name': 'CMS_fake_stat_m_2024',
    'skipCMS' : 1,
    'kind': 'weight',
    'type': 'shape',
    'samples': {
        'Fake': ['fakeWStatMuUp', 'fakeWStatMuDown'],
    }
}

autoStats = True
if autoStats:
    ## Use the following if you want to apply the automatic combine MC stat nuisances.
    nuisances['stat'] = {
        'type': 'auto',
        'maxPoiss': '10',
        'includeSignal': '0',
        #  nuisance ['maxPoiss'] =  Number of threshold events for Poisson modelling
        #  nuisance ['includeSignal'] =  Include MC stat nuisances on signal processes (1=True, 0=False)
        'samples': {}
    }

# nuisances['DYttnorm2j']  = {
#                'name'  : 'CMS_hww_DYttnorm2j',
#                'skipCMS' : 1,
#                'samples'  : {
#                    'DY' : '1.00',
#                    },
#                'type'  : 'rateParam',
#                'cuts'  : cuts2j
#               }
# '''
# nuisances['WWnorm2j']  = {
#                'name'  : 'CMS_hww_WWnorm2j',
#                'skipCMS' : 1,
#                'samples'  : {
#                    'WWjj_QCD' : '1.00',
#                    },
#                'type'  : 'rateParam',
#                'cuts'  : cuts2j
#               }
# '''
# nuisances['ggWWnorm2j']  = {
#                'name'  : 'CMS_hww_WWnorm2j',
#                'skipCMS' : 1,
#                'samples'  : {
#                    'ggWW' : '1.00',
#                    },
#                'type'  : 'rateParam',
#                'cuts'  : cuts2j
#               }

# nuisances['Topnorm2j']  = {
#                'name'  : 'CMS_hww_Topnorm2j',
#                'skipCMS' : 1,
#                'samples'  : {
#                    'top' : '1.00',
#                    },
#                'type'  : 'rateParam',
#                'cuts'  : cuts2j
#               }


# nuisances['QCDscale_CRSR_accept_dytt']  = {
#                'name'  : 'QCDscale_CRSR_accept_dytt',
#                'type'  : 'lnN',
#                'samples'  : {
#                    'DY' : '1.02',
#                    },
#                'cuts'  : [
#                  'hww2l2v_13TeV_dytt_of0j',
#                  'hww2l2v_13TeV_dytt_of1j',
#                  'hww2l2v_13TeV_dytt_of2j',
#                  'hww2l2v_13TeV_dytt_of2j_vbf',
#                  'hww2l2v_13TeV_dytt_of2j_vh2j'
#                 ]
#               }



# # nuisances['electronpt'] = {
# #     'name': 'scale_e_2017_UL',
# #     'kind': 'suffix',
# #     'type': 'shape',
# #     'mapUp': 'ElepTup',
# #     'mapDown': 'ElepTdo',
# #     'samples': dict((skey, ['1', '1']) for skey in mcALL),
# #     'folderUp': makeMCDirectory('ElepTup_suffix'),
# #     'folderDown': makeMCDirectory('ElepTdo_suffix'),
# # }



# ##### Lepton scale
# nuisances['lepscale'] = {
#     'name': 'lepscale_2023BPix',
#     'kind': 'suffix',
#     'type': 'shape',
#     'mapUp': 'leptonScaleup',
#     'mapDown': 'leptonScaledo',
#     'samples': dict((skey, ['1', '1']) for skey in mcALL),
#     'folderUp': makeMCDirectory('leptonScaleup_suffix'),
#     'folderDown': makeMCDirectory('leptonScaledo_suffix'),
#     'AsLnN': '0'
# }




# # # ------------------- muon efficiency and energy scale
# # nuisances['eff_m'] = {
# #     'name': 'eff_m_2024',
# #     'kind': 'weight',
# #     'type': 'shape',
# #     #                        nominal          up               down
# #     'samples': dict((skey, ['SFweightMu','SFweightMuUp', 'SFweightMuDown']) for skey in mcALL)
# # }