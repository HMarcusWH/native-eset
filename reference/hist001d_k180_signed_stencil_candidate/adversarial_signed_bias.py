#!/usr/bin/env python3
"""Fail-closed protected-result adversarial QA; independent checker is judge."""
import argparse,copy,hashlib,json,tempfile
from pathlib import Path
from verify_signed_bias import check

def sha(b):return hashlib.sha256(b).hexdigest()
def qa(upstream,point,band,original,out):
    base=json.loads(original.read_text())
    checks=[]
    def test(label,modify):
        trial=copy.deepcopy(base);modify(trial)
        with tempfile.TemporaryDirectory(prefix='hist001d-bias-adversarial-') as temp:
            f=Path(temp)/'tampered.json';f.write_text(json.dumps(trial,sort_keys=True)+'\n')
            try:check(upstream,point,band,f)
            except (ValueError,KeyError,IndexError,TypeError,AssertionError,ZeroDivisionError):
                checks.append({'case':label,'result':'REJECTED'});return
        raise AssertionError('tampered certificate passed: '+label)
    test('missing_lens',lambda z:z['lenses'].pop())
    test('duplicate_lens',lambda z:z['lenses'][0].update(lens=z['lenses'][1]['lens']))
    test('reorder_lenses',lambda z:z['lenses'].reverse())
    test('fake_source_46plus3',lambda z:z.update(original_46plus3_source_sha256='0'*64))
    test('fake_upstream_sha',lambda z:z.update(parent_upstream_sha256='0'*64))
    test('fake_fixedA_sha',lambda z:z.update(parent_fixed_A_sha256='0'*64))
    test('fake_band_sha',lambda z:z.update(parent_six_band_sha256='0'*64))
    test('wrong_schema',lambda z:z.update(schema='not-the-math'))
    test('wrong_node_sha',lambda z:z['lenses'][0].update(node_sha256='0'*64))
    test('wrong_point_A',lambda z:z['lenses'][0].update(A_diagnostic_hex='0x1.0p+0'))
    test('altered_band_left',lambda z:z['lenses'][0].update(A_band_left_rational=['1','2']))
    test('altered_band_right',lambda z:z['lenses'][2].update(A_band_right_rational=['100','1']))
    test('understated_point_lower',lambda z:z['lenses'][0].update(Q_source_minus_Q_sampled_exact_Mprime_integer_Msun=[999999999,9999999999]))
    test('understated_point_upper',lambda z:z['lenses'][0].update(Q_source_minus_Q_sampled_exact_Mprime_integer_Msun=[0,1]))
    test('altered_total_prior',lambda z:z['lenses'][0].update(Q_source_minus_continuum_Pstar_prior_integer_Msun=[1,2]))
    test('understated_quadrature_lower',lambda z:z['lenses'][0].update(Q_sampled_exact_Mprime_minus_continuum_Pstar_integer_Msun=[0,9000000000]))
    test('understated_quadrature_upper',lambda z:z['lenses'][2].update(Q_sampled_exact_Mprime_minus_continuum_Pstar_integer_Msun=[-999999999,0]))
    test('wrong_quadrature_sign',lambda z:z['lenses'][0].update(quadrature_remainder_sign_at_diagnostic='POSITIVE'))
    test('understated_prior_stencil_budget',lambda z:z['lenses'][0].update(inherited_source_vs_ideal_MassStencil_all_aperture_micro_Msun_upper=0))
    test('understated_ideal_stencil_bias',lambda z:z['lenses'][0].update(Q_ideal_MassStencil_minus_Q_sampled_exact_Mprime_integer_Msun=[999999999,9999999999]))
    test('false_ideal_whole_band_floor',lambda z:z['lenses'][0].update(ideal_mass_stencil_bias_full_band_min_lower_Msun=99999999999))
    test('false_point_positive',lambda z:z['lenses'][1].update(node_bias_strictly_positive_at_diagnostic=False))
    test('false_band_positive',lambda z:z['lenses'][1].update(node_bias_full_band_positive=False))
    test('missing_band_panel',lambda z:z['lenses'][0].update(panels=[]))
    test('modified_panel_lower',lambda z:z['lenses'][0]['panels'][0].update(node_bias_lower_floor_Msun=9999999999))
    test('modified_panel_upper',lambda z:z['lenses'][0]['panels'][0].update(node_bias_upper_ceil_Msun=1))
    test('broken_panel_coverage',lambda z:z['lenses'][0]['panels'][0].update(upper=['4','1']))
    test('wrong_panel_minimum',lambda z:z['lenses'][1].update(node_bias_full_band_min_lower_Msun=0))
    test('fabricate_unresolved_panel',lambda z:z['lenses'][1].update(unknown_count=1))
    test('false_global_band_pass',lambda z:z.update(all_six_bandwise_bias_positive=False))
    test('false_global_point_pass',lambda z:z.update(all_six_pointwise_bias_positive=False))
    test('false_global_quadrature_pass',lambda z:z.update(all_six_fixed_A_quadrature_remainder_sign_resolved=False))
    test('promote_physical_provider',lambda z:z.update(physical_provider_admitted=True))
    test('promote_empirical_validation',lambda z:z.update(empirical_validation='VALIDATED'))
    test('promote_per_lens_provider',lambda z:z['lenses'][0].update(selected_smooth_Mstar_physical_provider=True))
    test('false_independent_new_Bessel_engine',lambda z:z.update(independent_new_Bessel_engine_in_this_packet=True))
    test('falsely_mark_smooth_mass_physical',lambda z:z.update(source_continuum_is_selected_mathematical_Mstar_not_physical=False))
    test('promote_full_H_physical_roots',lambda z:z.update(full_H_physical_root_count_or_weyl_proved=True))
    test('remove_inherited_Bessel_prereq',lambda z:z.update(inherited_512bit_Bessel_all180_derivative_enclosure=False))
    if len(checks)!=39:raise AssertionError('QA case inventory not 39: '+str(len(checks)))
    outobj={'schema':'HIST001D_SIGNED_BIAS_ADVERSARIAL_QA_V1','all_rejected':True,'cases':checks,
            'claim_scope':'SOURCE_CONDITIONAL_MATHEMATICAL_ONLY','physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    out.write_text(json.dumps(outobj,sort_keys=True,indent=2)+'\n')
    print('QA_REJECTED',len(checks),'SHA',sha(out.read_bytes()),flush=True)
    return outobj

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    for key in ['upstream','point','band','receipt','out']:
        ap.add_argument('--'+key,type=Path,required=True)
    a=ap.parse_args();qa(a.upstream,a.point,a.band,a.receipt,a.out)
