#!/usr/bin/env python3
"""Independently check the all-real frozen March K180 stencil bound using exact IEEE754 integer decoding.
No imports from producer or original source; rereads source ZIP and immutable original 180 arrays.
"""
from __future__ import annotations
from pathlib import Path
import json,io,hashlib,zipfile,struct,math
from fractions import Fraction as Fr
from math import isqrt
ROOT=Path(__file__).resolve().parents[1]
PINS={
'J0822+1828':'3d354c12839b5bfce41c5e18184250ea8bfcea1f7ef8bc79949d6b92d4cb0938',
'J0915+4211':'ae0c8b7fe618ae9df6ee1de15aef42412f925581d504897d595b0d42aafb9a23',
'J0930+2855':'9a65b32e86ab7ab2f79268fbd883e44dd8f4b7deec2705a09f4d849b0126efae',
'J1021+2028':'4f9b7be29c1e060bc4a0489e4ddcbfff78d66746846b1a61f344b89e8816d9ee',
'J1111+2234':'25dba7a30e6e649ce8ff45e29a1433be2726b58dcbd09e0aac78e7274bab3923',
'J1135+3720':'16e316dea701a1b0863455db24213d3b243d1e5288f6e6578bc0c875e2cf16fd'}

def H(b):return hashlib.sha256(b).hexdigest()
def fdecode(b):
    if len(b)!=8:raise ValueError('binary64 length')
    v=int.from_bytes(b,'big')
    sign=-1 if v>>63 else 1
    exp=(v>>52)&2047;mant=v&((1<<52)-1)
    if exp==2047:raise ValueError('nonfinite source')
    if exp==0:
        factor=mant;shift=1-1023-52
    else:
        factor=(1<<52)+mant;shift=exp-1023-52
    return sign*Fr(factor*(1<<shift),1) if shift>=0 else sign*Fr(factor,1<<-shift)

def read_rows(path):
    content=path.read_bytes()
    if len(content)!=180*8*8:raise ValueError('binary source inventory wrong size')
    records=[]
    for off in range(0,len(content),64):
        records.append(tuple(fdecode(content[off+8*i:off+8*i+8]) for i in range(8)))
    return records,H(content)

def exact_sqrt_enclose(x):
    if x<0:raise ValueError('negative radicand')
    n,d=x.numerator,x.denominator
    a=isqrt(n*d)
    l=Fr(a,d)
    u=l if a*a==n*d else Fr(a+1,d)
    assert l*l<=x<=u*u
    return l,u

def shell(R,s):
    if not 0<R<=s:raise ValueError('not outside radial shell')
    root_lo,root_hi=exact_sqrt_enclose(s*s-R*R)
    return s*(s-root_hi),s*(s-root_lo)

def ceil(x):return -((-x).numerator//(-x).denominator)

def src_auth():
    # This intentionally does not trust the generated capture report for source identity.
    raw=(ROOT/'inputs/original_source_46_frozen.zip').read_bytes()
    assert H(raw)=='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
    lock=json.loads((ROOT/'inputs/original_46plus3_lock.json').read_bytes())
    assert lock['original_46plus3_composite_sha256']=='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
    with zipfile.ZipFile(io.BytesIO(raw)) as original:
        assert original.testzip() is None
        assert len(lock['source_filenames_sha256'])==46
        for path,digest in lock['source_filenames_sha256'].items():
            assert H(original.read('swells_pack_v2/'+path))==digest
    assert len(lock['archived_negative_controls_sha256'])==3
    for path,digest in lock['archived_negative_controls_sha256'].items():
        assert H((ROOT/'inputs/negative_controls'/path).read_bytes())==digest
    with zipfile.ZipFile(ROOT/'inputs/march_180_grid.zip') as z:
        assert z.testzip() is None
    return 'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'

def certify(candidate):
    assert candidate['schema']=='HIST001D_MARCH_180_FROZEN_SOURCE_STENCIL_ALL_REAL_R_PL_ENVELOPE_CANDIDATE_V1'
    assert candidate['claims']['original_total_H_error_bounded'] is False
    assert candidate['claims']['physical_provider_admitted'] is False
    assert candidate['claims']['original_continuum_root_count_proved'] is False
    assert candidate['claims']['q_aperture_or_baryon_projection_error_closed'] is False
    assert candidate['claims']['empirical_validation']=='NOT_ESTABLISHED'
    original=src_auth()
    assert candidate['original_source_lock_sha256']==original
    capture_path=ROOT/'results/source180_capture.json'
    assert H(capture_path.read_bytes())==candidate['source_capture_sha256']
    capture=json.loads(capture_path.read_bytes())
    assert len(candidate['lenses'])==len(capture['lenses'])==6
    firstR=None; independent=[]
    for cand,cap in zip(candidate['lenses'],capture['lenses'],strict=True):
        lid=cand['lens_id']
        assert lid==cap['lens_id'] and lid in PINS
        rows,sourcedigest=read_rows(ROOT/'inputs'/cap['node_file'])
        assert sourcedigest==cap['node_sha256']==cand['original_source_array_record_sha256']
        rr=[r[0] for r in rows]
        if firstR is None:firstR=rr
        assert rr==firstR and rr[0]==fdecode(struct.pack('>d',.02)) and rr[-1]==Fr(120)
        assert all(rr[i]<rr[i+1] for i in range(179))
        assert all(r[1]>0 and r[2]>0 and r[3]>=0 for r in rows)
        raw_rho=b''.join((ROOT/'inputs'/cap['node_file']).read_bytes()[64*i+24:64*i+32] for i in range(180))
        assert H(raw_rho)==PINS[lid]==cand['source_original_density_sha256']
        c=fdecode(struct.pack('>d',4*math.pi))
        all_data=[]
        for comp,offset_in,offset_out in [('BULGE_K180',2,4),('SHADOW_SPHERICAL_K180',3,5)]:
            originalP=[r[offset_out] for r in rows]
            a=[c*r[1]*r[offset_in] for r in rows]
            lo=[];hi=[]
            for i,R in enumerate(rr):
                lower=upper=Fr(0)
                for j,s in enumerate(rr):
                    if j<=i:x=y=s*s
                    else:x,y=shell(R,s)
                    lower+=a[j]*x;upper+=a[j]*y
                assert 0<=lower<=upper
                lo.append(lower);hi.append(upper)
            capnode=max(max(abs(lo[i]-originalP[i]),abs(hi[i]-originalP[i])) for i in range(180))
            assert all(lo[i+1]>=lo[i] and hi[i+1]>=hi[i] for i in range(179)), 'exact kernel monotonic broken'
            maxbound=Fr(0)
            for i in range(179):
                bound=max(Fr(0),hi[i+1]-min(originalP[i],originalP[i+1]),max(originalP[i],originalP[i+1])-lo[i])
                maxbound=max(maxbound,bound)
            rec=next(t for t in cand['component_bounds'] if t['component']==comp)
            assert ceil(capnode)<=int(rec['source_node_max_anchor_gap_upper_msun'])
            assert ceil(maxbound)<=int(rec['max_real_radius_source_stencil_vs_piecewise_linear_bound_upper_msun'])
            all_data.append({'component':comp,'max_source_node_gap_integer_ceil_msun':str(ceil(capnode)),'max_all_real_R_interpolation_bound_integer_ceil_msun':str(ceil(maxbound)),'agrees_with_producer_claims':True})
            print('INDEPENDENT_EXACT180_VERIFY',lid,comp,'node<=',ceil(capnode),'allreal<=',ceil(maxbound),flush=True)
        independent.append({'lens_id':lid,'bounds':all_data})
    return {'schema':'HIST001D_MARCH_180_FROZEN_SOURCE_STENCIL_INDEPENDENT_SOURCE_AND_ALL_CELL_CHECK_V1','status':'PASS_SCOPED_ALL_REAL_FIXED_180_NODE_STENCIL_MATH_ONLY','source_46plus3_sha256':original,'producer_sha256':H((ROOT/'results/frozen_stencil_all_real_envelope_producer.json').read_bytes()),'lenses':independent,'claims':{'full_original_H_error_certified':False,'original_continuum_root_count_proved':False,'source_11520_finite_proxy_substitution':False,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}}

def main():
    p=ROOT/'results/frozen_stencil_all_real_envelope_producer.json'
    d=json.loads(p.read_bytes());z=certify(d)
    raw=(json.dumps(z,sort_keys=True,separators=(',',':'))+'\n').encode()
    (ROOT/'results/frozen_stencil_all_real_envelope_independent.json').write_bytes(raw)
    print('INDEPENDENT_SOURCE180_STENCIL_PASS',H(raw))
if __name__=='__main__':main()
