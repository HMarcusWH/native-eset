#!/usr/bin/env python3
"""Fail-closed tests for twelve source-locked mathematical root-neighbor claims."""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path

from crossing_node_independent import check

ROOT=Path(__file__).resolve().parent

def mutate(doc,case):
    d=copy.deepcopy(doc)
    q=d['lenses'][0];n=q['two_crossing_source_nodes'][0]
    if case=='bad_schema':d['schema']='UNSIGNED_FAKE';return d
    if case=='wrong_parent':d['parent_sha256']='0'*64;return d
    if case=='wrong_source':d['original_46plus3_sha256']='0'*64;return d
    if case=='source_substitution':d['source_11520_shadow_substituted']=True;return d
    if case=='false_float_bound':d['original_general_float_operation_error_certified']=True;return d
    if case=='false_root_theorem':d['original_full_H_root_error_certified']=True;return d
    if case=='false_physical_provider':d['physical_provider_admitted']=True;return d
    if case=='false_empirical_validation':d['empirical_validation']='ESTABLISHED';return d
    if case=='node_count_wrong':d['node_count']=13;return d
    if case=='missing_lens':d['lenses'].pop();return d
    if case=='crossing_edge_wrong':q['sampled_final_H_sign_change_edge']+=1;return d
    if case=='source_sha_wrong':q['node_array_sha256']='0'*64;return d
    if case=='source_radius_wrong':n['source_radius_float_hex']='0x1.0p+1';return d
    if case=='source_rho_wrong':n['source_rho_float_hex']='0x1.0p+1';return d
    if case=='source_stored_gradient_wrong':n['source_mass_gradient_stored_exact']='1234';return d
    if case=='source_node_index_wrong':n['node_index']+=1;return d
    if case=='fake_stencil_pass':n['stored_minus_ideal_3point_fd_abs_strict_lt_1e_minus_3_msun_per_kpc']=False;return d
    if case=='understate_error_ceiling':n['stored_minus_ideal_3point_fd_abs_ceil_micro_msun_per_kpc']=0;return d
    if case=='overstate_gap':n['stored_minus_smooth_derivative_strict_lower_integer_msun_per_kpc']+=100000;return d
    if case=='overstate_ratio':n['stored_over_smooth_derivative_ratio_strict_floor_millipercent']+=100000;return d
    if case=='overstate_minimum':q['minimal_certified_smooth_derivative_gap_integer_msun_per_kpc']+=100000;return d
    raise ValueError('unknown negative case')

CASES=['bad_schema','wrong_parent','wrong_source','source_substitution','false_float_bound',
       'false_root_theorem','false_physical_provider','false_empirical_validation','node_count_wrong',
       'missing_lens','crossing_edge_wrong','source_sha_wrong','source_radius_wrong',
       'source_rho_wrong','source_stored_gradient_wrong','source_node_index_wrong',
       'fake_stencil_pass','understate_error_ceiling','overstate_gap','overstate_ratio','overstate_minimum']

def run(save=True):
    candidate=json.loads((ROOT/'results/crossing_node_producer.json').read_bytes())
    bad=[]
    for tag in CASES:
        edited=mutate(candidate,tag)
        try:
            with contextlib.redirect_stdout(io.StringIO()):check(edited,save=False)
        except (ValueError,TypeError,KeyError,IndexError,ArithmeticError,ZeroDivisionError):
            bad.append({'case':tag,'rejected':True})
        else:
            raise AssertionError('unsafe counterfeit proof accepted: '+tag)
    if len(bad)!=len(CASES):raise AssertionError('adversarial count inconsistent')
    report={'schema':'HIST001D_12_ROOT_NEIGHBOR_TAMPER_QA_V1','expected_rejections':len(CASES),
            'actual_rejections':len(bad),'all_intended_invalid_claims_rejected':True,
            'cases':bad,'no_original_full_H_error_theorem':True,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    if save:
        out=ROOT/'results/crossing_node_adversarial.json'
        out.write_bytes((json.dumps(report,sort_keys=True,indent=2)+'\n').encode())
        print('ADVERSARIAL_REJECTED',len(bad), 'SHA256',hashlib.sha256(out.read_bytes()).hexdigest())
    return report
if __name__=='__main__':run()
