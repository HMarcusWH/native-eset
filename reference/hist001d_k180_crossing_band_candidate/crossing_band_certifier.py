#!/usr/bin/env python3
"""NONPROMOTING source-bound candidate: whole crossing-cell K180 / smooth M* gap.

Proves only Q_frozen(A) - P_selected(A) > 0 for every real A in six
source-defined crossing-aperture bands IF all intervals finish with a positive
lower witness. No original H root theorem, physical density, provider or
empirical validation. Original 46+3 source/arrays are protected SHA-locked.
"""
from __future__ import annotations
import argparse,bisect,io,json,time,zipfile,sys,hashlib
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'hist001d_k180_root_aperture_candidate'))
from root_aperture_certifier import (
    Lens,Iv,load_external,load_apertures,euler_gamma,sqrt_outward,
    projected_u,sha,floor,ceil
)

def square_root(q:F)->Iv:
    if q<0:raise ValueError('negative radicand')
    return sqrt_outward(Iv(q))

def q_at_knot(row,q_b:F,q_d:F)->F:
    B=F.from_float(row[4]);D=F.from_float(row[6]);
    if B<=0 or D<=0:raise ValueError('nonpositive historical q baryon terms')
    return (q_b*B+q_d*D)/(B+D)

def q_source_metadata(external:Path):
    # original_parent.zip (and its entire parent hierarchy) is hash verified
    # by the first call to load_external in run().
    with zipfile.ZipFile(external) as outer:
        with zipfile.ZipFile(io.BytesIO(outer.read('original_parent.zip'))) as o:
            with zipfile.ZipFile(io.BytesIO(o.read('inputs/frozen_source_parent.zip'))) as f:
                with zipfile.ZipFile(io.BytesIO(f.read('inputs/original_march_D120_q_parent.zip'))) as d:
                    meta=json.loads(d.read('results/q_aperture_producer.json'))
                    capture=json.loads(d.read('results/source120_capture.json'))
    if meta['schema']!='HIST001D_COMMON180_SOURCE_FROZEN_QEFF_APERTURE_AND_SHADOW_ALLREAL_v1':
        raise ValueError('q theorem metadata schema')
    if len(meta['lenses'])!=len(capture['lenses'])!=6:
        raise ValueError('q theorem lens count')
    for x,y in zip(meta['lenses'],capture['lenses']):
        if x['lens_id'] != y['lens_id'] or x['source_qb_hex']!=y['qb_hex'] or x['source_qd_hex']!=y['qd_hex']:
            raise ValueError('q coefficients not original source')
        if not x['all_real_aperture_unsaturated_strictly_increasing']:
            raise ValueError('q theorem not source-proved')
    return meta['lenses']

def q_monotonic_all_cells(lens:Lens,q_b:F,q_d:F):
    """Independent conservative all-real q/A derivative sign in every source cell.

    q=N/P affine-fractional and 2q-Rq' > 0, checked with exact dyadics.
    """
    qmin=F(1);qmax=F(0);margin=None
    for j in range(len(lens.r)-1):
        r0,r1=lens.r[j:j+2];h=r1-r0
        B0=F.from_float(lens.rows[j][4]); B1=F.from_float(lens.rows[j+1][4])
        D0=F.from_float(lens.rows[j][6]); D1=F.from_float(lens.rows[j+1][6])
        P0=B0+D0; P1=B1+D1; N0=q_b*B0+q_d*D0;N1=q_b*B1+q_d*D1
        if min(P0,P1,N0,N1)<=0:raise ValueError('nonpositive piecewise q source')
        q0=N0/P0; q1=N1/P1
        qmin=min(qmin,q0,q1);qmax=max(qmax,q0,q1)
        C=N1*P0-N0*P1
        dmax=max(F(0),C/(h*min(P0,P1)**2))
        m=2*min(q0,q1)-r1*dmax
        if m<=0:raise ValueError('source q nonmonotonic certificate: '+str(j))
        margin=m if margin is None else min(margin,m)
    if not F(1,1000)<qmin<=qmax<1:raise ValueError('original q clipping not inactive')
    return margin

def band_geometry(lens:Lens,q_b:F,q_d:F,root_R:F):
    i=bisect.bisect_right(lens.r,root_R)-1
    if not 0<=i<len(lens.r)-1:raise ValueError('root outside source knot interior')
    R0,R1=lens.r[i:i+2]
    q0=q_at_knot(lens.rows[i],q_b,q_d);q1=q_at_knot(lens.rows[i+1],q_b,q_d)
    sq0,sq1=square_root(q0),square_root(q1)
    A_lo=R0/sq0.high();A_hi=R1/sq1.low()
    if not lens.r[0]<A_lo<A_hi<lens.r[-1]:raise ValueError('bad unsaturated band')
    return i,R0,R1,A_lo,A_hi

def curvature_upper(lens:Lens,A_lo:F,A_hi:F):
    """Certified integer ceil of max |P*''(A)|, for all A in [A_lo,A_hi].

    Correct identity (A in (rmin,rmax)):
      P''= integral_0^acos(A/b) M''(A secθ) secθ dθ - M'(b)/(b u_b).
    Bound secθ <= sec²θ and integral of sec²θ = tan θ.
    Each original radial cell is enclosed for all real r by sign-monotone F.
    """
    if not lens.r[0]<A_lo<A_hi<lens.r[-1]:raise ValueError('bad curvature range')
    r=[A_lo]+[x for x in lens.r if A_lo<x<lens.r[-1]]+[lens.r[-1]]
    value=0;weights=[];positivity_failures=[]
    for lo,hi in zip(r,r[1:]):
        Mp,Mpp=lens.derivatives(lo,hi)
        if Mp.low()<=0:positivity_failures.append((lo,hi))
        absM2=Mpp.bound_abs()
        if lo>=A_hi:
            # d(A)=sqrt(hi²-A²)-sqrt(lo²-A²) is increasing in A<=lo
            w0=square_root(hi*hi-A_hi*A_hi)
            w1=square_root(lo*lo-A_hi*A_hi)
            upper=(w0.high()-w1.low())/A_lo
        else:
            # A may lie within this radial cell.  The whole possible
            # active segment is bounded by the full [A,hi] tangent span.
            upper=square_root(hi*hi-A_lo*A_lo).high()/A_lo
        if upper<0:raise ValueError('negative geometric upper')
        val=ceil(absM2*upper)
        value+=val;weights.append(val)
    b=lens.r[-1];Mprime_b=lens.point(b)[1].bound_abs()
    ub_min=projected_u(A_hi,b).low()
    if ub_min<=0:raise ValueError('edge cusp touched')
    boundary=ceil(Mprime_b/(b*ub_min))
    return value+boundary,{
        'curvature_cell_count':len(weights),
        'integrated_Mpp_conservative_integer_ceiling':value,
        'boundary_Mprime_conservative_integer_ceiling':boundary,
        'Mprime_positive_count_not_claimed':len(weights)-len(positivity_failures),
        'curvature_worst_five_cell_upper_integer':sum(sorted(weights,reverse=True)[:5]),
    }

def q_and_gradient(lens:Lens,A:F):
    """Q(A) and one-sided (within-node-cell) Q'(A) with outward rationals."""
    v=Iv(0);vp=Iv(0)
    for r,w,rho in zip(lens.r,lens.w,lens.rho):
        mass=w*lens.C4pi*r*r*rho
        if r<=A:
            v=v+Iv(mass)
        else:
            u=projected_u(A,r)
            v=v+Iv(mass)*(1-u)
            vp=vp+Iv(mass*A/(r*r))/u
    return v,vp

def min_quad(C:F,B:F,K:int,x0:F,x1:F):
    """Minimum of C+B x + K x²/2 over closed rational interval."""
    vals=[C+B*x+F(K,2)*x*x for x in (x0,x1)]
    if K>0:
        t=-B/K
        if x0<t<x1:vals.append(C+B*t+F(K,2)*t*t)
    return min(vals)

def certify_panel(lens:Lens,L:F,U:F,P_L:Iv,P_U:Iv,K:int):
    if not L<U:raise ValueError('reversed panel')
    T=(L+U)/2;Q_T,QP=q_and_gradient(lens,T)
    dqL=floor(QP.low());dqU=ceil(QP.high())
    qlower=floor(Q_T.low())
    pL=ceil(P_L.high());pU=ceil(P_U.high())
    delta=U-L
    slope=F(pU-pL)/delta
    # Q convex within a single frozen source-radius cell. Its midpoint
    # tangent lies below Q(A). The upper slope is used on the left,
    # lower slope on the right; P chord+K*(A-L)*(U-A)/2 is an upper.
    vals=[]
    for lo,hi,d in ((F(0),delta/2,dqU),(delta/2,delta,dqL)):
        intercept=qlower-d*delta/2-pL
        B=d-slope-F(K)*delta/2
        vals.append(min_quad(intercept,B,K,lo,hi))
    lower=min(vals)
    return floor(lower),{'Q_mid_lower_integer':qlower,
          'Q_slope_lower_integer':dqL,'Q_slope_upper_integer':dqU,
          'P_left_upper_integer':pL,'P_right_upper_integer':pU}

def work_one(lens:Lens,qmeta,diag,*,bisects=70,max_depth=9,save_file=None):
    q_b=F.from_float(float.fromhex(qmeta['source_qb_hex']))
    q_d=F.from_float(float.fromhex(qmeta['source_qd_hex']))
    q_margin=q_monotonic_all_cells(lens,q_b,q_d)
    root_R=F.from_float(diag['sampled_R_root_kpc'])
    k,R0,R1,A_lo,A_hi=band_geometry(lens,q_b,q_d,root_R)
    K,kinfo=curvature_upper(lens,A_lo,A_hi)
    print('LENS',lens.name,'R',float(R0),float(R1),'A',float(A_lo),float(A_hi),'K',K,flush=True)
    # Split at source-radial knots: Q is convex on each open segment.
    knots=[A_lo]+[r for r in lens.r if A_lo<r<A_hi]+[A_hi]
    p_cache={}
    def getP(A):
        if A not in p_cache:
            p,err,n=lens.continuous(A,bisections=bisects)
            p_cache[A]=(p,err,n)
        return p_cache[A][0]
    leaves=[];unknown=[];attempts=0
    def search(L,U,depth):
        nonlocal attempts
        attempts+=1
        pL,pU=getP(L),getP(U)
        lower,values=certify_panel(lens,L,U,pL,pU,K)
        if lower>0:
            leaves.append({'left_n':str(L.numerator),'left_d':str(L.denominator),
              'right_n':str(U.numerator),'right_d':str(U.denominator),
              'depth':depth,'gap_lower_floor_Msun':lower,**values})
            return
        if depth>=max_depth:
            unknown.append({'left_n':str(L.numerator),'left_d':str(L.denominator),
              'right_n':str(U.numerator),'right_d':str(U.denominator),
              'depth':depth,'gap_lower_floor_Msun':lower,**values})
            return
        mid=(L+U)/2
        search(L,mid,depth+1)
        search(mid,U,depth+1)
    start=time.monotonic()
    for lo,hi in zip(knots,knots[1:]):
        search(lo,hi,0)
        print('  segment_done',round(float(lo),5),round(float(hi),5),'leaves',len(leaves),'unknown',len(unknown),'P_cache',len(p_cache),'seconds',round(time.monotonic()-start,1),flush=True)
    result={
       'lens':lens.name,'root_R_cell_index':k,
       'R_cell_left_binary64_hex':float(R0).hex(),
       'R_cell_right_binary64_hex':float(R1).hex(),
       'A_band_left_exact_n_over_d':[str(A_lo.numerator),str(A_lo.denominator)],
       'A_band_right_exact_n_over_d':[str(A_hi.numerator),str(A_hi.denominator)],
       'A_band_rounded_navigation':[float(A_lo),float(A_hi)],
       'q_b_original_hex':qmeta['source_qb_hex'],'q_d_original_hex':qmeta['source_qd_hex'],
       'q_monotonic_lower_exact':[str(q_margin.numerator),str(q_margin.denominator)],
       'uniform_P_second_derivative_abs_integer_Msun_per_kpc2':K,
       'uniform_P_second_derivative_decomposition':kinfo,
       'status':'PASS_POSITIVE_FOR_ENTIRE_APERTURE_BAND' if not unknown else 'UNKNOWN_UNRESOLVED_SUBBANDS',
       'minimum_gap_lower_floor_Msun':min([v['gap_lower_floor_Msun'] for v in leaves]) if leaves else None,
       'positive_subbands':leaves,'unknown_subbands':unknown,
       'P_interval_evaluations':len(p_cache),'certification_attempts':attempts,
       'point_certifier_bisections':bisects,
       'original_180_source_node_sha256':lens.node_sha,
       'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
    }
    if save_file is not None:
        save_file.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',type=int,required=True,choices=range(6))
    ap.add_argument('--external-zip',type=Path,required=True)
    ap.add_argument('--diagnostic-json',type=Path,required=True)
    ap.add_argument('--bisects',type=int,default=70)
    ap.add_argument('--max-depth',type=int,default=9)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    ext=a.external_zip
    source=a.diagnostic_json
    caps,infos,arrays=load_external(ext)
    qmeta=q_source_metadata(ext)
    diag=load_apertures(source)
    j=a.index
    lens=Lens(caps[j],infos[j],arrays[j],euler_gamma());lens.rows=arrays[j];lens.node_sha=caps[j]['node_sha256']
    result=work_one(lens,qmeta[j],diag[j],bisects=a.bisects,max_depth=a.max_depth,save_file=a.out)
    if result['status']!='PASS_POSITIVE_FOR_ENTIRE_APERTURE_BAND':
        raise SystemExit('UNKNOWN: source-locked band contains unresolved subbands')
