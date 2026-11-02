#!/usr/bin/env python3
"""Source-authenticated exact-rational Bessel-envelope supplier; no empirical/physical promotion."""
from __future__ import annotations
import hashlib, io, json, struct, zipfile, sys, time
from fractions import Fraction as Q
from pathlib import Path
from c3_envelope import certify_mesh
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'inputs/frozen_smooth_shadow_gradient_parent.zip'
EXPECTED_PARENT_SHA='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
EXPECTED_ORIGINAL_SHA='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
EXPECTED_46P3='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def ceilQ(f:Q)->int:return -(-f.numerator//f.denominator)

def source_data():
    if sha(PARENT.read_bytes())!=EXPECTED_PARENT_SHA:raise ValueError('parent source archive SHA mismatch')
    z0=zipfile.ZipFile(PARENT)
    if z0.testzip():raise ValueError('outer CRC')
    z1=zipfile.ZipFile(io.BytesIO(z0.read('inputs/frozen_source_parent.zip')))
    z2=zipfile.ZipFile(io.BytesIO(z1.read('inputs/original_march_D120_q_parent.zip')))
    z3=zipfile.ZipFile(io.BytesIO(z2.read('inputs/original_march180_parent_v1r1.zip')))
    if any(z.testzip() for z in (z1,z2,z3)):raise ValueError('inner CRC')
    original_zip=z3.read('inputs/original_source_46_frozen.zip')
    if sha(original_zip)!=EXPECTED_ORIGINAL_SHA: raise ValueError('original March source ZIP changed')
    original=zipfile.ZipFile(io.BytesIO(original_zip))
    lock=json.loads(z3.read('inputs/original_46plus3_lock.json'))
    if lock['original_46plus3_composite_sha256']!=EXPECTED_46P3:raise ValueError('46+3 composite mismatch')
    assert len(lock['source_filenames_sha256'])==46 and len(lock['archived_negative_controls_sha256'])==3
    for p,h in lock['source_filenames_sha256'].items():
        if sha(original.read('swells_pack_v2/'+p))!=h:raise ValueError('source byte changed '+p)
    for p,h in lock['archived_negative_controls_sha256'].items():
        if sha(z3.read('inputs/negative_controls/'+p))!=h:raise ValueError('negative byte changed '+p)
    old=json.loads(z3.read('results/source180_capture.json'))
    smooth=json.loads(z0.read('results/producer_analytic_source_gradient.json'))
    assert len(old['lenses'])==len(smooth['lenses'])==6
    return z3,old,smooth

def build(limit=None,parts:int=4):
    z3,original,smooth=source_data()
    result={'schema':'HIST001D_ORIGINAL_MARCH_MSH_BESSEL_HALF_INTEGER_EXACT_M2_M3_UPPER_V1',
            'scientific_scope':'SMOOTH_HISTORICAL_SOURCE_MATHEMATICAL_EXTENSION_ONLY',
            'source_sha256':EXPECTED_46P3,'parent_sha256':EXPECTED_PARENT_SHA,
            'theorem':'DLMF_I_integer_angle_integral_K_order_monotonic_half_integer_polynomial_global_bound',
            'source_real_power_domain':'all radius >=source binary64(0.02); 4<n<5',
            'float_operation_error_certified':False,
            'source_offgrid_clip_branch_certified':False,
            'D2d_11520_shadow_substituted':False,
            'source_true_continuum_gradient_error_certified':False,
            'mathematical_derivative_supremum_status':'EXACT_CONSERVATIVE_RATIONAL_UPPER_CANDIDATE',
            'external_mathematical_review':'NOT_DONE',
            'full_H_root_error_guard_met':False,
            'original_March_total_H_or_root_count_certified':False,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'subdivisions_per_original_cell':parts,'lenses':[]}
    for i,L in enumerate(smooth['lenses']):
        if limit is not None and i>=limit:break
        B=original['lenses'][i]
        if B['lens_id']!=L['lens_id']:raise ValueError('lens identity mismatch')
        data=z3.read('inputs/'+B['node_file'])
        if sha(data)!=B['node_sha256']:raise ValueError('nodal binary64 checksum mismatch')
        raw=list(struct.iter_unpack('>8d',data))
        if len(raw)!=180:raise ValueError('not original 180 values')
        radii=[Q.from_float(row[0]) for row in raw]
        oldRho=[row[3] for row in raw]
        if any(r<0 for r in oldRho):raise ValueError('source clipped density negative')
        p={k:Q.from_float(float.fromhex(L['source_scalar_binary64_hex'][k]))
           for k in ('Mb','Md','a','Rd','delta','r0','n')}
        if not (4<p['n']<5):raise ValueError('gate exponent unanticipated')
        begin=time.monotonic()
        data=certify_mesh(radii,p,parts=parts)
        elapsed=time.monotonic()-begin
        def allints(key):return [str(ceilQ(v)) for v in data[key]]
        entry={'lens_id':L['lens_id'],'source_node_sha256':B['node_sha256'],
               'source_scalar_hex':L['source_scalar_binary64_hex'],
               'M2_by_cell_upper_ceil':allints('cell_M2'),
               'M3_by_cell_upper_ceil':allints('cell_M3'),
               'ideal_exact_sample_gradient_error_upper_ceil':allints('ideal_gradient_absolute_error_cap'),
               'global_M2_upper_ceil':str(ceilQ(data['max_M2'])),
               'global_M3_upper_ceil':str(ceilQ(data['max_M3'])),
               'max_exact_gradient_error_upper_ceil':str(ceilQ(data['max_gradient_bound'])),
               'first_exact_gradient_error_upper_ceil':str(ceilQ(data['first_gradient_bound'])),
               'last_exact_gradient_error_upper_ceil':str(ceilQ(data['last_gradient_bound'])),
               'certifier':'half_integer_Bessel_exact_rational_v1'}
        result['lenses'].append(entry)
        print('C3_ENVELOPE',L['lens_id'],
              'M2log',len(entry['global_M2_upper_ceil'])-1,
              'M3log',len(entry['global_M3_upper_ceil'])-1,
              'gradientlog',len(entry['max_exact_gradient_error_upper_ceil'])-1,
              'elapsed',round(elapsed,2),flush=True)
    return result
if __name__=='__main__':
    args=sys.argv[1:]
    limit=int(args[0]) if args else None
    parts=int(args[1]) if len(args)>1 else 4
    doc=build(limit=limit,parts=parts)
    p=ROOT/'results/source_bound_M2_M3_rational_producer.json'
    p.write_text(json.dumps(doc,sort_keys=True,indent=2)+'\n')
    print('SHA256',sha(p.read_bytes()))
