#!/usr/bin/env python3
"""Source-conditional audit of the *final* March 180-node IEEE-754 operations.

This proves/reproduces ONLY the frozen stored input -> sampled H -> first sign
change -> interpolated root postprocessing. It does not certify how upstream
B/D/S densities were constructed, any fresh off-grid source evaluation, or a
physical continuous density. Protected parents are never needed in public CI.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import struct
import sys
import zipfile
from fractions import Fraction as Q
from math import isfinite
from pathlib import Path

HERE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(HERE/'reference'/'hist001d_full_h_bridge_candidate'))
from full_h_finite_source import FiniteLens  # noqa: E402

SAT_SHA='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
H_SHA='02c93bed1c2d5338972c192013270921264d00320b41d8d17ad44769b47dd7d6'
SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
TOP_PARENT_SHA='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')

def sha(data):return hashlib.sha256(data).hexdigest()
def qf(x):return Q.from_float(x)
def lower(x):return x.numerator//x.denominator
def upper(x):return -((-x.numerator)//x.denominator)
def rounded(x):
    """Exact rational of the nearest binary64 to exact rational x (ties-even)."""
    y=float(x)
    if not isfinite(y):raise ValueError('nonfinite floating operation')
    return qf(y)

def float_sample_H(B,D,S,R,pi,sigma):
    """Original NumPy expression order: ((B+D)+S) - ((pi*(R**2))*sigma)."""
    lhs=rounded(rounded(B+D)+S)
    r2=rounded(R*R)
    rhs=rounded(rounded(pi*r2)*sigma)
    return rounded(lhs-rhs)

def float_sample_root(r0,r1,y0,y1):
    """Source: x0 - y0*(x1-x0)/(y1-y0), each op rounded to binary64."""
    dx=rounded(r1-r0)
    dy=rounded(y1-y0)
    if dy==0:raise ValueError('zero interpolant slope')
    return rounded(r0-rounded(rounded(y0*dx)/dy))

def rational_sample_root(r0,r1,y0,y1):
    if y0==y1:raise ValueError('flat sampled interpolation')
    return (r0*y1-r1*y0)/(y1-y0)

def verify_manifest(z):
    meta=json.loads(z.read('MANIFEST_SHA256.json'))
    if not isinstance(meta.get('files'),dict):raise ValueError('no parent manifest')
    for path,digest in meta['files'].items():
        if sha(z.read(path))!=digest:raise ValueError('bad parent manifest: '+path)

def read_locked(sat_path,h_path):
    sat_bytes=sat_path.read_bytes();h_bytes=h_path.read_bytes()
    if sha(sat_bytes)!=SAT_SHA or sha(h_bytes)!=H_SHA:raise ValueError('wrong parent version')
    with zipfile.ZipFile(io.BytesIO(sat_bytes)) as z:
        verify_manifest(z)
        original=z.read('original_parent.zip')
    if sha(original)!=TOP_PARENT_SHA:raise ValueError('parent SHA mismatch')
    with zipfile.ZipFile(io.BytesIO(original)) as a:
        verify_manifest(a)
        frozen=a.read('inputs/frozen_source_parent.zip')
    with zipfile.ZipFile(io.BytesIO(frozen)) as b:
        verify_manifest(b)
        disk=b.read('inputs/original_march_D120_q_parent.zip')
    with zipfile.ZipFile(io.BytesIO(disk)) as d:
        verify_manifest(d)
        qmeta=json.loads(d.read('results/source120_capture.json'))['lenses']
        raw180=d.read('inputs/original_march180_parent_v1r1.zip')
    with zipfile.ZipFile(io.BytesIO(raw180)) as s:
        verify_manifest(s)
        cap=json.loads(s.read('results/source180_capture.json'))['lenses']
        grid=s.read('inputs/march_180_grid.zip')
        lock=json.loads(s.read('inputs/original_46plus3_lock.json'))
        if lock['original_46plus3_composite_sha256']!=SOURCE_SHA:raise ValueError('historical source changed')
        original_source=s.read('inputs/original_source_46_frozen.zip')
        with zipfile.ZipFile(io.BytesIO(original_source)) as o:
            for f,digest in lock['source_filenames_sha256'].items():
                if sha(o.read('swells_pack_v2/'+f))!=digest:raise ValueError('original source mismatch')
            for f,needle in [
                ('solv/run_j2141_axisym_lens.py','def solve_einstein_radius_projected'),
                ('solv/run_setA_port_cand.py','pred_re_kpc = solve_einstein_radius_projected'),
            ]:
                if needle not in o.read('swells_pack_v2/'+f).decode():raise ValueError('original solver source structure')
        arrays=[]
        for c in cap:
            raw=s.read('inputs/'+c['node_file'])
            if sha(raw)!=c['node_sha256'] or len(raw)!=180*64:raise ValueError('original 180-node bytes')
            arrays.append(list(struct.iter_unpack('>8d',raw)))
    with zipfile.ZipFile(io.BytesIO(grid)) as m:
        verify_manifest(m)
        strict_rows={v['lens_id']:v for v in csv.DictReader(io.StringIO(m.read('strict_original_regv2_6lens.csv').decode()))}
        scale_rows={v['lens_id']:v for v in csv.DictReader(io.StringIO(m.read('swells_pack_v2/cleaned/setA_scale_kpc_per_arcsec.csv').decode()))}
        meta=json.loads(m.read('original_march_180_grid_exact_dyadic_sampled_residual_diagnostic_v1.json'))
        samples=[]
        for item in meta['lenses']:
            buf=m.read(item['sampled_binary64_pair_file'])
            if sha(buf)!=item['sampled_binary64_pair_sha256'] or len(buf)!=180*16:raise ValueError('original H pair bytes')
            samples.append(list(struct.iter_unpack('>2d',buf)))
    with zipfile.ZipFile(io.BytesIO(h_bytes)) as h:
        verify_manifest(h)
        full=json.loads(h.read('results/full_H_finite_receipt.json'))
    assert [c['lens_id'] for c in cap]==list(LENSES)
    assert [c['lens_id'] for c in qmeta]==list(LENSES)
    assert [c['lens_id'] for c in meta['lenses']]==list(LENSES)
    assert [c['lens'] for c in full['lenses']]==list(LENSES)
    if set(strict_rows)!=set(LENSES) or set(scale_rows)!=set(LENSES):raise ValueError('original strict output lens keys')
    return cap,qmeta,arrays,meta['lenses'],samples,full['lenses'],strict_rows,scale_rows

def run(sat_path,h_path,out_path):
    captures,qs,arrays,metadata,samples,finite,strict_rows,scale_rows=read_locked(sat_path,h_path)
    collected=[]
    for c,q,rows,origin,pairs,prev in zip(captures,qs,arrays,metadata,samples,finite):
        pi=qf(float.fromhex(c['original_pi4_float_hex']))/4
        sigma=qf(float.fromhex(c['original_sigma_hex']))
        if pi!=qf(float.fromhex('0x1.921fb54442d18p+1')):raise ValueError('source pi incorrect')
        rr=[qf(z[0]) for z in rows]
        vals=[qf(z[1]) for z in pairs]
        if any(qf(r)!=r0 for (r,_),r0 in zip(pairs,rr)):raise ValueError('R samples changed')
        Hpred=[float_sample_H(qf(z[4]),qf(z[6]),qf(z[7]),r,pi,sigma) for z,r in zip(rows,rr)]
        if Hpred!=vals:raise ValueError('source IEEE-754 H replay differs from captured original')
        k=[i for i in range(179) if vals[i]>0>vals[i+1]]
        if len(k)!=1 or any(v==0 for v in vals):raise ValueError('source first-sign-change topology')
        ki=k[0]
        root=float_sample_root(rr[ki],rr[ki+1],vals[ki],vals[ki+1]);src=qf(origin['original_first_sign_change_root_kpc'])
        if root!=src:raise ValueError('original source-root binary64 replay mismatch')
        scale=float(scale_rows[c['lens_id']]['scale_kpc_per_arcsec'])
        strict_arc=float(strict_rows[c['lens_id']]['predicted_einstein_radius_arcsec'])
        if float(root)/scale!=strict_arc:raise ValueError('strict original output CSV arcsec mismatch')
        exact_root=rational_sample_root(rr[ki],rr[ki+1],vals[ki],vals[ki+1])
        mathematical_H=[qf(z[4])+qf(z[6])+qf(z[7])-pi*sigma*r*r for z,r in zip(rows,rr)]
        ideal_root=rational_sample_root(rr[ki],rr[ki+1],mathematical_H[ki],mathematical_H[ki+1])
        arith=max(abs(x-y) for x,y in zip(vals,mathematical_H))
        finite_lens=FiniteLens(c['lens_id'],rows,qf(float.fromhex(q['qb_hex'])),qf(float.fromhex(q['qd_hex'])),sigma,qf(float.fromhex(c['original_pi4_float_hex'])))
        worst_node_gap=Q(0);worst_geometry=Q(0)
        for j,(R,y) in enumerate(zip(rr,vals)):
            hlow,hhigh=finite_lens.source_H_box(R)
            if (y>0 and hlow<=0) or (y<0 and hhigh>=0):raise ValueError('finite/source nodal sign mismatch')
            worst_node_gap=max(worst_node_gap,abs(y-hlow),abs(y-hhigh))
            worst_geometry=max(worst_geometry,abs(mathematical_H[j]-hlow),abs(mathematical_H[j]-hhigh))
        bracket=[Q(v) for v in prev['root_bracket']]
        if not bracket[0]<bracket[1]:raise ValueError('old finite root bracket invalid')
        left=finite_lens.source_H_box(bracket[0]);right=finite_lens.source_H_box(bracket[1])
        if left[0]<=0 or right[1]>=0:raise ValueError('previous finite root bracket not signed')
        if src<bracket[0]:separation=bracket[0]-src;side='sampled_left_of_finite'
        elif src>bracket[1]:separation=src-bracket[1];side='sampled_right_of_finite'
        else:raise ValueError('source-root and finite-bracket overlap')
        result={
            'lens':c['lens_id'],'source_node_sha256':c['node_sha256'],
            'archived_source_R_H_pair_sha256':origin['sampled_binary64_pair_sha256'],
            'all_180_archived_H_exactly_reproduced_from_final_stored_source_columns':True,
            'source_float_root_exact_match_to_archived_binary64':True,
            'strict_original_6lens_portability_CSV_arcsec_reproduced':True,
            'source_float_root_hex':float(src).hex(),
            'source_crossing_index':ki,'all_source_R_nodes_have_same_sign_as_explicit_finite_PL_extension':True,
            'max_exact_real_postprocessing_vs_binary64_archived_H_upper_micro_Msun':upper(arith*10**6),
            'max_source_archived_H_vs_finite_PL_node_upper_micro_Msun':upper(worst_node_gap*10**6),
            'max_frozen_geometric_Snode_vs_selected_PL_S0_upper_micro_Msun':upper(worst_geometry*10**6),
            'source_float_root_vs_exact_archived_sampled_PL_root_upper_atto_kpc':upper(abs(src-exact_root)*10**18),
            'source_float_root_vs_exact_stored_component_algebra_nodal_PL_root_upper_atto_kpc':upper(abs(src-ideal_root)*10**18),
            'sampled_float_vs_unique_finite_PL_root_separation_strict_lower_nano_kpc':lower(separation*10**9),
            'sampled_vs_finite_root_order':side,
            'original_selected_finite_root_bracket':[str(v) for v in bracket],
            'reported_root_is_zero_of_offgrid_finite_PL_model':False,
            'original_floating_offgrid_source_error_bound_proved':False,
            'upstream_baryon_disk_shadow_projection_floating_error_proved':False,
        }
        collected.append(result)
        print(c['lens_id'],'H matched',len(vals),'root',result['source_float_root_hex'],
              'node upper micro',result['max_source_archived_H_vs_finite_PL_node_upper_micro_Msun'],
              'sample-finite separation nano',result['sampled_float_vs_unique_finite_PL_root_separation_strict_lower_nano_kpc'],flush=True)
    rec={'schema':'HIST001D_ORIGINAL_MARCH180_IEEE754_SAMPLED_H_POSTPROCESSING_AND_FINITE_PL_GAP_V1',
         'conditional_original_source_sha256':SOURCE_SHA,
         'saturation_archive_sha256':SAT_SHA,
         'finite_H_parent_sha256':H_SHA,
         'source_sampled_H_grid_values_replayed':1080,
         'source_sampled_roots_binary64_exact_replay_count':6,
         'actual_original_solver_root_rule':'FIRST_SIGN_CHANGE_PLUS_BINARY64_LINEAR_RESIDUAL_INTERPOLATION',
         'arbitrary_radius_original_March_source_theorem':False,
         'physical_provider_admitted':False,
         'empirical_validation':'NOT_ESTABLISHED',
         'lenses':collected}
    out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_bytes((json.dumps(rec,sort_keys=True,indent=2)+'\n').encode())
    return rec

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--saturation',type=Path,required=True)
    p.add_argument('--finite-H',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    run(a.saturation,a.finite_H,a.out)
