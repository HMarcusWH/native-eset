#!/usr/bin/env python3
"""Research-only all-180 node fixed-source rational Bessel audit (nonpromoting)."""
from __future__ import annotations
import argparse,io,zipfile,struct,json,hashlib,sys,time
from pathlib import Path
from fractions import Fraction as Q
from all180_math import Iv, source_mass, euler_gamma
P=Path(__file__).resolve().parent
TOP_ZIP=P/'inputs/frozen_smooth_shadow_gradient_parent.zip'
TOP_SHA='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'

def h(b):return hashlib.sha256(b).hexdigest()
def ceil(q):return -((-q.numerator)//q.denominator)
def floor(q):return q.numerator//q.denominator

def open_sources():
    if h(TOP_ZIP.read_bytes())!=TOP_SHA:raise ValueError('source parent SHA failure')
    z=zipfile.ZipFile(TOP_ZIP)
    z1=zipfile.ZipFile(io.BytesIO(z.read('inputs/frozen_source_parent.zip')))
    z2=zipfile.ZipFile(io.BytesIO(z1.read('inputs/original_march_D120_q_parent.zip')))
    z3=zipfile.ZipFile(io.BytesIO(z2.read('inputs/original_march180_parent_v1r1.zip')))
    orig=zipfile.ZipFile(io.BytesIO(z3.read('inputs/original_source_46_frozen.zip')))
    lock=json.loads(z3.read('inputs/original_46plus3_lock.json'))
    if lock['original_46plus3_composite_sha256']!=SOURCE_SHA:raise ValueError('source composite identity')
    for f,s in lock['source_filenames_sha256'].items():
        if h(orig.read('swells_pack_v2/'+f))!=s:raise ValueError('original file source mismatch '+f)
    for f,s in lock['archived_negative_controls_sha256'].items():
        if h(z3.read('inputs/negative_controls/'+f))!=s:raise ValueError('negative control mismatch '+f)
    capture=json.loads(z3.read('results/source180_capture.json'))
    smooth=json.loads(z.read('results/producer_analytic_source_gradient.json'))
    return z3,capture,smooth

def calc_one(index,storage=True):
    z3,capture,smooth=open_sources()
    c=capture['lenses'][index];s=smooth['lenses'][index];lens=c['lens_id']
    if lens!=s['lens_id']:raise ValueError('source mismatch')
    raw=z3.read('inputs/'+c['node_file'])
    if len(raw)!=180*64 or h(raw)!=c['node_sha256']:raise ValueError('original source nodes wrong')
    arr=list(struct.iter_unpack('>8d',raw))
    params={key:Q.from_float(float.fromhex(s['source_scalar_binary64_hex'][key])) for key in ('Mb','Md','a','Rd','delta','r0','n')}
    C=Q.from_float(float.fromhex(s['source_scalar_binary64_hex']['C4pi']))
    g=euler_gamma(n=1024,m=16)
    R=[Q.from_float(row[0]) for row in arr];W=[Q.from_float(row[1]) for row in arr]
    stored=[C*R[i]*R[i]*Q.from_float(arr[i][3]) for i in range(180)]
    if any(x<=0 for x in W) or any(row[3]<=0 for row in arr) or any(R[i]>=R[i+1] for i in range(179)):
        raise ValueError('source positive density, weight and monotone radius premises')
    M=[];Mp=[]
    for i,r in enumerate(R):
        a,b,_=source_mass(r,params,g,N=180)
        if b.low()<=0:raise ValueError(f'positive smooth derivative cannot be proved at {lens}/{i}')
        M.append(a);Mp.append(b)
        if i%30==29 or i==179:print('LENS_SOURCE_MASS_PASS',lens,i+1,'of 180',flush=True)
    eps=[];discrep=[];density_diff=[]
    proj_upper=Q(0)
    for i in range(180):
        if i==0:ideal=(M[1]-M[0])/(R[1]-R[0])
        elif i==179:ideal=(M[i]-M[i-1])/(R[i]-R[i-1])
        else:
            hm=R[i]-R[i-1];hp=R[i+1]-R[i]
            ideal=(hp*(M[i]-M[i-1])/hm+hm*(M[i+1]-M[i])/hp)/(hm+hp)
        e=Iv(stored[i])-ideal
        err=e.bound_abs()
        discrep.append((e.low(),e.high()))
        eps.append(ceil(err*1_000_000))
        d=Iv(stored[i])-Mp[i]
        dif=d.bound_abs()
        density_diff.append((d.low(),d.high()))
        proj_upper+=W[i]*dif
    max_e=max(eps)
    if max_e>=1_000_000:raise ValueError(f'Source/ideal-stencil discrepancy not <1 Msun/kpc for {lens}: {max_e}')
    envelope={
        'schema':'HIST001D_ORIGINAL_MARCH180_ALL_NODE_RATIONAL_BESSEL_SOURCE_AUDIT_CANDIDATE_V1',
        'lens_id':lens,'source_180_node_sha256':c['node_sha256'],
        'original_46plus3_source_composite_sha256':SOURCE_SHA,
        'original_smooth_parent_sha256':TOP_SHA,
        'source_regv2_180_nodes_not_D2d_11520':True,
        'selected_smooth_acceleration_equivalent_mass_math_only':True,
        'all_180_ideal_stencil_discrepancies_certified':True,
        'stored_vs_ideal_stencil_absolute_upper_micro_msun_per_kpc':eps,
        'max_ideal_stencil_discrepancy_upper_micro_msun_per_kpc':max_e,
        'original_source_density_positive_all_nodes':True,
        'smooth_math_derivative_positive_all_nodes':True,
        'original_source_180_kernel_weights_positive':True,
        'projected_shadow_all_R_difference_upper_integer_msun':ceil(proj_upper),
        'source_gradient_minus_smooth_Mprime_interval_integer_msun_per_kpc':[[floor(a),ceil(b)] for a,b in density_diff],
        'source_float_operational_error_certified_for_arbitrary_inputs':False,
        'physical_shadow_density_or_Weyl_proved':False,
        'original_March_continuum_H_error_or_root_count_proved':False,
        'empirical_validation':'NOT_ESTABLISHED',
        'physical_provider_admitted':False,
    }
    if storage:
        dest=P/'results'/('all180_rational_'+lens.replace('+','p')+'.json')
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(envelope,indent=2,sort_keys=True)+'\n')
        print('LENS_REPORT_SHA',lens,h(dest.read_bytes()),'MAX_ABS_IDEAL_FD_UPPER',max_e,'microMSun/kpc','ALL_R_PROJECTED_DIFFERENCE_UPPER',ceil(proj_upper),'MSun',flush=True)
    return envelope

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lens-index',type=int,required=True);o=ap.parse_args()
    calc_one(o.lens_index)
