#!/usr/bin/env python3
"""HIST001D source-locked decomposition of the March180 K180/smooth projection discrepancy.

Mathematical and nonpromoting only. Inherits (does NOT rederive) 512-bit
all-node Bessel derivative intervals and the selected mathematical continuum
P*(A) fixed-aperture enclosures. New result is exact rational kernel
accumulation of the signed nodal Qstored-QsampledDerivative term, with
whole crossing aperture band coverage and independent witness checks.
"""
from __future__ import annotations
import hashlib, io, json, math, struct, zipfile, time, argparse
from fractions import Fraction as F
from pathlib import Path

PARENT_46PLUS3 = 'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
UPSTREAM_SHA = 'd853e4184a570bb1de508658a53ac83eb2d12244b0b14699c14c314448cac5e5'
POINT_SHA = '54eeec715a8f2b9514b88d7806cef84cb90aea54cdada0e0c11bf9489362051e'
BAND_SHA = 'cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77'
LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')

def sha(b):return hashlib.sha256(b).hexdigest()
def floor(x):return x.numerator//x.denominator
def ceil(x):return -((-x.numerator)//x.denominator)
def fbin(x):return F.from_float(x)

def authenticated_zip(path, expected):
    data=Path(path).read_bytes()
    if sha(data)!=expected:raise ValueError('incorrect protected archive SHA '+str(path))
    z=zipfile.ZipFile(io.BytesIO(data))
    mf=json.loads(z.read('MANIFEST_SHA256.json'))
    if sorted(mf['files'])!=sorted(x for x in z.namelist() if x!='MANIFEST_SHA256.json'):raise ValueError('protected manifest inventory mismatch')
    for name,expected_digest in mf['files'].items():
        if sha(z.read(name))!=expected_digest:raise ValueError('archive member SHA mismatch '+name)
    if z.testzip() is not None:raise ValueError('CRC error')
    return z

def authenticated_nested(z,bytes_path):
    return zipfile.ZipFile(io.BytesIO(z.read(bytes_path)))

def phi_interval(A,r,bits=104):
    """Rational exact outward bounds for 1-sqrt(1-A²/r²)."""
    if r<=0 or A<0:raise ValueError('positive radius and nonnegative aperture')
    if A>=r:return F(1),F(1)
    if A==0:return F(0),F(0)
    v=F(1)-(A/r)**2
    scale=1<<bits
    integer=math.isqrt((v.numerator<<(2*bits))//v.denominator)
    check=integer*integer*v.denominator == v.numerator<<(2*bits)
    root_lower=F(integer,scale)
    root_upper=F(integer if check else integer+1,scale)
    if not root_lower**2 <= v <= root_upper**2:
        raise ValueError('UNRESOLVED: square-root cylinder interval failed outward enclosure')
    pL,pU=F(1)-root_upper,F(1)-root_lower
    if not F(0)<=pL<=pU<=F(1):raise ValueError('UNRESOLVED: invalid cylinder kernel enclosure')
    return pL,pU

def signed_node_interval(Alo,Ahi,r,w,err):
    if not 0<=Alo<=Ahi:raise ValueError('nonnegative ordered band')
    if not r or len(r)!=len(w) or len(r)!=len(err):
        raise ValueError('UNRESOLVED: signed stencil source node/weight/interval length mismatch')
    lo=hi=F(0)
    for x,weight,(el,eu) in zip(r,w,err):
        if not weight>0 or el>eu:raise ValueError('positive frozen weights / signed interval order')
        pl=phi_interval(Alo,x)[0]
        pu=phi_interval(Ahi,x)[1]
        candidates=(el*pl,el*pu,eu*pl,eu*pu)
        lo+=weight*min(candidates)
        hi+=weight*max(candidates)
    if lo>hi:raise ValueError('UNRESOLVED: inverted signed stencil sum interval')
    return lo,hi

def rat_tuple(q):return [str(q.numerator),str(q.denominator)]
def from_pair(p):return F(int(p[0]),int(p[1]))

def load_data(upstream_path, point_path, band_path):
    upstream=authenticated_zip(upstream_path,UPSTREAM_SHA)
    point=authenticated_zip(point_path,POINT_SHA)
    band=authenticated_zip(band_path,BAND_SHA)
    upstream_receipt=json.loads(upstream.read('results/upstream_float_split_v1.json'))
    if upstream_receipt['all_source_shadow_density_nodes_reproduced_bitwise']!=1080 or len(upstream_receipt['lenses'])!=6:
        raise ValueError('upstream source identity/verification missing')
    source_archive=authenticated_nested(upstream,'inputs/saturation_parent.zip')
    sat_man=json.loads(source_archive.read('MANIFEST_SHA256.json'))
    for p,sh in sat_man['files'].items():
        if sha(source_archive.read(p))!=sh:raise ValueError('saturation parent member '+p)
    all180=authenticated_nested(source_archive,'all180_parent.zip')
    all180_man=json.loads(all180.read('MANIFEST_SHA256.json'))
    for p,sh in all180_man['files'].items():
        if sha(all180.read(p))!=sh:raise ValueError('all180 parent member '+p)
    rootparent=authenticated_nested(source_archive,'original_parent.zip')
    frozen=authenticated_nested(rootparent,'inputs/frozen_source_parent.zip')
    ds=authenticated_nested(frozen,'inputs/original_march_D120_q_parent.zip')
    orig=authenticated_nested(ds,'inputs/original_march180_parent_v1r1.zip')
    lock=json.loads(orig.read('inputs/original_46plus3_lock.json'))
    if lock['original_46plus3_composite_sha256']!=PARENT_46PLUS3:raise ValueError('46+3 SHA')
    captures=json.loads(orig.read('results/source180_capture.json'))['lenses']
    points=json.loads(point.read('results/root_fixed_A_certificate.json'))['lenses']
    bands=json.loads(band.read('results/whole_band_certificate.json'))['lenses']
    if tuple(x['lens_id'] for x in captures)!=LENSES or tuple(x['lens'] for x in points)!=LENSES or tuple(x['lens'] for x in bands)!=LENSES:
        raise ValueError('lens count/identity/alignment')
    data=[]
    for i,c in enumerate(captures):
        source=c['lens_id']
        raw=orig.read('inputs/'+c['node_file'])
        if len(raw)!=180*64 or sha(raw)!=c['node_sha256']:raise ValueError('source original node SHA')
        rows=list(struct.iter_unpack('>8d',raw))
        intervals=json.loads(all180.read('results/all180_rational_'+source.replace('+','p')+'.json'))
        if intervals['source_180_node_sha256']!=c['node_sha256'] or intervals['original_46plus3_source_composite_sha256']!=PARENT_46PLUS3 or not intervals['all_180_ideal_stencil_discrepancies_certified']:
            raise ValueError('signed derivative source certificate identity')
        ee=intervals['source_gradient_minus_smooth_Mprime_interval_integer_msun_per_kpc']
        if len(ee)!=180 or any(len(v)!=2 or not all(type(x)==int for x in v) or v[0]>v[1] for v in ee):raise ValueError('invalid node derivative array')
        rr=[fbin(a[0]) for a in rows];ww=[fbin(a[1]) for a in rows]
        if any(rr[k]>=rr[k+1] for k in range(179)) or min(ww)<=0:raise ValueError('source mesh')
        pp=points[i]
        if pp['original_source_180_nodes_sha256']!=c['node_sha256']:raise ValueError('point source identity')
        A=fbin(float.fromhex(pp['aperture_selected_diagnostic_binary64_hex']))
        bandrec=bands[i]
        if bandrec['original_180_source_node_sha256']!=c['node_sha256'] or not bandrec['status'].startswith('PASS'):
            raise ValueError('band signed source identity')
        left=from_pair(bandrec['A_band_left_exact_n_over_d']);right=from_pair(bandrec['A_band_right_exact_n_over_d'])
        if not 0<left<A<right<rr[-1]:raise ValueError('diagnostic aperture outside source crossing band')
        prev=upstream_receipt['lenses'][i]
        if prev['lens_id']!=source or prev['original_node_sha256']!=c['node_sha256']:
            raise ValueError('previous upstream lens identity')
        prior_micro=prev['inherited_512bit_full_all180_source_vs_selected_math_stencil_all_apertures_micro_Msun_upper']
        if not (isinstance(prior_micro,int) and 0<prior_micro<10_000_000):
            raise ValueError('previous ideal-M stencil bound missing')
        data.append((source,rr,ww,[(F(l),F(u)) for l,u in ee],A,pp,bandrec,left,right,c['node_sha256'],prior_micro))
    return data

def certify_one(d, max_depth=18, max_panels=4000):
    source,rr,ww,errs,A,pp,band,L,U,nodesha,prior_micro=d
    l,u=signed_node_interval(A,A,rr,ww,errs)
    tlo,thi=pp['Q_March_minus_P_selected_continuum_interval_integer_Msun']
    # Rigorous signed continuum-integration quadrature remainder by exact interval subtraction.
    rlo,rhi=F(tlo)-u,F(thi)-l
    prior=F(prior_micro,10**6)
    ideal_lo,ideal_hi=l-prior,u+prior
    if not l>0:raise ValueError('finite-difference point bias sign not proved')
    status='POSITIVE' if rlo>0 else 'NEGATIVE' if rhi<0 else 'UNRESOLVED'
    panels=[];unknown=[]
    # Fully cover the original crossing band. Interval kernel monotone with aperture.
    def go(a,b,depth):
        if len(panels)+len(unknown)>max_panels:raise ValueError('subband budget exceeded')
        low,high=signed_node_interval(a,b,rr,ww,errs)
        if low>0:
            panels.append({'lower':rat_tuple(a),'upper':rat_tuple(b),'depth':depth,
                           'node_bias_lower_floor_Msun':floor(low),
                           'node_bias_upper_ceil_Msun':ceil(high)});return
        if depth>=max_depth:
            unknown.append({'lower':rat_tuple(a),'upper':rat_tuple(b),'depth':depth,
                            'node_bias_lower_floor_Msun':floor(low),
                            'node_bias_upper_ceil_Msun':ceil(high)});return
        mid=(a+b)/2
        go(a,mid,depth+1);go(mid,b,depth+1)
    go(L,U,0)
    if unknown:print('UNRESOLVED',source,len(unknown),flush=True)
    return {'lens':source,'node_sha256':nodesha,
            'A_diagnostic_hex':float(A).hex(),
            'A_band_left_rational':rat_tuple(L),'A_band_right_rational':rat_tuple(U),
            'Q_source_minus_Q_sampled_exact_Mprime_integer_Msun':[floor(l),ceil(u)],
            'inherited_source_vs_ideal_MassStencil_all_aperture_micro_Msun_upper':prior_micro,
            'Q_ideal_MassStencil_minus_Q_sampled_exact_Mprime_integer_Msun':[floor(ideal_lo),ceil(ideal_hi)],
            'Q_source_minus_continuum_Pstar_prior_integer_Msun':[tlo,thi],
            'Q_sampled_exact_Mprime_minus_continuum_Pstar_integer_Msun':[floor(rlo),ceil(rhi)],
            'quadrature_remainder_sign_at_diagnostic':status,
            'node_bias_strictly_positive_at_diagnostic':l>0,
            'node_bias_full_band_positive':not unknown,
            'node_bias_full_band_min_lower_Msun':min((p['node_bias_lower_floor_Msun'] for p in panels), default=None),
            'ideal_mass_stencil_bias_full_band_min_lower_Msun':min((p['node_bias_lower_floor_Msun'] for p in panels), default=0)-ceil(prior),
            'panel_count':len(panels),'unknown_count':len(unknown),'panels':panels,'unknown':unknown,
            'selected_smooth_Mstar_physical_provider':False,
            'empirical_validation':'NOT_ESTABLISHED'}

def run(upstream,point,band,out,max_depth=18):
    data=load_data(upstream,point,band)
    result=[];tt=time.monotonic()
    for x in data:
        st=time.monotonic();r=certify_one(x,max_depth=max_depth)
        result.append(r)
        print(x[0],'point bias',r['Q_source_minus_Q_sampled_exact_Mprime_integer_Msun'],'continuous quadrature',r['Q_sampled_exact_Mprime_minus_continuum_Pstar_integer_Msun'], 'sign',r['quadrature_remainder_sign_at_diagnostic'],'panels',r['panel_count'],'unknown',r['unknown_count'],'seconds',round(time.monotonic()-st,2),flush=True)
    aggregate={'schema':'HIST001D_MARCH180_K180_SIGNED_STENCIL_VS_SAMPLED_DERIVATIVE_VS_CONTINUUM_V1',
               'original_46plus3_source_sha256':PARENT_46PLUS3,
               'parent_upstream_sha256':UPSTREAM_SHA,'parent_fixed_A_sha256':POINT_SHA,'parent_six_band_sha256':BAND_SHA,
               'inherited_512bit_Bessel_all180_derivative_enclosure':True,
               'independent_new_Bessel_engine_in_this_packet':False,
               'source_continuum_is_selected_mathematical_Mstar_not_physical':True,
               'full_H_physical_root_count_or_weyl_proved':False,'physical_provider_admitted':False,
               'empirical_validation':'NOT_ESTABLISHED',
               'all_six_pointwise_bias_positive':all(x['node_bias_strictly_positive_at_diagnostic'] for x in result),
               'all_six_bandwise_bias_positive':all(x['node_bias_full_band_positive'] for x in result),
               'all_six_fixed_A_quadrature_remainder_sign_resolved':all(x['quadrature_remainder_sign_at_diagnostic']!='UNRESOLVED' for x in result),
               'lenses':result}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(aggregate,sort_keys=True,indent=2)+'\n')
    print('COMPLETE',len(result),'seconds',round(time.monotonic()-tt,2),'sha',sha(out.read_bytes()),flush=True)
    return aggregate

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--upstream',type=Path,required=True);ap.add_argument('--point',type=Path,required=True);ap.add_argument('--band',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--max-depth',type=int,default=18)
    a=ap.parse_args();run(a.upstream,a.point,a.band,a.out,a.max_depth)
