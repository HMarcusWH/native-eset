"""Candidate strict zero exclusion on all other crossing-aperture intervals.

Fail closed on unknown cells. Uses accepted local uniqueness certificates; source-locked
selected M*(r) only; not historical original projected H or physical lensing.
"""
from __future__ import annotations
import json,sys,hashlib,time
from fractions import Fraction as F
from pathlib import Path
from knot_derivative import lens_data,bound_derivative
from quadrature_points import PAIRLIST
from affine_kernel import kernel,kernel_integral
from real_integral_bessel import X
ROOT=Path(__file__).resolve().parents[2]/'results'

def floor(v):return v.numerator//v.denominator
def ceil(v):return -((-v.numerator)//v.denominator)

def gaps(j,timeout_s=210,max_depth=16):
    lens,nodes,leaves,E,t=lens_data(j)
    A0,A1=map(F,t['A_band']);knots=sorted(r for r,w,mp in nodes if A0<r<A1)
    roots=[(F(a),F(b)) for a,b in PAIRLIST[j]]
    if not all(A0<=a<b<=A1 for a,b in roots) or any(x[1]>y[0] for x,y in zip(roots,roots[1:])):
        raise ValueError('root brackets disordered')
    for a,b in roots:
        if any(a<r<=b for r in knots):raise ValueError('root bracket crosses frozen knot')
    cuts=sorted(set([A0,A1]+knots+[x for pair in roots for x in pair]))
    known_roots={(a,b) for a,b in roots}
    cache={}
    def point(A):
        if A in cache:return cache[A]
        Q=L=X(0)
        for r,w,mp in nodes:Q=Q+X(w)*mp*kernel(A,r)
        for d in leaves:L=L+d['slope']*kernel_integral(A,d['a'],d['b'])
        dd=X(Q.lower()-L.upper()-E,Q.upper()-L.lower()+E)
        cache[A]=(Q,L,dd)
        return cache[A]
    def signed(d):return 1 if d.lower()>0 else (-1 if d.upper()<0 else 0)
    intervals=[]
    for a,b in zip(cuts,cuts[1:]):
        if (a,b) in known_roots:continue
        if a<b:intervals.append((a,b))
    out=[];counter={'P':0,'D':0,'X':0};t0=time.time()
    for gi,(L,R) in enumerate(intervals):
        dL=point(L)[2];dR=point(R)[2];sg=signed(dL)
        if sg==0 or sg!=signed(dR):raise ValueError(f'unknown/opposite source signs at gap endpoints {lens} {[float(L),float(R)]} {sg} {signed(dR)}')
        todo=[(L,R,0)];accepted=[]
        while todo:
            if time.time()-t0>timeout_s:raise TimeoutError(f'TIMEOUT after {round(time.time()-t0,2)}s lens={lens}, gap={gi}, verified={len(accepted)}, unprocessed={len(todo)}')
            a,b,depth=todo.pop()
            Qa,La,Da=point(a);Qb,Lb,Db=point(b)
            if sg!=signed(Da) or sg!=signed(Db):
                raise ValueError(f'unverified/genuine additional zero or unresolved point {lens} A={float(a),float(b)} signs={(signed(Da),signed(Db))}')
            low=Qa.lower()-Lb.upper()-E; high=Qb.upper()-La.lower()+E
            if (sg>0 and low>0) or (sg<0 and high<0):
                method='MONOTONE_Q_L_PROJECTION';wlo,wup=low,high;counter['P']+=1
            else:
                derivative=None
                if not any(a<r<=b for r in knots):
                    derivative,_=bound_derivative(nodes,leaves,a,b)
                if derivative is not None and (derivative.lower()>0 or derivative.upper()<0):
                    method='DERIVATIVE_MONOTONE';wlo,wup=min(Da.lower(),Db.lower()),max(Da.upper(),Db.upper());counter['D']+=1
                else:
                    if derivative is not None:
                        dx=b-a; dlo=derivative.lower();dhi=derivative.upper()
                        lo=max(Da.lower()+min(F(0),dlo)*dx,Db.lower()+min(F(0),-dhi)*dx)
                        hi=min(Da.upper()+max(F(0),dhi)*dx,Db.upper()+max(F(0),-dlo)*dx)
                        if (sg>0 and lo>0) or (sg<0 and hi<0):
                            method='DERIVATIVE_ENVELOPE';wlo,wup=lo,hi;counter['X']+=1
                        else:method=''
                    else:method=''
                    if not method:
                        if depth>=max_depth:
                            raise RuntimeError(f'UNKNOWN signed gap cell {lens} gap={gi} depth={depth} interval={[float(a),float(b)]}, D endpoints={[float(Da.lower()),float(Db.upper())]} proxy={[float(low),float(high)]}')
                        mid=(a+b)/2
                        todo.extend([(mid,b,depth+1),(a,mid,depth+1)])
                        continue
            accepted.append({'a':str(a),'b':str(b),'sign':sg,'method':method,'level':depth,
                   'bound_integer_msun':[floor(wlo),ceil(wup)]})
        accepted.sort(key=lambda x:F(x['a']))
        if not accepted or F(accepted[0]['a'])!=L or F(accepted[-1]['b'])!=R or any(F(a['b'])!=F(b['a']) for a,b in zip(accepted,accepted[1:])):raise ValueError('gap coverage')
        out.append({'a':str(L),'b':str(R),'sign':sg,'subpanels':accepted,'accepted_subpanels':len(accepted)})
        print('GAP',lens,gi,'A',[round(float(L),5),round(float(R),5)],'sg',sg,'accepted',len(accepted),'methods',counter,'t',round(time.time()-t0,1),flush=True)
    return {'schema':'HIST001D_SELECTED_MSTAR_D_KNOT_SAFE_SIGN_EXCLUSION_CANDIDATE_V1','lens':lens,
      'original_node_sha256':t['source_node_sha256'],'a_band':[str(A0),str(A1)],
      'source_knots_in_band':[str(k) for k in knots],
      'local_unique_brackets':[[str(a),str(b)] for a,b in roots],
      'gap_blocks':out,'methods':counter,'source_all_real_selected_Mprime_positive':True,
      'all_gaps_excluded':True,'exact_zero_count_with_prior_local_uniqueness':len(roots),
      'original_March_Einstein_root_count_claim':False,'physical_provider_admitted':False,
      'empirical_validation':'NOT_ESTABLISHED'}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--lens',type=int,required=True);p.add_argument('--seconds',type=int,default=210);p.add_argument('--maxdepth',type=int,default=16);o=p.parse_args()
 v=gaps(o.lens,o.seconds,o.maxdepth)
 path=ROOT/f'exclusion_lens_{o.lens}.json';path.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');print('EXCLUDED',v['lens'],'blocks',len(v['gap_blocks']),'SHA',hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
