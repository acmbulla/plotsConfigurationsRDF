


nuisances['lumi_2023'] = {
    'name': 'lumi_2023',
    'type': 'lnN',
    'samples': dict((skey, '1.015') for skey in mcALL if skey not in ['tVx'])
}



nuisances['lumi_2025'] = {
    'name'    : 'lumi_2025',
    'type'    : 'shape',
    'samples' : dict((skey, '1.013') for skey in mcALL)
}



nuisances['lumi_2024'] = {
    'name'    : 'lumi_2024',
    'type'    : 'shape',
    'samples' : dict((skey, '1.013') for skey in mcALL)
}





# nuisances['electronpt'] = {
#     'name': 'scale_e_2018_UL',
#     'kind': 'suffix',
#     'type': 'shape',
#     'mapUp': 'ElepTup',
#     'mapDown': 'ElepTdo',
#     'samples': dict((skey, ['1', '1']) for skey in mcALL),
# }


##### Lepton scale
nuisances['lepscale_2022'] = {
    'name': 'lepscale_2022',
    'kind': 'suffix',
    'type': 'shape',
    'mapUp': 'leptonScaleup',
    'mapDown': 'leptonScaledo',
    'samples': dict((skey, ['1', '1']) for skey in mcALL),
    'AsLnN': '0'
}

nuisances['lepscale_2022EE'] = {
    'name': 'lepscale_2022EE',
    'kind': 'suffix',
    'type': 'shape',
    'mapUp': 'leptonScaleup',
    'mapDown': 'leptonScaledo',
    'samples': dict((skey, ['1', '1']) for skey in mcALL),
    'AsLnN': '0'
}

nuisances['lepscale_2023'] = {
    'name': 'lepscale_2023',
    'kind': 'suffix',
    'type': 'shape',
    'mapUp': 'leptonScaleup',
    'mapDown': 'leptonScaledo',
    'samples': dict((skey, ['1', '1']) for skey in mcALL),
    'AsLnN': '0'
}


##### Lepton scale
nuisances['lepscale_2023BPix'] = {
    'name': 'lepscale_2023BPix',
    'kind': 'suffix',
    'type': 'shape',
    'mapUp': 'leptonScaleup',
    'mapDown': 'leptonScaledo',
    'samples': dict((skey, ['1', '1']) for skey in mcALL),
    'AsLnN': '0'
}



# ------------------- muon efficiency and energy scale
# nuisances['eff_m'] = {
#     'name': 'eff_m_2024',
#     'kind': 'weight',
#     'type': 'shape',
#     #                        nominal          up               down
#     'samples': dict((skey, ['SFweightMu','SFweightMuUp', 'SFweightMuDown']) for skey in mcALL)
# }

# ------------------- muon efficiency and energy scale
# nuisances['eff_m'] = {
#     'name': 'eff_m_2025',
#     'kind': 'weight',
#     'type': 'shape',
#     #                        nominal          up               down
#     'samples': dict((skey, ['SFweightMu','SFweightMuUp', 'SFweightMuDown']) for skey in mcALL)
# }





