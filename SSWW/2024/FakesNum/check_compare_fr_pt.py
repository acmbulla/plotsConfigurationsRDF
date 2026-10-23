"""Numerical and end-to-end ROOT/plot checks; fixtures are synthetic, not FR results."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

import boost_histogram as bh
import numpy as np
import uproot

from compare_fr_pt import Counts, TAGS, needed_names, project_pt, read_counts


def write_hist(values, variances, pt, eta):
    hist=bh.Histogram(bh.axis.Variable(pt),bh.axis.Variable(eta),storage=bh.storage.Weight())
    hist.view().value[:]=values;hist.view().variance[:]=variances
    return hist


def main():
    # Unequal populations and unequal eta widths: averaging FR or integrating
    # histogram contents as densities must both give a different answer.
    pt=np.array([10.,20.,40.,80.]);eta=np.array([-2.5,-.8,0.,2.5])
    c=Counts(pt[:2],eta[:3],np.array([[1.,9.]]),np.array([[1.,9.]]),
             np.array([[99.,1.]]),np.array([[99.,1.]]))
    result=project_pt([c]);assert np.isclose(result['rate'][0],10/110)
    assert not np.isclose(result['rate'][0],np.mean([.01,.9]))
    bad=Counts(pt[:2],eta[:2],np.array([[-1.]]),np.array([[2.]]),np.array([[0.]]),np.array([[1.]]))
    assert not project_pt([bad])['valid'][0] and np.isnan(project_pt([bad])['rate'][0])
    negative=Counts(pt[:2],eta[:2],np.array([[-1.]]),np.array([[2.]]),np.array([[3.]]),np.array([[3.]]))
    assert project_pt([negative])['valid'][0] and project_pt([negative])['rate'][0]==-.5
    with tempfile.TemporaryDirectory(prefix='check_fr_pt_') as temporary:
        base=Path(temporary);inputs=base/'maps';out=base/'plots';reference={}
        for wi,wp in enumerate(['WP_A','WP_B']):
            folder=inputs/'2024'/wp;folder.mkdir(parents=True)
            for flavor in TAGS:
                definitions=[]
                for case in ['1l','2l_lep0','2l_lep1']:
                    for cat in ['incl','btag','bveto']:
                        definitions.extend((name,cat) for name in needed_names(flavor,case,cat,['sf','df']))
                for name,cat in definitions:
                    index=0 if '_1l_' in name else (1 if '_lep0_' in name else 3)+int('_emu_' in name)
                    ts,rs={'incl':(1.,1.),'btag':(.4,.2),'bveto':(.6,.7)}[cat]
                    td=np.array([[1.,9.,4.],[8.,1.,3.],[2.,8.,6.]])*(index+1)*(1+.1*wi)*ts
                    rd=np.array([[99.,1.,6.],[2.,99.,7.],[8.,2.,4.]])*(1+index%2)*rs
                    tm=np.ones_like(td)*ts;rm=np.ones_like(rd)*rs
                    vt=td.copy();vr=rd.copy();vtm=tm*1.5;vrm=rm*1.5
                    sf_t=np.array([.5,2.,1.5]);sf_r=np.array([1.2,.7,2.])
                    values={'h_tight_data':(td,vt),'h_rest_data':(rd,vr),
                            'h_tight_mc':(tm,vtm),'h_rest_mc':(rm,vrm),
                            'h_tight_mc_SF':(tm*sf_t,vtm*sf_t**2),
                            'h_rest_mc_SF':(rm*sf_r,vrm*sf_r**2)}
                    with uproot.recreate(folder/name) as root:
                        for key,(v,var) in values.items():root[key]=write_hist(v,var,pt,eta)
                    reference[wp,flavor,name]=(td-tm*sf_t,vt+vtm*sf_t**2,rd-rm*sf_r,vr+vrm*sf_r**2)
        script=Path(__file__).with_name('compare_fr_pt.py')
        done=subprocess.run([sys.executable,str(script),'--input',str(inputs),'--out',str(out)],
                            text=True,capture_output=True)
        if done.returncode:raise RuntimeError(done.stdout+done.stderr)
        assert len(list(out.rglob('*.png')))==16 and len(list(out.rglob('*.pdf')))==16
        for wp in ['WP_A','WP_B']:
            for flavor in TAGS:
                curves=json.loads((out/'2024'/wp/flavor/'curves.json').read_text());assert len(curves)==9
                for case in ['1l','2l_lep0','2l_lep1']:
                    for cat in ['incl','btag','bveto']:
                        names=needed_names(flavor,case,cat,['sf','df'])
                        n,vn,r,vr=[sum(reference[wp,flavor,name][i].sum(axis=1) for name in names) for i in range(4)]
                        expected=n/(n+r);err=np.sqrt((r*r*vn+n*n*vr)/(n+r)**4)
                        np.testing.assert_allclose(curves[f'{case}/{cat}']['rate'],expected)
                        np.testing.assert_allclose(curves[f'{case}/{cat}']['error'],err)
        # ROOT Sumw2 is essential for weighted/subtracted uncertainties.
        unweighted=base/'unweighted.root'
        with uproot.recreate(unweighted) as root:
            root['h_tight_data']=(np.ones((3,3)),pt,eta)
            root['h_rest_data']=(np.ones((3,3)),pt,eta)
        try:read_counts(str(unweighted),'raw')
        except ValueError as exc:assert 'Sumw2' in str(exc)
        else:raise AssertionError('unweighted errors silently accepted')
        # A missing DF input cannot silently turn the combined 2l into SF-only.
        (inputs/'2024/WP_A/EleFR_emu_lep0_incl.root').unlink()
        done=subprocess.run([sys.executable,str(script),'--input',str(inputs),'--out',str(base/'bad')],text=True,capture_output=True)
        assert done.returncode!=0 and 'Required maps are missing' in done.stderr
    print('PASS: eta counts projection, SF/DF union, corrected subtraction and variances, zero/negative denominators, all flavors/WPs,16 plot pairs, strict missing-input and Sumw2 checks')


if __name__=='__main__':main()
