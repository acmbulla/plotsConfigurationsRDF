import ROOT
import os
import multiprocessing as mp

# ─────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────
eleWP = 'cutBased_MediumID_tthMVA_Run3'
muWP  = 'cut_TightID_pfIsoTight_HWW_tthmva_67'

tight_ele = f'Lepton_isTightElectron_{eleWP}'
tight_mu  = f'Lepton_isTightMuon_{muWP}'

path   = '/eos/user/a/abulla/latinoRDF/plotsConfigurationsRDF/WW/2024/rootFile/260915_Fakes/snapshot/'
NCORES = 8

# ─────────────────────────────────────────────────────────────────
# Sample definitions
# ─────────────────────────────────────────────────────────────────
mc_samples = {
    'DY'    : {'files': ['DY.root'],
               'color': ROOT.kAzure+2,  'label': 'DY'},
    'top'   : {'files': ['top.root'],
               'color': ROOT.kYellow+1, 'label': 'Top'},
    'WW'    : {'files': ['WW.root', 'ggWW.root'],
               'color': ROOT.kOrange+1, 'label': 'WW'},
    'VV'    : {'files': ['WZ.root', 'WZS.root', 'ZZ.root', 'VVV.root'],
               'color': ROOT.kGreen+2,  'label': 'VV(V)'},
    'Vg'    : {'files': ['Wg.root', 'WgS.root', 'Zg.root', 'ZgS.root'],
               'color': ROOT.kCyan+2,   'label': 'Vγ'},
    'Higgs' : {'files': ['ggH_hww.root', 'qqH_hww.root'],
               'color': ROOT.kRed+2,    'label': 'Higgs'},
    # 'Fakes' : {'files': ['Fake.root'],
    #            'color': ROOT.kGray+2,   'label': 'Fakes'},
}

# ─────────────────────────────────────────────────────────────────
# Common cuts
# ─────────────────────────────────────────────────────────────────
qcd_cuts = 'PuppiMET_pt < 30 && mtw1 < 20'

z_veto = (
    '!((Lepton_pdgId[0] + Lepton_pdgId[1]) == 0'
    ' && mll > 60 && mll < 120)'
)

ss_ee   = '(Lepton_pdgId[0] * Lepton_pdgId[1]) == 121'
ss_mumu = '(Lepton_pdgId[0] * Lepton_pdgId[1]) == 169'
ss_emu  = '(Lepton_pdgId[0] * Lepton_pdgId[1]) == 143'

ww_sr_cut = (
    'Lepton_pt.size() == 2'
    ' && Lepton_pt[1] > 20'
    f' && ({ss_ee} || {ss_mumu} || {ss_emu})'
    ' && mll > 20'
    ' && PuppiMET_pt > 30'
    ' && bVeto == true'
    ' && zstar_max < 0.75'
    ' && mjj > 500'
    ' && detajj > 2.5'
)

# ─────────────────────────────────────────────────────────────────
# Regions
# ─────────────────────────────────────────────────────────────────
regions = {
    # ── DY CR ──────────────────────────────────────────────────
    'FR_DY_CR_LL_ee' : {
        'cut'         : 'isFR_DY_CR == true',
        'extra_cut'   : f'{qcd_cuts} && abs(Lepton_pdgId[0]) == 11 && abs(Lepton_pdgId[1]) == 11',
        'weight_mc'   : 'XSWeight * SFweight2l * PromptGenLepMatch2l',
        'weight_data' : 'METFilter_DATA',
        'label'       : 'DY CR - LL - ee',
        'lumi'        : 110.0,
    },
    'FR_DY_CR_LL_mumu' : {
        'cut'         : 'isFR_DY_CR == true',
        'extra_cut'   : f'{qcd_cuts} && abs(Lepton_pdgId[0]) == 13 && abs(Lepton_pdgId[1]) == 13',
        'weight_mc'   : 'XSWeight * SFweight2l * PromptGenLepMatch2l',
        'weight_data' : 'METFilter_DATA',
        'label'       : 'DY CR - LL - mumu',
        'lumi'        : 110.0,
    },
    'FR_DY_CR_TT_ee' : {
        'cut'         : 'isFR_DY_CR == true',
        'extra_cut'   : f'{qcd_cuts} && abs(Lepton_pdgId[0]) == 11 && abs(Lepton_pdgId[1]) == 11',
        'weight_mc'   : 'XSWeight * SFweight2l * float(LepWPCut) * LepWPSF * PromptGenLepMatch2l',
        'weight_data' : 'METFilter_DATA * float(LepWPCut)',
        'label'       : 'DY CR - TT - ee',
        'lumi'        : 110.0,
    },
    'FR_DY_CR_TT_mumu' : {
        'cut'         : 'isFR_DY_CR == true',
        'extra_cut'   : f'{qcd_cuts} && abs(Lepton_pdgId[0]) == 13 && abs(Lepton_pdgId[1]) == 13',
        'weight_mc'   : 'XSWeight * SFweight2l * float(LepWPCut) * LepWPSF * PromptGenLepMatch2l',
        'weight_data' : 'METFilter_DATA * float(LepWPCut)',
        'label'       : 'DY CR - TT - mumu',
        'lumi'        : 110.0,
    },
    # ── Top CR ─────────────────────────────────────────────────
    'FR_top_CR_LL' : {
        'cut'         : 'isFR_top_CR == true',
        'extra_cut'   : f'{qcd_cuts} && Lepton_pt.size() > 2 && {z_veto}',
        'weight_mc'   : 'XSWeight * SFweight2l * PromptGenLepMatch2l',
        'weight_data' : 'METFilter_DATA',
        'label'       : 'Top CR - LL',
        'lumi'        : 110.0,
    },
    'FR_top_CR_TT' : {
        'cut'         : 'isFR_top_CR == true',
        'extra_cut'   : f'{qcd_cuts} && Lepton_pt.size() > 2 && {z_veto}',
        'weight_mc'   : 'XSWeight * SFweight2l * float(LepWPCut) * LepWPSF * PromptGenLepMatch2l',
        'weight_data' : 'METFilter_DATA * float(LepWPCut)',
        'label'       : 'Top CR - TT',
        'lumi'        : 110.0,
    },
    # ── WW SR ──────────────────────────────────────────────────
    # 'WW_SR_LL' : {
    #     'cut'         : ww_sr_cut,
    #     'extra_cut'   : '',
    #     'weight_mc'   : 'XSWeight',
    #     'weight_data' : 'METFilter_DATA',
    #     'label'       : 'WW SR - LL',
    #     'lumi'        : 110.0,
    # },
    # 'WW_SR_TT' : {
    #     'cut'         : ww_sr_cut,
    #     'extra_cut'   : '',
    #     'weight_mc'   : 'XSWeight * SFweight2l * float(LepWPCut) * LepWPSF * PromptGenLepMatch2l',
    #     'weight_data' : 'METFilter_DATA * float(LepWPCut)',
    #     'label'       : 'WW SR - TT',
    #     'lumi'        : 110.0,
    # },
    # 'WW_SR_TT_ee' : {
    #     'cut'         : ww_sr_cut,
    #     'extra_cut'   : ss_ee,
    #     'weight_mc'   : 'XSWeight * SFweight2l * float(LepWPCut) * LepWPSF * PromptGenLepMatch2l',
    #     'weight_data' : 'METFilter_DATA * float(LepWPCut)',
    #     'label'       : 'WW SR - TT - ee',
    #     'lumi'        : 110.0,
    # },
    # 'WW_SR_TT_mumu' : {
    #     'cut'         : ww_sr_cut,
    #     'extra_cut'   : ss_mumu,
    #     'weight_mc'   : 'XSWeight * SFweight2l * float(LepWPCut) * LepWPSF * PromptGenLepMatch2l',
    #     'weight_data' : 'METFilter_DATA * float(LepWPCut)',
    #     'label'       : 'WW SR - TT - mumu',
    #     'lumi'        : 110.0,
    # },
    # 'WW_SR_TT_emu' : {
    #     'cut'         : ww_sr_cut,
    #     'extra_cut'   : ss_emu,
    #     'weight_mc'   : 'XSWeight * SFweight2l * float(LepWPCut) * LepWPSF * PromptGenLepMatch2l',
    #     'weight_data' : 'METFilter_DATA * float(LepWPCut)',
    #     'label'       : 'WW SR - TT - emu',
    #     'lumi'        : 110.0,
    # },
}

# ─────────────────────────────────────────────────────────────────
# Variables to plot
# ─────────────────────────────────────────────────────────────────
variables = {
    'mll' : {
        'expr': 'mll', 'nbins': 30, 'xmin': 0, 'xmax': 200,
        'xlabel': 'm_{ll} [GeV]',
    },
    'Lepton_pt0' : {
        'expr': 'Lepton_pt[0]', 'nbins': 30, 'xmin': 0, 'xmax': 150,
        'xlabel': 'p_{T}^{l1} [GeV]',
    },
    'Lepton_pt1' : {
        'expr': '(Lepton_pt.size()>1 ? Lepton_pt[1] : -99.f)',
        'nbins': 30, 'xmin': 0, 'xmax': 100,
        'xlabel': 'p_{T}^{l2} [GeV]',
    },
    'Lepton_eta0' : {
        'expr': 'Lepton_eta[0]', 'nbins': 30, 'xmin': -3, 'xmax': 3,
        'xlabel': '#eta^{l1}',
    },
    'PuppiMET_pt' : {
        'expr': 'PuppiMET_pt', 'nbins': 30, 'xmin': 0, 'xmax': 200,
        'xlabel': 'MET [GeV]',
    },
    'mjj' : {
        'expr': 'mjj', 'nbins': 30, 'xmin': 0, 'xmax': 1000,
        'xlabel': 'm_{jj} [GeV]',
    },
    'CleanJet_pt0' : {
        'expr': 'CleanJet_pt[0]', 'nbins': 30, 'xmin': 0, 'xmax': 300,
        'xlabel': 'p_{T}^{j1} [GeV]',
    },
    'CleanJet_pt1' : {
        'expr': 'CleanJet_pt[1]', 'nbins': 30, 'xmin': 0, 'xmax': 200,
        'xlabel': 'p_{T}^{j2} [GeV]',
    },
    'events' : {
        'expr': '1', 'nbins': 1, 'xmin': 0, 'xmax': 2,
        'xlabel': 'Events',
    },
}

# ─────────────────────────────────────────────────────────────────
# Worker function (one per region, runs in separate process)
# ─────────────────────────────────────────────────────────────────
def process_region(args):
    reg_name, reg, variables, mc_samples, path = args

    import ROOT as R
    R.gROOT.SetBatch(True)
    R.gStyle.SetOptStat(0)

    cut          = reg['cut']
    extra_cut    = reg['extra_cut']
    weight_mc    = reg['weight_mc']
    weight_data  = reg['weight_data']
    label        = reg['label']
    lumi         = reg['lumi']

    full_cut = cut
    if extra_cut:
        full_cut += f' && {extra_cut}'

    outdir = f'plots/{reg_name}'
    os.makedirs(outdir, exist_ok=True)

    print(f'[{reg_name}] Starting...')

    df_data = R.RDataFrame('Events', path + 'DATA.root').Filter(full_cut)

    for var_name, var in variables.items():
        expr   = var['expr']
        nbins  = var['nbins']
        xmin   = var['xmin']
        xmax   = var['xmax']
        xlabel = var['xlabel']

        # ── DATA ──
        h_data = df_data\
            .Define('_var',      expr)\
            .Define('_w_data',   weight_data)\
            .Histo1D(
                R.RDF.TH1DModel(f'data_{reg_name}_{var_name}', '', nbins, xmin, xmax),
                '_var', '_w_data'
            ).GetValue()
        h_data.SetMarkerStyle(20)
        h_data.SetMarkerSize(1.0)
        h_data.SetLineColor(R.kBlack)

        # ── MC ──
        mc_hists = []

        for sname, sinfo in mc_samples.items():
            h_group = None

            for fname in sinfo['files']:
                fpath = path + fname
                if not os.path.exists(fpath):
                    print(f'[{reg_name}] WARNING: {fname} not found, skipping')
                    continue

                df_mc = R.RDataFrame('Events', fpath).Filter(full_cut)
                if sname == 'Fakes': weight_mc = 'METFilter_DATA * fakeW / {lumi:.1f}'.format(lumi=lumi)
                else: weight_mc = reg['weight_mc']
                h_tmp = df_mc\
                    .Define('_var',   expr)\
                    .Define('_w_mc',  f'({weight_mc}) * {lumi}')\
                    .Histo1D(
                        R.RDF.TH1DModel(
                            f'{sname}_{fname}_{reg_name}_{var_name}', '',
                            nbins, xmin, xmax
                        ), '_var', '_w_mc'
                    ).GetValue()

                if h_group is None:
                    h_group = h_tmp.Clone(f'{sname}_{reg_name}_{var_name}')
                else:
                    h_group.Add(h_tmp)

            if h_group is None:
                continue

            h_group.SetFillColor(sinfo['color'])
            h_group.SetLineColor(R.kBlack)
            h_group.SetLineWidth(1)
            mc_hists.append((sname, h_group, sinfo))

        mc_hists_sorted = sorted(mc_hists, key=lambda x: x[1].Integral())

        stack = R.THStack(f'stack_{reg_name}_{var_name}', '')
        for _, h, _ in mc_hists_sorted:
            stack.Add(h)

        h_mc_tot = mc_hists_sorted[0][1].Clone('h_mc_tot')
        h_mc_tot.Reset()
        for _, h, _ in mc_hists_sorted:
            h_mc_tot.Add(h)
        h_mc_tot.SetFillStyle(0)
        h_mc_tot.SetLineColor(R.kBlack)
        h_mc_tot.SetLineWidth(2)

        # ── Canvas ──
        c    = R.TCanvas(f'c_{reg_name}_{var_name}', '', 800, 900)
        pad1 = R.TPad(f'pad1_{reg_name}_{var_name}', '', 0, 0.3, 1, 1.0)
        pad1.SetBottomMargin(0.02)
        pad1.SetTopMargin(0.08)
        pad1.SetLeftMargin(0.12)
        pad1.Draw()
        pad2 = R.TPad(f'pad2_{reg_name}_{var_name}', '', 0, 0.0, 1, 0.3)
        pad2.SetTopMargin(0.03)
        pad2.SetBottomMargin(0.35)
        pad2.SetLeftMargin(0.12)
        pad2.Draw()

        # Upper pad
        pad1.cd()
        ymax = max(h_data.GetMaximum(), h_mc_tot.GetMaximum()) * 1.5
        stack.SetMaximum(ymax)
        stack.SetMinimum(0)
        stack.Draw('HIST')
        stack.GetXaxis().SetLabelSize(0)
        stack.GetYaxis().SetTitle('Events')
        stack.GetYaxis().SetTitleSize(0.055)
        stack.GetYaxis().SetTitleOffset(1.0)
        h_mc_tot.Draw('HIST SAME')
        h_data.Draw('E1 SAME')

        leg = R.TLegend(0.55, 0.50, 0.92, 0.88)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.SetTextSize(0.032)
        leg.AddEntry(h_data,   f'Data ({int(h_data.Integral())})', 'ep')
        leg.AddEntry(h_mc_tot, f'MC tot ({int(h_mc_tot.Integral())})', 'l')
        for sname, h, sinfo in reversed(mc_hists_sorted):
            leg.AddEntry(h, f'{sinfo["label"]} ({int(h.Integral())})', 'f')
        leg.Draw()

        latex = R.TLatex()
        latex.SetNDC()
        latex.SetTextFont(61)
        latex.SetTextSize(0.055)
        latex.DrawLatex(0.12, 0.93, 'CMS')
        latex.SetTextFont(52)
        latex.SetTextSize(0.042)
        latex.DrawLatex(0.22, 0.93, 'Preliminary')
        latex.SetTextFont(42)
        latex.SetTextSize(0.042)
        latex.DrawLatex(0.50, 0.93, f'{lumi:.1f} fb^{{-1}} (13.6 TeV)')
        latex.SetTextSize(0.048)
        latex.DrawLatex(0.14, 0.86, label)

        # Lower pad
        pad2.cd()
        pad2.SetGridy()

        h_ratio = h_data.Clone('h_ratio')
        h_ratio.Divide(h_mc_tot)

        for i in range(1, h_ratio.GetNbinsX() + 1):
            if h_mc_tot.GetBinContent(i) == 0 or abs(h_ratio.GetBinContent(i)) > 10:
                h_ratio.SetBinContent(i, 0)
                h_ratio.SetBinError(i, 0)

        h_frame = pad2.DrawFrame(xmin, 0.0, xmax, 2.0)
        h_frame.GetYaxis().SetTitle('Data / MC')
        h_frame.GetYaxis().SetNdivisions(505)
        h_frame.GetYaxis().SetTitleSize(0.13)
        h_frame.GetYaxis().SetTitleOffset(0.35)
        h_frame.GetYaxis().SetLabelSize(0.10)
        h_frame.GetXaxis().SetTitle(xlabel)
        h_frame.GetXaxis().SetTitleSize(0.13)
        h_frame.GetXaxis().SetTitleOffset(1.1)
        h_frame.GetXaxis().SetLabelSize(0.10)

        line = R.TLine(xmin, 1.0, xmax, 1.0)
        line.SetLineColor(R.kRed)
        line.SetLineStyle(2)
        line.SetLineWidth(2)
        line.Draw()

        h_band = h_mc_tot.Clone('h_band')
        h_band.Divide(h_mc_tot)
        h_band.SetFillColor(R.kGray+2)
        h_band.SetFillStyle(3354)
        h_band.SetLineColor(0)
        h_band.SetMarkerSize(0)
        h_band.Draw('E2 SAME')

        h_ratio.SetMarkerStyle(20)
        h_ratio.SetMarkerSize(0.8)
        h_ratio.SetLineColor(R.kBlack)
        h_ratio.Draw('E1 SAME')

        pad2.Update()

        outbase = f'{outdir}/{var_name}'
        c.SaveAs(f'{outbase}.png')
        c.SaveAs(f'{outbase}.pdf')
        print(f'[{reg_name}] Saved: {outbase}.png')

        del c, stack, h_mc_tot, h_ratio, h_frame, h_band

    print(f'[{reg_name}] Done.')


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    os.makedirs('plots', exist_ok=True)

    args_list = [
        (reg_name, reg, variables, mc_samples, path)
        for reg_name, reg in regions.items()
    ]

    print(f'Running {len(args_list)} regions on {NCORES} cores...')
    with mp.Pool(processes=NCORES) as pool:
        pool.map(process_region, args_list)

    print('\nAll done!')