

# plot configuration

# groupPlot = {}
#
# Groups of samples to improve the plots.
# If not defined, normal plots is used
#

Red=632; Violet=880; Green=416; Orange=800; Yellow=400; Azure=860

palette = {
    "Orange": (242, 108, 13), #f26c0d
    "Yellow": (247, 195, 7), #f7c307
    "LightBlue": (153, 204, 255), #99ccff
    "MediumBlue": (72, 145, 234),  #4891ea
    "MediumBlue2": (56, 145, 224),    #3891e0
    "DarkBlue": (8, 103, 136), #086788
    "Green": (47, 181, 85), #2fb555
    "Green2": (55, 183, 76),  #37b74c
    "Green3": (16,235,52),#10eb34
    "Green4": (68, 175, 105), #44af69
    "Green5": (29,194,106),#1DC26A
    "Green6" : (27,177,97), #1BB161
    "Green7": (108, 198, 140), # 6CC68C
    "GreenLighter": (93, 192, 128),  #5DC080
    "GreenDarker": (14, 150, 78), # 14, 150, 78
    "LightGreen" : (82, 221, 135), #52dd87
    "Violet": (242, 67, 114), #f24372
    "Pink": (247, 191, 223), #F7BFDF,
    "Peach": (255, 143, 133), #F7C59F
    "Peach2": (255, 146, 51), #FF9233
    "Peach3": (255, 157, 71), #
    "Pink2" : (253, 161, 155), #FD9BA1
    "Orange": (255,156, 51),
    "Orange2": (255,135, 31)
}

palette2 = {
    "Yellow": (234,180,100), #SSWW
    "Violet": (121,16,255), # tVx
    "DeadViolet": (95,94,149), # Nonprompt
    "Red": (198,60,85), # WZ QCD
    "GreenPure": (0,108,0), # Vg
    "Swamp": (53,91,56), # EWK WZ
    "LightGreen": (122,142,70), # Other bkg
    "lightAzure": (153, 204, 255), # ZZ
    "fullAzure": (49,195,255), # Wrong sign
}



groupPlot['DY']  = {
    'nameHR':'DY',
    'isSignal':0,
    # 'color': palette2["DeadViolet"],
    'color': 418, # kGreen+2
    'samples':['DY'], #['Fake_lep_me', 'Fake_lep_em'],
    'fill': 1001
}


groupPlot['top']  = {
    'nameHR':"top and ttbar",
    'isSignal':1,
    'color': palette2["Yellow"],
    'samples':['top'],
    'fill': 1001
}



# keys here must match keys in samples.py

plot['top']  = {
    'color':Green + 10,
    'isSignal':0,
    'isData':0,
    'scale':1.0
}

plot['DY']  = {
    'color':Green + 10,
    'isSignal':0,
    'isData':0,
    'scale':1.0
}


##Data

plot['DATA']  = {
    'nameHR':'Data',
    'color':1,
    'isSignal':0,
    'isData':1,
    'isBlind':0,
    'scale':1.0
}

# additional options
legend['lumi'] = 'L = 41.48/fb'
legend['sqrt'] = '#sqrt{s} = 13 TeV'



