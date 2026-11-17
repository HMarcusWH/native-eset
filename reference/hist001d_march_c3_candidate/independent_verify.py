#!/usr/bin/env python3
"""Independent unimported verifier of exact-rational M2/M3 derivative upper bounds.

Uses an alternative Bessel K half-integer recurrence, 96-bit directed sqrt,
manual IEEE754 source R decoder, and independently recomputed 179 source cells.
This does NOT check original float-operation errors or physical/model admission.
"""
from __future__ import annotations
from fractions import Fraction as Q
from math import comb,factorial,isqrt
import hashlib,io,json,zipfile,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHA='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
SOURCE='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
ORIGINAL_ZIP='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
def sha(b):return hashlib.sha256(b).hexdigest()
def round_up(x):return -(-x.numerator//x.denominator)

def ieee_binary64(x:bytes)->Q:
    z=int.from_bytes(x,'big');sgn=(-1 if z>>63 else 1)
    e=(z>>52)&2047; mant=z&((1<<52)-1)
    if e==2047:raise ValueError('nonfinite original source byte')
    if e==0:
        sig=mant;power=-1022-52
    else:
        sig=(1<<52)|mant;power=e-1023-52
    return Q(sgn*sig*2**power) if power>=0 else Q(sgn*sig,2**(-power))

def sqrt_up_rational(x:Q)->Q:
    if x<=0:raise ValueError('positive square root contract')
    d=2**96;v=isqrt((x.numerator*d*d)//x.denominator)
    return Q(v if Q(v,d)**2==x else v+1,d)

def half_polynomials(inv:Q):
    # K_(j+1/2)=sqrt(pi/(2y))*exp(-y)*P_j(inv),
    # P0=1, P1=1+inv, P_(j+1)=P_(j-1)+(2j+1)*inv*P_j.
    p=[Q(1),Q(1)+inv]
    for j in range(1,4):p.append(p[j-1]+(2*j+1)*inv*p[j])
    return p

def independent_mass_bounds(lo:Q,hi:Q,p:dict):
    Mb,Md,a,Rd,delta,rzero,n=(p[k] for k in ('Mb','Md','a','Rd','delta','r0','n'))
    if not (0<lo<hi and min(Mb,Md,a,Rd,rzero)>0 and 0<delta<1 and 4<n<5):
        raise ValueError('invalid source identity/domain')
    x=lo/(2*Rd); X=hi/(2*Rd)
    t=half_polynomials(1/x)
    U=sqrt_up_rational(Q(11,7)/x)  # pi/(2x) < 11/(7x)
    Fbound=[]
    for k in range(4):
        val=Q(0)
        for ell in range(k+1):
            val+=comb(k,ell)*(t[ell]+t[ell+1])
        Fbound.append(val*U)
    d=[]
    for k in range(4):
        bd=Q(0)
        for z in range(min(k,3)+1):
            bd+=Q(comb(k,z)*factorial(3),factorial(3-z))*X**(3-z)*Fbound[k-z]
        d.append(Md*bd/(2*Rd)**k)
    b=[Mb,2*Mb*a*hi/(lo+a)**3,2*Mb*a*(a+2*hi)/(lo+a)**4,
       12*Mb*a*(a+hi)/(lo+a)**5]
    A=[x+y for x,y in zip(b,d)]
    fmax=(hi/rzero)**4 if hi<=rzero else Q(1)
    if lo>=rzero:pmax=min(Q(1,4),(rzero/lo)**4)
    elif hi<=rzero:pmax=min(Q(1,4),(hi/rzero)**4)
    else:pmax=Q(1,4)
    eps=1-delta*fmax
    if not (eps>0 and pmax>0):raise ValueError('invalid bound')
    f1=n*pmax/lo
    f2=n*pmax*(n+1)/lo**2
    f3=n*pmax*((n+1)*(n+2)+2*n*n*pmax)/lo**3
    v1=delta/eps**2;v2=2*delta**2/eps**3;v3=6*delta**3/eps**4
    B=[delta*fmax/eps, v1*f1, v2*f1*f1+v1*f2,
       v3*f1**3+3*v2*f1*f2+v1*f3]
    return (A[2]*B[0]+2*A[1]*B[1]+A[0]*B[2],
            A[3]*B[0]+3*A[2]*B[1]+3*A[1]*B[2]+A[0]*B[3])

def verify(candidate=None,write=True):
    parent=ROOT/'inputs/frozen_smooth_shadow_gradient_parent.zip'
    if sha(parent.read_bytes())!=SHA:raise ValueError('parent hash mismatch')
    z0=zipfile.ZipFile(parent)
    z1=zipfile.ZipFile(io.BytesIO(z0.read('inputs/frozen_source_parent.zip')))
    z2=zipfile.ZipFile(io.BytesIO(z1.read('inputs/original_march_D120_q_parent.zip')))
    z3=zipfile.ZipFile(io.BytesIO(z2.read('inputs/original_march180_parent_v1r1.zip')))
    original=z3.read('inputs/original_source_46_frozen.zip')
    if sha(original)!=ORIGINAL_ZIP:raise ValueError('original March ZIP tampered')
    src=zipfile.ZipFile(io.BytesIO(original))
    lk=json.loads(z3.read('inputs/original_46plus3_lock.json'))
    if lk['original_46plus3_composite_sha256']!=SOURCE or len(lk['source_filenames_sha256'])!=46 or len(lk['archived_negative_controls_sha256'])!=3:raise ValueError('source lock')
    for path,digest in lk['source_filenames_sha256'].items():
        if sha(src.read('swells_pack_v2/'+path))!=digest:raise ValueError('modified source:'+path)
    for path,digest in lk['archived_negative_controls_sha256'].items():
        if sha(z3.read('inputs/negative_controls/'+path))!=digest:raise ValueError('modified negative:'+path)
    old=json.loads(z3.read('results/source180_capture.json'))
    smooth=json.loads(z0.read('results/producer_analytic_source_gradient.json'))
    given=candidate if candidate is not None else json.loads((ROOT/'results/source_bound_M2_M3_rational_producer.json').read_bytes())
    claims_false=['float_operation_error_certified','original_March_total_H_or_root_count_certified',
                 'source_offgrid_clip_branch_certified','D2d_11520_shadow_substituted',
                 'source_true_continuum_gradient_error_certified','full_H_root_error_guard_met',
                 'physical_provider_admitted']
    if (given.get('schema')!='HIST001D_ORIGINAL_MARCH_MSH_BESSEL_HALF_INTEGER_EXACT_M2_M3_UPPER_V1'
        or given.get('scientific_scope')!='SMOOTH_HISTORICAL_SOURCE_MATHEMATICAL_EXTENSION_ONLY'
        or given.get('parent_sha256')!=SHA or given.get('source_sha256')!=SOURCE
        or any(given.get(k) is not False for k in claims_false)
        or given.get('empirical_validation')!='NOT_ESTABLISHED'
        or given.get('external_mathematical_review')!='NOT_DONE'
        or given.get('subdivisions_per_original_cell')!=4
        or given.get('mathematical_derivative_supremum_status')!='EXACT_CONSERVATIVE_RATIONAL_UPPER_CANDIDATE'):
        raise ValueError('scientific claim or identity tamper')
    if any(len(x['lenses'])!=6 for x in (given,old,smooth)):raise ValueError('lens inventory')
    result={'schema':'HIST001D_MSH_EXACT_M2_M3_INDEPENDENT_RATIONAL_96BIT_V1',
            'source_46plus3_verified':True,'verified_full_lenses':6,'verified_180_cells_per_lens':179,
            'source_mathematical_smooth_only':True,'floating_source_error_certified':False,
            'actual_historical_continuum_root_count_certified':False,
            'physical_provider_admitted':False,'lenses':[]}
    for j,declared in enumerate(given['lenses']):
        ol=old['lenses'][j];sl=smooth['lenses'][j]
        if not declared['lens_id']==ol['lens_id']==sl['lens_id'] or declared['source_node_sha256']!=ol['node_sha256'] or declared['source_scalar_hex']!=sl['source_scalar_binary64_hex']:
            raise ValueError('lens source and exact scalar declaration mismatch')
        raw=z3.read('inputs/'+ol['node_file'])
        if sha(raw)!=ol['node_sha256'] or len(raw)!=180*8*8:raise ValueError('source node tamper')
        RR=[ieee_binary64(raw[i*64:i*64+8]) for i in range(180)]
        p={k:ieee_binary64(struct.pack('>d',float.fromhex(sl['source_scalar_binary64_hex'][k])))
            for k in ('Mb','Md','a','Rd','delta','r0','n')}
        # Separate 96-bit half-polynomial recurrence; all 4 subcells of each original source cell.
        caps2=[];caps3=[]
        for i in range(179):
            lo,hi=RR[i:i+2];h=(hi-lo)/4
            point=[independent_mass_bounds(lo+h*k,lo+h*(k+1),p) for k in range(4)]
            cap2=max(x[0] for x in point);cap3=max(x[1] for x in point)
            caps2.append(cap2);caps3.append(cap3)
            if cap2>int(declared['M2_by_cell_upper_ceil'][i]) or cap3>int(declared['M3_by_cell_upper_ceil'][i]):
                raise ValueError('producer derivative bound underestimated at source cell '+str(i))
        gradients=[(RR[1]-RR[0])*caps2[0]/2]
        for i in range(1,179):
            gradients.append((RR[i]-RR[i-1])*(RR[i+1]-RR[i])/6 *max(caps3[i-1],caps3[i]))
        gradients.append((RR[-1]-RR[-2])*caps2[-1]/2)
        for i,c in enumerate(gradients):
            if c>int(declared['ideal_exact_sample_gradient_error_upper_ceil'][i]):
                raise ValueError('producer ideal-gradient bound underestimated '+str(i))
        max2=max(caps2);max3=max(caps3);maxE=max(gradients)
        if any(x>int(declared[key]) for x,key in [(max2,'global_M2_upper_ceil'),(max3,'global_M3_upper_ceil'),
                                                   (maxE,'max_exact_gradient_error_upper_ceil'),
                                                   (gradients[0],'first_exact_gradient_error_upper_ceil'),
                                                   (gradients[-1],'last_exact_gradient_error_upper_ceil')]):
            raise ValueError('global/edge aggregate bound underestimated')
        result['lenses'].append({'lens_id':declared['lens_id'],'independent_real_cell_count':179,
            'number_of_checked_source_gradient_nodes':180,
            'independent_M2_cap_ceiling':str(round_up(max2)),
            'independent_M3_cap_ceiling':str(round_up(max3)),
            'independent_gradient_error_cap_ceiling':str(round_up(maxE)),
            'all_producer_caps_conservative':True})
        print('INDEPENDENT_M2_M3_PASS',declared['lens_id'],flush=True)
    if write:
        outfile=ROOT/'results/independent_M2_M3_envelope.json'
        outfile.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        print('INDEPENDENT_JSON_SHA256',sha(outfile.read_bytes()))
    return result
if __name__=='__main__':verify()
