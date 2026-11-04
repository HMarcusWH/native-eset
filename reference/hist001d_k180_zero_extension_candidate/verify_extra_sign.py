#!/usr/bin/env python3
"""Independent 192-bit rational checker of THREE additional selected-M* sign witnesses.

Reads the immutable protected PR63 ZIP and its already verified Peano bounds,
then reassembles the selected derivative-sampled Q and refined mass interpolant
with a separate independent kernel implementation. No SciPy, no source producer
interval class, no physics claim.
"""
from __future__ import annotations
import json,hashlib,struct,sys,zipfile,os
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(os.environ.get('HIST001D_PRIOR_EXTRACT_DIR', Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(ROOT/'reference/hist001d_k180_targeted_candidate'))
from verify_targeted import load,phi,jprim

ZIP=Path(os.environ.get('HIST001D_PRIOR_ARCHIVE', Path(__file__).resolve().parents[2]/'inputs'/'targeted_parent_v1.zip'))
PARENT_SHA='0eec91a8e531516529a58cf811685581233aba6d5bc8150c9897b50de88ae651'
INDICES={0:25,3:33,5:29}

def sha(b):return hashlib.sha256(b).hexdigest()
def floor(x):return x.numerator//x.denominator
def ceil(x):return -((-x.numerator)//x.denominator)

def run():
    if sha(ZIP.read_bytes())!=PARENT_SHA:raise ValueError('protected PR63 parent SHA mismatch')
    top=zipfile.ZipFile(ZIP)
    manifest=json.loads(top.read('MANIFEST_SHA256.json'))
    assert len(manifest['files'])==36
    for name,h in manifest['files'].items():
        if sha(top.read(name))!=h:raise ValueError('parent member SHA mismatch: '+name)
    audit=json.loads(top.read('results/independent_fraction_audit.json'))
    if not audit['all_pass'] or audit['total_distinct_zeros_at_least']!=10 or len(audit['lenses'])!=6:
        raise ValueError('prior independent audited lower bound missing')
    z,iz,src,capture,analytic,bands=load()
    results=[]
    for j,index in INDICES.items():
        obj=json.loads(top.read(f'results/targeted_lens_{j}.json'))
        if sha(top.read(f'results/targeted_lens_{j}.json'))!=audit['lenses'][j]['source_receipt_sha256'] or not audit['lenses'][j]['verified']:
            raise ValueError('prior source audit/receipt mismatch')
        nodal=json.loads(iz.read(f'results/lens_{j}.json'))['lenses'][0]
        radial=json.loads(iz.read(f'results/continuous_lens_{j}.json'))
        raw=src.read('inputs/'+capture[j]['node_file'])
        if sha(raw)!=capture[j]['node_sha256'] or nodal['node_file_sha256']!=capture[j]['node_sha256']:
            raise ValueError('source node identity')
        rows=list(struct.iter_unpack('>8d',raw))
        if len(rows)!=180 or len(nodal['nodes'])!=180:raise ValueError('node count')
        pts={}
        radius_weights=[]
        for row,v in zip(rows,nodal['nodes']):
            r=F.from_float(row[0]);pts[r]=tuple(map(F,v['selected_M_interval']))
            radius_weights.append((r,F.from_float(row[1]),tuple(map(F,v['selected_Mprime_interval']))))
        for mid in radial['midpoints']:
            r=F(mid['r']);pts[r]=tuple(map(F,mid['M']))
        active={}
        for k,rec in enumerate(radial['panels']):
            a,b=F(rec['lo']),F(rec['hi'])
            if a not in pts or b not in pts:raise ValueError('initial radial gap')
            active[(k,a,b)]=0
        for v in obj['split_history']:
            k=int(v['origin']);a=F(v['a']);b=F(v['b']);m=F(v['mid']);dep=int(v['depth'])
            if m!=(a+b)/2 or (k,a,b) not in active or active.pop((k,a,b))!=dep-1:
                raise ValueError('bad canonical split geometry')
            if m in pts:raise ValueError('duplicate dyadic midpoint')
            pts[m]=tuple(map(F,v['M']))
            active[(k,a,m)]=dep;active[(k,m,b)]=dep
        ordered=sorted(active,key=lambda q:q[1]);
        if len(ordered)!=obj['refined_radial_panels'] or any(u[2]!=v[1] for u,v in zip(ordered,ordered[1:])):
            raise ValueError('refined mesh coverage gap')
        A0,A1=map(F,obj['A_band']);A=A0+(A1-A0)*F(index,128)
        Qlo=Qhi=F()
        for r,w,(mp0,mp1) in radius_weights:
            q=phi(A,r)
            if mp0<=0 or w<=0:raise ValueError('positive derivative-weight premise')
            Qlo+=w*mp0*q.lower();Qhi+=w*mp1*q.upper()
        Llo=Lhi=F()
        for k,a,b in ordered:
            m0,m1=pts[a],pts[b]
            slope0=(m1[0]-m0[1])/(b-a);slope1=(m1[1]-m0[0])/(b-a)
            if slope0<=0:raise ValueError('positive selected mass interpolation slope')
            J=jprim(A,a,b)
            Llo+=slope0*J.lower();Lhi+=slope1*J.upper()
        E=F(obj['E_symmetric_ceiling_integer_Msun'])
        lo=Qlo-Lhi-E;hi=Qhi-Llo+E
        if lo<=0:raise ValueError('independent additional positive sign is not certified')
        old=[(int(a['index']),int(a['strict_sign'])) for a in obj['anchors']]
        if any(x[0]==index for x in old):raise ValueError('additional witness already claimed')
        sequence=sorted(old+[(index,1)])
        zeros=sum(s!=t for (_,s),(_,t) in zip(sequence,sequence[1:]))
        if zeros!=obj['certified_distinct_zero_lower_bound']+2:
            raise ValueError('independent added crossing count mismatch')
        out={'lens':obj['lens'],'additional_index':index,'A_exact':str(A),
             'independent_D_outward_integer_Msun':[floor(lo),ceil(hi)],
             'prior_zero_lower_bound':obj['certified_distinct_zero_lower_bound'],
             'augmented_zero_lower_bound':zeros,
             'prior_receipt_sha256':sha(top.read(f'results/targeted_lens_{j}.json'))}
        print('INDEPENDENT_PASS',obj['lens'],index,[floor(lo),ceil(hi)],'zeros>=',zeros,flush=True)
        results.append(out)
    count=sum(x['augmented_zero_lower_bound'] for x in results)+sum(audit['lenses'][j]['zeros_at_least'] for j in (1,2,4))
    if count!=16:raise ValueError('six-lens lower bound not 16')
    combined={'schema':'HIST001D_ADDITIONAL_ZERO_192BIT_FRACTION_VERIFY_V1',
              'prior_ten_zero_receipt_sha256':sha(top.read('results/targeted_aggregate.json')),
              'parent_release_sha256':PARENT_SHA,'extra_witnesses':results,
              'certified_total_distinct_zeros_at_least':count,
              'exact_zero_count_proved':False,'Einstein_root_count_proved':False,
              'physical_provider_admitted':False,
              'empirical_validation':'NOT_ESTABLISHED'}
    path=Path(os.environ.get('HIST001D_ZERO_OUT_DIR', Path(__file__).resolve().parents[2]/'results'))/'extra_fraction_verify.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(combined,sort_keys=True,indent=2)+'\n')
    print('SIX_LENS_INDEPENDENT_PASS zeros>=',count,'SHA',sha(path.read_bytes()))

if __name__=='__main__':run()
