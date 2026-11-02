#!/usr/bin/env python3
"""Exact algebraic K180 shadow-difference bound on six source March crossing cells.

Uses ORIGINAL frozen 180-ring stencil, source B/D arrays and all-180 per-ring
rational difference intervals. Does not re-evaluate mathematical Bessel functions,
does not claim original March continuous-root/physical provider identity.
"""
from __future__ import annotations
import zipfile,io,struct,json,hashlib,math
from fractions import Fraction as Q
from pathlib import Path
from all180_producer import open_sources
P=Path(__file__).resolve().parent

def ceil(q):return -((-q.numerator)//q.denominator)

def sqrt_lower(q:Q,bits=120):
    if q<0:raise ValueError('negative squared guard')
    n=q.numerator*(1<<(2*bits))//q.denominator
    a=math.isqrt(n)
    z=Q(a,1<<bits)
    if not z*z<=q:raise ValueError('bad outward square root lower guard')
    return z

def sqrt_upper(q:Q,bits=120):
    v=sqrt_lower(q,bits)
    if v*v==q:return v
    return v+Q(1,1<<bits)

def calc_one(index):
    z3,cap,sm=open_sources();c=cap['lenses'][index];s=sm['lenses'][index];lid=c['lens_id'];tag=lid.replace('+','p')
    if lid!=s['lens_id']:raise ValueError('lens model identity')
    raw=z3.read('inputs/'+c['node_file'])
    if hashlib.sha256(raw).hexdigest()!=c['node_sha256'] or len(raw)!=180*64:raise ValueError('source node sha')
    rows=[[Q.from_float(q) for q in t] for t in struct.iter_unpack('>8d',raw)]
    B=[x[4] for x in rows];D=[x[6] for x in rows]
    if any(x<=0 for x in B+D):raise ValueError('positive source baryon B,D corner premise')
    q_min=min(Q.from_float(float.fromhex(s['source_scalar_binary64_hex'][k])) for k in ['qb','qd'])
    if q_min<=0:raise ValueError('positive q convex mixture')
    hzip=zipfile.ZipFile(io.BytesIO(z3.read('inputs/march_180_grid.zip')))
    H=list(struct.iter_unpack('>dd',hzip.read(f'sampled_binary64/{tag}.R_H_be64.bin')))
    if len(H)!=180 or any(Q.from_float(t[0])!=r[0] for t,r in zip(H,rows)):
        raise ValueError('source original 180 sampled radii mismatch')
    edges=[i for i in range(179) if H[i][1]*H[i+1][1]<0]
    if len(edges)!=1 or any(t[1]==0 for t in H):raise ValueError('sampled topology premise not valid')
    index=edges[0]
    left=rows[index][0];right=rows[index+1][0]
    A_up=min(Q(120),sqrt_upper(right*right/q_min,bits=120))
    assert A_up>=right
    producer=json.loads((P/'results'/f'all180_rational_{tag}.json').read_text())
    if producer['source_180_node_sha256']!=c['node_sha256']:raise ValueError('producer mismatch')
    interval=producer['source_gradient_minus_smooth_Mprime_interval_integer_msun_per_kpc']
    if len(interval)!=180:raise ValueError('incomplete derivative intervals')
    sum_all=Q();max_weight=Q();contributors=[]
    for j,row in enumerate(rows):
        r,w=row[0],row[1]
        if w<=0:raise ValueError('source projection negative weights')
        if r<=A_up:phi=Q(1)
        else:
            t=1-(A_up/r)**2
            if t<=0:raise ValueError('aperture/radius inequality')
            phi=1-sqrt_lower(t,bits=120)
        assert 0<=phi<=1
        diff=max(abs(interval[j][0]),abs(interval[j][1]))
        sum_all+=w*diff*phi
        contributors.append({'j':j,'max_gradient_gap_integer_msun_per_kpc':diff,'kernel_factor_upper_float':float(phi)})
    new=ceil(sum_all)
    if new<=0 or new>=producer['projected_shadow_all_R_difference_upper_integer_msun']:
        raise ValueError('root-band bound not stricter than global K180 comparison')
    return {'lens_id':lid,'source_original_node_sha256':c['node_sha256'],
        'original_March_sampled_crossing_edge_index':index,
        'real_radius_band_left_exact':str(left),'real_radius_band_right_exact':str(right),
        'original_source_qmin_exact':str(q_min),'outward_upper_aperture_exact':str(A_up),
        'all_radii_in_original_March_crossing_cell_covered':True,
        'positive_original_source_baryonic_PL_masses':True,
        'old_11520_source_data_substituted':False,
        'certified_frozen_K180_shadow_density_substitution_crossing_cell_upper_integer_msun':new,
        'previous_all_real_global_frozen_projection_bound_integer_msun':producer['projected_shadow_all_R_difference_upper_integer_msun'],
        'not_a_smooth_physical_density_or_original_H_error':True,
        'not_an_original_March_root_count_proof':True}

if __name__=='__main__':
    out={'schema':'HIST001D_MARCH180_ORIGINAL_CROSSING_CELL_PROJECTION_WEIGHTED_DIFFERENCE_MATH_CANDIDATE_V1',
         'original_46plus3_sha256':'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a',
         'exact_source_first_original_180_nodes_only':True,
         'physical_provider_admitted':False,
         'empirical_validation':'NOT_ESTABLISHED',
         'original_full_H_or_root_count_proved':False,
         'lenses':[calc_one(i) for i in range(6)]}
    f=P/'results/crossing_band_producer.json';f.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('CROSSING_BAND_SOURCE_PASS',[(x['lens_id'],x['certified_frozen_K180_shadow_density_substitution_crossing_cell_upper_integer_msun']) for x in out['lenses']]);print('SHA256',hashlib.sha256(f.read_bytes()).hexdigest())
