#!/usr/bin/env python3
"""Independent directed 128-bit knot/Peano verifier; no producer imports.

Source-dependent interval inputs are protected serialized boxes, derived from
authenticated prior candidate receipts. This verifies derivative inequalities,
strict endpoint signs, full radial-knot and aperture coverage, not physics.
"""
from __future__ import annotations
import hashlib,json,sys,time
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'results'
BITS=128
S=1<<BITS

def cdiv(a,b):return -(-a//b)
def fl(x):return x.numerator//x.denominator
def ce(x):return -((-x.numerator)//x.denominator)
class I:
 __slots__=('a','b')
 def __init__(self,a,b=None,raw=False):
  if raw:self.a,self.b=int(a),int(a if b is None else b)
  else:
   lo=F(a);hi=lo if b is None else F(b)
   self.a=fl(lo*S);self.b=ce(hi*S)
  if self.a>self.b:raise ValueError('inverted interval')
 @classmethod
 def conv(cls,o):return o if isinstance(o,cls) else cls(o)
 def lo(self):return F(self.a,S)
 def hi(self):return F(self.b,S)
 def __add__(self,v):
  v=self.conv(v);return I(self.a+v.a,self.b+v.b,True)
 __radd__=__add__
 def __neg__(self):return I(-self.b,-self.a,True)
 def __sub__(self,v):return self+-self.conv(v)
 def __rsub__(self,v):return self.conv(v)+-self
 def __mul__(self,v):
  v=self.conv(v);vals=[x*y for x in (self.a,self.b) for y in (v.a,v.b)]
  return I(min(vals)//S,cdiv(max(vals),S),True)
 __rmul__=__mul__
 def inv(self):
  if self.a<=0<=self.b:raise ZeroDivisionError('interval containing zero')
  # signed intervals not needed for reciprocal; formula for positives only
  if self.a<0:raise ValueError('negative reciprocal unsupported in independent check')
  return I((S*S)//self.b,cdiv(S*S,self.a),True)
 def __truediv__(self,v):return self*self.conv(v).inv()
 def __rtruediv__(self,v):return self.conv(v)*self.inv()
 def square(self):
  a,b=self.a,self.b
  if a<=0<=b:return I(0,cdiv(max(a*a,b*b),S),True)
  return I(min(a*a,b*b)//S,cdiv(max(a*a,b*b),S),True)

def sqrtbox(v):
 v=I.conv(v)
 if v.a<0:raise ValueError('negative sqrt')
 l=isqrt(v.a*S);h=isqrt(v.b*S)
 if h*h<v.b*S:h+=1
 return I(l,h,True)

def arctanbox(v):
 v=I.conv(v)
 if v.a<0:raise ValueError('negative arctan')
 factor=1
 for _ in range(32):
  if 4*v.b<=S:break
  v=v/(1+sqrtbox(1+v.square()));factor*=2
 else:raise ValueError('arctan reduction did not terminate')
 # Alternating odd-power series. End at k=19 (negative) for lower and
 # k=18 (positive) for upper. Cross-dependency handled by intervals.
 vv=v.square();term=v;sm=v;up=None;low=None
 for k in range(1,20):
  term=-term*vv
  sm=sm+term/F(2*k+1)
  if k==18:up=sm.hi()
  if k==19:low=sm.lo()
 return I(factor*low,factor*up)

def node_kernel(A,r):
 A,r=F(A),F(r)
 if A>=r:return I(1)
 if not(0<=A<r):raise ValueError('node_kernel A domain')
 return 1-sqrtbox(1-I(A/r).square())

def deriv_kernel(A,r):
 A,r=F(A),F(r)
 if not(0<A<r):raise ValueError('derivative kernel domain')
 return I(A)/(I(r)*sqrtbox(I(r*r-A*A)))

def weight_omega(A,a,b):
 A,a,b=F(A),F(a),F(b)
 if not(0<A and 0<a<b):raise ValueError('omega domain')
 if A>=b:return I(0)
 U=sqrtbox(I(b*b-A*A))
 if A>=a:return arctanbox(U/I(A))
 V=sqrtbox(I(a*a-A*A))
 return arctanbox(I(A)*(U-V)/(I(A*A)+U*V))

def cylinder_cell(A,a,b):
 A,a,b=F(A),F(a),F(b)
 if A<=0 or not 0<a<b:raise ValueError('cylinder_cell domain')
 if A>=b:return I(b-a)
 m=max(a,A)
 U=sqrtbox(I(b*b-A*A));V=I(0) if m==A else sqrtbox(I(m*m-A*A))
 delta=arctanbox(I(A)*(U-V)/(I(A*A)+U*V))
 res=I(b-a)-(U-V)+I(A)*delta
 if res.lo()<0 or res.hi()>b-a:raise ValueError('cylinder cell integral out of range')
 return res

def read(j):
 d=json.loads((ROOT/f'inputs_lens_{j}.json').read_text())
 if d['schema']!='HIST001D_SOURCE_LOCKED_MSTAR_KNOT_AUDIT_INPUTS_V1':raise ValueError('input schema')
 if d['physical_provider_admitted'] is not False or d['empirical_validation']!='NOT_ESTABLISHED':raise ValueError('physical claims')
 nodes=[]
 for v in d['nodes']:
  nodes.append((F(v['r']),F(v['w']),I(F(v['Mp'][0]),F(v['Mp'][1]))))
 leaves=[]
 for v in d['leaves']:
  a,b=F(v['a']),F(v['b']);h=b-a;C=F(v['C'])
  ma=I(F(v['M_a'][0]),F(v['M_a'][1]));mb=I(F(v['M_b'][0]),F(v['M_b'][1]))
  mpa=I(F(v['Mp_a'][0]),F(v['Mp_a'][1]));mpb=I(F(v['Mp_b'][0]),F(v['Mp_b'][1]))
  slope=(mb-ma)/I(h)
  lo=min(mpa.lo(),mpb.lo())-C*h/2
  hi=max(mpa.hi(),mpb.hi())+C*h/2
  if lo<=0 or slope.lo()<=0:raise ValueError('nonpositive inherited selected mass derivative')
  leaves.append((a,b,h,slope,C,lo,hi))
 if len(nodes)!=180 or len(leaves)<179:raise ValueError('source dimensions')
 if any(nodes[k][0]>=nodes[k+1][0] for k in range(179)):raise ValueError('source radial order')
 if any(leaves[k][1]!=leaves[k+1][0] for k in range(len(leaves)-1)):raise ValueError('radial coverage')
 if leaves[0][0]!=nodes[0][0] or leaves[-1][1]!=nodes[-1][0]:raise ValueError('original mesh support')
 band=list(map(F,d['A_band']));E=F(d['Peano_symmetric_exact'])
 if not(0<band[0]<band[1]<nodes[-1][0] and E>0):raise ValueError('band geometry')
 return d,nodes,leaves,band,E

def point(A,nodes,leaves,E):
 q=l=I(0)
 for r,w,mp in nodes:q=q+I(w)*mp*node_kernel(A,r)
 for a,b,h,s,C,lo,hi in leaves:l=l+s*cylinder_cell(A,a,b)
 return q,l,I(q.lo()-l.hi()-E,q.hi()-l.lo()+E)

def dp_box(a,b,nodes,leaves,precise=False):
 # All node radii must lie strictly outside (a,b]; on a radius knot,
 # the one-sided derivative from the right is used.
 a,b=F(a),F(b)
 if not 0<a<b:raise ValueError('derivative interval')
 if any(a<r<=b for r,w,mp in nodes):raise ValueError('straddles source knot')
 qlo=qhi=I(0)
 for r,w,mp in nodes:
  if r>a:
   qlo=qlo+I(w)*mp*deriv_kernel(a,r)
   qhi=qhi+I(w)*mp*deriv_kernel(b,r)
 p_lo=p_hi=I(0)
 for c,d,h,s,C,mlo,mhi in leaves:
  if d<=a:continue
  if c>b:
   # Same proof but independent interval arithmetic, full primitive optional.
   if precise:
    omega_lo=weight_omega(a,c,d);omega_hi=weight_omega(b,c,d)
   else:
    omega_lo=I(h)*deriv_kernel(a,(c+d)/2)
    omega_hi=I(h)*(deriv_kernel(b,c)+deriv_kernel(b,d))/2
   term=I(C*h*h/8)*(deriv_kernel(b,c)-deriv_kernel(b,d))
   p_lo=p_lo+s*I(omega_lo.lo())-I(term.hi())
   p_hi=p_hi+s*I(omega_hi.hi())+I(term.hi())
  else:
   wl=weight_omega(a,c,d);wr=weight_omega(b,c,d)
   top=weight_omega(max(a,min(c,b)),c,d)
   p_lo=p_lo+I(mlo*min(wl.lo(),wr.lo()))
   p_hi=p_hi+I(mhi*top.hi())
 return I(qlo.lo()-p_hi.hi(),qhi.hi()-p_lo.lo())

# signed lower/upper envelopes by derivative MVT at both endpoints
def envelope(dl,dr,deriv,a,b):
 dx=F(b)-F(a)
 low=max(dl.lo()+min(F(0),deriv.lo())*dx,dr.lo()+min(F(0),-deriv.hi())*dx)
 high=min(dl.hi()+max(F(0),deriv.hi())*dx,dr.hi()+max(F(0),-deriv.lo())*dx)
 return low,high

def verify_lens(j):
 d,nodes,leaves,band,E=read(j)
 local=json.loads((ROOT/f'local_lens_{j}.json').read_text())
 excl=json.loads((ROOT/f'exclusion_lens_{j}.json').read_text())
 if local['lens']!=d['lens'] or excl['lens']!=d['lens']:raise ValueError('lens identities')
 if local['original_source_node_sha256']!=d['original_180_node_sha256'] or excl['original_node_sha256']!=d['original_180_node_sha256']:raise ValueError('source node identity')
 cache={};n_deriv=0;method_count={'P':0,'D':0,'X':0};root_count=0
 def get(A):
  if A not in cache:cache[A]=point(A,nodes,leaves,E)
  return cache[A]
 knots=sorted(r for r,w,mp in nodes if band[0]<r<band[1])
 if [str(r) for r in knots]!=excl['source_knots_in_band']:raise ValueError('knot list')
 for root in local['roots']:
  L,R=F(root['a']),F(root['b']);sg=root['expected_monotone_derivative']
  if any(L<r<=R for r in knots):raise ValueError('root bracket hits a knot')
  if len(root['derivative_panels'])!=root['accepted_panels']:raise ValueError('root panel count')
  dl=get(L)[2];dr=get(R)[2]
  if not ((sg==1 and dl.hi()<0<dr.lo()) or (sg==-1 and dr.hi()<0<dl.lo())):raise ValueError('root endpoints not strict')
  bars=sorted(root['derivative_panels'],key=lambda x:F(x['a']))
  if F(bars[0]['a'])!=L or F(bars[-1]['b'])!=R or any(F(x['b'])!=F(y['a']) for x,y in zip(bars,bars[1:])):raise ValueError('root panel gap')
  for e in bars:
   a,b=F(e['a']),F(e['b']);deriv=dp_box(a,b,nodes,leaves)
   if (sg==1 and deriv.lo()<=0) or (sg==-1 and deriv.hi()>=0):
    deriv=dp_box(a,b,nodes,leaves,precise=True)
    if (sg==1 and deriv.lo()<=0) or (sg==-1 and deriv.hi()>=0):raise ValueError(f'UNKNOWN independent Dprime sign on root {d["lens"]} {float(a),float(b)}')
   n_deriv+=1
  root_count+=1

 blocks=excl['gap_blocks']
 if len(blocks)!=len(excl['gap_blocks']):raise ValueError('gap count')
 support=[]
 for root in local['roots']:support.append((F(root['a']),F(root['b']),'root'))
 for block in blocks:
  L,R=F(block['a']),F(block['b']);sg=block['sign'];pieces=sorted(block['subpanels'],key=lambda x:F(x['a']))
  if len(pieces)!=block['accepted_subpanels'] or not pieces:raise ValueError('gap panel count')
  if F(pieces[0]['a'])!=L or F(pieces[-1]['b'])!=R or any(F(x['b'])!=F(y['a']) for x,y in zip(pieces,pieces[1:])):raise ValueError('gap panel coverage')
  support.append((L,R,'gap'))
  for item in pieces:
   a,b=F(item['a']),F(item['b']);Qa,La,Da=get(a);Qb,Lb,Db=get(b)
   if sg==1:
    if not (Da.lo()>0 and Db.lo()>0):raise ValueError('positive gap endpoints')
   else:
    if not (Da.hi()<0 and Db.hi()<0):raise ValueError('negative gap endpoints')
   meth=item['method'];bounds=(Qa.lo()-Lb.hi()-E,Qb.hi()-La.lo()+E)
   if meth=='MONOTONE_Q_L_PROJECTION':
    if (sg==1 and bounds[0]<=0) or (sg==-1 and bounds[1]>=0):raise ValueError('gap proxy cannot exclude zero')
    method_count['P']+=1
   elif meth in ('DERIVATIVE_MONOTONE','DERIVATIVE_ENVELOPE'):
    deriv=dp_box(a,b,nodes,leaves)
    if meth=='DERIVATIVE_MONOTONE':
     if not (deriv.lo()>0 or deriv.hi()<0):
      deriv=dp_box(a,b,nodes,leaves,precise=True)
     if not (deriv.lo()>0 or deriv.hi()<0):raise ValueError('gap derivative not monotone')
     method_count['D']+=1
    else:
     low,high=envelope(Da,Db,deriv,a,b)
     if (sg==1 and low<=0) or (sg==-1 and high>=0):
      deriv=dp_box(a,b,nodes,leaves,precise=True)
      low,high=envelope(Da,Db,deriv,a,b)
     if (sg==1 and low<=0) or (sg==-1 and high>=0):raise ValueError('gap Dprime envelope failed')
     method_count['X']+=1
   else:raise ValueError('unknown proof method')
 support.sort()
 if not support or support[0][0]!=band[0] or support[-1][1]!=band[1]:raise ValueError('aperture support ends')
 if any(x[1]!=y[0] for x,y in zip(support,support[1:])):raise ValueError('aperture band unproved gap/overlap')
 if root_count!=len(local['roots']) or root_count!=excl['exact_zero_count_with_prior_local_uniqueness']:raise ValueError('root number')
 return dict(lens=d['lens'],root_brackets=root_count,derivative_panels=n_deriv,
    exclusion_panels=sum(q['accepted_subpanels'] for q in blocks),proof_methods=method_count,
    knots=len(knots),checked_Q_L_endpoints=len(cache),all_real_A_band_excluded_outside_unique_brackets=True,
    selected_mathematical_D_exact_zero_count=root_count,physical_provider_admitted=False,empirical_validation='NOT_ESTABLISHED')

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--lens',type=int,required=True);args=ap.parse_args()
 t=time.time();o=verify_lens(args.lens)
 path=ROOT/f'independent_lens_{args.lens}.json';path.write_text(json.dumps(o,sort_keys=True,indent=2)+'\n')
 print('INDEPENDENT',o,'SHA256',hashlib.sha256(path.read_bytes()).hexdigest(),'seconds',round(time.time()-t,2),flush=True)
