#!/usr/bin/env python3
"""Separate independent exact rational re-evaluation of March vs finite-proxy mismatch.

No import of bridge_exact or its helper classes. A fixed binary64 bit parser,
weighted-average interpolation and explicit distance-to-interval are used instead.
Remains conditional on the separately source-pinned mathematical proxy endpoint
intervals; not an original continuous March floating/numerical error theorem.
"""
import csv
import hashlib
import io
import json
import struct
import sys
import zipfile
from fractions import Fraction
from pathlib import Path

OLD='7b4e29bd4048a8558af5e7985a9a6ada529e27a7ef4eb068f892f5f3a7bc24b1'
PROXY='138669c971b07652d24b76c34e32cb0a74c3cbc893de3d254c7a5170eec08bb5'
SIGNS='5f74321ad4140640e56bf0a9a3147817879c52c40f4e91eab6487d0b61c36899'
MARCH_REPORT='b845dd11e262a8fab93ce120928a8e5f50d0ff35bd93d26dd00727388367d7cc'
ORIGINAL_ARCH='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
SOURCE='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
NODALKIT='804fd8e26b208c9837638ceee90998843e29b484aa3e5ca794dd5d81b3988973'
LENSES=['J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720']

class IndependentError(Exception):pass
def sh(raw):return hashlib.sha256(raw).hexdigest()
def verify(ok,msg):
    if not ok:raise IndependentError(msg)
def exact_pair(obj):
    verify(isinstance(obj,dict) and set(obj)=={'num','den'},'pair fields wrong')
    return Fraction(int(obj['num']),int(obj['den']))
def byte_float64(bits):
    sign=-1 if bits>>63 else 1
    exp=(bits>>52)&0x7ff
    mant=bits&((1<<52)-1)
    verify(exp!=2047,'nonfinite frozen binary64')
    if exp==0:
        power=-1074
        sig=mant
    else:
        power=exp-1023-52
        sig=(1<<52)|mant
    v=sign*sig
    return Fraction(v*(1<<power)) if power>=0 else Fraction(v,1<<(-power))
def numerical_pairs(blob):
    verify(len(blob)==180*16,'wrong recorded numerical array size')
    vals=[]
    for k in range(180):
        a,b=struct.unpack_from('>QQ',blob,16*k)
        vals.append((byte_float64(a),byte_float64(b)))
    return vals

def attested_archive(raw,expected,name):
    verify(sh(raw)==expected,name+' external archive hash drift')
    z=zipfile.ZipFile(io.BytesIO(raw))
    names=[i.filename for i in z.infolist()]
    verify(len(names)==len(set(names)) and z.testzip() is None,name+' invalid ZIP/duplicate')
    verify(all(not s.startswith('/') and '..' not in s.split('/') for s in names),name+' unsafe path')
    return z

def derive(root):
    zm=attested_archive((root/'inputs/march_180_grid.zip').read_bytes(),OLD,'March 180')
    zp=attested_archive((root/'inputs/proxy_narrow.zip').read_bytes(),PROXY,'Proxy narrow')
    prior=zp.read('input/narrow_endpoint_signs.json')
    recorded=zm.read('original_march_180_grid_exact_dyadic_sampled_residual_diagnostic_v1.json')
    verify(sh(prior)==SIGNS and sh(recorded)==MARCH_REPORT,'source output evidence SHA drift')
    kit=zp.read('input/source_nodal.zip')
    zk=attested_archive(kit,NODALKIT,'Original-source nodal kit')
    lock=json.loads(zk.read('evidence/source_lock_46plus3.json'))
    src=zk.read('source/dma_swells_benchmark_pack_v2_frozen_exact.zip')
    verify(sh(src)==ORIGINAL_ARCH and lock['original_46plus3_composite_sha256']==SOURCE,'original source archive identity')
    with zipfile.ZipFile(io.BytesIO(src)) as zsource:
        verify(len(lock['source_filenames_sha256'])==46,'original 46 files missing')
        for name,pin in lock['source_filenames_sha256'].items():
            verify(sh(zsource.read('swells_pack_v2/'+name))==pin,'original 46 source altered')
    verify(len(lock['archived_negative_controls_sha256'])==3,'three source negative controls missing')
    for name,pin in lock['archived_negative_controls_sha256'].items():
        verify(sh(zk.read('negative_controls/'+name))==pin,'negative control source changed')
    signentries=json.loads(prior)['lenses']
    recentries=json.loads(recorded)['lenses']
    verify(len(signentries)==6 and len(recentries)==6,'six lens identity')
    witness=[]
    for k,name in enumerate(LENSES):
        sn=signentries[k];num=recentries[k]
        verify(sn['lens_id']==name and num['lens_id']==name,'lens changed')
        raw=zm.read('sampled_binary64/'+name.replace('+','p')+'.R_H_be64.bin')
        verify(sh(raw)==num['sampled_binary64_pair_sha256'],'source array hash drift')
        curve=numerical_pairs(raw)
        verify(curve[0][0]==Fraction.from_float(0.02) and curve[-1][0]==120, 'radius bounds')
        verify(all(curve[k][0]<curve[k+1][0] for k in range(179)),'radius not increasing')
        flips=[]
        for t in range(179):
            if curve[t][1]==0 or curve[t+1][1]==0:
                raise IndependentError('sampled zero not covered by scope')
            if curve[t][1]*curve[t+1][1]<0:flips.append(t)
        verify(len(flips)==1,'March sampled sign-change count changed')
        t=flips[0]
        (x,y),(X,Y)=curve[t],curve[t+1]
        root=(x*Y-X*y)/(Y-y)
        verify(root==exact_pair(num['exact_dyadic_piecewise_linear_intervals'][0]['unique_piecewise_linear_root_exact']),'March exact root changed')
        a=exact_pair(sn['rational_bracket_radius']['lower']);b=exact_pair(sn['rational_bracket_radius']['upper'])
        verify(b-a==Fraction(1,10),'proxy 1/10 kpc endpoints changed')
        checks=[]
        for side,R,key in [('LEFT',a,'left_strict_positive_exact_enclosure'),('RIGHT',b,'right_strict_negative_exact_enclosure')]:
            # Linear interpolation using independent barycentric weighted numerator.
            hits=[j for j in range(179) if curve[j][0]<=R<=curve[j+1][0]]
            verify(len(hits)==1,'expected internal radius query unique edge')
            z=hits[0];(x,y),(X,Y)=curve[z],curve[z+1]
            h=( (X-R)*y+(R-x)*Y )/(X-x)
            rec=sn[key]
            verify(exact_pair(rec['R_exact'])==R and rec['all_intermediate_bounds_outward_rational'],'proxy pointwise enclosure mismatch')
            ell=Fraction(int(rec['H_lower_msun_integer']));high=Fraction(int(rec['H_upper_msun_integer']))
            verify(ell<=high,'proxy bound reversed')
            if side=='LEFT':verify(ell>0 and rec['H_lower_strict_positive'],'positive source proxy left')
            else:verify(high<0 and rec['H_upper_strict_negative'],'negative source proxy right')
            if h<ell:
                gap=ell-h
                direction='MARCH_BELOW_PROXY_INTERVAL'
            elif h>high:
                gap=h-high
                direction='MARCH_ABOVE_PROXY_INTERVAL'
            else:
                gap=Fraction(0)
                direction='INTERVALS_OVERLAP'
            checks.append({'side':side,'R_exact':R,'H_march':h,'pointwise_lower':gap,'status':direction,'index':z})
        best=max(checks,key=lambda z:z['pointwise_lower'])
        verify(best['pointwise_lower']>0,'no source-conditional lower bound')
        sep=max(Fraction(0),a-root,root-b)
        witness.append({'lens_id':name,'two_bounds':checks,'best':best,'root_displacement_lower':sep,'one_march_interpolated_root':root})
    return witness

def validate_producer(root,checkfile):
    trusted=derive(root)
    prod=json.loads(Path(checkfile).read_bytes())
    verify(prod['status']=='PASS_SCOPED_CONDITIONAL_EXACT_POINTWISE_MODEL_DIFFERENCE_LOWER_BOUNDS','producer status forged')
    verify(prod['claims']['March_180x120_continuum_discretization_error_certified'] is False and
           prod['claims']['uniform_upper_error_bound_between_models'] is False and
           prod['claims']['original_March_continuum_root_count_certified'] is False and
           prod['claims']['physical_Weyl_provider_admitted'] is False,'invalid science promotion')
    got=prod.get('lenses',[])
    verify(len(got)==len(trusted)==6,'six count in alleged producer')
    for p,w in zip(got,trusted,strict=True):
        verify(p['lens_id']==w['lens_id'],'identity mismatch')
        verify(exact_pair(p['march_interpolant_unique_root_kpc'])==w['one_march_interpolated_root'],'March root differs')
        verify(exact_pair(p['guaranteed_root_position_separation_lower_kpc'])==w['root_displacement_lower'],'root separation differs')
        verify(exact_pair(p['max_certified_endpoint_difference_lower_exact_msun'])==w['best']['pointwise_lower'],'best pointwise lower differs')
        verify(p['max_certified_endpoint_difference_floor_msun']==str(w['best']['pointwise_lower'].numerator//w['best']['pointwise_lower'].denominator),'lower floor differs')
        verify(p['max_endpoint_with_strict_disjoint_interval']==w['best']['side'],'selected endpoint differs')
        verify(len(p['exact_endpoint_discrepancies'])==2,'both endpoint proofs absent')
        for rec,check in zip(p['exact_endpoint_discrepancies'],w['two_bounds'],strict=True):
            verify(rec['side']==check['side'] and exact_pair(rec['R_exact_kpc'])==check['R_exact'] and
                   exact_pair(rec['march_H_exact_interpolated_msun'])==check['H_march'] and
                   exact_pair(rec['proxy_minus_march_abs_difference_lower_exact_msun'])==check['pointwise_lower'] and
                   rec['disposition']==check['status'] and rec['grid_left_index']==check['index'],
                   'endpoint interpolation or interval-distance witness differs')
    return {'schema':'HIST001D_G4B1C_SEPARATE_INDEPENDENT_BINARY64_BITWISE_DISCREPANCY_VERIFICATION_v1',
      'status':'PASS_SCOPED_INDEPENDENT_SOURCE_ATTESTED_EXACT_LOWER_DISCREPANCY_VERIFICATION',
      'six_original_mathematical_differences_pinned_and_independently_verified':True,
      'march_46_source_files_and_3_negative_controls_rehashed_again':True,
      'march_source_180_grid_root_one_per_interpolant':True,
      'exact_same_radii_two_endpoint_comparisons_per_lens':12,
      'claim_ceiling':{'not_numerical_approximation_error_upper':True,'not_original_March_continuum_root_count':True,
                       'not_current_theory_or_physical_Weyl':True,'no_empirical_validation':True},
      'lenses':[{'id':w['lens_id'],'best_pointwise_floor_msun':str(w['best']['pointwise_lower'].numerator//w['best']['pointwise_lower'].denominator),
                 'root_separation_lower_kpc_decimal_display':format(float(w['root_displacement_lower']),'.12f')} for w in trusted]}

def main():
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    path=root/'results/bridge_discrepancy_producer.json'
    obj=validate_producer(root,path)
    raw=(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    out=root/'results/bridge_discrepancy_independent.json';out.write_bytes(raw)
    print('INDEPENDENT PASS',sh(raw),[(x['id'],x['best_pointwise_floor_msun']) for x in obj['lenses']])
if __name__=='__main__':main()
