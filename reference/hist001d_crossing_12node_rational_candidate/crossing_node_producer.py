#!/usr/bin/env python3
"""Exact-rational 12 crossing-adjacent March gradient-node discrepancies.

Mathematical fixed-source diagnostic only. Never substitutes D2d 11520-node rho,
never establishes original general SciPy/NumPy floating-point error, and does
not prove original off-grid H, physical Weyl or empirical validity.
"""
from __future__ import annotations

import hashlib
import io
import json
import struct
import zipfile
from fractions import Fraction as Q
from pathlib import Path

from first_node_certificate import Iv, gamma_iv, load_sources, source_mass_derivative

ROOT=Path(__file__).resolve().parent
SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
PARENT_SHA='fa2d720a34ad80644c7e9f9a96b2ac9eab2e9ad0aa4955d8357f05b934e9cd6f'
BOUND=Q(1,1000)  # strict absolute-stencil-mismatch cap in Msun/kpc

def h(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def floor_frac(x:Q)->int:return x.numerator//x.denominator

def calculate(save=True):
    top=ROOT/'inputs/first_node_rational_parent.zip'
    if h(top.read_bytes())!=PARENT_SHA:raise ValueError('first-node parent ZIP SHA mismatch')
    # Existing original 46+3 source verifier is imported from the exact hash-pinned
    # prior first-node archive and rereads EVERY original source file.
    z,candidates,capture=load_sources()
    if len(candidates['lenses'])!=6 or len(capture['lenses'])!=6:raise ValueError('six-lens source count')
    hzip=zipfile.ZipFile(io.BytesIO(z.read('inputs/march_180_grid.zip')))
    gamma=gamma_iv(500)
    result={'schema':'HIST001D_CROSSING_ADJACENT_12_NODE_EXACT_RATIONAL_SOURCE_MATH_CANDIDATE_V1',
            'parent_sha256':PARENT_SHA,'original_46plus3_sha256':SOURCE_SHA,
            'source_11520_shadow_substituted':False,
            'selected_smooth_mathematical_continuation_only':True,
            'original_full_H_root_error_certified':False,
            'original_general_float_operation_error_certified':False,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'node_count':12,'lenses':[]}
    for cap,par in zip(capture['lenses'],candidates['lenses']):
        lid=cap['lens_id']
        if lid!=par['lens_id']:raise ValueError('source lens identity mismatch')
        raw=z.read('inputs/'+cap['node_file'])
        if h(raw)!=cap['node_sha256'] or len(raw)!=180*64:raise ValueError('original exact source node array')
        arr=list(struct.iter_unpack('>8d',raw)); tag=lid.replace('+','p')
        orig_H=hzip.read(f'sampled_binary64/{tag}.R_H_be64.bin')
        if len(orig_H)!=180*16:raise ValueError('original H series length')
        H=list(struct.iter_unpack('>dd',orig_H))
        if any(a[0]!=b[0] for a,b in zip(arr,H)):raise ValueError('original source H radius differs')
        sign_changes=[i for i in range(179) if H[i][1]*H[i+1][1]<0]
        if len(sign_changes)!=1 or any(t[1]==0 for t in H):raise ValueError('source sampled H topology changed')
        i=sign_changes[0]
        if i<1 or i+2>=180:raise ValueError('cannot bound interior crossing nodes')
        p={key:Q.from_float(float.fromhex(par['source_scalar_binary64_hex'][key])) for key in ('Mb','Md','a','Rd','delta','r0','n')}
        c4pi=Q.from_float(float.fromhex(par['source_scalar_binary64_hex']['C4pi']))
        xs=[Q.from_float(row[0]) for row in arr]
        # No general domain extension beyond this exact bounded root-adjacent set.
        if any(xs[j]>=p['r0'] or xs[j]/(2*p['Rd'])>Q(3,2) for j in range(i-1,i+3)):
            raise ValueError('root-neighborhood outside previously certified Bessel/gate series domain')
        d={};mass={}
        for j in range(i-1,i+3):
            d[j],detail=source_mass_derivative(xs[j],p,gamma,N=32)
            mass[j]=detail['smooth_M']
            if d[j].l<=0:raise ValueError('positive smooth Mprime must be certified')
        output=[]
        for j in (i,i+1):
            hm=xs[j]-xs[j-1];hp=xs[j+1]-xs[j]
            if hm<=0 or hp<=0:raise ValueError('bad radial mesh')
            ideal_fd=(hp*(mass[j]-mass[j-1])/hm + hm*(mass[j+1]-mass[j])/hp)/(hm+hp)
            raw_rho=Q.from_float(arr[j][3]); stored=c4pi*xs[j]*xs[j]*raw_rho
            if raw_rho<=0:raise ValueError('original gradient clip not strictly positive at this node')
            abs_error=(Iv(stored)-ideal_fd).absmax()
            if not abs_error<BOUND:raise ValueError('original source stored vs ideal 3-point stencil not close')
            if stored<=d[j].u:raise ValueError('original stored gradient must strictly exceed smooth derivative')
            floor_gap=floor_frac(stored-d[j].u)
            if floor_gap<1_000_000:raise ValueError('insufficient certified fixed-node gap')
            ratio=Iv(stored)/d[j]
            record={'node_index':j,'source_radius_float_hex':arr[j][0].hex(),
                    'source_rho_float_hex':arr[j][3].hex(),
                    'source_mass_gradient_stored_exact':str(stored),
                    'stored_minus_ideal_3point_fd_abs_strict_lt_1e_minus_3_msun_per_kpc':True,
                    'stored_minus_ideal_3point_fd_abs_ceil_micro_msun_per_kpc':int(-floor_frac(-abs_error*1_000_000)),
                    'stored_minus_smooth_derivative_strict_lower_integer_msun_per_kpc':floor_gap,
                    'stored_over_smooth_derivative_ratio_strict_floor_millipercent':floor_frac(ratio.l*100_000),
                    'source_real_bessel_series_domain_valid':True}
            output.append(record)
            print('RATIONAL_CROSSING_NODE_PASS',lid,j,'abs_source_vs_ideal',float(abs_error),'lower_derivative_gap',floor_gap,flush=True)
        result['lenses'].append({'lens_id':lid,'node_array_sha256':cap['node_sha256'],
                  'sampled_final_H_sign_change_edge':i,
                  'two_crossing_source_nodes':output,
                  'minimal_certified_smooth_derivative_gap_integer_msun_per_kpc':min(x['stored_minus_smooth_derivative_strict_lower_integer_msun_per_kpc'] for x in output)})
    if save:
        out=ROOT/'results/crossing_node_producer.json';out.parent.mkdir(exist_ok=True,parents=True)
        out.write_bytes((json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
        print('PRODUCER_SHA256',h(out.read_bytes()),flush=True)
    return result

if __name__=='__main__':calculate()
