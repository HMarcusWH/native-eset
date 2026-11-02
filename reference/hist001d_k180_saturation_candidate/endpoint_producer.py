#!/usr/bin/env python3
"""Narrow conditional exact-real selected smooth-M first/last endpoint K180 comparison.
This is not a general error theorem or physical density model.
"""
from __future__ import annotations
import zipfile,io,json,struct,hashlib
from fractions import Fraction as F
from pathlib import Path
from all180_math import euler_gamma, source_mass
from signed_gap_contract import source_return_minus_k180_from_legacy
ROOT=Path(__file__).resolve().parent
TOP_SHA='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'

def sha(b):return hashlib.sha256(b).hexdigest()
def ceil(x:F):return -((-x.numerator)//x.denominator)
def floor(x:F):return x.numerator//x.denominator

def open_input():
    raw=(ROOT/'original_parent.zip').read_bytes()
    if sha(raw)!=TOP_SHA:raise ValueError('source parent invalid')
    p=zipfile.ZipFile(io.BytesIO(raw))
    q=zipfile.ZipFile(io.BytesIO(p.read('inputs/frozen_source_parent.zip')))
    d=zipfile.ZipFile(io.BytesIO(q.read('inputs/original_march_D120_q_parent.zip')))
    s=zipfile.ZipFile(io.BytesIO(d.read('inputs/original_march180_parent_v1r1.zip')))
    original=zipfile.ZipFile(io.BytesIO(s.read('inputs/original_source_46_frozen.zip')))
    lock=json.loads(s.read('inputs/original_46plus3_lock.json'))
    assert lock['original_46plus3_composite_sha256']==SOURCE_SHA
    for key,val in lock['source_filenames_sha256'].items():
        assert sha(original.read('swells_pack_v2/'+key))==val
    for key,val in lock['archived_negative_controls_sha256'].items():
        assert sha(s.read('inputs/negative_controls/'+key))==val
    capture=json.loads(s.read('results/source180_capture.json'))['lenses']
    info=json.loads(p.read('results/producer_analytic_source_gradient.json'))['lenses']
    return s,capture,info

def calculate():
    s,capture,info=open_input()
    assert len(capture)==len(info)==6
    gamma=euler_gamma()
    out=[]
    for c,sm in zip(capture,info):
        assert c['lens_id']==sm['lens_id']
        raw=s.read('inputs/'+c['node_file'])
        assert len(raw)==180*64 and sha(raw)==c['node_sha256']
        rows=list(struct.iter_unpack('>8d',raw));r=[F.from_float(row[0]) for row in rows]
        w=[F.from_float(row[1]) for row in rows]
        rho=[F.from_float(row[3]) for row in rows]
        assert all(r[i]<r[i+1] for i in range(179))
        assert all(x>=0 for x in rho) and all(x>0 for x in w)
        hexes=sm['source_scalar_binary64_hex'];params={key:F.from_float(float.fromhex(hexes[key])) for key in ('Mb','Md','a','Rd','delta','r0','n')}
        C=F.from_float(float.fromhex(hexes['C4pi']))
        masslo,masshi=source_mass(r[0],params,gamma)[0],source_mass(r[-1],params,gamma)[0]
        continuous_mass=masshi-masslo
        assert continuous_mass.low()>0
        original_projection_return=F.from_float(rows[-1][5])
        raw_K180=sum((w[i]*C*r[i]*r[i]*rho[i] for i in range(180)),F())
        discrepancy=raw_K180-continuous_mass
        source_report_gap=raw_K180-original_projection_return
        h=[r[i+1]-r[i] for i in range(179)]
        wmath=[h[0]/2]+[(h[i-1]+h[i])/2 for i in range(1,179)]+[h[-1]/2]
        weightdelta=sum((abs(w[i]-wmath[i])*C*r[i]**2*rho[i] for i in range(180)),F())
        legacy_signed_gap=[floor(source_report_gap*10**6),ceil(source_report_gap*10**6)]
        v={
            'lens_id':c['lens_id'], 'source_180_node_sha256':c['node_sha256'],
            'original_exact_binary64_R0':r[0].hex() if hasattr(r[0],'hex') else rows[0][0].hex(),
            'support_source_Rmax_binary64':rows[-1][0].hex(),
            'source_46plus3_sha256':SOURCE_SHA,
            'selected_mathematical_Msh_mass_change_interval_integer_Msun':[floor(continuous_mass.low()),ceil(continuous_mass.high())],
            'recorded_original_S0_at_Rmax_source_binary64_Msun':rows[-1][5].hex(),
            'K180_original_stored_weight_exact_rational_minus_continuum_mass_interval_integer_micro_Msun':[floor(discrepancy.low()*10**6),ceil(discrepancy.high()*10**6)],
            'source_float_S0_at_Rmax_minus_exact_K180_integer_micro_Msun':legacy_signed_gap,
            'source_float_S0_at_Rmax_minus_exact_K180_CORRECTED_integer_micro_Msun':source_return_minus_k180_from_legacy(legacy_signed_gap),
            'legacy_signed_field_warning':'V1_LEGACY_KEY_IS_K180_MINUS_S0_NOT_S0_MINUS_K180',
            'original_weight_vs_ideal_exact_mesh_weight_error_upper_micro_Msun':ceil(weightdelta*10**6),
            'source_specific_K180_vs_smooth_M_endpoints_absolute_error_upper_milli_Msun':ceil(discrepancy.bound_abs()*10**3),
            'original_source_S0_at_Rmax_vs_smooth_M_endpoints_absolute_error_upper_milli_Msun':ceil((continuous_mass-F.from_float(rows[-1][5])).bound_abs()*10**3),
            'mathematical_scope':'SELECTED_SMOOTH_ACCELERATION_EQUIVALENT_MSH_ONLY_NOT_PHYSICAL_DENSITY',
            'Rmax_120_saturation_only':True,
            'original_March_full_R_continuum_error_certified':False,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
        }
        out.append(v)
        print('LENS',c['lens_id'],'|Qsrc-I|<',v['source_specific_K180_vs_smooth_M_endpoints_absolute_error_upper_milli_Msun']/1000,'Msun','S0rounded',v['original_source_S0_at_Rmax_vs_smooth_M_endpoints_absolute_error_upper_milli_Msun']/1000,flush=True)
    obj={'schema':'HIST001D_SOURCE_FROZEN_MARCH180_K180_SATURATION_ENDPOINT_IDENTITY_PRODUCER_V1',
         'source_original_46plus3':SOURCE_SHA,'source_original_parent_sha256':TOP_SHA,'lenses':out,
         'global_uniform_aperture_quadrature_error_proved':False,'saturated_aperture_only':True,
         'no_regenerated_D2d_11520_shadow':True,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    output=ROOT/'endpoint_saturation_producer.json'
    output.write_bytes((json.dumps(obj,sort_keys=True,indent=2)+'\n').encode())
    print('OUTPUT_SHA',sha(output.read_bytes()))
    return obj
if __name__=='__main__':calculate()
