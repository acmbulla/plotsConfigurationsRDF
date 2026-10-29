"""Numerical and end-to-end ROOT/plot checks; fixtures are synthetic, not FR results."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import os
from unittest.mock import patch

import boost_histogram as bh
import numpy as np
import uproot

from compare_fr_pt import Counts, TAGS, needed_names, project_pt, read_counts, overlay, snap_bands


def write_hist(values, variances, pt, eta):
    hist=bh.Histogram(bh.axis.Variable(pt),bh.axis.Variable(eta),storage=bh.storage.Weight())
    hist.view().value[:]=values;hist.view().variance[:]=variances
    return hist


def main():
    # Unequal populations and unequal eta widths: averaging FR or integrating
    # histogram contents as densities must both give a different answer.
    pt=np.array([10.,20.,40.,80.]);eta=np.array([-2.5,-.8,0.,2.5])
    c=Counts(pt[:2],eta[:3],np.array([[1.,9.]]),np.array([[1.,9.]]),
             np.array([[100.,10.]]),np.array([[100.,10.]]))
    result=project_pt([c]);assert np.isclose(result['rate'][0],10/110)
    assert not np.isclose(result['rate'][0],np.mean([.01,.9]))
    bad=Counts(pt[:2],eta[:2],np.array([[-1.]]),np.array([[2.]]),np.array([[-1.]]),np.array([[3.]]))
    assert not project_pt([bad])['valid'][0] and np.isnan(project_pt([bad])['rate'][0])
    negative=Counts(pt[:2],eta[:2],np.array([[-1.]]),np.array([[2.]]),np.array([[2.]]),np.array([[5.]]))
    assert project_pt([negative])['valid'][0] and project_pt([negative])['rate'][0]==-.5
    with tempfile.TemporaryDirectory(prefix='check_fr_pt_') as temporary:
        base=Path(temporary);inputs=base/'maps';out=base/'plots';reference={}
        os.environ.setdefault('MPLCONFIGDIR', str(base/'.matplotlib'))
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.container import ErrorbarContainer
        with patch('matplotlib.pyplot.close'):
            overlay({'curve':result}, [('curve','test')], 'markers', 'subtitle', base/'markers')
            fig=plt.gcf()
            containers=[item for item in fig.axes[0].containers if isinstance(item,ErrorbarContainer)]
            assert len(containers)==1 and containers[0].lines[0].get_linestyle().lower()=='none'
        plt.close(fig)
        for wi,wp in enumerate(['WP_A','WP_B']):
            folder=inputs/'2024'/wp;folder.mkdir(parents=True)
            for flavor in TAGS:
                definitions=[]
                for case in ['1l','2l_lep0','2l_lep1']:
                    for cat in ['incl','btag','bveto']:
                        definitions.extend((name,cat) for name in needed_names(flavor,case,cat,['sf','df']))
                definitions.extend((f'{TAGS[flavor][0]}PR_{TAGS[flavor][1]}_lep{slot}.root','incl')
                                   for slot in (0,1))
                for name,cat in definitions:
                    index=0 if '_1l_' in name else (1 if '_lep0_' in name else 3)+int('_emu_' in name)
                    ts,rs={'incl':(1.,1.),'btag':(.4,.2),'bveto':(.6,.7)}[cat]
                    td=np.array([[1.,9.,4.],[8.,1.,3.],[2.,8.,6.]])*(index+1)*(1+.1*wi)*ts
                    rd=np.array([[99.,1.,6.],[2.,99.,7.],[8.,2.,4.]])*(1+index%2)*rs
                    tm=np.ones_like(td)*ts;rm=np.ones_like(rd)*rs
                    vt=td.copy();vr=rd.copy();vtm=tm*1.5;vrm=rm*1.5
                    # Distinct tight and loose factors, so a run that mixed
                    # them up could not pass: the rate is tight/loose and the
                    # two levels are subtracted with factors of their own.
                    sf_t=np.array([.5,2.,1.5]);sf_l=np.array([1.2,.7,2.])
                    ld=td+rd;lm=tm+rm;vl=vt+vr;vlm=vtm+vrm
                    values={'h_tight_data':(td,vt),'h_rest_data':(rd,vr),
                            'h_loose_data':(ld,vl),
                            'h_tight_mc':(tm,vtm),'h_rest_mc':(rm,vrm),
                            'h_loose_mc':(lm,vlm),
                            'h_tight_mc_SF':(tm*sf_t,vtm*sf_t**2),
                            'h_loose_mc_SF':(lm*sf_l,vlm*sf_l**2)}
                    with uproot.recreate(folder/name) as root:
                        for key,(v,var) in values.items():root[key]=write_hist(v,var,pt,eta)
                    reference[wp,flavor,name,'corrected']=(td-tm*sf_t,vt+vtm*sf_t**2,ld-lm*sf_l,vl+vlm*sf_l**2)
                    reference[wp,flavor,name,'ewk']=(td-tm,vt+vtm,ld-lm,vl+vlm)
        script=Path(__file__).with_name('compare_fr_pt.py')
        done=subprocess.run([sys.executable,str(script),'--input',str(inputs),'--out',str(out)],
                            text=True,capture_output=True)
        if done.returncode:raise RuntimeError(done.stdout+done.stderr)
        assert len(list(out.rglob('*.png')))==32 and len(list(out.rglob('*.pdf')))==32
        for wp in ['WP_A','WP_B']:
            for flavor in TAGS:
                for variant,tag in [('ewk','EWK'),('corrected','EWKcorr')]:
                    curves=json.loads((out/'2024'/wp/flavor/f'curves_{tag}.json').read_text());assert len(curves)==9
                    for case in ['1l','2l_lep0','2l_lep1']:
                        for cat in ['incl','btag','bveto']:
                            names=needed_names(flavor,case,cat,['sf','df'])
                            n,vn,l,vl=[sum(reference[wp,flavor,name,variant][i].sum(axis=1) for name in names) for i in range(4)]
                            expected=n/l;err=np.sqrt((vn*l*l+n*n*vl)/l**4)
                            np.testing.assert_allclose(curves[f'{case}/{cat}']['rate'],expected)
                            np.testing.assert_allclose(curves[f'{case}/{cat}']['error'],err)
        example=out/'2024/WP_A/ele'
        ewk=json.loads((example/'curves_EWK.json').read_text())
        corr=json.loads((example/'curves_EWKcorr.json').read_text())
        assert not np.allclose(ewk['1l/incl']['rate'],corr['1l/incl']['rate'])
        selected=base/'only_ewk'
        done=subprocess.run([sys.executable,str(script),'--input',str(inputs),'--out',str(selected),
                             '--flavor','ele','--wp','WP_A','--variant','ewk'],text=True,capture_output=True)
        if done.returncode:raise RuntimeError(done.stdout+done.stderr)
        assert len(list(selected.rglob('*.png')))==4
        assert not list(selected.rglob('*EWKcorr*'))
        # Legacy maps: own pT binning, |eta| bins that do not line up with the
        # measured ones, and numerator/denominator counts with no Sumw2.
        legacy_root=base/'legacy';legacy_folder=legacy_root/'2024'/'WP_A';legacy_folder.mkdir(parents=True)
        legacy_pt=np.array([10.,25.,50.]);legacy_eta=np.array([0.,1.479,2.5])
        num=np.array([[3.,7.],[11.,2.]]);den=np.array([[30.,70.],[55.,8.]])
        rate_var=np.array([[1e-4,4e-4],[9e-4,2.5e-5]])
        for jet in [20,30]:
            scale=jet/30.
            with uproot.recreate(legacy_folder/f'EleFR_jet{jet}.root') as root:
                root['FR_pT_eta_EWKcorr']=write_hist(num*scale/den,rate_var,legacy_pt,legacy_eta)
                root['FR_pT_eta']=write_hist(2*num*scale/den,rate_var,legacy_pt,legacy_eta)
                root['FR_pT_eta_EWKcorr_numerator']=(num*scale,legacy_pt,legacy_eta)
                root['FR_pT_eta_EWKcorr_denominator']=(den,legacy_pt,legacy_eta)
                root['FR_pT_eta_numerator']=(2*num*scale,legacy_pt,legacy_eta)
                root['FR_pT_eta_denominator']=(den,legacy_pt,legacy_eta)
        pr_values=np.array([[.6,.4],[.9,.8]]);pr_var=np.array([[1e-4,2e-4],[3e-4,4e-4]])
        with uproot.recreate(legacy_folder/'ElePR.root') as root:
            root['h_Ele_signal_pt_eta_bin']=write_hist(pr_values,pr_var,legacy_pt,legacy_eta)
        compared=base/'legacy_plots'
        done=subprocess.run([sys.executable,str(script),'--input',str(inputs),'--out',str(compared),
                             '--legacy-input',str(legacy_root),'--flavor','ele','--wp','WP_A','--variant','ewk'],
                            text=True,capture_output=True)
        if done.returncode:raise RuntimeError(done.stdout+done.stderr)
        example=compared/'2024/WP_A/ele'
        for name in ['legacy_jet_scan_EWK','legacy_vs_measured_EWK','prompt_rate_eta0_EWK','prompt_rate_eta1_EWK']:
            assert (example/f'{name}.png').exists() and (example/f'{name}.pdf').exists(),name
        curves=json.loads((example/'curves_EWK.json').read_text())
        assert len(curves)==11 and sorted(k for k in curves if k.startswith('legacy'))==['legacy/jet20','legacy/jet30']
        for jet in [20,30]:
            tight=(num*jet/30.).sum(axis=1);denominator=den.sum(axis=1)
            weight=den/denominator[:,None]
            np.testing.assert_allclose(curves[f'legacy/jet{jet}']['rate'],tight/denominator)
            np.testing.assert_allclose(curves[f'legacy/jet{jet}']['error'],
                                       np.sqrt((weight**2*rate_var).sum(axis=1)))
        # The eta-integrated legacy rate is not the average of the two bins.
        assert not np.allclose(curves['legacy/jet30']['rate'],(num/den).mean(axis=1))
        prompt=json.loads((example/'prompt_rate_EWK.json').read_text())
        assert len(prompt)==10
        for index in range(2):
            np.testing.assert_allclose(prompt[f'legacy/eta{index}']['rate'],pr_values[:,index])
            np.testing.assert_allclose(prompt[f'legacy/eta{index}']['error'],np.sqrt(pr_var[:,index]))
        # 1.479 has no counterpart in the measured binning: it is snapped to 0.8
        # and the band actually used is reported, not assumed equal.
        bands=snap_bands(legacy_eta,eta)
        assert [band[2:4] for band in bands]==[(0.,.8),(.8,2.5)]
        assert prompt['lep0/eta0']['eta_band']==[0.,.8] and prompt['lep1/eta1']['eta_band']==[.8,2.5]
        for slot in (0,1):
            T,VT,L,VL=reference['WP_A','ele',f'ElePR_ee_lep{slot}.root','ewk']
            for index,(_,_,_,_,mask) in enumerate(bands):
                n,vn,l,vl=[part[:,mask].sum(axis=1) for part in (T,VT,L,VL)]
                np.testing.assert_allclose(prompt[f'lep{slot}/eta{index}']['rate'],n/l)
                np.testing.assert_allclose(prompt[f'lep{slot}/eta{index}']['error'],
                                           np.sqrt((vn*l*l+n*n*vl)/l**4))
            raw=prompt[f'lep{slot}_raw/eta0']['rate']
            assert not np.allclose(raw,prompt[f'lep{slot}/eta0']['rate'])
        # A WP with no legacy maps is reported, never fatal.
        done=subprocess.run([sys.executable,str(script),'--input',str(inputs),'--out',str(base/'legacy_gap'),
                             '--legacy-input',str(legacy_root),'--flavor','ele','--wp','WP_B','--variant','ewk'],
                            text=True,capture_output=True)
        if done.returncode:raise RuntimeError(done.stdout+done.stderr)
        assert 'no EleFR_jet*.root for WP WP_B' in done.stdout
        assert len(json.loads((base/'legacy_gap'/'2024/WP_B/ele/curves_EWK.json').read_text()))==9
        # ROOT Sumw2 is essential for weighted/subtracted uncertainties.
        unweighted=base/'unweighted.root'
        with uproot.recreate(unweighted) as root:
            root['h_tight_data']=(np.ones((3,3)),pt,eta)
            root['h_loose_data']=(np.ones((3,3)),pt,eta)
        try:read_counts(str(unweighted),'raw')
        except ValueError as exc:assert 'Sumw2' in str(exc)
        else:raise AssertionError('unweighted errors silently accepted')
        # A missing DF input cannot silently turn the combined 2l into SF-only.
        (inputs/'2024/WP_A/EleFR_emu_lep0_incl.root').unlink()
        done=subprocess.run([sys.executable,str(script),'--input',str(inputs),'--out',str(base/'bad')],text=True,capture_output=True)
        assert done.returncode!=0 and 'Required maps are missing' in done.stderr
    print('PASS: eta counts projection, SF/DF union, corrected subtraction and variances, zero/negative denominators, all flavors/WPs,32 distinct EWK/EWKcorr plot pairs, EWK-only selection, no connecting lines, strict missing-input and Sumw2 checks, legacy jet-threshold integration with the denominators as weights, snapped |eta| bands, legacy vs measured prompt rate, missing legacy maps reported and not fatal')


if __name__=='__main__':main()
