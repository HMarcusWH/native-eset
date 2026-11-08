#!/usr/bin/env python3
"""Strict archive member SHA/CRC, claim guard and protected source-lock verification."""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path

def sha(raw):return hashlib.sha256(raw).hexdigest()

def verify(path:Path):
    with zipfile.ZipFile(path) as z:
        bad=z.testzip()
        if bad:raise ValueError('CRC error '+bad)
        man=json.loads(z.read('MANIFEST_SHA256.json'))
        if man['schema']!='HIST001D_FULL_H_BRIDGE_PROTECTED_SOURCE_MANIFEST_V1':raise ValueError('schema')
        members=set(z.namelist())
        if members!={*man['files'],'MANIFEST_SHA256.json'}:raise ValueError('unexpected/missing member')
        for name,digest in man['files'].items():
            if sha(z.read(name))!=digest:raise ValueError('member SHA mismatch '+name)
        if man['original_source_46plus3_sha256']!='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a':raise ValueError('source authority')
        if man['physical_provider_admitted'] or man['empirical_validation']!='NOT_ESTABLISHED':raise ValueError('claim gate')
        parent=z.read('inputs/HIST001D_MARCH180_K180_SIX_CROSSING_BANDS_CONDITIONAL_v1r2_NONPROMOTING.zip')
        if sha(parent)!='cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77':raise ValueError('previous wholeband evidence parent')
        diagnostic=z.read('inputs/HIST001D_K180_Root_Aperture_Six_Lens_Diagnostic_NONPROOF_v1_2026_11_02.json')
        if sha(diagnostic)!='298a467e6ceab5c48ced00e08ac2fdb1082627eebedb6340139021f090430812':raise ValueError('diagnostic identity')
        receipt=json.loads(z.read('results/full_H_bridge_aggregate.json'))
        qa=json.loads(z.read('results/QA_full_H_bridge.json'))
        independent=json.loads(z.read('results/independent_finite_H_witness_check.json'))
        if not (qa['all_rejected'] and qa['count']==23 and all(x['rejected'] for x in qa['mutations'])):raise ValueError('adversarial QA false')
        if independent['status']!='PASS_CONDITIONAL_EXACT_RATIONAL_FINITE_H_WITNESS' or independent['global_sign_leaves']!=1150 or independent['crossing_derivative_leaves']!=8:raise ValueError('finite witness not replayed')
        if not(receipt['source_PL_finite_full_H_global_one_root_each_6_of_6'] and receipt['selected_Mstar_smooth_full_H_at_least_one_in_each_root_cell_6_of_6']):raise ValueError('unproven result')
        if receipt['selected_smooth_global_root_uniqueness_proved'] or receipt['physical_provider_admitted'] or receipt['empirical_validation']!='NOT_ESTABLISHED':raise ValueError('false science promotion')
        with zipfile.ZipFile(io.BytesIO(parent)) as prior:
            if prior.testzip() is not None:raise ValueError('nested prior ZIP CRC')
            prior_manifest=json.loads(prior.read('MANIFEST_SHA256.json'))
            for name,digest in prior_manifest['files'].items():
                if sha(prior.read(name))!=digest:raise ValueError('nested prior manifest mismatch')
            orig=prior.read('inputs/HIST001D_K180_SATURATED_REVIEW_REPAIR_V1R1_NONPROMOTING_2026_11_02.zip')
            if sha(orig)!='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce':raise ValueError('nested saturation source lock')
    return {'archive_status':'PASS_PROTECTED_FULL_H_RELEASE_INTEGRITY',
            'manifest_sha256_members':len(man['files']),
            'archive_members':len(members),
            'source_46plus3_locked':True,
            'finite_full_H_one_root_6_of_6':True,
            'selected_smooth_root_exists_in_cell_6_of_6':True,
            'selected_smooth_global_uniqueness_proved':False,
            'physical_provider_admitted':False,
            'empirical_validation':'NOT_ESTABLISHED'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('zip_file',type=Path);a=ap.parse_args()
    print(json.dumps(verify(a.zip_file),sort_keys=True,indent=2))
