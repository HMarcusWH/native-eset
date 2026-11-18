#!/usr/bin/env python3
"""Assemble immutable, fail-closed mathematical full-H bridge from source receipts.

Only named PL off-grid frozen-March H and selected mathematical smooth shadow H.
No physical or empirical provider, no original off-grid floating solver theorem.
"""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from fractions import Fraction as F
from pathlib import Path
from full_h_finite_source import load_source,LENSES,SOURCE_SHA
from verify_full_h_witness import verify as verify_finite

SOURCE_ARCHIVE_SHA='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
BAND_ARCHIVE_SHA='cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77'
DIAGNOSTIC_SHA='298a467e6ceab5c48ced00e08ac2fdb1082627eebedb6340139021f090430812'

def sha(data):return hashlib.sha256(data).hexdigest()

def verify_inputs(source,band_archive,diag):
    for p,x in ((source,SOURCE_ARCHIVE_SHA),(band_archive,BAND_ARCHIVE_SHA),(diag,DIAGNOSTIC_SHA)):
        if not p.is_file() or sha(p.read_bytes())!=x:raise ValueError('wrong protected archive/dataset hash: '+p.name)
    with zipfile.ZipFile(band_archive) as z:
        manifest=json.loads(z.read('MANIFEST_SHA256.json'))
        for path,digest in manifest['files'].items():
            if sha(z.read(path))!=digest:raise ValueError('whole-band protected manifest mismatch')
        whole=json.loads(z.read('results/whole_band_certificate.json'))
        derivatives=[json.loads(z.read(f'results/selected_mass_prime_{i}.json')) for i in range(6)]
    if whole['original_46plus3_source_sha256']!=SOURCE_SHA or whole['all_six_crossing_aperture_bands_positive'] is not True:
        raise ValueError('whole band theory/source gate')
    return whole,derivatives

def build(finite,source,diag,band_archive,endpoint_dir,out):
    whole,derivatives=verify_inputs(source,band_archive,diag)
    finite_receipt=json.loads(finite.read_text())
    caps,qs,arrays,env,diagnostics=load_source(source,diag)
    witness=None
    # Independent arithmetic / coverage verification is run again, rather
    # than accepting a previously generated PASS label.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        with zipfile.ZipFile(band_archive) as z:
            path=Path(td)/'band_result.json'
            path.write_bytes(z.read('results/whole_band_certificate.json'))
        witness=verify_finite(finite,source,diag,path)
    rows=[]
    for i in range(6):
        f=finite_receipt['lenses'][i]
        s=json.loads((endpoint_dir/f'selected_H_endpoint_{i}.json').read_text())
        b=whole['lenses'][i]
        d=derivatives[i]
        node_gap=env[i]['component_bounds'][1]['source_node_max_anchor_gap_upper_exact']
        E=F(int(node_gap['n']),int(node_gap['d']))
        if any(v!=LENSES[i] for v in (f['lens'],s['lens'],b['lens'],d['lens'])):raise ValueError('six-lens alignment')
        if b['original_180_source_node_sha256']!=caps[i]['node_sha256'] or s['node_sha256']!=caps[i]['node_sha256'] or d['source_180_node_sha256']!=caps[i]['node_sha256']:
            raise ValueError('misbound original 180 source')
        if not 0<=E<1:raise ValueError('unsupported nodal interp bridge')
        if not (f['global_offgrid_PL_source_other_cells_excluded'] and f['H_source_strictly_decreasing_full_root_cell'] and f['global_offgrid_other_cells_unknown']==0 and f['derivative_unresolved']==0):
            raise ValueError('finite full H uniqueness missing')
        if not f['original_sample_root_is_not_root_of_this_offgrid_finite_model']:
            raise ValueError('sample-root identity distinct not demonstrated')
        if not (s['selected_continuum_H_has_root_in_source_cell'] and s['selected_Mprime_all_real_positive_certificate'] and d['selected_mathematical_Mstar_prime_positive_everywhere'] is True and d['unresolved_cells']==0):
            raise ValueError('selected smooth source-root existence missing')
        # The finite certificate records exact fractions; the endpoint receipt
        # records the original binary64 knot spelling. Check the same knot.
        L=F(int(f['R_left_n_over_d'][0]),int(f['R_left_n_over_d'][1]))
        if s['R_cell_left_binary64_hex']!=float(L).hex():raise ValueError('R left alignment')
        R=F(int(f['R_right_n_over_d'][0]),int(f['R_right_n_over_d'][1]))
        if s['R_cell_right_binary64_hex']!=float(R).hex():raise ValueError('R right alignment')
        if s['H_selected_left_integer_Msun_lower']<=0 or s['H_selected_right_integer_Msun_upper']>=0:
            raise ValueError('smooth crossing sign unresolved')
        if b['status']!='PASS_POSITIVE_FOR_ENTIRE_APERTURE_BAND' or b['unknown_subbands']:
            raise ValueError('whole band proof missing')
        band_lower=b['minimum_gap_lower_floor_Msun']
        if band_lower<=1:raise ValueError('band gap too narrow for nodal floor')
        rec={'lens':LENSES[i], 'source_root_one_per_whole_original_180_domain':True,
             'finite_source_unique_root_bracket_exact_rational':f['root_bracket'],
             'finite_source_unique_root_bracket_rounded_kpc':f['root_bracket_rounded'],
             'original_sampled_root_kpc':diagnostics[i]['sampled_R_root_kpc'],
             'historical_sampled_root_not_source_PL_finite_H_root':True,
             'H_source_at_original_reported_root_integer_Msun':f['source_H_at_original_sample_root_interval_integer_Msun'],
             'H_selected_continuum_left_lower_integer_Msun':s['H_selected_left_integer_Msun_lower'],
             'H_selected_continuum_right_upper_integer_Msun':s['H_selected_right_integer_Msun_upper'],
             'root_cell_source_k':f['root_cell_index'],
             'selected_continuum_H_has_at_least_one_root_strictly_left_of_finite_root':True,
             'selected_continuum_roots_in_cell_to_right_of_finite_root_excluded':True,
             'selected_continuum_global_root_uniqueness_proved':False,
             'whole_band_QminusP_mathematical_gap_lower_integer_Msun':band_lower,
             'source_S0_PL_minus_Q_lower_strictly_greater_than_minus_1_Msun':True,
             'full_H_source_minus_H_smooth_strictly_greater_than_integer_Msun':band_lower-1,
             'source_node_gap_upper_exact':[node_gap['n'],node_gap['d']],
             'global_non_crossing_H_sign_subbands':f['global_offgrid_other_cells_signed_subbands'],
             'root_cell_derivative_subbands':f['derivative_certified_subcells']}
        rows.append(rec)
    receipt={'schema':'HIST001D_MARCH180_FULL_H_PL_SOURCE_VS_SELECTED_SMOOTH_MATHEMATICAL_BRIDGE_V1',
             'original_source_46plus3_sha256':SOURCE_SHA,
             'source_archive_sha256':SOURCE_ARCHIVE_SHA,
             'whole_band_archive_sha256':BAND_ARCHIVE_SHA,
             'source_aperture_diagnostic_sha256':DIAGNOSTIC_SHA,
             'finite_witness':witness,
             'source_PL_finite_full_H_global_one_root_each_6_of_6':True,
             'selected_Mstar_smooth_full_H_at_least_one_in_each_root_cell_6_of_6':True,
             'selected_smooth_roots_in_original_cell_strictly_left_of_finite_PL_roots':True,
             'selected_smooth_global_root_uniqueness_proved':False,
             'full_original_March_arbitrary_radius_floating_H_error_proved':False,
             'current_native_ESET_1_7_2_lensing_provider_validated':False,
             'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
             'lenses':rows}
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('ASSEMBLED',len(rows),'lenses',witness['global_sign_leaves'],'global signed subbands',flush=True)
    return receipt

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    for k in ['finite','source','diag','band_archive','endpoint_dir','out']:
        ap.add_argument('--'+k.replace('_','-'),type=Path,required=True,dest=k)
    a=ap.parse_args()
    build(a.finite,a.source,a.diag,a.band_archive,a.endpoint_dir,a.out)
