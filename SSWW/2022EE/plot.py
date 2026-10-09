

# plot configuration

# groupPlot = {}
#
# Groups of samples to improve the plots.
# If not defined, normal plots is used
#
import ROOT

palette = {
    "FerrariRed": (255,40,0),
    "Orange": (255,156, 51),
    "Orange2": (255,135, 31),
    "Yellow": (247, 195, 7),
    "LightBlue": (153, 204, 255),
    "MediumBlue": (72, 145, 234),
    "MediumBlue2": (56, 145, 224),
    "DarkBlue": (8, 103, 136),
    "Green": (47, 181, 85),
    "Green2": (55, 183, 76),
    "Green3": (16,235,52),
    "Green4": (68, 175, 105),
    "Green5": (29,194,106),
    "Green6" : (27,177,97),
    "Green7": (108, 198, 140),
    "GreenLighter": (93, 192, 128),
    "GreenDarker": (14, 150, 78),
    "LightGreen" : (82, 221, 135),
    "Violet": (242, 67, 114),
    "Pink": (247, 191, 223),
    "Peach": (255, 143, 133),
    "Peach2": (255, 146, 51),
    "Peach3": (255, 157, 71),
    "Pink2" : (253, 161, 155),
    # segnali
    "CrimsonSig" : (210,  35,  60),
    "RoseWZ"     : (180,  80, 140),
    "LightRose"  : (210, 120, 160),
    "OrangeQCD"  : (220,  80,  40),
}

def rgb(r, g, b):
    return ROOT.TColor.GetColor(r/255., g/255., b/255.)

groupPlot['top'] = {
    'nameHR'  : 'top / t#bar{t} + tVx',
    'isSignal': 0,
    'color'   : rgb(*palette["GreenDarker"]),
    'samples' : ['top', 'tVx'],
    'fill'    : 1001,
}

groupPlot['Wrong sign'] = {
    'nameHR'  : 'Wrong sign',
    'isSignal': 0,
    'color'   : rgb(*palette["Pink"]),
    'samples' : ['DY', 'OSWW'],
    'fill'    : 1001,
}

groupPlot['Fake'] = {
    'nameHR'  : 'Nonprompt',
    'isSignal': 0,
    'color'   : rgb(*palette["LightBlue"]),
    'samples' : ['Fake'],
    'fill'    : 1001,
}

groupPlot['WZ_EWK'] = {
    'nameHR'  : 'WZ EWK',
    'isSignal': 0,
    'color'   : rgb(*palette["RoseWZ"]),
    'samples' : ['WZJJ_EWK', 'WZSJJ_EWK'],
    'fill'    : 1001,
}

groupPlot['WZ_QCD'] = {
    'nameHR'  : 'WZ QCD',
    'isSignal': 0,
    'color'   : rgb(*palette["MediumBlue"]),
    'samples' : ['WZJJ_QCD', 'WZSJJ_QCD','WZJJ_Int'],
    'fill'    : 1001,
}

groupPlot['VV'] = {
    'nameHR'  : 'VV(V)',
    'isSignal': 0,
    'color'   : rgb(*palette["Orange"]),
    'samples' : ['ZZ', 'Vg', 'VgS', 'VVV', 'ggWW', 'WgS', 'ZgS', 'Wg', 'Zg', 'WW_DPS'],
    'fill'    : 1001,
}

groupPlot['Higgs'] = {
    'nameHR'  : 'Higgs',
    'isSignal': 0,
    'color'   : rgb(*palette["Pink2"]),
    'samples' : ['qqH_hww', 'ggH_hww', 'higgs'],
    'fill'    : 1001,
}

groupPlot['VBS SSWW'] = {
    'nameHR'  : 'VBS SSWW',
    'isSignal': 0,
    'color'   : rgb(*palette["CrimsonSig"]),
    'samples' : ['WW_EWK'],
    'fill'    : 1001,
}

groupPlot['QCD SSWW'] = {
    'nameHR'  : 'QCD SSWW',
    'isSignal': 0,
    'color'   : rgb(*palette["Yellow"]),
    'samples' : ['WW_QCD', 'WW_Int'],
    'fill'    : 1001,
}

# ------------------------------------------------
# plot
# ------------------------------------------------

# plot['VBS_SSWW'] = {
#     'color'   : rgb(*palette["DarkBlue"]),
#     'isSignal': 0,
#     'isData'  : 0,
#     'scale'   : 1.0,
# }

plot['WW_EWK'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['WW_QCD'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['WW_Int'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['DY'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['top'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['ggWW'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['WZJJ_EWK'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['WZJJ_QCD'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['WZJJ_Int'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['ZZ'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['WW_DPS'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['Zg'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['Wg'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['ZgS'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['WgS'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['WZSJJ_EWK'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['WZSJJ_QCD'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['VVV'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['ggH_hww'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['qqH_hww'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['higgs'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['OSWW'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['tVx'] = {
    'color'   : rgb(*palette["Violet"]),
    'isSignal': 0,
    'isData'  : 0,
    'scale'   : 1.0,
}

plot['Fake'] = {
    'color'   : rgb(*palette["Violet"]),
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
legend['lumi']   = 'L = 26.7 fb^{-1}'
legend['sqrt']   = '#sqrt{s} = 13.6 TeV'
legend['period'] = 5