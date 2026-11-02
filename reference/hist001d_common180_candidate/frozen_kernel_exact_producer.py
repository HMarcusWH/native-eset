#!/usr/bin/env python3
"""Exact source-180 frozen-stencil, continuous-radius projected mass inclusion.

MATHEMATICAL/NUMERICAL SCOPED ONLY. Not quadrature accuracy against an unknown
physical continuum density, not original 180x120 H(R) root certification.
"""
from __future__ import annotations
import json,struct,hashlib,math
from pathlib import Path
from fractions import Fraction as Q
from math import isqrt
ROOT=Path(__file__).resolve().parents[1]
BITS=72
SCALE=1<<BITS
PINS={
'J0822+1828':'3d354c12839b5bfce41c5e18184250ea8bfcea1f7ef8bc79949d6b92d4cb0938',
'J0915+4211':'ae0c8b7fe618ae9df6ee1de15aef42412f925581d504897d595b0d42aafb9a23',
'J0930+2855':'9a65b32e86ab7ab2f79268fbd883e44dd8f4b7deec2705a09f4d849b0126efae',
'J1021+2028':'4f9b7be29c1e060bc4a0489e4ddcbfff78d66746846b1a61f344b89e8816d9ee',
'J1111+2234':'25dba7a30e6e649ce8ff45e29a1433be2726b58dcbd09e0aac78e7274bab3923',
'J1135+3720':'16e316dea701a1b0863455db24213d3b243d1e5288f6e6578bc0c875e2cf16fd'}

def pair(f):return {'n':str(f.numerator),'d':str(f.denominator)}
def sha(b):return hashlib.sha256(b).hexdigest()
def read_binary(root, lid):
    p=root/'inputs'/('March180_source_nodes_'+lid.replace('+','p')+'.be64')
    raw=p.read_bytes()
    if len(raw)!=180*64:raise ValueError('wrong input size')
    rows=[tuple(Q.from_float(f) for f in rec) for rec in struct.iter_unpack('>8d',raw)]
    return rows,sha(raw)

def sqrt_band(x):
    if x<0:raise ValueError('negative radicand')
    a=isqrt((x.numerator*SCALE*SCALE)//x.denominator)
    low=Q(a,SCALE)
    up=low if low*low==x else Q(a+1,SCALE)
    assert low*low<=x<=up*up
    return low,up

def kernel_band(R,r):
    if not (0<R<=r):raise ValueError('invalid geometry')
    x=r*r-R*R
    lo,hi=sqrt_band(x)
    return r*(r-hi),r*(r-lo)

def make_matrix(rr):
    res=[]
    for i,R in enumerate(rr):
        row=[]
        for j,r in enumerate(rr):
            if j<=i:row.append((r*r,r*r))
            else:row.append(kernel_band(R,r))
        res.append(row)
    return res

def floor(x):return x.numerator//x.denominator
def ceil(x):return -floor(-x)

def calculate_ideal_nodes(rr,ww,rho,coeff,stencil):
    a=[coeff*w*d for w,d in zip(ww,rho,strict=True)]
    assert min(a)>=0
    out=[]
    for row in stencil:
        lo=hi=Q(0)
        for scalar,(x,y) in zip(a,row,strict=True):
            lo+=scalar*x;hi+=scalar*y
        assert 0<=lo<=hi
        out.append((lo,hi))
    return out

def main():
    authority=json.loads((ROOT/'results/source180_capture.json').read_bytes())
    if authority['source_lock_sha256']!='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a':raise ValueError('source drift')
    lenses=authority['lenses'];assert len(lenses)==6
    rr=[row[0] for row in read_binary(ROOT,lenses[0]['lens_id'])[0]]
    assert all(rr[i]<rr[i+1] for i in range(179)) and rr[0]==Q.from_float(.02) and rr[-1]==Q(120)
    stencil=make_matrix(rr)
    out=[]
    for entry in lenses:
        lid=entry['lens_id'];rows,h=read_binary(ROOT,lid)
        assert h==entry['node_sha256']
        assert [row[0] for row in rows]==rr
        w=[row[1] for row in rows]
        assert all(x>0 for x in w)
        # Source floating trapezoid weights freeze explicitly, rather than converting into exact-difference weights.
        rhoB=[row[2] for row in rows];rhoS=[row[3] for row in rows]
        assert all(b>0 and s>=0 for b,s in zip(rhoB,rhoS))
        orig_sha=sha(b''.join(struct.pack('>d',float(x)) for x in rhoS))
        assert orig_sha==PINS[lid]==entry['shadow_density_sha256']
        coeff=Q.from_float(float.fromhex(entry['original_pi4_float_hex']))
        assert coeff==Q.from_float(4*math.pi)
        records=[]
        for name, density_col, output_col in [('BULGE_K180',2,4),('SHADOW_SPHERICAL_K180',3,5)]:
            rho=[row[density_col] for row in rows]
            P=[row[output_col] for row in rows]
            ideals=calculate_ideal_nodes(rr,w,rho,coeff,stencil)
            max_node=max(max(abs(lo-Pi),abs(hi-Pi)) for (lo,hi),Pi in zip(ideals,P))
            worst_node_index=max(range(180),key=lambda i:max(abs(ideals[i][0]-P[i]),abs(ideals[i][1]-P[i])))
            interval_caps=[];min_step_gap=Q(10**100)
            for i in range(179):
                lowF=ideals[i][0];hiF=ideals[i+1][1]
                assert lowF<=hiF
                smaller=min(P[i],P[i+1]);larger=max(P[i],P[i+1])
                cap=max(Q(0),hiF-smaller,larger-lowF)
                interval_caps.append(cap)
                gap=ideals[i+1][0]-ideals[i][1]
                min_step_gap=min(min_step_gap,gap)
            max_cap=max(interval_caps)
            worst_cap_index=max(range(179),key=lambda i:interval_caps[i])
            record={'component':name,'source_nodal_values_nonnegative':True,'stencil_math_coefficient_is_exact_binary64_4pi':True,'input_raw_binary64_nodal_sha256':h,'source_float64_nodal_results_contained_by_exact_ideal_stencil_bounds_plus_recorded_node_residual':True,'all_180_source_node_projection_mathematical_intervals_certified':True,'all_179_real_radius_cells_upper_bounded':True,'source_node_max_anchor_gap_upper_msun':str(ceil(max_node)),'source_node_max_anchor_gap_upper_exact':pair(max_node),'source_node_worst_index':worst_node_index,'max_real_radius_source_stencil_vs_piecewise_linear_bound_upper_msun':str(ceil(max_cap)),'max_real_radius_bound_exact':pair(max_cap),'max_cell_index':worst_cap_index,'max_cell_original_float_hex_radii':[float(rr[worst_cap_index]).hex(),float(rr[worst_cap_index+1]).hex()],'min_exact_monotonic_step_lower_msun':str(floor(min_step_gap)),'monotonic_stencil_derivation':'Every frozen finite-source weight rho >=0 and each cylinder kernel f(R,r) nondecreasing, hence F(Ri)<=F(R)<=F(Ri+1). Original nodal PL lies between its two binary64 source-returned endpoint values. Bound is max(F_hi(Ri+1)-min(Pi,Pi+1), max(Pi,Pi+1)-F_lo(Ri)); if negative clamp to zero.','not_source_gradient_error':True,'not_quad_continuum_error':True,'not_q_aperture_error':True,'not_original_total_H_error':True}
            print('ENVELOPE',lid,name,'node_gap_msun<=',ceil(max_node),'all_R_PL_gap_Msun<=',ceil(max_cap),'maxcell',worst_cap_index,flush=True)
            records.append(record)
        out.append({'lens_id':lid,'source_original_density_sha256':PINS[lid],'original_source_array_record_sha256':h,'component_bounds':records})
    doc={'schema':'HIST001D_MARCH_180_FROZEN_SOURCE_STENCIL_ALL_REAL_R_PL_ENVELOPE_CANDIDATE_V1','status':'PASS_SCOPED_SOURCE180_FIXED_NODAL_STENCIL_MATHEMATICAL_ENVELOPE_ONLY','original_source_lock_sha256':authority['source_lock_sha256'],'source_capture_sha256':sha((ROOT/'results/source180_capture.json').read_bytes()),'radius_domain':'[float64(0.02), float64(120.0)] kpc','float64_source_coefficient':'4*pi source binary64, exact as rational','source_180_node_shadow_density_reused_unchanged':True,'new_11520_source_density_used':False,'sqrt_outward_precision_dyadic_bits':BITS,'lenses':out,'claims':{'all_real_original_K180_frozen_stencil_projection_vs_recorded_nodal_PL_enveloped':True,'numerical_roundoff_input_source_nodes_handled_as_exact_binary64':True,'physically_continuous_shadow_density_equivalence':False,'original_total_H_error_bounded':False,'q_aperture_or_baryon_projection_error_closed':False,'original_continuum_root_count_proved':False,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}}
    raw=(json.dumps(doc,sort_keys=True,separators=(',',':'))+'\n').encode()
    (ROOT/'results/frozen_stencil_all_real_envelope_producer.json').write_bytes(raw)
    print('SOURCE180_STENCIL_MATH_PASS',sha(raw))
if __name__=='__main__':main()
