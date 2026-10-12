


def makeMCDirectory(var=""):
    treeBaseDir = '/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano'
    mcProduction = 'Summer20UL18_106x_nAODv9_Full2018v9'
    mcSteps = 'MCl1loose2018v9__MCCorr2018v9NoJERInHorn__l2tightOR2018v9'
    _treeBaseDir = treeBaseDir + ""
    if var == "":
        return "/".join([_treeBaseDir, mcProduction, mcSteps])
    else:
        return "/".join([_treeBaseDir, mcProduction, mcSteps + "__" + var])


# mcALL     = [skey for skey in samples if skey not in ('DATA', 'Fake_lep')]








nuisances['lumi_Uncorrelated'] = {
    'name': 'lumi_13TeV_2018',
    'type': 'lnN',
    'samples': dict((skey, '1.015') for skey in mcALL if skey not in ['top', 'dytt'])
}

nuisances['lumi_correlated'] = {
    'name': 'lumi_13TeV_correlated',
    'type': 'lnN',
    'samples': dict((skey, '1.009') for skey in mcALL if skey not in ['top', 'dytt'])
}

nuisances['lumi_correlated_1718'] = {
    'name': 'lumi_13TeV_correlated_1718',
    'type': 'lnN',
    'samples': dict((skey, '1.006') for skey in mcALL if skey not in ['top', 'dytt'])
}



# nuisances['fake_syst_e'] = {
#     'name': 'CMS_fake_syst_e',
#     'skipCMS' : 1,
#     'type': 'lnN',
#     'samples': {
#         'Fake_e': '1.3'
#     },
# }
#
# nuisances['fake_syst_m'] = {
#     'name': 'CMS_fake_syst_m',
#     'skipCMS' : 1,
#     'type': 'lnN',
#     'samples': {
#         'Fake_m': '1.3'
#     },
# }
#
# nuisances['fake_ele'] = {
#     'name': 'CMS_fake_e_2018',
#     'skipCMS' : 1,
#     'kind': 'weight',
#     'type': 'shape',
#     'samples': {
#         'Fake_e': ['fakeWEleUp', 'fakeWEleDown'],
#         'Fake_m': ['fakeWEleUp', 'fakeWEleDown'],
#     }
# }
#
#
# nuisances['fake_ele_stat'] = {
#     'name': 'CMS_fake_stat_e_2018',
#     'skipCMS' : 1,
#     'kind': 'weight',
#     'type': 'shape',
#     'samples': {
#         'Fake_e': ['fakeWStatEleUp', 'fakeWStatEleDown'],
#         'Fake_m': ['fakeWStatEleUp', 'fakeWStatEleDown']
#     }
# }
#
# nuisances['fake_mu'] = {
#     'name': 'CMS_fake_m_2018',
#     'skipCMS' : 1,
#     'kind': 'weight',
#     'type': 'shape',
#     'samples': {
#         'Fake_e': ['fakeWMuUp', 'fakeWMuDown'],
#         'Fake_m': ['fakeWMuUp', 'fakeWMuDown']
#     }
# }
#
# nuisances['fake_mu_stat'] = {
#     'name': 'CMS_fake_stat_m_2018',
#     'skipCMS' : 1,
#     'kind': 'weight',
#     'type': 'shape',
#     'samples': {
#         'Fake_e': ['fakeWStatMuUp', 'fakeWStatMuDown'],
#         'Fake_m': ['fakeWStatMuUp', 'fakeWStatMuDown']
#     }
# }







### B-tagger
# Fixed BTV SF variations
# for flavour in ['bc', 'light']:
#     for corr in ['uncorrelated', 'correlated']:
#         btag_syst = [f'btagSF{flavour}_up_{corr}/btagSF{flavour}', f'btagSF{flavour}_down_{corr}/btagSF{flavour}']
#         if corr == 'correlated':
#             name = f'CMS_btagSF{flavour}_{corr}'
#         else:
#             name = f'CMS_btagSF{flavour}_2018'
#         nuisances[f'btagSF{flavour}{corr}'] = {
#             'name': name,
#             'skipCMS' : 1,
#             'kind': 'weight',
#             'type': 'shape',
#             'samples': dict((skey, btag_syst) for skey in mcALL),
#         }
#



##### Trigger Efficiency

trig_syst = ['TriggerSFWeight_2l_u/TriggerSFWeight_2l', 'TriggerSFWeight_2l_d/TriggerSFWeight_2l']

nuisances['trigg'] = {
    'name': 'CMS_eff_hwwtrigger_2018',
    'skipCMS' : 1,
    'kind': 'weight',
    'type': 'shape',
    'samples': dict((skey, trig_syst) for skey in mcALL)
}




##### Electron Efficiency and energy scale

nuisances['eff_e'] = {
    'name': 'CMS_eff_e_2018',
    'skipCMS' : 1,
    'kind': 'weight',
    'type': 'shape',
    'samples': dict((skey, ['SFweightEleUp', 'SFweightEleDown']) for skey in mcALL)
}

# nuisances['electronpt'] = {
#     'name': 'CMS_scale_e_2018',
#     'skipCMS' : 1,
#     'kind': 'suffix',
#     'type': 'shape',
#     'mapUp': 'ElepTup',
#     'mapDown': 'ElepTdo',
#     'samples': dict((skey, ['1', '1']) for skey in mcALL),
#     'folderUp': makeMCDirectory('ElepTup_suffix'),
#     'folderDown': makeMCDirectory('ElepTdo_suffix'),
#     'AsLnN': '0'
# }

##### Muon Efficiency and energy scale

nuisances['eff_m'] = {
    'name': 'CMS_eff_m_2018',
    'skipCMS' : 1,
    'kind': 'weight',
    'type': 'shape',
    'samples': dict((skey, ['SFweightMuUp', 'SFweightMuDown']) for skey in mcALL)
}

# nuisances['muonpt'] = {
#     'name': 'CMS_scale_m_2018',
#     'skipCMS' : 1,
#     'kind': 'suffix',
#     'type': 'shape',
#     'mapUp': 'MupTup',
#     'mapDown': 'MupTdo',
#     'samples': dict((skey, ['1', '1']) for skey in mcALL),
#     'folderUp': makeMCDirectory('MupTup_suffix'),
#     'folderDown': makeMCDirectory('MupTdo_suffix'),
#     'AsLnN': '0'
# }


### PU ID SF uncertainty
puid_syst = ['Jet_PUIDSF_up/Jet_PUIDSF', 'Jet_PUIDSF_down/Jet_PUIDSF']

nuisances['jetPUID'] = {
    'name': 'CMS_PUID_2018',
    'skipCMS' : 1,
    'kind': 'weight',
    'type': 'shape',
    'samples': dict((skey, puid_syst) for skey in mcALL)
}


##### Jet energy scale
# jes_systs = ['JESAbsolute','JESAbsolute_2018','JESBBEC1','JESBBEC1_2018','JESEC2','JESEC2_2018','JESFlavorQCD','JESHF','JESHF_2018','JESRelativeBal','JESRelativeSample_2018']
#
# for jes in jes_systs:
#     # Split source, applied to jets and MET
#     nuisances[jes] = {
#         'name': 'CMS_scale_'+jes,
#         'skipCMS' : 1,
#         'kind': 'suffix',
#         'type': 'shape',
#         'mapUp': jes+'up',
#         'mapDown': jes+'do',
#         'samples': dict((skey, ['1', '1']) for skey in mcALL),
#         'folderUp': makeMCDirectory('RDF__JESup_suffix'),
#         'folderDown': makeMCDirectory('RDF__JESdo_suffix'),
#         'AsLnN': '0'
#     }



#
# If a nuisance has no effect in a given phase space/sample, then the histogram is NOT filled
# FIXME: how should I handle this?
#
#
#
##### MET energy scale
# nuisances['met'] = {
#     'name': 'CMS_scale_met_2018',
#     'skipCMS' : 1,
#     'kind': 'suffix',
#     'type': 'shape',
#     'mapUp': 'METup',
#     'mapDown': 'METdo',
#     'samples': dict((skey, ['1', '1']) for skey in mcALL),
#     'folderUp': makeMCDirectory('METup_suffix'),
#     'folderDown': makeMCDirectory('METdo_suffix'),
#     'AsLnN': '0'
# }

##### Jet energy resolution
nuisances['JER'] = {
    'name': 'CMS_res_j_2018',
    'skipCMS' : 1,
    'kind': 'suffix',
    'type': 'shape',
    'mapUp': 'JERup',
    'mapDown': 'JERdo',
    'samples': dict((skey, ['1', '1']) for skey in mcALL),
    'folderUp': makeMCDirectory('JERup_suffix'),
    'folderDown': makeMCDirectory('JERdo_suffix'),
    'AsLnN': '0'
}



#
# New JER implementation on the fly!
#
#
# nuisances['myJER'] = {
#     'name': 'CMS_res_j_2018_fly',
#     'skipCMS' : 1,
#     'kind': 'suffixFly',
#     'type': 'shape',
#     'external' : "code/jer_on_the_fly.c",
#     'code_in_main' : "code/jer_on_the_fly_main.c",
#     'pattern' : 'CMS_my_res_j_XXXX',
#     'numVariations' : 3,
#     'samples': dict((skey, ['1', '1']) for skey in mcALL),
#     'AsLnN': '0'
# }

# /cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/2018_UL/jet_jerc.json.gz





##### Pileup

nuisances['PU'] = {
    'name': 'CMS_PU_2018',
    'skipCMS' : 1,
    'kind': 'weight',
    'type': 'shape',
    'samples': {
        'top'               : ['puWeightUp/puWeight',   'puWeightDown/puWeight'],
        'dytt'              : ['puWeightUp/puWeight',   'puWeightDown/puWeight'],
        'WWjj_QCD'          : ['puWeightUp/puWeight',   'puWeightDown/puWeight'],
        'ggWW'              : ['puWeightUp/puWeight',   'puWeightDown/puWeight'],
        'WWewk_CMWWW_LL'    : ['puWeightUp/puWeight',   'puWeightDown/puWeight'],
        'WWewk_CMWWW_LT'    : ['puWeightUp/puWeight',   'puWeightDown/puWeight'],
        'WWewk_CMWWW_TL'    : ['puWeightUp/puWeight',   'puWeightDown/puWeight'],
        'WWewk_CMWWW_TT'    : ['puWeightUp/puWeight',   'puWeightDown/puWeight'],
        'WWewk_LL'          : ['puWeightUp/puWeight',   'puWeightDown/puWeight'],
        'WWewk_LT'          : ['puWeightUp/puWeight',   'puWeightDown/puWeight'],
        'WWewk_TL'          : ['puWeightUp/puWeight',   'puWeightDown/puWeight'],
        'WWewk_TT'          : ['puWeightUp/puWeight',   'puWeightDown/puWeight'],
    },
    'AsLnN': '0',
}




# ##### PS fixed
# samples_dict = dict((skey, ['PSWeight[2]', 'PSWeight[0]']) for skey in mcALL if 'WWewk' not in skey)
# samples_dict.update(dict((skey, ['PSWeight[2]*NormTHU_' + skey + '_PS_ISR_Up', 'PSWeight[0]*NormTHU_' + skey + '_PS_ISR_Do']) for skey in mcALL if skey in ['WWewk_CMWW_LL', 'WWewk_CMWW_LT', 'WWewk_CMWW_TL', 'WWewk_CMWW_TT', 'WWewk_LL', 'WWewk_LT', 'WWewk_TL', 'WWewk_TT']))
# nuisances['PS_ISR']  = {
#     'name'    : 'ps_isr',
#     'kind'    : 'weight',
#     'type'    : 'shape',
#     'samples' : samples_dict,
#     'AsLnN'   : '0',
# }
#
# samples_dict = dict((skey, ['PSWeight[3]', 'PSWeight[1]']) for skey in mcALL if 'WWewk' not in skey)
# samples_dict.update(dict((skey, ['PSWeight[3]*NormTHU_' + skey + '_PS_FSR_Up', 'PSWeight[1]*NormTHU_' + skey + '_PS_FSR_Do']) for skey in mcALL if skey in ['WWewk_CMWW_LL', 'WWewk_CMWW_LT', 'WWewk_CMWW_TL', 'WWewk_CMWW_TT', 'WWewk_LL', 'WWewk_LT', 'WWewk_TL', 'WWewk_TT']))
# nuisances['PS_FSR']  = {
#     'name'    : 'ps_fsr',
#     'kind'    : 'weight',
#     'type'    : 'shape',
#     'samples' : samples_dict,
#     'AsLnN'   : '0',
# }



##### Renormalization & factorization scales

## Shape nuisance due to QCD scale variations
# LHE scale variation weights (w_var / w_nominal)

## This should work for samples with either 8 or 9 LHE scale weights (nLHEScaleWeight == 8 or 9)
# variations = ['LHEScaleWeight[0]',
#               'LHEScaleWeight[1]',
#               'LHEScaleWeight[3]',
#               'LHEScaleWeight[nLHEScaleWeight - 4]',
#               'LHEScaleWeight[nLHEScaleWeight - 2]',
#               'LHEScaleWeight[nLHEScaleWeight - 1]']




# nuisances['QCDscale_top_2j']  = {
#     'name'  : 'QCDscale_top_2j',
#     'kind'  : 'weight_envelope',
#     'type'  : 'shape',
#     'samples'  : {
#        'top' : variations,
#     }
# }
#
# nuisances['QCDscale_WW_2j']  = {
#     'name'  : 'QCDscale_WW_2j',
#     'kind'  : 'weight_envelope',
#     'type'  : 'shape',
#     'samples'  : {
#        'WWjj_QCD' : variations,
#     }
# }
#
# nuisances['QCDscale_V'] = {
#     'name': 'QCDscale_V',
#     'skipCMS': 1,
#     'kind': 'weight_envelope',
#     'type': 'shape',
#     'samples': {
#        'dytt' : variations,
#     },
# }



nuisances['QCDscale_ggVV'] = {
    'name': 'QCDscale_ggVV',
    'type': 'lnN',
    'samples': {
        'ggWW': '1.15',
    },
}



## Use the following if you want to apply the automatic combine MC stat nuisances.
nuisances['stat'] = {
    'type': 'auto',
    'maxPoiss': '10',
    'includeSignal': '0',
    #  nuisance ['maxPoiss'] =  Number of threshold events for Poisson modelling
    #  nuisance ['includeSignal'] =  Include MC stat nuisances on signal processes (1=True, 0=False)
    'samples': {}
}



nuisances['DYttnorm2j']  = {
               'name'  : 'CMS_hww_DYttnorm2j',
               'skipCMS' : 1,
               'samples'  : {
                   'dytt' : '1.00',
                   },
               'type'  : 'rateParam',
               # 'cuts'  : cuts2j
}

nuisances['WWnorm2j']  = {
               'name'  : 'CMS_hww_WWnorm2j',
               'skipCMS' : 1,
               'samples'  : {
                   'WWjj_QCD' : '1.00',
                   },
               'type'  : 'rateParam',
               # 'cuts'  : cuts2j
}

nuisances['ggWWnorm2j']  = {
               'name'  : 'CMS_hww_WWnorm2j',
               'skipCMS' : 1,
               'samples'  : {
                   'ggWW' : '1.00',
                   },
               'type'  : 'rateParam',
               # 'cuts'  : cuts2j
}

nuisances['Topnorm2j']  = {
               'name'  : 'CMS_hww_Topnorm2j',
               'skipCMS' : 1,
               'samples'  : {
                   'top' : '1.00',
                   },
               'type'  : 'rateParam',
               # 'cuts'  : cuts2j
}




















#
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


#
# nuisances['electronpt'] = {
#     'name': 'scale_e_2018_UL',
#     'kind': 'suffix',
#     'type': 'shape',
#     'mapUp': 'ElepTup',
#     'mapDown': 'ElepTdo',
#     'samples': dict((skey, ['1', '1']) for skey in mcALL),
#     'folderUp': makeMCDirectory('ElepTup_suffix'),
#     'folderDown': makeMCDirectory('ElepTdo_suffix'),
# }


#
# # ------------------- muon efficiency and energy scale
# nuisances['eff_m'] = {
#     'name': 'eff_m_2018',
#     'kind': 'weight',
#     'type': 'shape',
#     #                        nominal          up                     down
#     'samples': dict((skey, ['LepWPSF',   'LepWPSF*SFweightMuUp', 'LepWPSF*SFweightMuDown']) for skey in mcALL)
# }
#
#
#
#


# nuisances['eff_m'] = {
#     'name': 'eff_m_2018_UL',
#     'kind': 'weight',
#     'type': 'shape',
#     #                        nominal          up               down
#     'samples': dict((skey, ['SFweightMu','SFweightMuUp', 'SFweightMuDown']) for skey in mcALL)
# }


# aliases['SFweightMuUp'] = {
#     'expr': 'LepSF3l__mu_'+muWP+'__Up',
#     'samples': mcALL
# }
# aliases['SFweightMuDown'] = {
#     'expr': 'LepSF3l__mu_'+muWP+'__Do',
#     'samples': mcALL
# }












