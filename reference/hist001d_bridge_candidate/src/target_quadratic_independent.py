#!/usr/bin/env python3
"""Independent all-cell exact proof of source quadratic-target interpolant bound.
No primary target_quadratic_exact code imported. No source physical claim.
"""
import hashlib,json,struct
from pathlib import Path
from fractions import Fraction
R=Path(__file__).resolve().parents[1]
SHA='1421d1eea8a43105c6c54805766c3d08924ae3db2e32aa918e52ad8a9acf38b2'
C_SHA='b4bc1211623aee1e65690b2fb382a42cbd159f65c74c8f7d1a01f62dca8438ea'
T_SHA='ad549d2e6aaf290a5cfeb31496928f0136191d8a05e92a1bbde6924c36610eab'
sha=lambda x:hashlib.sha256(x).hexdigest()
q=lambda o:Fraction(int(o['num']),int(o['den']))
def check():
    prod=(R/'results/source_target_quadratic_uniform_bound.json').read_bytes()
    coeff=(R/'results/source_target_coefficient_witness.json').read_bytes()
    trace=(R/'results/original_180_component_trace.json').read_bytes()
    assert sha(prod)==SHA and sha(coeff)==C_SHA and sha(trace)==T_SHA
    rows=json.loads(prod)['lenses'];sigs=json.loads(coeff)['lenses'];inputs=json.loads(trace)['lenses']
    checked=0;cases=0
    for w,coef,src in zip(rows,sigs,inputs,strict=True):
        assert w['lens_id']==coef['lens_id']==src['lens_id']
        raw=(R/src['component_archive_member']).read_bytes()
        assert sha(raw)==src['component_file_SHA256']
        data=list(struct.iter_unpack('>6d',raw))
        x=[Fraction.from_float(row[0]) for row in data]
        y=[Fraction.from_float(row[4]) for row in data]
        C=Fraction.from_float(float.fromhex(coef['source_sigma_crit_float64_hex']))*Fraction.from_float(float.fromhex(coef['source_pi_float64_hex']))
        assert C==q(w['C_source_stored_binary64_product_exact'])
        eps=[y[i]-C*x[i]**2 for i in range(180)]
        m=max(abs(v) for v in eps)
        assert m==q(w['max_binary64_node_target_roundoff_abs_msun_exact'])
        max_D=max(x[i+1]-x[i] for i in range(179))
        upper=C*max_D**2/4+m
        assert upper==q(w['full_real_grid_target_interpolation_sup_error_upper_exact_msun'])
        midpointlower=Fraction(0)
        for i in range(179):
            ri,rj=x[i:i+2]; vi,vj=y[i:i+2]; di,dj=eps[i:i+2];D=rj-ri
            assert D>0
            for t in (Fraction(0),Fraction(1,10),Fraction(1,3),Fraction(1,2),Fraction(4,5),Fraction(1)):
                z=ri+t*D
                line=vi+t*(vj-vi)
                remainder=C*(z-ri)*(rj-z)+(1-t)*di+t*dj
                assert line-C*z*z==remainder,'algebraic identity failed'
                assert abs(line-C*z*z)<=upper,'global inequality failed'
                cases+=1
            mid=(ri+rj)/2
            midpointlower=max(midpointlower,abs((vi+vj)/2-C*mid*mid))
            checked+=1
        assert midpointlower==q(w['full_real_grid_target_interpolation_sup_error_lower_exact_msun'])
        assert midpointlower<=upper
    result={'schema':'HIST001D_SOURCE_TARGET_QUADRATIC_INDEPENDENT_EXACT_ALL_CELL_AUDIT_v1',
            'status':'PASS_SCOPED_179_CELLS_PER_LENS_ALL_R_UNIFORM_ISOLATED_TARGET_TERM',
            'cells_checked':checked,'rational_identity_sample_points_checked':cases,
            'all_source_stored_binary64_coefficients_and_arrays_match':True,
            'scope':'sole target term, not total March source numerical error nor root count',
            'physical_provider_admitted':False,'empirical_validation':False}
    raw=(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n').encode()
    (R/'results/source_target_quadratic_independent.json').write_bytes(raw)
    print('TARGET_INDEPENDENT_PASS',sha(raw),checked,cases)
if __name__=='__main__':check()
