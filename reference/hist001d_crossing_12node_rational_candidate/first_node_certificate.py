#!/usr/bin/env python3
"""Candidate rational first-March-node Bessel/density comparator, explicitly nonphysical.

Proves a discrepancy only between an archived binary64 shadow-density datum
and a separately defined analytic (real-parameter, source-formula) smooth derivative.
Not a proof of any original SciPy operation error, global M''/M''' bound or root count.
"""
from __future__ import annotations
import hashlib
import io
import json
import math
import struct
import zipfile
from fractions import Fraction as Q
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PARENT_SHA="3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18"
SOURCE_SHA="fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
SOURCE_ARCHIVE_SHA="283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e"
SCALE=1<<140

def down(q:Q)->Q:return Q(q.numerator*SCALE//q.denominator,SCALE)
def up(q:Q)->Q:return -down(-q)

class Iv:
    __slots__=("l","u")
    def __init__(self,l,u=None):
        l=Q(l);u=Q(l if u is None else u)
        if l>u:raise ValueError('inverted interval')
        self.l=down(l);self.u=up(u)
    def __add__(self,o):
        o=asiv(o);return Iv(self.l+o.l,self.u+o.u)
    __radd__=__add__
    def __neg__(self):return Iv(-self.u,-self.l)
    def __sub__(self,o):return self+-asiv(o)
    def __rsub__(self,o):return asiv(o)+-self
    def __mul__(self,o):
        o=asiv(o);v=[a*b for a in (self.l,self.u) for b in (o.l,o.u)];return Iv(min(v),max(v))
    __rmul__=__mul__
    def inv(self):
        if self.l<=0<=self.u:raise ValueError('interval denominator crosses zero')
        return Iv(Q(1)/self.u,Q(1)/self.l)
    def __truediv__(self,o):return self*asiv(o).inv()
    def __rtruediv__(self,o):return asiv(o)*self.inv()
    def __pow__(self,n):
        if type(n) is not int or n<0:raise ValueError('bad integer power')
        if n==0:return Iv(1)
        z=Iv(1);x=self
        while n:
            if n&1:z=z*x
            x=x*x;n>>=1
        return z
    def absmax(self):return max(abs(self.l),abs(self.u))
    def out(self):return {'lower_num':str(self.l.numerator),'lower_den':str(self.l.denominator),'upper_num':str(self.u.numerator),'upper_den':str(self.u.denominator)}

def asiv(q):return q if isinstance(q,Iv) else Iv(q)

def ln_pos(x:Q,N=100)->Iv:
    if x<=0:raise ValueError('log argument must be positive')
    # Decompose x=2^e*u with 1<=u<2. The atanh parameter is in [0,1/3].
    e=0;u=x
    while u>=2:e+=1;u/=2
    while u<1:e-=1;u*=2
    def atanh_log(q:Q)->Iv:
        t=(q-1)/(q+1)
        if not 0<=t<=Q(1,3):raise ValueError('log reduction contract')
        v=Q(0);term=t
        for k in range(N):
            v+=2*term/(2*k+1);term*=t*t
        rem=2*term/((2*N+1)*(1-t*t))
        return Iv(v,v+rem)
    return atanh_log(u)+e*atanh_log(Q(2))

def gamma_iv(n=500)->Iv:
    # H_n-ln n = gamma+1/(2n)-1/(12n^2)+r_n, 0<r_n<=1/(120n^4).
    # This classical Euler–Maclaurin remainder is the only external analytic lemma here.
    h=sum((Q(1,k) for k in range(1,n+1)),Q(0))
    c=Iv(h-Q(1,2*n)+Q(1,12*n*n))-ln_pos(Q(n))
    return Iv(c.l-Q(1,120*n**4),c.u)

def positive_series(y:Q,N=32):
    if y<=0 or y>Q(3,2):raise ValueError('Bessel first-node argument outside controlled series domain')
    z=y*y/4
    i0=Q(1);i1=Q(y,2);sm=Q(0);sk=Q(0)
    t0=Q(1);t1=Q(y,2);H=Q(0)
    for k in range(1,N):
        t0=t0*z/(k*k)
        t1=t1*z/(k*(k+1))
        H+=Q(1,k)
        i0+=t0;i1+=t1;sm+=H*t0;sk+=k*H*t0
    # Next term k=N; geometric ratio bounds for k>=N, N>1.
    t0n=t0*z/(N*N);t1n=t1*z/(N*(N+1));Hn=H+Q(1,N)
    def tail(next_term:Q,rat:Q)->Q:
        if not 0<=rat<1:raise ValueError('tail ratio contract')
        return next_term/(1-rat)
    return (Iv(i0,i0+tail(t0n,z/(N+1)**2)),
            Iv(i1,i1+tail(t1n,z/((N+1)*(N+2)))),
            Iv(sm,sm+tail(Hn*t0n,2*z/(N+1)**2)),
            Iv(sk,sk+tail(N*Hn*t0n,4*z/(N+1)**2)))

def bessel_values(y:Q,N=32,gamm=None):
    if gamm is None:gamm=gamma_iv()
    I0,I1,S,S1=positive_series(y,N)
    L=ln_pos(y/2)+gamm
    K0=-L*I0+S
    K1=I0/y+L*I1-2*S1/y
    F=I0*K0-I1*K1
    Fp=2*(I1*K0-I0*K1+(I1*K1)/y)
    return F,Fp,{'I0':I0,'I1':I1,'K0':K0,'K1':K1}

def exp_pos(q:Iv,terms=42)->Iv:
    if q.l<0:raise ValueError('negative exp bound argument')
    # Scale by power of 2 until upper <=1/2, sum positive Taylor series.
    bits=0
    while q.u/(1<<bits)>Q(1,2):bits+=1
    a=q/(1<<bits)
    def evaluate(v):
        t=Q(1);s=t
        for k in range(1,terms):
            t=t*v/k;s+=t
        rem=t*v/terms
        # next remaining geometric ratio is <=v/(terms+1)
        return s,rem/(1-v/Q(terms+1))
    ll,_=evaluate(a.l);uu,err=evaluate(a.u)
    return Iv(ll,uu+err)**(1<<bits)

def gate(R:Q,r0:Q,n:Q,delta:Q)->tuple[Iv,Iv]:
    if not (R>0 and r0>0 and n>0 and 0<delta<1):raise ValueError('gate inputs')
    q=n*ln_pos(r0/R)
    if q.l<0:raise ValueError('only the first two source nodes R<r0 handled')
    small=exp_pos(q).inv()  # (R/r0)^n
    f=small/(1+small)
    p=f*(1-f)
    g=delta*f/(1-delta*f)
    gp=delta*n*p/(R*(1-delta*f)**2)
    return g,gp

def source_mass_derivative(R:Q,p:dict,gamma=None,N=32)->tuple[Iv,dict]:
    Mb,Md,a,Rd,delta,r0,n=(p[k] for k in ('Mb','Md','a','Rd','delta','r0','n'))
    y=R/(2*Rd)
    F,Fp,b=bessel_values(y,N=N,gamm=gamma)
    A=Mb*R**2/(R+a)**2+Md*y**3*F
    Ap=2*Mb*a*R/(R+a)**3+Md/(2*Rd)*(3*y**2*F+y**3*Fp)
    G,Gp=gate(R,r0,n,delta)
    answer=Ap*G+A*Gp
    return answer,{'bessel_F':F,'bessel_dF':Fp,'smooth_M':A*G,'smooth_Mprime':answer,'positive_derivative':answer.l>0}

def load_sources():
    parent=ROOT/'inputs/frozen_smooth_shadow_gradient_parent.zip'
    if hashlib.sha256(parent.read_bytes()).hexdigest()!=PARENT_SHA:raise ValueError('wrong external parent identity')
    z0=zipfile.ZipFile(parent)
    z1=zipfile.ZipFile(io.BytesIO(z0.read('inputs/frozen_source_parent.zip')))
    z2=zipfile.ZipFile(io.BytesIO(z1.read('inputs/original_march_D120_q_parent.zip')))
    z3=zipfile.ZipFile(io.BytesIO(z2.read('inputs/original_march180_parent_v1r1.zip')))
    srcraw=z3.read('inputs/original_source_46_frozen.zip')
    if hashlib.sha256(srcraw).hexdigest()!=SOURCE_ARCHIVE_SHA:raise ValueError('original source ZIP mismatch')
    zsrc=zipfile.ZipFile(io.BytesIO(srcraw))
    lock=json.loads(z3.read('inputs/original_46plus3_lock.json'))
    if lock['original_46plus3_composite_sha256']!=SOURCE_SHA or len(lock['source_filenames_sha256'])!=46 or len(lock['archived_negative_controls_sha256'])!=3:raise ValueError('original source lock mismatch')
    for path,digest in lock['source_filenames_sha256'].items():
        if hashlib.sha256(zsrc.read('swells_pack_v2/'+path)).hexdigest()!=digest:raise ValueError('tampered original source')
    for path,digest in lock['archived_negative_controls_sha256'].items():
        if hashlib.sha256(z3.read('inputs/negative_controls/'+path)).hexdigest()!=digest:raise ValueError('tampered archived negative')
    smooth=json.loads(z0.read('results/producer_analytic_source_gradient.json'))
    capture=json.loads(z3.read('results/source180_capture.json'))
    return z3,smooth,capture

def produce(N=32,gamman=500,write=True):
    z,smooth,capture=load_sources()
    if len(smooth['lenses'])!=6 or len(capture['lenses'])!=6:raise ValueError('lens counts incorrect')
    gamma=gamma_iv(gamman)
    report={'schema':'HIST001D_FIRST_NODE_EXACT_RATIONAL_LOG_EULER_BESSEL_SOURCE_DISCREPANCY_CANDIDATE_V1',
            'source_lock_sha256':SOURCE_SHA,'parent_sha256':PARENT_SHA,
            'original_180_node_source_locked':True,
            'exact_source_smooth_math_model_only':True,
            'same_source_physical_density_proved':False,
            'original_float_operation_error_certified':False,
            'original_full_H_or_root_count_certified':False,
            'empirical_validation':'NOT_ESTABLISHED','physical_provider_admitted':False,
            'series_terms':N,'gamma_harmonic_n':gamman,'first_node_pairs':[]}
    for c,s in zip(capture['lenses'],smooth['lenses']):
        if c['lens_id']!=s['lens_id']:raise ValueError('lens order mismatch')
        b=z.read('inputs/'+c['node_file'])
        if hashlib.sha256(b).hexdigest()!=c['node_sha256'] or len(b)!=180*8*8:raise ValueError('node bytes wrong')
        arr=struct.unpack('>8d',b[:64]);next_arr=struct.unpack('>8d',b[64:128]);R=Q.from_float(arr[0]);R1=Q.from_float(next_arr[0]);rho=Q.from_float(arr[3]);
        if R!=Q.from_float(0.02) or rho<=0 or R1<=R:raise ValueError('not positive original r=0.02 density or next source radius')
        p={k:Q.from_float(float.fromhex(s['source_scalar_binary64_hex'][k])) for k in ('Mb','Md','a','Rd','delta','r0','n')}
        mp,metrics=source_mass_derivative(R,p,gamma,N)
        next_metrics=source_mass_derivative(R1,p,gamma,N)[1]
        C4pi=Q.from_float(float.fromhex(s['source_scalar_binary64_hex']['C4pi']))
        # Under a SPECIFIC mathematically defined comparison, these operands are exact stored dyadics.
        grid_gradient=C4pi*R*R*rho
        if not mp.l>0 or not mp.u<grid_gradient:
            raise ValueError('strict positive gradient discrepancy cannot be certified')
        ratio=Iv(grid_gradient)/mp
        ideal_secant=(next_metrics['smooth_M']-metrics['smooth_M'])/(R1-R)
        secant_difference=Iv(grid_gradient)-ideal_secant
        if not secant_difference.absmax()<Q(3,10**6):
            raise ValueError('a posteriori first-node float-output versus exact mass secant bound failed')
        # Report downward certified integer ratio and upward smooth density bound.
        floor_ratio=ratio.l.numerator//ratio.l.denominator
        if floor_ratio<2:raise ValueError('no strict first-node gap')
        result={'lens_id':c['lens_id'],'r0_float_hex':float(arr[0]).hex(),'node_digest':c['node_sha256'],
                'first_source_rho_float_hex':float(arr[3]).hex(),
                'source_gradient_from_stored_binary64_dyadics':str(grid_gradient),
                'source_true_smooth_Mprime_interval':mp.out(),
                'certified_rho_source_over_rho_smooth_floor':str(floor_ratio),
                'source_gradient_exceeds_smooth_upper':True,
                'next_source_radius_float_hex':next_arr[0].hex(),
                'source_ideal_smooth_secant_interval':ideal_secant.out(),
                'a_posteriori_stored_source_grid_gradient_minus_ideal_secant_interval':secant_difference.out(),
                'a_posteriori_first_node_stored_grid_vs_ideal_secant_absolute_lt_3e_minus_6_msun_per_kpc':True,
                'mathematical_reference_only':True,'source_float_error_theorem':False}
        report['first_node_pairs'].append(result)
        print('FIRST_NODE_RATIONAL_PASS',c['lens_id'],'ratio >=',floor_ratio,flush=True)
    if write:
        out=ROOT/'results/first_node_candidate_producer.json';out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
        print('RECEIPT_SHA256',hashlib.sha256(out.read_bytes()).hexdigest())
    return report

if __name__=='__main__':produce()
