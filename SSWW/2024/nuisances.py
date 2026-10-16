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
# Samples carrying LHE weights. MUST stay identical to the list in aliases.py,
# which is what decides whether LHEScaleWeight_vec / LHEPdfWeight_vec are
# Define()d at all: a nuisance naming a sample that has no *_vec alias kills
# the job. ggWW is mcfm, ZZ is partly gg->ZZ (mcfm) and WW_DPS is pure pythia8,
# so none of the three has LHEScaleWeight / LHEPdfWeight branches.
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

############################### EXPERIMENTAL UNCERTAINTIES  #################################

# https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun3
# 2022: 34.75 fb-1  (+-1.4%)
# 2023: 28.40 fb-1  (+-1.3%)
# 2024: 110.11 fb-1 (+-1.6%)
# 2025: 125.07 fb-1 (+-5%)   -- preliminary
# 2026: no uncertainty available yet
#
# NB: these five lines were NOT commented out, so nuisances.py did not even
# parse ("invalid character '⁻'") and every mkShapes/mkDatacards run that
# loads this file died on the exec(). Keep them behind a '#'.
#
# The 1.6% total for 2024 is split into the three Run-3 correlation pieces
# below (uncorrelated / partially-correlated / fully-correlated), which add in
# quadrature to it: sqrt(0.20^2 + 0.68^2 + 1.44^2) = 1.6%.


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


nuisances['JER'] = {
    'name': 'CMS_res_j_2024',
    'skipCMS' : 1,
    'kind': 'suffix',
    'type': 'shape',
    'mapUp': 'jerup',
    'mapDown': 'jerdo',
    #'separator': '__',
    'samples': dict((skey, ['1', '1']) for skey in mc),
    'folderUp': makeMCDirectory('jerup_suffix'),
    'folderDown': makeMCDirectory('jerdo_suffix'),
    'AsLnN': '0'
}


jes_sources = ['Absolute_2024','Absolute','BBEC1_2024','BBEC1','EC2_2024','EC2','FlavorQCD','HF_2024','HF','RelativeBal','RelativeSample_2024']
jes_sources = ["jesRegroed_"+ _ for _ in jes_sources] 
for js in jes_sources:
    nuisances[js] = {
        'name': f'CMS_scale_{js}',
        'skipCMS' : 1,
        'kind': 'suffix',
        'type': 'shape',
        'mapUp': f'{js}up',
        'mapDown': f'{js}do',
        #'separator': '__',
        'samples': dict((skey, ['1', '1']) for skey in mc),
        'folderUp': makeMCDirectory(f'{js}up_suffix'),
        'folderDown': makeMCDirectory(f'{js}do_suffix'),
        'AsLnN': '0'
    }

# #BUGGED FIXME TODO
nuisances['MET'] = {
    'name': 'CMS_scale_met_2024',
    'skipCMS' : 1,
    'kind': 'suffix',
    'type': 'shape',
    'mapUp': 'unclustEnup',
    'mapDown': 'unclustEndo',
    #'separator': '__',
    'samples': dict((skey, ['1', '1']) for skey in mc),
    'folderUp': makeMCDirectory('unclustEnup_suffix'),
    'folderDown': makeMCDirectory('unclustEndo_suffix'),
    'AsLnN': '0'
}


##### Lepton scale
nuisances['lepscale'] = {
    'name': 'CMS_lepscale_2024',
    'skipCMS' : 1,
    'kind': 'suffix',
    'type': 'shape',
    'mapUp': 'leptonScaleup',
    'mapDown': 'leptonScaledo',
    #'separator': '__',
    'samples': dict((skey, ['1', '1']) for skey in mc),
    'folderUp': makeMCDirectory('leptonScaleup_suffix'),
    'folderDown': makeMCDirectory('leptonScaledo_suffix'),
    'AsLnN': '0'
}

##### Lepton resolution
nuisances['lepres'] = {
    'name': 'CMS_lepres_2024',
    'skipCMS' : 1,
    'kind': 'suffix',
    'type': 'shape',
    'mapUp': 'leptonResolutionup',
    'mapDown': 'leptonResolutiondo',
    #'separator': '__',
    'samples': dict((skey, ['1', '1']) for skey in mc),
    'folderUp': makeMCDirectory('leptonResolutionup_suffix'),
    'folderDown': makeMCDirectory('leptonResolutiondo_suffix'),
    'AsLnN': '0'
}

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
#
# PSWeight is indexed as [0] isr_dn, [1] fsr_dn, [2] isr_up, [3] fsr_up in the
# 4-weight convention. Samples generated without PS weights carry a PSWeight of
# size 1 (a single 1.0), and an out-of-range RVec access throws at event level,
# killing the job -- so every index is size-guarded, exactly like the LHE scale
# weights below. A sample with no PS weights then simply gets a nuisance equal
# to the nominal, instead of crashing.
_ps = lambda i: f'(PSWeight.size() > {i} ? PSWeight[{i}] : 1.)'

nuisances['PS_ISR']  = {
    'name'    : 'ps_isr',
    'kind'    : 'weight',
    'type'    : 'shape',
    'samples' : dict((skey, [_ps(2), _ps(0)]) for skey in mc),
    'AsLnN'   : '0',
}

nuisances['PS_FSR']  = {
    'name'    : 'ps_fsr',
    'kind'    : 'weight',
    'type'    : 'shape',
    'samples' : dict((skey, [_ps(3), _ps(1)]) for skey in mc),
    'AsLnN'   : '0',
}

nuisances['UE_CP5']  = {
    'name'    : 'UEPS',
    'skipCMS' : 1,
    'type'    : 'lnN',
    'samples' : dict((skey, '1.015') for skey in mc),
}


# -----------------------------------------------------------------------------
# QCD scale uncertainties
#
# RDataFrame syntax: no Alt(), and the index is guarded because the number of
# LHE scale weights is 8 in some productions and 9 in others. [0] and
# [size-1] are the two extremes of the correlated muR/muF variation in both
# conventions, so the pair below is the same physical variation either way.
#
# One nuisance per physical process, grouped the way plot.py groups the
# samples, so no stacked process ends up carrying two uncorrelated scale
# parameters. Everything that is in `lhesamples` must appear exactly once in
# _qcdScaleGroups -- the check right after the loop enforces it, so adding a
# sample to samples.py without giving it a scale nuisance fails loudly here
# instead of silently producing a datacard with a missing uncertainty.
#
# ggWW, ZZ and WW_DPS are absent on purpose: no LHE weights (mcfm / pure
# pythia8), hence they are not in `lhesamples` and the *_vec aliases are never
# defined for them. Their scale uncertainty has to be a lnN, not a shape.
# -----------------------------------------------------------------------------

# The outer parentheses are NOT cosmetic: mkShapes builds the varied weight as
#     (my_sample_weight) * <entry>
# with no brackets around <entry> (mkShapes._build_cpp_variations_weights), so a
# bare ternary would parse as ((w * vec.size()) > 0) ? vec[0] : 1. and drop the
# event weight entirely. Any entry that is not a plain product or ratio has to
# bracket itself.
_lhe_up   = '(LHEScaleWeight_vec.size() > 0 ? LHEScaleWeight_vec[0] : 1.)'
_lhe_down = '(LHEScaleWeight_vec.size() > 0 ? LHEScaleWeight_vec[LHEScaleWeight_vec.size()-1] : 1.)'

_qcdScaleGroups = {
    # --- signal: same-sign WW
    # WW_EWK and the three polarisation samples are the same process (the
    # polarised ones are its decomposition), so one correlated parameter.
    # the inclusive VBS_SSWW is commented out in samples.py (it double counts
    # WW_EWK + WW_QCD + WW_Int); add it back here if it is ever re-enabled.
    'QCDscale_VBS_SSWW' : ['WW_EWK',
                           'VBS_SSWW_WWCM_LL', 'VBS_SSWW_WWCM_TL', 'VBS_SSWW_WWCM_TT'],
    'QCDscale_SSWW_QCD' : ['WW_QCD', 'WW_Int'],

    # --- WZ, split EWK / QCD exactly as groupPlot does in plot.py
    'QCDscale_WZ_EWK'   : ['WZJJ_EWK', 'WZSJJ_EWK'],
    'QCDscale_WZ'       : ['WZJJ_QCD', 'WZSJJ_QCD', 'WZJJ_Int'],

    # --- top
    'QCDscale_ttbar'    : ['top'],
    'QCDscale_tVx'      : ['tVx'],

    # --- wrong-sign / charge-mismeasurement sources (groupPlot 'Wrong sign')
    'QCDscale_DY'       : ['DY'],
    'QCDscale_OSWW'     : ['OSWW'],

    # --- remaining diboson / triboson (groupPlot 'VV(V)')
    # name kept as QCDscale_VV so the datacards do not change parameter name
    'QCDscale_VV'       : ['Wg', 'Zg', 'WgS', 'ZgS'],
    'QCDscale_VVV'      : ['VVV'],

    # --- Higgs
    'QCDscale_ggH'      : ['ggH_hww'],
    'QCDscale_qqH'      : ['qqH_hww'],
    'QCDscale_higgs'    : ['higgs'],
}

for _nuis, _slist in _qcdScaleGroups.items():
    nuisances[_nuis] = {
        'name'    : _nuis,
        'kind'    : 'weight',
        'type'    : 'shape',
        'samples' : {s: [_lhe_up, _lhe_down] for s in _slist}
    }

# coherence check: every LHE sample covered once, and no group naming a sample
# that samples.py does not define.
_qcdScaleFlat    = [s for _l in _qcdScaleGroups.values() for s in _l]
_qcdScaleUnknown = sorted(set(_qcdScaleFlat) - set(samples))
_qcdScaleDup     = sorted(s for s in set(_qcdScaleFlat) if _qcdScaleFlat.count(s) > 1)
_qcdScaleMissing = sorted(set(lhesamples) - set(_qcdScaleFlat))
if _qcdScaleUnknown or _qcdScaleDup or _qcdScaleMissing:
    raise ValueError(
        'QCD scale nuisances out of sync with samples.py:'
        + (f' unknown samples {_qcdScaleUnknown};' if _qcdScaleUnknown else '')
        + (f' sample in two groups {_qcdScaleDup};' if _qcdScaleDup else '')
        + (f' LHE samples with no scale nuisance {_qcdScaleMissing};' if _qcdScaleMissing else '')
    )

# ggWW and ZZ had a shape nuisance here before, but neither carries LHE
# weights, so it could never have worked. Left as a reminder that they still
# need a lnN:
# nuisances['QCDscale_ggWW'] = {'name': 'QCDscale_ggWW', 'type': 'lnN',
#                               'samples': {'ggWW': '1.15'}}
# nuisances['QCDscale_ZZ']   = {'name': 'QCDscale_ZZ',   'type': 'lnN',
#                               'samples': {'ZZ': '1.10'}}
# nuisances['QCDscale_WW_DPS'] = {'name': 'QCDscale_WW_DPS', 'type': 'lnN',
#                                 'samples': {'WW_DPS': '1.50'}}
#
# And QCDscale_WW / QCDscale_WZ(S) used to name samples 'WW', 'WZ' and 'WZS',
# none of which exist in samples.py -- mkDatacards would have written no
# uncertainty at all for the processes they were meant to cover. Replaced by
# QCDscale_SSWW_QCD / QCDscale_VBS_SSWW and the WZ groups above.

# -----------------------------------------------------------------------------
# PDF uncertainties - RDataFrame syntax (no Alt())
#
# 103 = 1 nominal + 100 Hessian eigenvectors + 2 alpha_s members (NNPDF4.0
# hessian). Up and Down are the same expression on purpose: a Hessian member is
# already a +1 sigma displacement in one eigendirection, so the nuisance is
# symmetrised by combine rather than built from two members.
#
# Cost warning: 103 nuisances x len(lhesamples) samples x every cut x every
# variable. With the flavour categories added in cuts.py this is the dominant
# term in both the job time and the output file size. If a run is only about
# shapes and not about the final fit, comment this loop out.
#
# Restricted to `lhesamples` for the same reason as the scale weights above:
# ggWW / ZZ / WW_DPS have no LHEPdfWeight branch and no *_vec alias. The
# pdf_ev0 member is the nominal, so that one nuisance is a no-op by
# construction; it is kept so the member indices match the PDF set.
# -----------------------------------------------------------------------------
for i in range(103):
    _pdf_w = f'(LHEPdfWeight_vec.size() > {i} ? LHEPdfWeight_vec[{i}] : 1.)'
    nuisances[f'pdf_ev{i}'] = {
        'name'    : f'pdf_ev{i}',
        'kind'    : 'weight',
        'type'    : 'shape',
        'samples' : {s: [_pdf_w, _pdf_w] for s in lhesamples}
    }


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