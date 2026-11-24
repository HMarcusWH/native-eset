#!/usr/bin/env python3
"""Fail-closed BV bounds and direct positive M' integral enclosures over 6 crossing A bands."""
from __future__ import annotations
from fractions import Fraction as Q
from math import isqrt
from pathlib import Path
import json,struct,zipfile,hashlib,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'reference/hist001d_k180_bessel_integral_candidate'))
from source_audit import open_inputs
RADIAL=ROOT/'inputs/saturation_parent_v1r1.zip'
BANDS=ROOT/'inputs/crossing_band_parent_v1r2.zip'
SQ=1<<192

def upq(v):return -(-v.numerator//v.denominator)
def loq(v):return v.numerator//v.denominator

def sqrt_interval(v):
    if not v>=0:raise ValueError('negative radicand')
    k=isqrt(v.numerator*SQ*SQ//v.denominator)
    if k*k*v.denominator==v.numerator*SQ*SQ:return Q(k,SQ),Q(k,SQ)
    return Q(k,SQ),Q(k+1,SQ)

def phi(A,r):
    if A<0 or r<=0:raise ValueError('domain')
    if A>=r:return Q(1),Q(1)
    l,u=sqrt_interval(1-(A/r)**2)
    return 1-u,1-l

def max_delta(Alo,Ahi,a,b):
    # phi_A(a)-phi_A(b) rises for 0<A<a, then falls for a<A<b.
    if not 0<=Alo<=Ahi or not 0<a<b:raise ValueError('ordered domains')
    A=max(Alo,min(a,Ahi))
    # interval subtraction: positive envelope clamp at zero
    plo=phi(A,a);phiHi=phi(A,b)
    return max(Q(0),plo[1]-phiHi[0])

def source_bands():
    z=zipfile.ZipFile(BANDS)
    rows=json.loads(z.read('results/whole_band_certificate.json'))['lenses']
    if len(rows)!=6:raise ValueError('six source bands required')
    return rows

def run_lens(j):
    band=source_bands()[j]
    d=json.loads((ROOT/'results'/f'continuous_lens_{j}.json').read_text())
    src,caps,analytic,_=open_inputs(RADIAL.read_bytes())
    if d['lens_id']!=caps[j]['lens_id'] or d['node_sha256']!=caps[j]['node_sha256'] or band['lens']!=caps[j]['lens_id'] or band['original_180_source_node_sha256']!=caps[j]['node_sha256'] or not d['all_real_selected_Mprime_positive'] or d['unresolved']:
        raise ValueError('source identity / derivative coverage not validated')
    A0=Q(*map(int,band['A_band_left_exact_n_over_d']));A1=Q(*map(int,band['A_band_right_exact_n_over_d']))
    rows=list(struct.iter_unpack('>8d',src.read('inputs/'+caps[j]['node_file'])))
    r=[Q.from_float(row[0]) for row in rows]
    w=[Q.from_float(row[1]) for row in rows]
    panels=d['panels'];w_mesh=[(r[1]-r[0])/2]+[(r[i+1]-r[i-1])/2 for i in range(1,179)]+[(r[-1]-r[-2])/2]
    e_kernel=e_curve=lowP=highP=Q(0)
    jnode=json.loads((ROOT/f'results/lens_{j}.json').read_text())['lenses'][0]['nodes']
    if len(jnode)!=180:raise ValueError('original nodes missing')
    for panel in panels:
        idx=panel['cell'];a,b=Q(panel['lo']),Q(panel['hi']);h=b-a;H=r[idx+1]-r[idx]
        if h<=0 or H<=0 or panel['Mprime_lower_micro']<=0 or panel['Mprime_upper_micro']<=0 or panel['Msecond_abs_ceil']<0:
            raise ValueError('invalid certificate panel')
        lower=Q(panel['Mprime_lower_micro'],10**6)
        upper=Q(panel['Mprime_upper_micro'],10**6)
        C=Q(panel['Msecond_abs_ceil'])
        # Cell-local BV bound for original (coarse-grid) trapezoid
        e_kernel+=H*upper*max_delta(A0,A1,a,b)/2
        e_curve+=H*h*C*phi(A1,a)[1]/2
        # Independent direct continuous projection enclosure for all A in band
        lowP+=h*lower*phi(A0,b)[0]
        highP+=h*upper*phi(A1,a)[1]
    e_weight=Q(0)
    for j0 in range(180):
        Mp_high=Q(jnode[j0]['selected_Mprime_interval'][1])
        e_weight+=abs(w[j0]-w_mesh[j0])*Mp_high*phi(A1,r[j0])[1]
    E=e_kernel+e_curve+e_weight
    ret={'lens':d['lens_id'],'A_band_exact':[str(A0),str(A1)],
        'accepted_original_radial_cells':179,'accepted_subpanels':len(panels),
        'uniform_band_derivative_sampled_trap_vs_mathematical_continuum_error_ceiling_Msun':upq(E),
        'uniform_band_error_kernel_variation_ceiling_Msun':upq(e_kernel),
        'uniform_band_error_Mprime_variation_ceiling_Msun':upq(e_curve),
        'uniform_band_original_weight_rounding_ceiling_micro_Msun':upq(e_weight*10**6),
        'P_mathematical_continuum_all_A_band_integer_Msun_enclosure':[loq(lowP),upq(highP)],
        'useful_for_full_root_gap':False,
        'source_scope':'SELECTED_MSTAR_ONLY_NOT_PHYSICAL_SOURCE','physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    dest=ROOT/'results'/f'bv_band_lens_{j}.json';dest.write_text(json.dumps(ret,sort_keys=True,indent=2)+'\n')
    print('BV',ret['lens'],'E <',ret['uniform_band_derivative_sampled_trap_vs_mathematical_continuum_error_ceiling_Msun'],'P band',ret['P_mathematical_continuum_all_A_band_integer_Msun_enclosure'],'weightmicro',ret['uniform_band_original_weight_rounding_ceiling_micro_Msun'],flush=True)
    return ret
if __name__=='__main__':
 for i in range(6):run_lens(i)
