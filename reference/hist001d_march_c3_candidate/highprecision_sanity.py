#!/usr/bin/env python3
"""Nonproof mpmath Bessel sanity, using an independently symbolic differentiated jet."""
from __future__ import annotations
from fractions import Fraction as Q
import hashlib,io,json,struct,zipfile
from pathlib import Path
import mpmath as mp
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
mp.mp.dps=45
Y,I0,I1,K0,K1=sp.symbols('Y I0 I1 K0 K1')
base=I0*K0-I1*K1
partial={I0:I1,I1:I0-I1/Y,K0:-K1,K1:-K0-K1/Y}
def derivative(expr):return sp.diff(expr,Y)+sum(sp.diff(expr,x)*dx for x,dx in partial.items())
fun=[]
for d in range(4):
    fun.append(sp.lambdify((Y,I0,I1,K0,K1),base,modules='mpmath',cse=True))
    base=sp.expand(derivative(base))

def exact_mpf_hex(s):
    x=Q.from_float(float.fromhex(s));return mp.mpf(x.numerator)/x.denominator

def sample_M2_M3(r,P):
    Mb,Md,a,Rd,delta,r0,n=(P[k] for k in ('Mb','Md','a','Rd','delta','r0','n'))
    y=r/(2*Rd)
    vals=[mp.besseli(0,y),mp.besseli(1,y),mp.besselk(0,y),mp.besselk(1,y)]
    F=[f(y,*vals) for f in fun]
    abar=[Mb,
          2*Mb*a*r/(r+a)**3,
          2*Mb*a*(a-2*r)/(r+a)**4,
          12*Mb*a*(r-a)/(r+a)**5]
    dbar=[]
    for k in range(4):
        v=mp.mpf(0)
        for j in range(min(k,3)+1):
            v+=sp.binomial(k,j)*mp.factorial(3)/mp.factorial(3-j)*y**(3-j)*F[k-j]
        dbar.append(v*Md/(2*Rd)**k)
    A=[abar[i]+dbar[i] for i in range(4)]
    t=(r/r0)**n;f=t/(1+t);p=f*(1-f)
    f1=n*p/r
    f2=n*p*(n*(1-2*f)-1)/r**2
    f3=n*p*((n*(1-2*f)-2)*(n*(1-2*f)-1)-2*n*n*p)/r**3
    eps=1-delta*f
    G=[delta*f/eps,delta*f1/eps**2,
       2*delta**2*f1**2/eps**3+delta*f2/eps**2,
       6*delta**3*f1**3/eps**4+6*delta**2*f1*f2/eps**3+delta*f3/eps**2]
    return A[2]*G[0]+2*A[1]*G[1]+A[0]*G[2], A[3]*G[0]+3*A[2]*G[1]+3*A[1]*G[2]+A[0]*G[3]

def run():
    d=json.loads((ROOT/'results/source_bound_M2_M3_rational_producer.json').read_text())
    base=zipfile.ZipFile(ROOT/'inputs/frozen_smooth_shadow_gradient_parent.zip')
    p1=zipfile.ZipFile(io.BytesIO(base.read('inputs/frozen_source_parent.zip')))
    p2=zipfile.ZipFile(io.BytesIO(p1.read('inputs/original_march_D120_q_parent.zip')))
    p3=zipfile.ZipFile(io.BytesIO(p2.read('inputs/original_march180_parent_v1r1.zip')))
    old=json.loads(p3.read('results/source180_capture.json'))
    tested=[]
    for j,item in enumerate(d['lenses']):
        P={k:exact_mpf_hex(item['source_scalar_hex'][k]) for k in ('Mb','Md','a','Rd','delta','r0','n')}
        raw=p3.read('inputs/'+old['lenses'][j]['node_file'])
        RR=[mp.mpf(Q.from_float(struct.unpack('>d',raw[i*64:i*64+8])[0]).numerator)/Q.from_float(struct.unpack('>d',raw[i*64:i*64+8])[0]).denominator for i in range(180)]
        for cell in (0,5,40,178):
            r=(RR[cell]+RR[cell+1])/2
            m2,m3=sample_M2_M3(r,P)
            cap2=mp.mpf(item['M2_by_cell_upper_ceil'][cell]);cap3=mp.mpf(item['M3_by_cell_upper_ceil'][cell])
            if not (abs(m2)<cap2 and abs(m3)<cap3):raise ValueError('sanity failure')
            tested.append({'lens':item['lens_id'],'cell':cell,
                           'envelope_over_numeric_abs_m2':mp.nstr(cap2/(abs(m2)+mp.mpf('1e-90')),6),
                           'envelope_over_numeric_abs_m3':mp.nstr(cap3/(abs(m3)+mp.mpf('1e-90')),6)})
        print('MPMATH_ANALYTIC_JET_SANITY_PASS',item['lens_id'],flush=True)
    result={'status':'INDEPENDENT_NUMERIC_SANITY_NOT_RIGOROUS_PROOF','count':len(tested),
            'precision_decimal':mp.mp.dps,'samples':tested,
            'method':'mpmath I0/I1/K0/K1 values + independently symbolically differentiated product jets and logistic composition'}
    o=ROOT/'results/high_precision_sanity.json';o.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('SANITY_SHA256',hashlib.sha256(o.read_bytes()).hexdigest())
if __name__=='__main__':run()
