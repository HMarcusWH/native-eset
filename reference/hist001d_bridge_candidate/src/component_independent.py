#!/usr/bin/env python3
"""Independent rational audit of source-replayed 180-grid component decomposition.
Uses independent weighted interpolation and reconstructs intervals from original
frozen records, without importing the primary component_interval module.
"""
from __future__ import annotations
import json,hashlib,struct,zipfile
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[1]
COMP='c9d0cf9fc627ef8b7f1e955acd5799668793c01d788f6a97b0b82769b0a17302'
SOURCE='ad549d2e6aaf290a5cfeb31496928f0136191d8a05e92a1bbde6924c36610eab'
SIGN='5f74321ad4140640e56bf0a9a3147817879c52c40f4e91eab6487d0b61c36899'
sha=lambda b:hashlib.sha256(b).hexdigest()
frac=lambda x:Fraction(int(x['num']),int(x['den']))
def run():
    source=(ROOT/'results/original_180_component_trace.json').read_bytes()
    certraw=(ROOT/'results/bridge_component_attribution_candidate.json').read_bytes()
    assert sha(source)==SOURCE and sha(certraw)==COMP
    traces=json.loads(source)['lenses']
    comp=json.loads(certraw)
    with zipfile.ZipFile(ROOT/'inputs/proxy_narrow.zip') as z:
        narrow_raw=z.read('input/narrow_endpoint_signs.json')
    assert sha(narrow_raw)==SIGN
    signs=json.loads(narrow_raw)
    pi_lo,pi_hi=map(frac,signs['exact_pi_enclosure'])
    assert 3<pi_lo<pi_hi<Fraction(22,7)
    out=[]
    for tr,sign,pr in zip(traces,signs['lenses'],comp['lenses'],strict=True):
        lid=tr['lens_id'];assert lid==sign['lens_id']==pr['lens_id']
        original=(ROOT/tr['component_archive_member']).read_bytes()
        assert sha(original)==tr['component_file_SHA256'] and len(original)==180*48
        mesh=list(struct.iter_unpack('>6d',original))
        bnd=sign['rational_bracket_radius'];side=pr['selected_endpoint']
        R=frac(bnd['lower'] if side=='LEFT' else bnd['upper'])
        assert R==frac(pr['R_exact'])
        # Brute-force exact vector interpolation; separate algebraic numerator form.
        ids=[i for i in range(179) if Fraction.from_float(mesh[i][0])<=R<=Fraction.from_float(mesh[i+1][0])]
        assert len(ids)==1
        j=ids[0];x=Fraction.from_float(mesh[j][0]);y=Fraction.from_float(mesh[j+1][0])
        derived=[]
        for col in range(6):
            a=Fraction.from_float(mesh[j][col]);b=Fraction.from_float(mesh[j+1][col]);derived.append(((y-R)*a+(R-x)*b)/(y-x))
        source_bound=sign['left_strict_positive_exact_enclosure'] if side=='LEFT' else sign['right_strict_negative_exact_enclosure']
        reconstructed=[]
        for k,source_key in enumerate(['mass_bulge_enclosure_msun','mass_disk_enclosure_msun','mass_shadow_enclosure_msun']):
            l,h=map(frac,source_bound[source_key]);reconstructed.append((l-derived[k+1],h-derived[k+1]))
        l,h=map(frac,source_bound['G4a_sigma_crit_enclosure_msun_per_kpc2'])
        reconstructed.append((pi_lo*l*R*R-derived[4],pi_hi*h*R*R-derived[4]))
        for pair,field in zip(reconstructed,pr['components_B_D_S_T'],strict=True):
            assert pair[0]==frac(field['math_minus_March_PL_lower'])
            assert pair[1]==frac(field['math_minus_March_PL_upper'])
        roundoff=derived[5]-sum(derived[1:4])+derived[4]
        assert roundoff==frac(pr['signed_original_binary64_assembly_roundoff_exact'])
        lower=sum(z[0] for z in reconstructed[:3])-reconstructed[3][1]-roundoff
        upper=sum(z[1] for z in reconstructed[:3])-reconstructed[3][0]-roundoff
        assert [lower,upper]==list(map(frac,pr['total_signed_proxy_minus_March_PL_interval_from_components']))
        direct=(Fraction(int(source_bound['H_lower_msun_integer']))-derived[5],Fraction(int(source_bound['H_upper_msun_integer']))-derived[5])
        assert direct==tuple(map(frac,pr['tight_total_signed_proxy_minus_March_PL_interval_from_source_endpoint']))
        assert lower<=direct[1] and direct[0]<=upper
        assert reconstructed[0][0]>0 and reconstructed[1][0]>0 and reconstructed[2][1]<0 and reconstructed[3][1]<0
        out.append({'lens_id':lid,'source_trace_sha256':tr['component_file_SHA256'],
        'historical_H_bitwise_matching':tr['component_reassembles_original_H_byte_exact'],
        'exact_binary64_component_interpolation_verified':True,'component_signs':{'B':'+','D':'+','S':'-','T':'-'},
        'source_float_assembly_roundoff_abs_msun_display':format(float(abs(roundoff)),'.8g'),
        'sum_interval_exact_consistent_with_total_residual_inclusion':True})
    report={'schema':'HIST001D_G4B1C_INDEPENDENT_SOURCE_COMPONENT_RATIONAL_REVIEW_v1',
            'status':'PASS_SCOPED_INDEPENDENT_COMPONENT_INTERPOLATION_AND_INTERVAL_ALGEBRA',
            'lenses':out,'claim_limits':{'not_original_continuum_numerical_error_certified':True,
                                        'different_shadow_interpolant_models':True,
                                        'no_physical_provider_or_empirical_validation':True}}
    b=(json.dumps(report,sort_keys=True,separators=(',',':'))+'\n').encode()
    (ROOT/'results/bridge_component_independent.json').write_bytes(b)
    print('COMPONENT_INDEPENDENT_PASS',sha(b),[(x['lens_id'],x['source_float_assembly_roundoff_abs_msun_display']) for x in out])
if __name__=='__main__':run()
