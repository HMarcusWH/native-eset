#!/usr/bin/env python3
"""Assemble six independent protected source-dependent band witnesses into a fail-closed receipt.

A numerical receipt is NOT a physical lensing, root-uniqueness or validation claim.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'hist001d_k180_root_aperture_candidate'))
from root_aperture_certifier import load_external,load_apertures,SOURCE_SHA,PARENT_SHA,DIAGNOSTIC_SHA  # noqa: E402
from crossing_band_certifier import q_source_metadata,q_monotonic_all_cells,band_geometry,Lens,euler_gamma  # noqa: E402
from verify_band_witness import validate,adversarial  # noqa: E402
from fractions import Fraction as F

SCHEMA='HIST001D_MARCH180_SIX_CROSSING_APERTURE_BANDS_CONDITIONAL_V1'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def assemble(external:Path,diagnostic:Path,result_dir:Path):
    caps,infos,rows=load_external(external)
    root_diag=load_apertures(diagnostic)
    qmeta=q_source_metadata(external)
    gamma=euler_gamma()
    proofs=[];radii={}
    for k,(c,info,row,q,d) in enumerate(zip(caps,infos,rows,qmeta,root_diag)):
        lens=Lens(c,info,row,gamma);lens.rows=row; lens.node_sha=c['node_sha256']
        q_b=F.from_float(float.fromhex(q['source_qb_hex']))
        q_d=F.from_float(float.fromhex(q['source_qd_hex']))
        q_margin=q_monotonic_all_cells(lens,q_b,q_d)
        index,r0,r1,a0,a1=band_geometry(lens,q_b,q_d,F.from_float(d['sampled_R_root_kpc']))
        proof=json.loads((result_dir/f'lens{k}.json').read_text())
        if (proof['lens']!=c['lens_id'] or proof['root_R_cell_index']!=index or
            proof['original_180_source_node_sha256']!=c['node_sha256'] or
            proof['R_cell_left_binary64_hex']!=float(r0).hex() or
            proof['R_cell_right_binary64_hex']!=float(r1).hex() or
            proof['A_band_left_exact_n_over_d']!=[str(a0.numerator),str(a0.denominator)] or
            proof['A_band_right_exact_n_over_d']!=[str(a1.numerator),str(a1.denominator)] or
            proof['q_b_original_hex']!=q['source_qb_hex'] or
            proof['q_d_original_hex']!=q['source_qd_hex'] or
            proof['q_monotonic_lower_exact']!=[str(q_margin.numerator),str(q_margin.denominator)]):
            raise ValueError('mismatch between protected source, q/R/A geometry and lens proof: '+c['lens_id'])
        radii[c['lens_id']]=lens.r
        proofs.append(proof)
    receipt={
        'schema':SCHEMA,'date':'2026-11-02',
        'external_saturation_archive_sha256':digest(external),
        'original_source_parent_sha256':PARENT_SHA,
        'original_46plus3_source_sha256':SOURCE_SHA,
        'diagnostic_A_input_sha256':digest(diagnostic),
        'source_defined_aperture_bands_are_mathematical_PL_q':True,
        'all_six_crossing_aperture_bands_positive':True,
        'all_original_nodes_frozen_and_sha_locked':True,
        'selected_smooth_mathematical_mass_not_ESET_physical_source':True,
        'independent_Bessel_engine_or_external_referee_completed':False,
        'original_off_grid_H_root_count_proved':False,
        'same_source_physical_lensing_proved':False,
        'physical_provider_admitted':False,
        'empirical_validation':'NOT_ESTABLISHED',
        'lenses':proofs,
    }
    if receipt['diagnostic_A_input_sha256']!=DIAGNOSTIC_SHA:raise ValueError('wrong diagnostic SHA')
    minval=validate(receipt,radii)
    negatives=adversarial(receipt,radii)
    return receipt,negatives,minval

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--external-zip',required=True,type=Path)
    p.add_argument('--diagnostic-json',required=True,type=Path)
    p.add_argument('--result-dir',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    p.add_argument('--adversarial-out',required=True,type=Path)
    a=p.parse_args()
    r,qa,minval=assemble(a.external_zip,a.diagnostic_json,a.result_dir)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    a.adversarial_out.write_text(json.dumps({'schema':'HIST001D_BAND_WITNESS_ADVERSARIAL_QA_V1',
          'cases':qa,'all_rejected':True,'no_physical_promotion':True},indent=2,sort_keys=True)+'\n')
    print('SIX_BAND_SOURCE_BOUND_CERTIFICATE',len(r['lenses']),'MIN',minval,'QA_REJECTED',len(qa),
          'RECEIPT_SHA256',digest(a.out),flush=True)
if __name__=='__main__':main()
