#!/usr/bin/env python3
"""Independent fixed-source crossing-neighbor derivative discrepancy verifier.

No producer import. Rechecks 46+3 original SHA source, 6x180 samples, original
source H sign edges, and independently bounds mathematical source M and M'
using distinct harmonic/Bessel/log arithmetic from independent_first_node.
"""
from __future__ import annotations

import hashlib
import io
import json
import struct
import zipfile
from fractions import Fraction as F
from pathlib import Path

from independent_first_node import B, euler_range, mass_at_first

P=Path(__file__).resolve().parent
PARENT='fa2d720a34ad80644c7e9f9a96b2ac9eab2e9ad0aa4955d8357f05b934e9cd6f'
NESTED='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
ORIG='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
SOURCE='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'

def sha(x):return hashlib.sha256(x).hexdigest()
def floorf(x):return x.numerator//x.denominator

def check(candidate=None,save=True):
    top=P/'inputs/first_node_rational_parent.zip'
    raw=top.read_bytes()
    if sha(raw)!=PARENT:raise ValueError('first-node parent ZIP mismatch')
    topzip=zipfile.ZipFile(io.BytesIO(raw))
    nested=topzip.read('inputs/frozen_smooth_shadow_gradient_parent.zip')
    if sha(nested)!=NESTED:raise ValueError('source parent identity mismatch')
    z=zipfile.ZipFile(io.BytesIO(nested))
    z1=zipfile.ZipFile(io.BytesIO(z.read('inputs/frozen_source_parent.zip')))
    z2=zipfile.ZipFile(io.BytesIO(z1.read('inputs/original_march_D120_q_parent.zip')))
    z3=zipfile.ZipFile(io.BytesIO(z2.read('inputs/original_march180_parent_v1r1.zip')))
    source_raw=z3.read('inputs/original_source_46_frozen.zip')
    if sha(source_raw)!=ORIG:raise ValueError('original frozen source ZIP mismatch')
    zsrc=zipfile.ZipFile(io.BytesIO(source_raw));lock=json.loads(z3.read('inputs/original_46plus3_lock.json'))
    if lock['original_46plus3_composite_sha256']!=SOURCE or len(lock['source_filenames_sha256'])!=46 or len(lock['archived_negative_controls_sha256'])!=3:
        raise ValueError('original source/negative lock identity mismatch')
    for name,digest in lock['source_filenames_sha256'].items():
        if sha(zsrc.read('swells_pack_v2/'+name))!=digest:raise ValueError('modified original source file')
    for name,digest in lock['archived_negative_controls_sha256'].items():
        if sha(z3.read('inputs/negative_controls/'+name))!=digest:raise ValueError('modified archived negative case')
    capture=json.loads(z3.read('results/source180_capture.json'))
    params=json.loads(z.read('results/producer_analytic_source_gradient.json'))
    if candidate is None:candidate=json.loads((P/'results/crossing_node_producer.json').read_bytes())
    if candidate.get('schema')!='HIST001D_CROSSING_ADJACENT_12_NODE_EXACT_RATIONAL_SOURCE_MATH_CANDIDATE_V1' or candidate.get('parent_sha256')!=PARENT or candidate.get('original_46plus3_sha256')!=SOURCE:
        raise ValueError('producer identity declaration mismatch')
    for flag in ('original_full_H_root_error_certified','original_general_float_operation_error_certified','physical_provider_admitted','source_11520_shadow_substituted'):
        if candidate.get(flag) is not False:raise ValueError('forbidden scientific claim or source substitution')
    if candidate.get('empirical_validation')!='NOT_ESTABLISHED' or candidate.get('node_count')!=12 or len(candidate.get('lenses',[]))!=6:raise ValueError('invalid proof scope')
    base=zipfile.ZipFile(io.BytesIO(z3.read('inputs/march_180_grid.zip')))
    gamma=euler_range()
    output={'schema':'HIST001D_INDEPENDENT_CROSSING_12_NODE_RATIONAL_SOURCE_VERIFIER_V1',
            'original_46plus3_sha256':SOURCE,'parent_sha256':PARENT,
            'all_12_stencil_checks':True,'all_12_strict_smooth_gradient_gaps':True,
            'original_source_float_error_for_general_inputs_certified':False,
            'original_all_R_H_or_root_count_certified':False,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED','lenses':[]}
    for o,p,cand in zip(capture['lenses'],params['lenses'],candidate['lenses']):
        name=o['lens_id']
        if p['lens_id']!=name or cand['lens_id']!=name or cand['node_array_sha256']!=o['node_sha256']:
            raise ValueError('lens source identity or order mismatch')
        source_bytes=z3.read('inputs/'+o['node_file'])
        if sha(source_bytes)!=o['node_sha256'] or len(source_bytes)!=180*64:raise ValueError('180-node source array mismatch')
        arr=list(struct.iter_unpack('>8d',source_bytes));tag=name.replace('+','p')
        hs=list(struct.iter_unpack('>dd',base.read('sampled_binary64/'+tag+'.R_H_be64.bin')))
        if len(hs)!=180 or any(h[0]!=a[0] for a,h in zip(arr,hs)):
            raise ValueError('original H source dimensions or radii')
        zeros=[k for k in range(179) if hs[k][1]*hs[k+1][1]<0]
        if len(zeros)!=1 or any(x[1]==0 for x in hs):raise ValueError('unexpected source H roots')
        i=zeros[0]
        if i!=cand['sampled_final_H_sign_change_edge'] or [v['node_index'] for v in cand['two_crossing_source_nodes']]!=[i,i+1]:
            raise ValueError('crossing source indices incorrectly registered')
        r=[F.from_float(a[0]) for a in arr]
        coeff={k:F.from_float(float.fromhex(p['source_scalar_binary64_hex'][k])) for k in ('Mb','Md','a','Rd','delta','r0','n')}
        C=F.from_float(float.fromhex(p['source_scalar_binary64_hex']['C4pi']))
        if any(r[j]/(2*coeff['Rd'])>=F(3,2) or r[j]>=coeff['r0'] for j in range(i-1,i+3)):
            raise ValueError('independent controlled Bessel/log domain fails')
        mass={}; deriv={}
        for j in range(i-1,i+3):
            deriv[j],mass[j]=mass_at_first(r[j],coeff,gamma)
            if deriv[j].l<=0:raise ValueError('nonpositive selected smooth derivative interval')
        found=[]
        for given in cand['two_crossing_source_nodes']:
            j=given['node_index'];hm=r[j]-r[j-1];hp=r[j+1]-r[j]
            # Different algebraic path from the source producer's weighted secants:
            # direct nonuniform NumPy-gradient 3-point Lagrange coefficients.
            a=-hp/(hm*(hm+hp));b=(hp-hm)/(hm*hp);c=hm/(hp*(hm+hp))
            stencil=a*mass[j-1]+b*mass[j]+c*mass[j+1]
            original=F.from_float(float.fromhex(p['source_scalar_binary64_hex']['C4pi']))*r[j]*r[j]*F.from_float(arr[j][3])
            if given['source_radius_float_hex']!=arr[j][0].hex() or given['source_rho_float_hex']!=arr[j][3].hex() or given['source_mass_gradient_stored_exact']!=str(original):
                raise ValueError('stored binary64 source data modified')
            err=(B(original)-stencil).absmax()
            if err>=F(1,1000) or given.get('stored_minus_ideal_3point_fd_abs_strict_lt_1e_minus_3_msun_per_kpc') is not True:
                raise ValueError('independent exact stencil discrepancy too large')
            if original<=deriv[j].h:raise ValueError('selected smooth derivative not strictly smaller than stored source')
            gap=floorf(original-deriv[j].h)
            if gap<given['stored_minus_smooth_derivative_strict_lower_integer_msun_per_kpc'] or gap<1_000_000:
                raise ValueError('producer derivative lower bound overstated')
            if F.from_float(float(arr[j][3]))<=0:raise ValueError('actual source density must not be clipped to zero')
            # Source-declared conservative ceil is an UPPER on exact interval error.
            ceil_error=-floorf(-err*1_000_000)
            if ceil_error>given['stored_minus_ideal_3point_fd_abs_ceil_micro_msun_per_kpc']:
                raise ValueError('producer fixed-node error ceiling understated')
            ratio=B(original)/deriv[j]
            if floorf(ratio.l*100_000)<given['stored_over_smooth_derivative_ratio_strict_floor_millipercent']:
                raise ValueError('producer strict ratio lower overstated')
            found.append({'node_index':j,'independent_exact_stencil_error_strict_lt_1e_minus_3':True,
                          'independent_stencil_error_ceil_micro_msun_per_kpc':ceil_error,
                          'independent_derivative_difference_lower_integer_msun_per_kpc':gap})
            print('INDEPENDENT_ROOT_NODE_PASS',name,j,'abs_stencil_max',float(err),'gap_floor',gap,flush=True)
        min_gap=min(v['independent_derivative_difference_lower_integer_msun_per_kpc'] for v in found)
        if min_gap<cand['minimal_certified_smooth_derivative_gap_integer_msun_per_kpc']:
            raise ValueError('producer minimum gap understated/altered')
        output['lenses'].append({'lens_id':name,'sampled_final_H_sign_change_edge':i,
                                'source_node_sha256':o['node_sha256'],'two_nodes':found,
                                'minimum_root_neighborhood_smooth_derivative_gap':min_gap})
    if save:
        path=P/'results/crossing_node_independent.json';path.write_bytes((json.dumps(output,sort_keys=True,indent=2)+'\n').encode())
        print('INDEPENDENT_SHA256',sha(path.read_bytes()),flush=True)
    return output
if __name__=='__main__':check()
