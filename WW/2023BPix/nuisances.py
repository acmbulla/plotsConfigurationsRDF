


def makeMCDirectory(var=""):
    treeBaseDir = '/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano'
    mcProduction = 'Summer23BPix_130x_nAODv12_Full2023BPixv12'
    mcSteps      = 'MCl2loose2023BPixv12__MCCorr2023BPixv12JetScaling__l2tight'
    _treeBaseDir = treeBaseDir + ""
    if var == "":
        return "/".join([_treeBaseDir, mcProduction, mcSteps])
    else:
        return "/".join([_treeBaseDir, mcProduction, mcSteps + "__" + var])




nuisances['lumi_2023BPix'] = {
    'name'    : 'lumi_2023BPix',
    'type'    : 'lnN',
    'samples' : dict((skey, '1.013') for skey in mcALL)
}




nuisances['QCDscale_CRSR_accept_dytt']  = {
               'name'  : 'QCDscale_CRSR_accept_dytt',
               'type'  : 'lnN',
               'samples'  : {
                   'DY' : '1.02',
                   },
               'cuts'  : [
                 'hww2l2v_13TeV_dytt_of0j',
                 'hww2l2v_13TeV_dytt_of1j',
                 'hww2l2v_13TeV_dytt_of2j',
                 'hww2l2v_13TeV_dytt_of2j_vbf',
                 'hww2l2v_13TeV_dytt_of2j_vh2j'
                ]
              }



# nuisances['electronpt'] = {
#     'name': 'scale_e_2017_UL',
#     'kind': 'suffix',
#     'type': 'shape',
#     'mapUp': 'ElepTup',
#     'mapDown': 'ElepTdo',
#     'samples': dict((skey, ['1', '1']) for skey in mcALL),
#     'folderUp': makeMCDirectory('ElepTup_suffix'),
#     'folderDown': makeMCDirectory('ElepTdo_suffix'),
# }



##### Lepton scale
nuisances['lepscale'] = {
    'name': 'lepscale_2023BPix',
    'kind': 'suffix',
    'type': 'shape',
    'mapUp': 'leptonScaleup',
    'mapDown': 'leptonScaledo',
    'samples': dict((skey, ['1', '1']) for skey in mcALL),
    'folderUp': makeMCDirectory('leptonScaleup_suffix'),
    'folderDown': makeMCDirectory('leptonScaledo_suffix'),
    'AsLnN': '0'
}




# ------------------- muon efficiency and energy scale
nuisances['eff_m'] = {
    'name': 'eff_m_2023',
    'kind': 'weight',
    'type': 'shape',
    #                        nominal          up               down
    'samples': dict((skey, ['SFweightMu','SFweightMuUp', 'SFweightMuDown']) for skey in mcALL)
}












