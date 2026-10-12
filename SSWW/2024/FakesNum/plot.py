

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
    "Red"        : (198,  60,  85),  # WZ QCD
    "GreenPure"  : (  0, 108,   0),  # Vgamma
    "Swamp"      : ( 53,  91,  56),  # VVV
    "LightGreen" : (122, 142,  70),  # Other bkg
    "lightAzure" : (153, 204, 255),  # ZZ
    "Orange"     : (255, 156,  51),  # top
    "DarkBlue"   : (  8, 103, 136),  # DY
    "Peach2"     : (255, 146,  51),  # WgS/ZgS
    "Pink"       : (247, 191, 223),  # Higgs
}

def rgb(r, g, b):
    ci = ROOT.TColor.GetFreeColorIndex()
    c  = ROOT.TColor(ci, r/255., g/255., b/255.)
    return ci


# ------------------------------------------------
# groupPlot
# ------------------------------------------------

groupPlot['WW'] = {
    'nameHR'  : 'EWK W^{#pm}W^{#pm}',
    'isSignal': 1,
    'color'   : rgb(*palette2["Yellow"]),
    'samples' : ['WW'],
    'fill'    : 1001,
}

groupPlot['top'] = {
    'nameHR'  : 'top / t#bar{t}',
    'isSignal': 0,
    'color'   : rgb(*palette2["Orange"]),
    'samples' : ['top'],
    'fill'    : 1001,
}

groupPlot['DY'] = {
    'nameHR'  : 'DY',
    'isSignal': 0,
    'color'   : rgb(*palette2["DarkBlue"]),
    'samples' : ['DY'],
    'fill'    : 1001,
}

groupPlot['ggWW'] = {
    'nameHR'  : 'ggWW',
    'isSignal': 0,
    'color'   : rgb(*palette2["DarkBlue"]),
    'samples' : ['ggWW'],
    'fill'    : 1001,
}

# groupPlot['Fake'] = {
#     'nameHR'  : 'Nonprompt',
#     'isSignal': 0,
#     'color'   : rgb(*palette2["DeadViolet"]),
#     'samples' : ['Fake'],
#     'fill'    : 1001,
# }

groupPlot['WZ'] = {
    'nameHR'  : 'WZ',
    'isSignal': 0,
    'color'   : rgb(*palette2["Red"]),
    'samples' : ['WZ'],
    'fill'    : 1001,
}

groupPlot['ZZ'] = {
    'nameHR'  : 'ZZ',
    'isSignal': 0,
    'color'   : rgb(*palette2["lightAzure"]),
    'samples' : ['ZZ'],
    'fill'    : 1001,
}

groupPlot['Vg'] = {
    'nameHR'  : 'V#gamma',
    'isSignal': 0,
    'color'   : rgb(*palette2["GreenPure"]),
    'samples' : ['Wg', 'Zg'],
    'fill'    : 1001,
}

groupPlot['VgS'] = {
    'nameHR'  : 'V#gamma*',
    'isSignal': 0,
    'color'   : rgb(*palette2["Peach2"]),
    'samples' : ['WgS', 'ZgS', 'WZS'],
    'fill'    : 1001,
}

groupPlot['VVV'] = {
    'nameHR'  : 'VVV',
    'isSignal': 0,
    'color'   : rgb(*palette2["Swamp"]),
    'samples' : ['VVV'],
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

plot['WW'] = {
    'color'   : rgb(*palette2["Yellow"]),
    'isSignal': 1,
    'isData'  : 0,
    'scale'   : 1.0,
}

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

# plot['Fake'] = {
#     'color'   : rgb(*palette2["DeadViolet"]),
#     'isSignal': 0,
#     'isData'  : 0,
#     'scale'   : 1.0,
# }

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