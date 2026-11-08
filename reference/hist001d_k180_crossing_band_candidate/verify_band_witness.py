#!/usr/bin/env python3
"""Independent exact-rational arithmetic / topology audit of whole-band witnesses.

Does not independently reproduce Bessel interval calculations; a full replay
must execute crossing_band_certifier against original protected sources.
"""
import argparse,copy,json
from fractions import Fraction as F
from pathlib import Path
LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')

def get_f(cell,prefix):
    return F(int(cell[prefix+'_n']),int(cell[prefix+'_d']))

def exact_panel_floor(w,K):
    L=get_f(w,'left');U=get_f(w,'right')
    if not L<U or type(K) is not int or K<=0:raise ValueError('invalid panel/curvature')
    d=U-L;q=int(w['Q_mid_lower_integer']);plo=int(w['P_left_upper_integer']);phi=int(w['P_right_upper_integer'])
    Dlo=int(w['Q_slope_lower_integer']);Dhi=int(w['Q_slope_upper_integer'])
    if Dlo>Dhi or min(Dlo,Dhi)<0:raise ValueError('invalid convex source derivative')
    s=F(phi-plo,d)
    out=[]
    for l,r,dslope in ((F(0),d/2,Dhi),(d/2,d,Dlo)):
        aa=F(q)-dslope*d/2-plo
        bb=F(dslope)-s-F(K)*d/2
        def f(x):return aa+bb*x+F(K,2)*x*x
        cand=[f(l),f(r)]
        v=-bb/K
        if l<v<r:cand.append(f(v))
        out.append(min(cand))
    res=min(out)
    return res.numerator//res.denominator

def check_lens(d,source_r=None):
    if d.get('physical_provider_admitted') is not False or d.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('bad scientific claims')
    if d.get('status')!='PASS_POSITIVE_FOR_ENTIRE_APERTURE_BAND':raise ValueError('unproved status')
    if d.get('unknown_subbands')!=[]:raise ValueError('unresolved subbands')
    K=d['uniform_P_second_derivative_abs_integer_Msun_per_kpc2']
    if type(K) is not int or K<=0:raise ValueError('bad K')
    a=F(*map(int,d['A_band_left_exact_n_over_d']));b=F(*map(int,d['A_band_right_exact_n_over_d']))
    if not 0<a<b<120:raise ValueError('band geometry')
    lst=d['positive_subbands']
    if not lst:raise ValueError('missing panels')
    ordered=sorted(lst,key=lambda x:get_f(x,'left'))
    if get_f(ordered[0],'left')!=a or get_f(ordered[-1],'right')!=b:raise ValueError('end coverage')
    low=None
    for j,w in enumerate(ordered):
        l,r=get_f(w,'left'),get_f(w,'right')
        if j and l!=get_f(ordered[j-1],'right'):raise ValueError('panel gap/overlap')
        if source_r and any(l<node<r for node in source_r):raise ValueError('crosses source cusp node')
        z=exact_panel_floor(w,K)
        if z!=w['gap_lower_floor_Msun'] or z<=0:raise ValueError('false interval lower')
        low=z if low is None else min(low,z)
    if low!=d['minimum_gap_lower_floor_Msun']:
        raise ValueError('minimum gap statement mismatch')
    if d['certification_attempts']<len(ordered):
        raise ValueError('attempt count smaller than certified leaves')
    return low

def validate(obj,source_radii=None):
    if obj.get('schema')!='HIST001D_MARCH180_SIX_CROSSING_APERTURE_BANDS_CONDITIONAL_V1':raise ValueError('schema')
    if obj.get('physical_provider_admitted') is not False or obj.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('science status')
    if obj.get('original_off_grid_H_root_count_proved') is not False or obj.get('same_source_physical_lensing_proved') is not False:raise ValueError('root/physical promotion')
    rows=obj.get('lenses',[])
    if len(rows)!=6 or tuple(x['lens'] for x in rows)!=LENSES:raise ValueError('lens set/order')
    results=[]
    for r in rows:
        rad=source_radii[r['lens']] if source_radii else None
        results.append(check_lens(r,rad))
    if obj.get('all_six_crossing_aperture_bands_positive') is not True:raise ValueError('false summary')
    return min(results)

def adversarial(obj,source_radii):
    cases=[]
    def bad(name,fun):
        x=copy.deepcopy(obj);fun(x)
        try:validate(x,source_radii)
        except (ValueError,TypeError,KeyError,ZeroDivisionError):cases.append({'case':name,'rejected':True});return
        raise AssertionError('false claim accepted: '+name)
    bad('missing_lens',lambda x:x['lenses'].pop())
    bad('duplicate_lens',lambda x:x['lenses'][1].update(lens=x['lenses'][0]['lens']))
    bad('reversed_order',lambda x:x['lenses'].reverse())
    bad('physical_provider',lambda x:x.update(physical_provider_admitted=True))
    bad('empirical_validation',lambda x:x.update(empirical_validation='VALIDATED'))
    bad('false_full_root_theorem',lambda x:x.update(original_off_grid_H_root_count_proved=True))
    bad('false_physical_lensing',lambda x:x.update(same_source_physical_lensing_proved=True))
    bad('missing_subband',lambda x:x['lenses'][0]['positive_subbands'].pop(0))
    bad('duplicate_subband',lambda x:x['lenses'][0]['positive_subbands'].append(copy.deepcopy(x['lenses'][0]['positive_subbands'][-1])))
    bad('changed_gap',lambda x:x['lenses'][0]['positive_subbands'][0].update(gap_lower_floor_Msun=999999999999))
    bad('changed_P_endpoint_upper',lambda x:x['lenses'][0]['positive_subbands'][0].update(P_right_upper_integer=0))
    bad('negative_K',lambda x:x['lenses'][0].update(uniform_P_second_derivative_abs_integer_Msun_per_kpc2=-1))
    bad('unknown_subband',lambda x:x['lenses'][0]['unknown_subbands'].append({'status':'UNKNOWN'}))
    bad('false_summary',lambda x:x.update(all_six_crossing_aperture_bands_positive=False))
    bad('corrupt_aperture_edge',lambda x:x['lenses'][0]['A_band_left_exact_n_over_d'].__setitem__(0,'0'))
    bad('corrupt_order',lambda x:x['lenses'][0]['positive_subbands'][0].update(left_n='0'))
    return cases

def main():
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--negative-output',type=Path);args=p.parse_args()
    obj=json.loads(args.receipt.read_text());m=validate(obj)
    print('WITNESS_GEOMETRY_AND_ARITHMETIC_PASS',len(obj['lenses']),'MIN_FLOOR',m)
    if args.negative_output:
        a=adversarial(obj,None)
        args.negative_output.write_text(json.dumps({'cases':a,'all_rejected':True,'scientific_promotion':False},sort_keys=True,indent=2)+'\n')
        print('ADVERSARIAL',len(a),'REJECTED')
if __name__=='__main__':main()
