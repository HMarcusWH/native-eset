#!/usr/bin/env python3
"""Source-dependent supplemental selected M* quadrature sign probes.
Reads immutable PR63 protected release; data-dependent result is not public.
Never asserts uniqueness, physical lensing, or true original March off-grid roots.
"""
from __future__ import annotations
import sys,json,time,hashlib,os
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(os.environ.get('HIST001D_PRIOR_EXTRACT_DIR', Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(ROOT/'reference/hist001d_k180_targeted_candidate'))
from targeted_refine import original, sp, X, kernel_integral, LENSES
from signed_affine_producer import kernel
EXTRA={0:25,3:33,5:29}

def recompute(j):
    started=time.time()
    src=ROOT/'results'/f'targeted_lens_{j}.json'
    rec=json.loads(src.read_text())
    assert rec['lens']==LENSES[j]
    lens,source,p,panels=original(j)
    _,_,nodes,_=sp.endpoints(j)
    active={ (panel.origin,panel.a,panel.b) :(panel.pa['M'],panel.pb['M'],panel.depth) for panel in panels }
    for split in rec['split_history']:
        origin=int(split['origin']);a=F(split['a']);b=F(split['b']);mid=F(split['mid']);d=split['depth']
        assert mid==(a+b)/2
        old=active.pop((origin,a,b))
        assert old[2]+1==d
        Mmid=X(F(split['M'][0]),F(split['M'][1]))
        active[(origin,a,mid)]=(old[0],Mmid,d)
        active[(origin,mid,b)]=(Mmid,old[1],d)
    ordered=sorted(active.items(),key=lambda x:x[0][1])
    assert len(ordered)==rec['refined_radial_panels']
    assert all(x[0][2]==y[0][1] for x,y in zip(ordered,ordered[1:]))
    assert ordered[0][0][1]==panels[0].a and ordered[-1][0][2]==panels[-1].b
    idx=EXTRA[j];Alo,Ahi=map(F,rec['A_band']);A=Alo+(Ahi-Alo)*F(idx,128)
    Q=X(0)
    for r,w,mp in nodes:
        Q+=X(w)*mp*kernel(A,r)
    L=X(0)
    for (_,a,b),(ma,mb,_) in ordered:
        L+=(mb-ma)/(b-a)*kernel_integral(A,a,b)
    E=F(rec['E_symmetric_exact'])
    lo=Q.lower()-L.upper()-E;hi=Q.upper()-L.lower()+E
    assert lo>0, (lens,idx,float(lo),float(hi))
    # Distinct additional brackets when spliced into the existing strict witness sequence
    old_anchors=rec['anchors'];anchors=sorted([(int(x['index']),int(x['strict_sign'])) for x in old_anchors]+[(idx,1)])
    cnt=sum(1 for x,y in zip(anchors,anchors[1:]) if x[1]!=y[1])
    assert cnt>=rec['certified_distinct_zero_lower_bound']+2
    result={'lens':lens,'index':idx,'A_exact':str(A),'Q':[str(Q.lower()),str(Q.upper())],
            'Lrefined':[str(L.lower()),str(L.upper())],'E_symmetric_exact':str(E),
            'D_interval':[str(lo),str(hi)],'D_outward_integer_Msun':[lo.numerator//lo.denominator,-(-hi.numerator//hi.denominator)],
            'strict_sign':1,'existing_zero_lower_bound':rec['certified_distinct_zero_lower_bound'],
            'expanded_zero_lower_bound':cnt,'source_parent_receipt_sha256':hashlib.sha256(src.read_bytes()).hexdigest()}
    print('DONE',lens,'at',round(float(A),9),'D_enclosure_Msun',result['D_outward_integer_Msun'],'old',result['existing_zero_lower_bound'],'new',cnt,'secs',round(time.time()-started,2),flush=True)
    return result

if __name__=='__main__':
    entries=[recompute(j) for j in EXTRA]
    dest=Path(os.environ.get('HIST001D_ZERO_OUT_DIR', Path(__file__).resolve().parents[2]/'results'))/'extra_sign_witnesses.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps({'schema':'HIST001D_SELECTED_MSTAR_ADDITIONAL_STRICT_SIGN_WITNESSES_V1',
                                'status':'SOURCE_CONDITIONAL_MATHEMATICAL_CANDIDATE_NONPROMOTING',
                                'lenses':entries,'sum_lower_bound':sum(x['expanded_zero_lower_bound'] for x in entries)+2+3+2,
                                'original_zero_lower_bound':10,
                                'additional_witnesses_count':3,
                                'exact_zero_count_proved':False,'Einstein_root_count_proved':False,
                                'no_new_Bessel_evaluations':True,
                                'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'},sort_keys=True,indent=2)+'\n')
    print('SHA',hashlib.sha256(dest.read_bytes()).hexdigest())
