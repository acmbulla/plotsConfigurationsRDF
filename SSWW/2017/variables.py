

#'fold' : # 0 = not fold (default), 1 = fold underflowbin, 2 = fold overflow bin, 3 = fold underflow and overflow

#
#
#
# NB: if a variable is defined in "aliases.py" it will NOT be overwritten here! Change the name if you want a new definition of a variable!
#
#


variables['events']  = {   'name': '1',
                           'range' : (1,0,2),
                           'xaxis' : 'events',
                           'fold' : 3
}

variables['ptj1']  = {
                           'name': 'CleanJet_pt.size() > 0 ? CleanJet_pt[0] : -9999.',
                           # 'name': 'Alt(CleanJet_pt,0,-9999.)',
                           'range' : (15,0.,200),
                           'xaxis' : 'p_{T} 1st jet',
                           'fold'  : 3
                           }



variables['ptj2']  = {
                           'name': 'CleanJet_pt.size() > 1 ? CleanJet_pt[1] : -9999.',
                           # 'name': 'Alt(CleanJet_pt,1,-9999.)',
                           'range' : (15,0.,150),
                           'xaxis' : 'p_{T} 2nd jet',
                           'fold'  : 3
                           }
variables['ptl1']  = {
                           'name': 'Lepton_pt.size() > 0 ? Lepton_pt[0] : -9999.',
                           # 'name': 'Alt(Lepton_pt,0,-9999.)',
                           'range' : (15,0.,200),
                           'xaxis' : 'p_{T} 1st jet',
                           'fold'  : 3
                           }

variables['mll']  = {   'name': 'mll',
                        'range' : (200,10,500),
                        'xaxis' : 'mll [GeV]',
                        'fold' : 3,
                        }


variables['mll_mybins']  = {   'name': 'mll',
                        'range' : ([12, 17, 25, 30, 35, 40, 45, 65, 200]),
                        'xaxis' : 'mll [GeV]',
                        'fold' : 3,
                        }

#
# NB: both x and y variables must be defined somewhere or already in the variables in the ttree
#
variables['mllVSmth'] = {
                        'name'  : 'mll:mth',
                        'range' : ([12, 17, 25, 30, 35, 40, 45, 65, 200],[60, 95, 110, 135, 200],),
                        'xaxis' : 'm_{ll} : m_{T}^{H}',
                        'fold'  : 3,
                        'is2d'  : 1
}


variables['njet']  = {
                       'name': 'Sum(CleanJet_pt>30)',
                       'range' : (8,0,8),
                       'xaxis' : 'Number of jets',
                       'fold' : 2   # 0 = not fold (default), 1 = fold underflowbin, 2 = fold overflow bin, 3 = fold underflow and overflow
                       }


