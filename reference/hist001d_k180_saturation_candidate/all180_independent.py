#!/usr/bin/env python3
"""Separate all-node fixed-source rational verifier. Never imports the producer/math source.

This audits a narrow mathematical model: original binary64 sample data versus
an explicitly defined exact-real smooth source mass and its 3-point stencil.
No original general floating-operation or physical-continuum theorem.
"""
from __future__ import annotations
import hashlib,io,json,struct,zipfile,argparse
from pathlib import Path
from math import comb
from fractions import Fraction as F

ROOT=Path(__file__).resolve().parent
SOURCE='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
PARENT='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
BITS=608
DEN=1<<BITS

def lower(x):return x.numerator*DEN//x.denominator
def upper(x):return -((-x.numerator*DEN)//x.denominator)
def ceil(x):return -(-x.numerator//x.denominator)

class Box:
    __slots__=('a','b')
    def __init__(self,l,h=None,stored=False):
        if stored:self.a,self.b=int(l),int(l if h is None else h)
        else:
            l=F(l);h=l if h is None else F(h)
            self.a,self.b=lower(l),upper(h)
        if self.a>self.b:raise ValueError('inverted interval')
    def __add__(self,x):
        x=bx(x);return Box(self.a+x.a,self.b+x.b,True)
    __radd__=__add__
    def __neg__(self):return Box(-self.b,-self.a,True)
    def __sub__(self,x):return self+-bx(x)
    def __rsub__(self,x):return bx(x)-self
    def __mul__(self,x):
        x=bx(x);c=[p*q for p in (self.a,self.b) for q in (x.a,x.b)]
        return Box(min(c)//DEN,-(-max(c)//DEN),True)
    __rmul__=__mul__
    def reciprocal(self):
        if self.a<=0<=self.b:raise ValueError('denominator includes 0')
        return Box(DEN*DEN//self.b,-(-DEN*DEN//self.a),True)
    def __truediv__(self,x):return self*bx(x).reciprocal()
    def __rtruediv__(self,x):return bx(x)*self.reciprocal()
    def __pow__(self,p):
        if not isinstance(p,int) or p<0:raise ValueError('bad exponent')
        z=Box(1);x=self
        while p:
            if p&1:z=z*x
            x=x*x;p//=2
        return z
    def lo(self):return F(self.a,DEN)
    def hi(self):return F(self.b,DEN)
    def err(self):return max(abs(self.lo()),abs(self.hi()))

def bx(x):return x if isinstance(x,Box) else Box(x)

def decode_ieee(b8):
    u=struct.unpack('>Q',b8)[0]
    sign=-1 if u>>63 else 1
    exp=(u>>52)&0x7ff;mant=u&((1<<52)-1)
    if exp==2047:raise ValueError('NaN/Infinity not permitted')
    if exp==0:n=mant;k=1-1023-52
    else:n=(1<<52)+mant;k=exp-1023-52
    if k>=0:return F(sign*n*(1<<k))
    return F(sign*n,1<<(-k))

def log_exact(x,N=190):
    if x<=0:raise ValueError('log positive')
    u=x;e=0
    while u<1:u*=2;e-=1
    while u>=2:u/=2;e+=1
    def ln_one(y):
        t=(y-1)/(y+1);square=t*t;term=t;s=F()
        for j in range(N):s+=term*2/(2*j+1);term*=square
        tail=2*term/((2*N+1)*(1-square))
        return Box(s,s+tail)
    return ln_one(u)+e*ln_one(F(2))

def bernoulli(m):
    nums=[F(1)]
    for j in range(1,2*m+3):
        nums.append(-sum((F(comb(j+1,k))*nums[k] for k in range(j)),F())/F(j+1))
    return [nums[2*j] for j in range(m+2)]

def euler_gamma(n=2048,m=18):
    nums=bernoulli(m+1)
    H=sum((F(1,k) for k in range(1,n+1)),F())
    v=Box(H-F(1,2*n))-log_exact(F(n))
    for j in range(1,m+1):v=v+nums[j]/F(2*j*n**(2*j))
    next_term=nums[m+1]/F(2*(m+1)*n**(2*m+2))
    return Box(min(v.lo(),v.lo()+next_term),max(v.hi(),v.hi()+next_term))

def expo_nonnegative(w,N=100):
    if w.a<0:raise ValueError('exp argument negative')
    steps=0
    while w.b//(1<<steps)>DEN//2:steps+=1
    x=w/(1<<steps)
    t=Box(1);s=Box(1)
    for k in range(1,N):
        t=t*x/k;s=s+t
    rem=(t*x/N).hi()/(1-x.hi()/F(N+1))
    return Box(s.lo(),s.hi()+rem)**(1<<steps)

def series_products(y,gamma,N=200):
    if not y>0:raise ValueError('positive argument')
    yy=Box(y);z=Box(y*y/4)
    q0=Box(1);q1=yy/2
    a=q0;b=q1;h=F();u=Box(0);v=Box(0)
    for k in range(1,N):
        q0=q0*z/F(k*k);q1=q1*z/F(k*(k+1))
        h+=F(1,k)
        a=a+q0;b=b+q1
        u=u+h*q0;v=v+k*h*q0
    q0n=q0*z/(N*N);q1n=q1*z/(N*(N+1));hn=h+F(1,N)
    if 4*z.hi()>=(N+1)**2:raise ValueError('series tail ratio fails')
    a=a+Box(0,q0n.hi()/(1-z.hi()/(N+1)**2))
    b=b+Box(0,q1n.hi()/(1-z.hi()/((N+1)*(N+2))))
    u=u+Box(0,hn*q0n.hi()/(1-2*z.hi()/(N+1)**2))
    v=v+Box(0,N*hn*q0n.hi()/(1-4*z.hi()/(N+1)**2))
    L=log_exact(y/2)+gamma
    # Algebraically combined I0K0-I1K1, independent of producer subtraction structure.
    f=-(L*(a*a+b*b))+a*u-a*b/yy+2*b*v/yy
    k0=-L*a+u
    k1=a/yy+L*b-2*v/yy
    df=2*(b*k0-a*k1+b*k1/yy)
    return f,df

def source_m_and_prime(r,p,gamma):
    Mb,Md,a,Rd,delta,r0,n=(p[x] for x in ('Mb','Md','a','Rd','delta','r0','n'))
    y=r/(2*Rd)
    f,df=series_products(y,gamma)
    bary=Mb*Box(r)**2/(r+a)**2+Md*Box(y)**3*f
    dbary=2*Mb*a*r/Box(r+a)**3+Md/(2*Rd)*(3*Box(y)**2*f+Box(y)**3*df)
    if r<r0:
        t=expo_nonnegative(n*log_exact(r0/r)).reciprocal()
        a=t/(1+t)
    else:
        t=expo_nonnegative(n*log_exact(r/r0)).reciprocal()
        a=1/(1+t)
    b=a*(1-a)
    gate=delta*a/(1-delta*a)
    dgate=delta*n*b/(r*(1-delta*a)**2)
    return bary*gate,dbary*gate+bary*dgate

def read_source():
    p=ROOT/'inputs/frozen_smooth_shadow_gradient_parent.zip'
    if hashlib.sha256(p.read_bytes()).hexdigest()!=PARENT:raise ValueError('source parent digest changed')
    top=zipfile.ZipFile(p)
    z1=zipfile.ZipFile(io.BytesIO(top.read('inputs/frozen_source_parent.zip')))
    z2=zipfile.ZipFile(io.BytesIO(z1.read('inputs/original_march_D120_q_parent.zip')))
    z3=zipfile.ZipFile(io.BytesIO(z2.read('inputs/original_march180_parent_v1r1.zip')))
    data=zipfile.ZipFile(io.BytesIO(z3.read('inputs/original_source_46_frozen.zip')))
    lock=json.loads(z3.read('inputs/original_46plus3_lock.json'))
    if lock['original_46plus3_composite_sha256']!=SOURCE:raise ValueError('original source identity')
    for path,h in lock['source_filenames_sha256'].items():
        if hashlib.sha256(data.read('swells_pack_v2/'+path)).hexdigest()!=h:raise ValueError('original source file altered')
    for path,h in lock['archived_negative_controls_sha256'].items():
        if hashlib.sha256(z3.read('inputs/negative_controls/'+path)).hexdigest()!=h:raise ValueError('negative file altered')
    return z3,json.loads(z3.read('results/source180_capture.json')),json.loads(top.read('results/producer_analytic_source_gradient.json'))

def calc_one(index,receipt=None,save=True):
    z3,caps,sm=read_source()
    a=caps['lenses'][index];b=sm['lenses'][index];lens=a['lens_id']
    if lens!=b['lens_id']:raise ValueError('lens mismatch')
    raw=z3.read('inputs/'+a['node_file'])
    if len(raw)!=180*64 or hashlib.sha256(raw).hexdigest()!=a['node_sha256']:raise ValueError('invalid node array')
    rows=[[decode_ieee(raw[i*64+j*8:i*64+(j+1)*8]) for j in range(8)] for i in range(180)]
    def from_hex(s):return decode_ieee(struct.pack('>d',float.fromhex(s)))
    par={k:from_hex(b['source_scalar_binary64_hex'][k]) for k in ('Mb','Md','a','Rd','delta','r0','n')}
    C=from_hex(b['source_scalar_binary64_hex']['C4pi']);gamma=euler_gamma()
    R=[r[0] for r in rows];W=[r[1] for r in rows]
    if any(w<=0 for w in W) or any(r[3]<=0 for r in rows) or any(R[i]>=R[i+1] for i in range(179)):
        raise ValueError('invalid source sign/mesh')
    smass=[];sder=[]
    for i,rad in enumerate(R):
        v,d=source_m_and_prime(rad,par,gamma)
        if d.lo()<=0:raise ValueError('smooth derivative not positive at node')
        smass.append(v);sder.append(d)
        if (i+1)%30==0:print('INDEPENDENT_SOURCE_BOUND_PASS',lens,i+1,flush=True)
    errors=[];allR=F();signed=[]
    for i in range(180):
        if i==0:fd=(smass[1]-smass[0])/(R[1]-R[0])
        elif i==179:fd=(smass[179]-smass[178])/(R[179]-R[178])
        else:
            # Distinct Lagrange coefficient formulation, not weighted-secant producer expression.
            hl=R[i]-R[i-1];hr=R[i+1]-R[i]
            fd=(-hr/(hl*(hl+hr))*smass[i-1]
                +(hr-hl)/(hl*hr)*smass[i]
                +hl/(hr*(hl+hr))*smass[i+1])
        actual=C*R[i]**2*rows[i][3]
        diff=Box(actual)-fd
        errors.append(ceil(diff.err()*10**6))
        wide=Box(actual)-sder[i]
        signed.append([wide.lo().numerator//wide.lo().denominator,ceil(wide.hi())])
        allR+=W[i]*wide.err()
    maxerr=max(errors)
    if receipt is not None:
        if receipt.get('lens_id')!=lens or receipt.get('source_180_node_sha256')!=a['node_sha256']:
            raise ValueError('source receipt identity wrong')
        for key in ('physical_provider_admitted','source_float_operational_error_certified_for_arbitrary_inputs','original_March_continuum_H_error_or_root_count_proved'):
            if receipt.get(key) is not False:raise ValueError('forbidden source claim')
        ceilings=receipt['stored_vs_ideal_stencil_absolute_upper_micro_msun_per_kpc']
        if len(ceilings)!=180 or any(our>their for our,their in zip(errors,ceilings)):
            raise ValueError('producer overclaimed finite-stencil precision')
        if ceil(allR)>int(receipt['projected_shadow_all_R_difference_upper_integer_msun']):
            raise ValueError('producer falsely low all-radius shadow difference')
        original_signed=receipt['source_gradient_minus_smooth_Mprime_interval_integer_msun_per_kpc']
        if len(original_signed)!=180 or any(a>c or b<d for (a,b),(c,d) in zip(original_signed,signed)):
            raise ValueError('producer original minus smooth derivative per-node bounds overstated')
        if maxerr>int(receipt['max_ideal_stencil_discrepancy_upper_micro_msun_per_kpc']):
            raise ValueError('producer max bound understated')
    if maxerr>=1_000_000:raise ValueError('independent all-node comparison >1 Msun/kpc')
    report={'schema':'HIST001D_ALL180_INDEPENDENT_FIXED_DENSITY_COMPARISON_V1','lens_id':lens,'source_sha256':SOURCE,'node_sha256':a['node_sha256'],'all180_node_abs_error_upper_micro_msun_per_kpc':errors,'max_upper_micro_msun_per_kpc':maxerr,'all_R_K180_density_comparison_upper_integer_msun':ceil(allR),'signed_source_minus_smooth_Mprime_integer_intervals':signed,'approved_mathematical_source_only':True,'physical_provider_admitted':False,'original_source_float_error_theorem':False,'original_full_H_root_theorem':False}
    if save:
        f=ROOT/'results'/('independent_all180_'+lens.replace('+','p')+'.json')
        f.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
        print('INDEPENDENT_LENS_PASS',lens,'max_error_micro',maxerr,'all_R_K180_upper',ceil(allR),'SHA256',hashlib.sha256(f.read_bytes()).hexdigest(),flush=True)
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lens-index',type=int,required=True);x=ap.parse_args()
    f=ROOT/'results'/('all180_rational_'+['J0822p1828','J0915p4211','J0930p2855','J1021p2028','J1111p2234','J1135p3720'][x.lens_index]+'.json')
    calc_one(x.lens_index,receipt=json.loads(f.read_text()))
