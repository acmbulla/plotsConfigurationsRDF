

# plot configuration

# groupPlot = {}
#
# Groups of samples to improve the plots.
# If not defined, normal plots is used
#
import ROOT

palette2 = {
    "Yellow"     : (234, 180, 100),  # SSWW signal
    "DeadViolet" : ( 95,  94, 149),  # Nonprompt
    "Red"        : (198,  60,  85),  # WZ
    "RedDark"  : (180,  35,  55),  # rosso scuro, freddo — vicino al tuo Red ma più profondo
    "RedWarm"  : (230,  80,  40),  # rosso-arancio caldo — si distingue nettamente
    "GreenPure"  : (  0, 140,  60),  # Vgamma
    "Swamp"      : ( 53,  91,  56),  # VVV
    "lightAzure" : (100, 180, 240),  # ZZ
    "Orange"     : (230, 110,  30),  # top
    "DarkBlue"   : (  8, 103, 136),  # DY
    "Teal"       : ( 38, 180, 160),  # ggWW
    "Salmon"     : (220, 100,  80),  # VgS
    "Pink"       : (220, 150, 200),  # Higgs
    "SigLL" : (120, 160, 230),  # blu chiaro
    "SigTL" : ( 80, 110, 200),  # blu medio  
    "SigTT" : ( 50,  60, 170),  # blu scuro
}


def rgb(r, g, b):
    return ROOT.TColor.GetColor(r/255., g/255., b/255.)

groupPlot['top'] = {
    'nameHR'  : 'top / t#bar{t}',
    'isSignal': 0,
    'color'   : rgb(*palette2["GreenPure"]),
    'samples' : ['top'],
    'fill'    : 1001,
}

groupPlot['DY'] = {
    'nameHR'  : 'DY',
    'isSignal': 0,
    'color'   : rgb(*palette2["Orange"]),
    'samples' : ['DY'],
    'fill'    : 1001,
}

groupPlot['Fake'] = {
    'nameHR'  : 'Nonprompt',
    'isSignal': 0,
    'color'   : rgb(*palette2["lightAzure"]),
    'samples' : ['Fake'],
    'fill'    : 1001,
}

groupPlot['WZ'] = {
    'nameHR'  : 'WZ',
    'isSignal': 0,
    'color'   : rgb(*palette2["Red"]),
    'samples' : ['WZ'],
    'fill'    : 1001,
}

groupPlot['VBS_SSWW'] = {
    'nameHR'  : 'VBS_SSWW',
    'isSignal': 0,
    'color'   : rgb(*palette2["RedDark"]),
    'samples' : ['VBS_SSWW'],
    'fill'    : 1001,
}
# groupPlot['VBS_SSWW_WWCM_LL'] = {
#     'nameHR'  : 'VBS_SSWW_WWCM_LL',
#     'isSignal': 1,
#     'color'   : rgb(*palette2["SigLL"]),
#     'samples' : ['VBS_SSWW_WWCM_LL'],
#     'fill'    : 1001,
# }
# groupPlot['VBS_SSWW_WWCM_TL'] = {
#     'nameHR'  : 'VBS_SSWW_WWCM_TL',
#     'isSignal': 1,
#     'color'   : rgb(*palette2["SigTL"]),
#     'samples' : ['VBS_SSWW_WWCM_TL'],
#     'fill'    : 1001,
# }
# groupPlot['VBS_SSWW_WWCM_TT'] = {
#     'nameHR'  : 'VBS_SSWW_WWCM_TT',
#     'isSignal': 1,
#     'color'   : rgb(*palette2["SigTT"]),
#     'samples' : ['VBS_SSWW_WWCM_TT'],
#     'fill'    : 1001,
# }



groupPlot['VV'] = {
    'nameHR'  : 'VV(V)',
    'isSignal': 0,
    'color'   : rgb(*palette2["DeadViolet"]),
    'samples' : ['ZZ', 'Vg', 'VgS', 'VVV', 'ggWW', 'WZS', 'WgS', 'ZgS', 'Wg', 'Zg'],
    'fill'    : 1001,
}

groupPlot['Higgs'] = {
    'nameHR'  : 'Higgs',
    'isSignal': 0,
    'color'   : rgb(*palette2["Pink"]),
    'samples' : ['qqH_hww', 'ggH_hww'],
    'fill'    : 1001,
}


# ------------------------------------------------
# plot
# ------------------------------------------------

plot['VBS_SSWW'] = {
    'color'   : rgb(*palette2["Yellow"]),
    'isSignal': 1,
    'isData'  : 0,
    'scale'   : 1.0,
}
# plot['VBS_SSWW_WWCM_LL'] = {
#     'color'   : rgb(*palette2["Yellow"]),
#     'isSignal': 1,
#     'isData'  : 0,
#     'scale'   : 1.0,
# }
# plot['VBS_SSWW_WWCM_TL'] = {
#     'color'   : rgb(*palette2["Yellow"]),
#     'isSignal': 1,
#     'isData'  : 0,
#     'scale'   : 1.0,
# }
# plot['VBS_SSWW_WWCM_TT'] = {
#     'color'   : rgb(*palette2["Yellow"]),
#     'isSignal': 1,
#     'isData'  : 0,
#     'scale'   : 1.0,
# }

plot['top'] = {
    'color'   : rgb(*palette2["Orange"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['DY'] = {
    'color'   : rgb(*palette2["DarkBlue"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['Fake'] = {
    'color'   : rgb(*palette2["DeadViolet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['ggWW'] = {
    'color'   : rgb(*palette2["Red"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['WZ'] = {
    'color'   : rgb(*palette2["Red"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['ZZ'] = {
    'color'   : rgb(*palette2["lightAzure"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['Zg'] = {
    'color'   : rgb(*palette2["Pink"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['Wg'] = {
    'color'   : rgb(*palette2["Pink"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['ZgS'] = {
    'color'   : rgb(*palette2["Pink"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['WgS'] = {
    'color'   : rgb(*palette2["Pink"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['WZS'] = {
    'color'   : rgb(*palette2["Pink"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['VVV'] = {
    'color'   : rgb(*palette2["Swamp"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['ggH_hww'] = {
    'color'   : rgb(*palette2["Pink"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['qqH_hww'] = {
    'color'   : rgb(*palette2["Pink"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['DATA'] = {
    'nameHR'  : 'Data',
    'color'   : 1,
    'isSignal': 0,
    'isData'  : 1,
    'isBlind' : 0,
    'scale'   : 1.0,
}


# ------------------------------------------------
# legend
# ------------------------------------------------
legend['lumi']   = 'L = 110.11 fb^{-1}'
legend['sqrt']   = '#sqrt{s} = 13.6 TeV'
legend['period'] = 5