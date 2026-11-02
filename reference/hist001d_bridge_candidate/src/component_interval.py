#!/usr/bin/env python3
"""Bound historical 180-node numeric components against distinct finite-proxy math.
Source-executed historical arrays are identity-matched to the prior 180 H arrays;
proxy mass intervals are the pinned strict antecedent, NOT fresh continuum proofs.
"""
from fractions import Fraction as F
import bisect,struct,json,hashlib,zipfile,io,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PI_CERT_SHA='5f74321ad4140640e56bf0a9a3147817879c52c40f4e91eab6487d0b61c36899'
TRACE_SHA='ad549d2e6aaf290a5cfeb31496928f0136191d8a05e92a1bbde6924c36610eab'

def h(b):return hashlib.sha256(b).hexdigest()
def frac(x):return F(int(x['num']),int(x['den']))
def pair(x):return {'num':str(x.numerator),'den':str(x.denominator)}
def floor(x):return x.numerator//x.denominator
def main():
    report_raw=(ROOT/'results/original_180_component_trace.json').read_bytes()
    assert h(report_raw)==TRACE_SHA
    report=json.loads(report_raw)
    with zipfile.ZipFile(ROOT/'inputs/proxy_narrow.zip') as zn:
        sign_raw=zn.read('input/narrow_endpoint_signs.json')
    assert h(sign_raw)==PI_CERT_SHA
    signs=json.loads(sign_raw)
    pi_lo,pi_hi=[frac(z) for z in signs['exact_pi_enclosure']]
    assert 3<pi_lo<pi_hi<F(22,7)
    output=[]
    for src,sign in zip(report['lenses'],signs['lenses'],strict=True):
        lid=src['lens_id'];assert sign['lens_id']==lid
        data=(ROOT/src['component_archive_member']).read_bytes()
        assert h(data)==src['component_file_SHA256'] and len(data)==180*48
        rows=[tuple(F.from_float(z) for z in ar) for ar in struct.iter_unpack('>6d',data)]
        with zipfile.ZipFile(ROOT/'inputs/march_180_grid.zip') as zm:
            original=zm.read('sampled_binary64/'+lid.replace('+','p')+'.R_H_be64.bin')
        for row,(r,H) in zip(rows,struct.iter_unpack('>dd',original),strict=True):
            assert row[0]==F.from_float(r) and row[5]==F.from_float(H)
        radii=[x[0] for x in rows]
        b=sign['rational_bracket_radius']
        # Determine stronger source-conditional difference lower endpoint from original proof.
        with (ROOT/'results/bridge_discrepancy_producer.json').open() as f:
            proc=next(x for x in json.load(f)['lenses'] if x['lens_id']==lid)
        which=proc['max_endpoint_with_strict_disjoint_interval']
        R=frac(b['lower'] if which=='LEFT' else b['upper'])
        cert=sign['left_strict_positive_exact_enclosure'] if which=='LEFT' else sign['right_strict_negative_exact_enclosure']
        i=max(0,min(178,bisect.bisect_right(radii,R)-1)); assert radii[i]<=R<=radii[i+1]
        weight=(R-radii[i])/(radii[i+1]-radii[i])
        vals=[rows[i][j]+weight*(rows[i+1][j]-rows[i][j]) for j in range(6)]
        component_bounds=[]
        for key,nidx,symbol in (('mass_bulge_enclosure_msun',1,'B'),('mass_disk_enclosure_msun',2,'D'),('mass_shadow_enclosure_msun',3,'S')):
            lo,hi=[frac(z) for z in cert[key]]
            dlo,dhi=lo-vals[nidx],hi-vals[nidx]
            component_bounds.append({'symbol':symbol,'math_minus_March_PL_lower':pair(dlo),
                                     'math_minus_March_PL_upper':pair(dhi),
                                     'low_floor_msun':str(floor(dlo)),'high_ceil_msun':str(-floor(-dhi)),
                                     'source_numeric_component_hex':[float(rows[i][nidx]).hex(),float(rows[i+1][nidx]).hex()]})
        sig_lo,sig_hi=[frac(z) for z in cert['G4a_sigma_crit_enclosure_msun_per_kpc2']]
        dlo=pi_lo*sig_lo*R*R-vals[4];dhi=pi_hi*sig_hi*R*R-vals[4]
        component_bounds.append({'symbol':'T','math_minus_March_PL_lower':pair(dlo),
                                 'math_minus_March_PL_upper':pair(dhi),'low_floor_msun':str(floor(dlo)),
                                 'high_ceil_msun':str(-floor(-dhi)),
                                 'source_numeric_component_hex':[float(rows[i][4]).hex(),float(rows[i+1][4]).hex()]})
        # H_March_PL != I(B)+I(D)+I(S)-I(T) exactly, due original binary64 assembly rounding.
        roundoff=vals[5]-(vals[1]+vals[2]+vals[3]-vals[4])
        combined_lo=sum(frac(x['math_minus_March_PL_lower']) for x in component_bounds[:3])-frac(component_bounds[3]['math_minus_March_PL_upper'])-roundoff
        combined_hi=sum(frac(x['math_minus_March_PL_upper']) for x in component_bounds[:3])-frac(component_bounds[3]['math_minus_March_PL_lower'])-roundoff
        pl=vals[5]; direct_lo=F(int(cert['H_lower_msun_integer']))-pl; direct_hi=F(int(cert['H_upper_msun_integer']))-pl
        assert combined_lo<=direct_hi and direct_lo<=combined_hi
        assert all(frac(x['math_minus_March_PL_lower'])>0 for x in component_bounds[:2])
        assert frac(component_bounds[2]['math_minus_March_PL_upper'])<0
        assert frac(component_bounds[3]['math_minus_March_PL_upper'])<0
        output.append({'lens_id':lid,'selected_endpoint':which,'R_exact':pair(R),
          'source_node_edge_index':i,'components_B_D_S_T':component_bounds,
          'signed_original_binary64_assembly_roundoff_exact':pair(roundoff),
          'total_signed_proxy_minus_March_PL_interval_from_components':[pair(combined_lo),pair(combined_hi)],
          'tight_total_signed_proxy_minus_March_PL_interval_from_source_endpoint':[pair(direct_lo),pair(direct_hi)],
          'each_baryon_component_positive_relative_to_180x120':True,
          'finite_shadow_component_negative_relative_to_march_180':True,
          'target_convex_interp_component_negative_relative_to_march':True})
    doc={'schema':'HIST001D_G4B1C_SOURCE_COMPONENT_DISCREPANCY_DECOMPOSITION_v1',
         'status':'PASS_SCOPED_SOURCE_EXACT_180_COMPONENTS_AND_EXTERNAL_CONDITIONAL_FINITE_PROXY_BOUNDS',
         'note':'B, D, S and critical-target T differ between historical 180x120 sampled projection/interpolation and an independently defined finite proxy. Component signs are grounded in archived source output and mathematical intervals; not physical errors or an isolated causal error attribution.',
         'input_original_source_lock_sha256':'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a',
         'source_exact_trace_sha256':TRACE_SHA,'lenses':output,
         'claims':{'component_wise_differences_certified_if_proxy_intervals_sound':True,
                   'one_source_model_or_physically_equivalent':False,
                   'March_solver_full_float_error_certified':False,
                   'physical_provider_admitted':False,'independent_empirical_validation':False}}
    b=(json.dumps(doc,sort_keys=True,separators=(',',':'))+'\n').encode()
    (ROOT/'results/bridge_component_attribution_candidate.json').write_bytes(b)
    print('COMPONENT_PASS',h(b))
    for r in output:
        print(r['lens_id'],r['selected_endpoint'],[(v['symbol'],round(float(frac(v['math_minus_March_PL_lower']))/1e9,3),round(float(frac(v['math_minus_March_PL_upper']))/1e9,3)) for v in r['components_B_D_S_T']])
if __name__=='__main__':main()
