#!/usr/bin/env python3
"""Exact closed-form uniform source target-INTERPOLATION bound (one isolated term).

For source stored float64 C=pi_float64*sigma_float64 and exactly recorded
binary64 T_i, let delta_i=T_i-C*r_i^2. On each real mesh cell [ri,rj],
I_PL(T)(R)-C*R^2 = C*(R-ri)*(rj-R) + I_PL(delta)(R).
So on entire mesh, abs(error) <= C * max_cell(deltaR)^2/4 + max_node|delta|.
The midpoint values give independent exact lower bounds on the SUPREMUM.
NOT an original full-source continuous residual-error theorem.
"""
from __future__ import annotations
import hashlib,json,struct,sys
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parents[1]
COEF_SHA='b4bc1211623aee1e65690b2fb382a42cbd159f65c74c8f7d1a01f62dca8438ea'
TRACE_SHA='ad549d2e6aaf290a5cfeb31496928f0136191d8a05e92a1bbde6924c36610eab'
sha=lambda b:hashlib.sha256(b).hexdigest()
def pair(x):return {'num':str(x.numerator),'den':str(x.denominator)}
def floor(x):return x.numerator//x.denominator

def run():
    c_raw=(ROOT/'results/source_target_coefficient_witness.json').read_bytes()
    t_raw=(ROOT/'results/original_180_component_trace.json').read_bytes()
    assert sha(c_raw)==COEF_SHA and sha(t_raw)==TRACE_SHA
    cs=json.loads(c_raw)['lenses'];ts=json.loads(t_raw)['lenses'];out=[]
    for a,b in zip(cs,ts,strict=True):
        assert a['lens_id']==b['lens_id'];lid=a['lens_id']
        p=Q.from_float(float.fromhex(a['source_pi_float64_hex']));s=Q.from_float(float.fromhex(a['source_sigma_crit_float64_hex']))
        C=p*s
        assert C>0
        raw=(ROOT/b['component_archive_member']).read_bytes();assert sha(raw)==b['component_file_SHA256']
        rows=[tuple(Q.from_float(x) for x in r) for r in struct.iter_unpack('>6d',raw)]
        r=[x[0] for x in rows];target=[x[4] for x in rows]
        assert len(r)==180 and r[0]==Q.from_float(.02) and r[-1]==120
        shifts=[target[i]-C*r[i]*r[i] for i in range(180)]
        d=max(map(abs,shifts))
        delta=max(r[i+1]-r[i] for i in range(179))
        global_upper=C*delta*delta/4+d
        # Evaluated exact difference at the source cell midpoint, no missing rounding assumption.
        candidates=[]
        for i in range(179):
            midpoint=(r[i]+r[i+1])/2
            linear=(target[i]+target[i+1])/2
            err=abs(linear-C*midpoint*midpoint)
            candidates.append((err,i,midpoint))
        global_lower,index,point=max(candidates,key=lambda x:x[0])
        assert 0<global_lower<=global_upper
        out.append({'lens_id':lid,'pi_source_binary64_hex':a['source_pi_float64_hex'],
         'sigma_source_binary64_hex':a['source_sigma_crit_float64_hex'],
         'C_source_stored_binary64_product_exact':pair(C),
         'max_source_knot_spacing_exact_kpc':pair(delta),
         'max_binary64_node_target_roundoff_abs_msun_exact':pair(d),
         'max_signed_node_roundoff_positive_exact_msun':pair(max(shifts)),
         'min_signed_node_roundoff_negative_exact_msun':pair(min(shifts)),
         'full_real_grid_target_interpolation_sup_error_lower_exact_msun':pair(global_lower),
         'full_real_grid_target_interpolation_sup_error_upper_exact_msun':pair(global_upper),
         'lower_floor_msun':str(floor(global_lower)),
         'upper_ceiling_msun':str(-floor(-global_upper)),
         'witness_sample_cell_index':index,'midpoint_witness_radius_exact':pair(point),
         'finite_source_piecewise_linear_target_numerical_assumption':True,
         'full_H_error_bound_or_physical_validation':False})
    doc={'schema':'HIST001D_MARCH_ORIGINAL_TARGET_SOURCE_BINARY64_COEFFICIENT_AND_PIECEWISE_QUADRATIC_INTERPOLATION_EXACT_V1',
         'status':'PASS_SCOPED_ANALYTIC_UNIFORM_TARGET_INTERPOLATION_BOUND_ONE_ISOLATED_COMPONENT',
         'equation':'I[T_i](R)-C*R^2=C*(R-r_i)*(r_(i+1)-R)+I[T_i-C*r_i^2](R); C=pi_float64*sigma_source_float64 exact stored float64 factors.',
         'scope':'the sole quadratic critical-density target interpolation term, not all original 180x120 source residual, no physical model equivalence',
         'lenses':out,'claims':{'exact_all_R_target_term_lower_and_upper_sup_bounds':True,
          'all_R_total_H_numerical_error_bounded':False,'G4b1c_finite_proxy_equivalent_to_original_March':False,
          'March_continuum_root_count_proved':False,'physical_provider_admitted':False,
          'empirical_validation':'NOT_ESTABLISHED'}}
    raw=(json.dumps(doc,sort_keys=True,separators=(',',':'))+'\n').encode()
    (ROOT/'results/source_target_quadratic_uniform_bound.json').write_bytes(raw)
    print('TARGET_QUADRATIC_PASS',sha(raw))
    for z in out:
        from fractions import Fraction
        q=lambda f:Fraction(int(f['num']),int(f['den']))
        print(z['lens_id'],'tight lower/upper billions Msun',round(float(q(z['full_real_grid_target_interpolation_sup_error_lower_exact_msun']))/1e9,7),round(float(q(z['full_real_grid_target_interpolation_sup_error_upper_exact_msun']))/1e9,7),'node_abs_error_sun',float(q(z['max_binary64_node_target_roundoff_abs_msun_exact'])))
if __name__=='__main__':run()
