#
# Used by mkDatacards.py
#

structure['DY']  = {
    'isSignal' : 0,
    'isData'   : 0,
}

structure['top'] = {
    'isSignal' : 1,
    'isData'   : 0,
    'scaleSampleForDatacard' : 10 # scaling signal to have sensitivity
}

# Data
structure['DATA']  = {
    'isSignal' : 0,
    'isData'   : 1
}


