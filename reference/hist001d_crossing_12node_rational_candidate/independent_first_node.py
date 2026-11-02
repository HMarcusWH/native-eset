#!/usr/bin/env python3
"""Independent rational first-node source-discrepancy audit.

No import from producer. Uses distinct 160-bit quantization, gamma H_700,
45 series terms, and the cancellation-aware *combined* I/K expression.
This validates the first-node inequality, NOT original software float error.
"""
from __future__ import annotations
import hashlib, io, json, struct, zipfile
from fractions import Fraction as F
from pathlib import Path
P=Path(__file__).resolve().parent
PAR='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
ORIG='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
SOURCE='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
UNIT=1<<160

def dn(q):return F((q.numerator*UNIT)//q.denominator,UNIT)
def upp(q):return -dn(-q)
class B:
    def __init__(self,a,b=None):
        if isinstance(a,B):self.l,self.h=a.l,a.h;return
        a=F(a);b=F(a if b is None else b)
        if a>b:raise ValueError('inverted rational box')
        self.l,self.h=dn(a),upp(b)
    def __add__(self,o):
        q=V(o);return B(self.l+q.l,self.h+q.h)
    __radd__=__add__
    def __neg__(self):return B(-self.h,-self.l)
    def __sub__(self,o):return self+-V(o)
    def __rsub__(self,o):return V(o)-self
    def __mul__(self,o):
        q=V(o);c=[v*w for v in (self.l,self.h) for w in(q.l,q.h)];return B(min(c),max(c))
    __rmul__=__mul__
    def inverse(self):
        if self.l<=0<=self.h:raise ValueError('zero denominator range')
        return B(1/self.h,1/self.l)
    def __truediv__(self,o):return self*V(o).inverse()
    def __rtruediv__(self,o):return V(o)/self
    def __pow__(self,n):
        if n<0:raise ValueError('only nonnegative powers')
        z=B(1);v=self
        while n:
            if n&1:z=z*v
            v=v*v;n//=2
        return z
    def absmax(self):return max(abs(self.l),abs(self.h))
    def includes(self,q):return self.l<=q<=self.h

def V(o):return o if isinstance(o,B) else B(o)

def log_bin(x,terms=120):
    if x<=0:raise ValueError('ln positivity contract')
    e=0
    while x>=2:x/=2;e+=1
    while x<1:x*=2;e-=1
    def atanh_bound(v):
        t=(v-1)/(v+1)
        c=F(0);u=t
        for j in range(terms):c+=2*u/(2*j+1);u*=t*t
        return B(c,c+2*u/((2*terms+1)*(1-t*t)))
    return atanh_bound(x)+e*atanh_bound(F(2))

def euler_range():
    n=700
    H=sum((F(1,k) for k in range(1,n+1)),F(0))
    c=B(H-F(1,2*n)+F(1,12*n*n))-log_bin(F(n))
    return B(c.l-F(1,120*n**4),c.h)

def exp_bound(w,terms=54):
    if w.l<0:raise ValueError('negative exponential argument')
    b=0
    while w.h/(2**b)>F(1,2):b+=1
    t=w/(2**b)
    def series(x):
        p=F(1);s=p
        for k in range(1,terms):p=p*x/k;s+=p
        first=p*x/terms
        return s,first/(1-x/F(terms+1))
    low,_=series(t.l);hi,rem=series(t.h)
    return B(low,hi+rem)**(2**b)

def bessels(y,gamma):
    if not 0<y<F(3,2):raise ValueError('first knot Y only')
    z=y*y/4
    N=45
    a=F(1);b=F(y,2);I0=a;I1=b;H=F(0);S=F(0);S1=F(0)
    for i in range(1,N):
        a*=z/(i*i);b*=z/(i*(i+1));H+=F(1,i)
        I0+=a;I1+=b;S+=H*a;S1+=i*H*a
    an=a*z/(N*N);bn=b*z/(N*(N+1));hn=H+F(1,N)
    x0=B(I0,I0+an/(1-z/(N+1)**2))
    x1=B(I1,I1+bn/(1-z/((N+1)*(N+2))))
    s0=B(S,S+hn*an/(1-2*z/(N+1)**2))
    s1=B(S1,S1+N*hn*an/(1-4*z/(N+1)**2))
    logterm=log_bin(y/2)+gamma
    # Alternate algebra: insert K0/K1 series directly into I0*K0-I1*K1.
    combo=-logterm*(x0*x0+x1*x1)+x0*s0-x0*x1/y+2*x1*s1/y
    k0=-logterm*x0+s0
    k1=x0/y+logterm*x1-2*s1/y
    # Use the exact first-order I/K differential recurrence for dF/dy.
    dcombo=2*(x1*k0-x0*k1+x1*k1/y)
    return combo,dcombo

def mass_at_first(r,p,gamma):
    Mb,Md,a,Rd,delta,r0,n=(p[k] for k in ('Mb','Md','a','Rd','delta','r0','n'))
    y=r/(2*Rd)
    ff,fp=bessels(y,gamma)
    A=Mb*r*r/(r+a)**2+Md*y**3*ff
    Ap=2*Mb*a*r/(r+a)**3+Md/(2*Rd)*(3*y*y*ff+y**3*fp)
    ratio=exp_bound(n*log_bin(r0/r)).inverse()
    f=ratio/(1+ratio)
    p=f*(1-f)
    gate=delta*f/(1-delta*f)
    gatep=delta*n*p/(r*(1-delta*f)**2)
    return Ap*gate+A*gatep, A*gate

def verify(candidate=None,write=True):
    z=zipfile.ZipFile(P/'inputs/frozen_smooth_shadow_gradient_parent.zip')
    raw=(P/'inputs/frozen_smooth_shadow_gradient_parent.zip').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PAR:raise ValueError('wrong parent')
    z1=zipfile.ZipFile(io.BytesIO(z.read('inputs/frozen_source_parent.zip')))
    z2=zipfile.ZipFile(io.BytesIO(z1.read('inputs/original_march_D120_q_parent.zip')))
    z3=zipfile.ZipFile(io.BytesIO(z2.read('inputs/original_march180_parent_v1r1.zip')))
    sourceraw=z3.read('inputs/original_source_46_frozen.zip')
    if hashlib.sha256(sourceraw).hexdigest()!=ORIG:raise ValueError('original source wrong')
    source=zipfile.ZipFile(io.BytesIO(sourceraw));lk=json.loads(z3.read('inputs/original_46plus3_lock.json'))
    if lk['original_46plus3_composite_sha256']!=SOURCE:raise ValueError('source lock wrong')
    for path,dig in lk['source_filenames_sha256'].items():
        if hashlib.sha256(source.read('swells_pack_v2/'+path)).hexdigest()!=dig:raise ValueError('modified historical source')
    for path,dig in lk['archived_negative_controls_sha256'].items():
        if hashlib.sha256(z3.read('inputs/negative_controls/'+path)).hexdigest()!=dig:raise ValueError('modified negative control')
    origin=json.loads(z3.read('results/source180_capture.json'))
    params=json.loads(z.read('results/producer_analytic_source_gradient.json'))
    given=candidate if candidate is not None else json.loads((P/'results/first_node_candidate_producer.json').read_bytes())
    if given['schema']!='HIST001D_FIRST_NODE_EXACT_RATIONAL_LOG_EULER_BESSEL_SOURCE_DISCREPANCY_CANDIDATE_V1' or given['source_lock_sha256']!=SOURCE or given['parent_sha256']!=PAR or len(given['first_node_pairs'])!=6:
        raise ValueError('proof source or schema mismatch')
    for key in ('same_source_physical_density_proved','original_float_operation_error_certified','original_full_H_or_root_count_certified','physical_provider_admitted'):
        if given.get(key) is not False:raise ValueError('forbidden scientific claim')
    if given.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('forbidden validation claim')
    gamma=euler_range();report={'schema':'HIST001D_FIRST_KNOT_INDEPENDENT_RATIONAL_COMBINED_BESSEL_V1','lenses':[],'all_six_strict':True,'physical_provider_admitted':False}
    for a,b,c in zip(origin['lenses'],params['lenses'],given['first_node_pairs']):
        if a['lens_id']!=b['lens_id'] or a['lens_id']!=c['lens_id'] or a['node_sha256']!=c['node_digest']:
            raise ValueError('source identity mismatch')
        raw=z3.read('inputs/'+a['node_file'])
        if hashlib.sha256(raw).hexdigest()!=a['node_sha256'] or len(raw)!=180*64:raise ValueError('source node hash mismatch')
        numbers=struct.unpack('>8d',raw[:64]);next_numbers=struct.unpack('>8d',raw[64:128]);R=F.from_float(numbers[0]);R1=F.from_float(next_numbers[0]);rho=F.from_float(numbers[3]);
        if c['r0_float_hex']!=numbers[0].hex() or c['first_source_rho_float_hex']!=numbers[3].hex() or c['next_source_radius_float_hex']!=next_numbers[0].hex():raise ValueError('source float data declaration mismatch')
        p={k:F.from_float(float.fromhex(b['source_scalar_binary64_hex'][k])) for k in ('Mb','Md','a','Rd','delta','r0','n')}
        computed,mass0=mass_at_first(R,p,gamma)
        _nextder,mass1=mass_at_first(R1,p,gamma)
        grid=F.from_float(float.fromhex(b['source_scalar_binary64_hex']['C4pi']))*R**2*rho
        if c['source_gradient_from_stored_binary64_dyadics']!=str(grid):raise ValueError('declared source gradient changed')
        if computed.l<=0 or computed.h>=grid:raise ValueError('first-knot density discrepancy not strictly verified')
        ratio=grid/computed.h
        if ratio < int(c['certified_rho_source_over_rho_smooth_floor']):raise ValueError('producer ratio lower overstated')
        secant=(mass1-mass0)/(R1-R)
        grid_delta=B(grid)-secant
        if not grid_delta.absmax()<F(3,10**6) or c.get('a_posteriori_first_node_stored_grid_vs_ideal_secant_absolute_lt_3e_minus_6_msun_per_kpc') is not True:
            raise ValueError('first-node actual source stored data versus selected exact secant not bounded')
        report['lenses'].append({'lens_id':a['lens_id'],'independent_certified_ratio_floor':str(ratio.numerator//ratio.denominator), 'producer_ratio_bound_accepted':True,
            'independent_source_grid_vs_ideal_secant_abs_lt_3e_minus_6_msun_per_kpc':True})
        print('INDEPENDENT_FIRST_NODE_PASS',a['lens_id'], 'floor',ratio.numerator//ratio.denominator,flush=True)
    if write:
        dest=P/'results/first_node_candidate_independent.json'
        dest.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
        print('INDEPENDENT_SHA',hashlib.sha256(dest.read_bytes()).hexdigest())
    return report


if __name__=='__main__':verify()
