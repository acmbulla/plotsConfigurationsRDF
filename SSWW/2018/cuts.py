



#
# Cut to be applied on top of everything else --> speed up
#
supercut = '  (Lepton_pdgId.size() > 0 ? Lepton_pt[0]: -99) > 25 \
           && (Lepton_pdgId.size() > 1 ? Lepton_pt[1]: -99) > 10 \
           && abs(Lepton_pdgId.size() > 0 ? Lepton_eta[0]: -99) < 2.5 \
           && abs(Lepton_pdgId.size() > 1 ? Lepton_eta[1]: -99) < 2.5 '




cuts['lowmll_ee']  = 'mll>40 && mll<120 && ee'

cuts['highmll_ee'] = 'mll>120 && ee'

cuts['lowmll_mumu']  = 'mll>40 && mll<120  && mumu'

cuts['highmll_mumu'] = 'mll>120 && mumu'



cuts['DY_cr'] = {
   'expr': 'mll>70 && mll<120',
    # Define the sub-categorization of sr
   'categories' : {
      'eleele' : 'ee',     # "ee" is defined in aliases.py
      'mumu'   : 'mumu',   # "mm" is defined in aliases.py
   }
}







#    #
#    # Alt(Lepton_pdgId,0,-9999))==11 --> ele
#    # Alt(Lepton_pdgId,0,-9999))==13 --> mu
#    #
#
#
#    #
#    # (Lepton_pdgId.size() > 1 ? Lepton_pdgId[1]: -99)
#    #
#
#
#    # cuts['lowmll']  = '(Lepton_pdgId.size() > 0 ? Lepton_pt[0]: -99) > 25 \
#    #                 && (Lepton_pdgId.size() > 1 ? Lepton_pt[1]: -99) > 10 \
#    #                 && (Lepton_pdgId.size() > 1 ? Lepton_pt[1]: -99) > 10 \
#    #                 && abs(Lepton_pdgId.size() > 0 ? Lepton_eta[0]: -99) < 2.5 \
#    #                 && abs(Lepton_pdgId.size() > 1 ? Lepton_eta[1]: -99) < 2.5 \
#    #                 && mll>40 && mll<120'
#    #
#    # cuts['highmll'] = 'mll>120'
#
#
#    #
#    # Cut to be applied on top of everything else --> speed up
#    #
#    supercut = '  (Lepton_pdgId.size() > 0 ? Lepton_pt[0]: -99) > 25 \
#               && (Lepton_pdgId.size() > 1 ? Lepton_pt[1]: -99) > 10 \
#               && abs(Lepton_pdgId.size() > 0 ? Lepton_eta[0]: -99) < 2.5 \
#               && abs(Lepton_pdgId.size() > 1 ? Lepton_eta[1]: -99) < 2.5 '
#
#
#
#
#    # cuts['lowmll_ee']  = 'mll>40 && mll<120 && ee'
#    #
#    # cuts['highmll_ee'] = 'mll>120 && ee'
#    #
#    # cuts['lowmll_mumu']  = 'mll>40 && mll<120  && mumu'
#    #
#    # cuts['highmll_mumu'] = 'mll>120 && mumu'
#
#    cuts['jets2'] = 'njet==2'
#
#
#
#    # cuts['DY_cr'] = {
#    cuts['DrellYan_cr'] = {
#       'expr': 'mll>70 && mll<120',
#        # Define the sub-categorization of sr
#       'categories' : {
#          'eleele' : 'ee',     # "ee" is defined in aliases.py
#          'mumu'   : 'mumu',   # "mm" is defined in aliases.py
#       }
#    }
#
#
#

# cuts['DY'] = {
#     'expr' : 'Alt(Lepton_pt,2,0) < 15 && (abs(Lepton_pdgId[0])==abs(Lepton_pdgId[1]))',
#     'categories' : {
#         '0j'  : 'Alt(CleanJet_pt,0,0) < 30',
#         '1j'  : 'Alt(CleanJet_pt,1,0) < 30 && Alt(CleanJet_pt,0,0) > 30',
#         '2j'  : 'Alt(CleanJet_pt,2,0) < 30 && Alt(CleanJet_pt,1,0) > 30',
#     }
# }
