#!/usr/bin/env python3
"""Independent source-conditional exact-arithmetic witness for HIST001D split.

Does not import the producer, any Bessel implementation, NumPy or SciPy.
Manually decodes binary64 and computes outward square-root bounds using
integer bisection (not math.isqrt). Rechecks each frozen source list, each
signed derivative interval, all fixed aperture bias/continuum remainder
integers, and all whole-band witness intervals. Does not independently prove
the inherited all-node Bessel or continuum interval algorithms.
"""
import argparse,hashlib,io,json,struct,zipfile
from pathlib import Path
from fractions import Fraction as F

EXPECTED={
'upstream':'d853e4184a570bb1de508658a53ac83eb2d12244b0b14699c14c314448cac5e5',
'point':'54eeec715a8f2b9514b88d7806cef84cb90aea54cdada0e0c11bf9489362051e',
'band':'cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77',
}
LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')
def sha(b):return hashlib.sha256(b).hexdigest()
def check_zip(path,hashvalue):
    b=Path(path).read_bytes()
    if sha(b)!=hashvalue:raise ValueError('incorrect parent archive digest '+str(path))
    z=zipfile.ZipFile(io.BytesIO(b));m=json.loads(z.read('MANIFEST_SHA256.json'))
    if sorted(z.namelist())!=sorted(['MANIFEST_SHA256.json']+list(m['files'])):raise ValueError('unexpected ZIP member')
    for fn,h in m['files'].items():
        if sha(z.read(fn))!=h:raise ValueError('modified protected ZIP member '+fn)
    if z.testzip() is not None:raise ValueError('bad ZIP CRC')
    return z

def decoded_binary64(raw):
    if len(raw)!=8:raise ValueError('binary64 length')
    u=int.from_bytes(raw,'big');sign=-1 if u>>63 else 1
    exponent=(u>>52)&2047;fraction=u&((1<<52)-1)
    if exponent==2047:raise ValueError('nonfinite binary64')
    if exponent==0:
        mantissa=fraction;power=-1074
    else:
        mantissa=(1<<52)+fraction;power=exponent-1075
    if power>=0:return sign*F(mantissa<<power)
    return sign*F(mantissa,1<<(-power))

def sqrt_outward(v,bits=84):
    if v<0 or v>1:raise ValueError('sqrt test domain')
    num=v.numerator<<(2*bits);den=v.denominator
    lo=0;hi=(1<<bits)+1
    while lo+1<hi:
        mid=(lo+hi)//2
        if mid*mid*den <= num:lo=mid
        else:hi=mid
    if not lo*lo*den <= num < (lo+1)*(lo+1)*den:
        raise ValueError('UNRESOLVED: independent integer-bisection square root floor invalid')
    cap=lo if lo*lo*den==num else lo+1
    low=F(lo,1<<bits);up=F(cap,1<<bits)
    if not low*low <= v <= up*up:
        raise ValueError('UNRESOLVED: independent square root outward interval invalid')
    return low,up

def phi_box(a,r):
    if a<=0:return F(0),F(0)
    if a>=r:return F(1),F(1)
    sr=sqrt_outward(1-a*a/(r*r));return F(1)-sr[1],F(1)-sr[0]

def box_sum(r,w,e,left,right):
    if not r or len(r)!=len(w) or len(r)!=len(e):
        raise ValueError('UNRESOLVED: independent signed stencil list length mismatch')
    lower=upper=F(0)
    for j in range(len(r)):
        e0,e1=e[j];p0=phi_box(left,r[j])[0];p1=phi_box(right,r[j])[1]
        vals=(e0*p0,e1*p0,e0*p1,e1*p1)
        lower+=w[j]*min(vals);upper+=w[j]*max(vals)
    return lower,upper

def pair(x):return F(int(x[0]),int(x[1]))
def floor(x):return x.numerator//x.denominator
def ceil(x):return -((-x.numerator)//x.denominator)

def check(upstream,point,band,receipt_path):
    us=check_zip(upstream,EXPECTED['upstream']);ps=check_zip(point,EXPECTED['point']);bs=check_zip(band,EXPECTED['band'])
    recorded=json.loads(Path(receipt_path).read_bytes())
    if recorded.get('schema')!='HIST001D_MARCH180_K180_SIGNED_STENCIL_VS_SAMPLED_DERIVATIVE_VS_CONTINUUM_V1' or len(recorded['lenses'])!=6:raise ValueError('receipt schema/count')
    if (recorded.get('original_46plus3_source_sha256')!='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a' or
            recorded.get('parent_upstream_sha256')!=EXPECTED['upstream'] or
            recorded.get('parent_fixed_A_sha256')!=EXPECTED['point'] or
            recorded.get('parent_six_band_sha256')!=EXPECTED['band']):
        raise ValueError('receipt parent source hash chain')
    if (recorded.get('inherited_512bit_Bessel_all180_derivative_enclosure') is not True or
            recorded.get('independent_new_Bessel_engine_in_this_packet') is not False or
            recorded.get('source_continuum_is_selected_mathematical_Mstar_not_physical') is not True or
            recorded.get('full_H_physical_root_count_or_weyl_proved') is not False):
        raise ValueError('receipt mathematical scope incorrect')
    sat=zipfile.ZipFile(io.BytesIO(us.read('inputs/saturation_parent.zip')))
    all180=zipfile.ZipFile(io.BytesIO(sat.read('all180_parent.zip')))
    orig_parent=zipfile.ZipFile(io.BytesIO(sat.read('original_parent.zip')))
    froz=zipfile.ZipFile(io.BytesIO(orig_parent.read('inputs/frozen_source_parent.zip')))
    d=zipfile.ZipFile(io.BytesIO(froz.read('inputs/original_march_D120_q_parent.zip')))
    o=zipfile.ZipFile(io.BytesIO(d.read('inputs/original_march180_parent_v1r1.zip')))
    cap=json.loads(o.read('results/source180_capture.json'))['lenses']
    prior_upstream=json.loads(us.read('results/upstream_float_split_v1.json'))['lenses']
    pl=json.loads(ps.read('results/root_fixed_A_certificate.json'))['lenses']
    bl=json.loads(bs.read('results/whole_band_certificate.json'))['lenses']
    if (tuple(x['lens_id'] for x in cap)!=LENSES or tuple(x['lens'] for x in recorded['lenses'])!=LENSES
        or tuple(x['lens'] for x in pl)!=LENSES or tuple(x['lens'] for x in bl)!=LENSES):raise ValueError('source inventory')
    report=[]
    for i,name in enumerate(LENSES):
        src=cap[i];rpt=recorded['lenses'][i]
        raw=o.read('inputs/'+src['node_file'])
        if sha(raw)!=src['node_sha256'] or rpt['node_sha256']!=src['node_sha256'] or len(raw)!=180*64:raise ValueError('source node SHA')
        r=[decoded_binary64(raw[k*64:k*64+8]) for k in range(180)]
        w=[decoded_binary64(raw[k*64+8:k*64+16]) for k in range(180)]
        if min(w)<=0:raise ValueError('source weights')
        ee=json.loads(all180.read('results/all180_rational_'+name.replace('+','p')+'.json'))
        e=[(F(x[0]),F(x[1])) for x in ee['source_gradient_minus_smooth_Mprime_interval_integer_msun_per_kpc']]
        if len(e)!=180 or any(x>y for x,y in e):raise ValueError('signed intervals')
        A=decoded_binary64(struct.pack('>d',float.fromhex(rpt['A_diagnostic_hex'])))
        L=pair(rpt['A_band_left_rational']);U=pair(rpt['A_band_right_rational'])
        if not 0<L<A<U<r[-1]:raise ValueError('aperture crossing band')
        if (L!=pair(bl[i]['A_band_left_exact_n_over_d']) or U!=pair(bl[i]['A_band_right_exact_n_over_d']) or
                rpt['A_diagnostic_hex']!=pl[i]['aperture_selected_diagnostic_binary64_hex']):
            raise ValueError('original selected aperture band and point identities changed')
        q0,q1=box_sum(r,w,e,A,A)
        saved=rpt['Q_source_minus_Q_sampled_exact_Mprime_integer_Msun']
        if floor(q0)<saved[0] or ceil(q1)>saved[1]:raise ValueError('point stencil bias underestimated')
        prior=pl[i]['Q_March_minus_P_selected_continuum_interval_integer_Msun']
        if prior!=rpt['Q_source_minus_continuum_Pstar_prior_integer_Msun']:raise ValueError('altered prior numerical result')
        rest=(F(prior[0])-q1,F(prior[1])-q0)
        saved_rem=rpt['Q_sampled_exact_Mprime_minus_continuum_Pstar_integer_Msun']
        if floor(rest[0])<saved_rem[0] or ceil(rest[1])>saved_rem[1]:raise ValueError('quadrature remainder underbound')
        panels=rpt['panels']
        if rpt['unknown_count']!=0 or rpt['unknown'] or rpt['panel_count']!=len(panels):raise ValueError('unresolved whole band')
        cursor=L
        for p in panels:
            li,ui=pair(p['lower']),pair(p['upper'])
            if li!=cursor or not li<ui<=U:raise ValueError('band coverage gap/overlap')
            bx=box_sum(r,w,e,li,ui)
            if floor(bx[0])<p['node_bias_lower_floor_Msun'] or ceil(bx[1])>p['node_bias_upper_ceil_Msun']:
                raise ValueError('panel signed bias enclosure underestimated')
            if not bx[0]>0 or not p['node_bias_lower_floor_Msun']>0:raise ValueError('positive band not proved')
            cursor=ui
        if cursor!=U:raise ValueError('band not fully covered')
        if rpt['node_bias_full_band_min_lower_Msun']!=min(p['node_bias_lower_floor_Msun'] for p in panels):raise ValueError('minimum false')
        prev=prior_upstream[i]
        inherited_micro=prev['inherited_512bit_full_all180_source_vs_selected_math_stencil_all_apertures_micro_Msun_upper']
        if prev['lens_id']!=name or rpt['inherited_source_vs_ideal_MassStencil_all_aperture_micro_Msun_upper']!=inherited_micro:
            raise ValueError('inherited mass-stencil budget identity')
        E=F(inherited_micro,10**6)
        ideal=rpt['Q_ideal_MassStencil_minus_Q_sampled_exact_Mprime_integer_Msun']
        if floor(q0-E)<ideal[0] or ceil(q1+E)>ideal[1]:
            raise ValueError('ideal-mass-stencil versus derivative-samples bound understated')
        if rpt['ideal_mass_stencil_bias_full_band_min_lower_Msun']!=rpt['node_bias_full_band_min_lower_Msun']-ceil(E) or rpt['ideal_mass_stencil_bias_full_band_min_lower_Msun']<=0:
            raise ValueError('whole-band strict ideal mass stencil bias not proved')
        if not rpt['node_bias_full_band_positive'] or not rpt['node_bias_strictly_positive_at_diagnostic'] or not q0>0:
            raise ValueError('unsupported claim')
        if (rpt['quadrature_remainder_sign_at_diagnostic']=='POSITIVE')!=(rest[0]>0) or (rpt['quadrature_remainder_sign_at_diagnostic']=='NEGATIVE')!=(rest[1]<0):
            raise ValueError('wrong signed quadrature remainder')
        if rpt['selected_smooth_Mstar_physical_provider'] or rpt['empirical_validation']!='NOT_ESTABLISHED':raise ValueError('physical claim promoted')
        report.append({'lens':name,'source_positive':True,'panels':len(panels),'point_bias_Msun_lower':floor(q0),'point_bias_Msun_upper':ceil(q1),'quadrature_sign':rpt['quadrature_remainder_sign_at_diagnostic']})
    if not recorded['all_six_pointwise_bias_positive'] or not recorded['all_six_bandwise_bias_positive'] or not recorded['all_six_fixed_A_quadrature_remainder_sign_resolved'] or recorded['physical_provider_admitted'] or recorded['empirical_validation']!='NOT_ESTABLISHED':raise ValueError('aggregate claim check failed')
    return {'schema':'HIST001D_INDEPENDENT_SIGNED_BIAS_VERIFY_V1','all_lenses_passed':True,'lenses':report}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for key in ['upstream','point','band','receipt']:
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();res=check(a.upstream,a.point,a.band,a.receipt)
    a.out.write_text(json.dumps(res,sort_keys=True,indent=2)+'\n');print('PASS_INDEPENDENT',len(res['lenses']),sha(a.out.read_bytes()),flush=True)
