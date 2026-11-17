#!/usr/bin/env python3
"""EXPERIMENTAL exact outward interval mass kernels for D2d finite-proxy mathematics.

Source input provenance remains an external SHA-pinned archive; no physics claims.
Kernel bounds are rational and cover every real R in a registered cell, subject
only to the declared finite source and mathematical continuum baryon model.
"""
from __future__ import annotations
from bisect import bisect_right
from fractions import Fraction as Q
from functools import lru_cache
from math import isqrt

RMAX=Q(120)
RMIN=Q.from_float(.02)


def floor_to(x, scale=1): return Q((x.numerator*scale)//x.denominator,scale)
def ceil_to(x,scale=1): return -floor_to(-x,scale)
def pair(x):return {'num':str(x.numerator),'den':str(x.denominator)}
def fpair(x):return Q(int(x['num']),int(x['den']))

def atan_partial(k,n):
    x=Q(1,k); term=x;total=Q(0)
    for i in range(n):
        total+= (term if i%2==0 else -term)/(2*i+1)
        term*=x*x
    return total
# Machin  pi/4=4atan(1/5)-atan(1/239). Even # terms => lower, odd => upper.
PI_LOW=16*atan_partial(5,14)-4*atan_partial(239,13)
PI_HIGH=16*atan_partial(5,13)-4*atan_partial(239,14)
assert Q(314159,100000)<PI_LOW<PI_HIGH<Q(314160,100000)

class Enclosure:
    def __init__(self, bits=42):
        self.bits=bits;self.scale=1<<bits
    def sqrt_lo(self,x):
        if x<0:raise ValueError('negative exact sqrt input')
        b=isqrt((x.numerator*self.scale*self.scale)//x.denominator)
        z=Q(b,self.scale)
        assert z*z<=x
        return z
    def sqrt_hi(self,x):
        if x<0:raise ValueError('negative exact sqrt input')
        b=isqrt((x.numerator*self.scale*self.scale)//x.denominator)
        z=Q(b,self.scale)
        hi=z if z*z==x else Q(b+1,self.scale)
        assert hi*hi>=x
        return hi
    def exp_neg(self,x):
        """Both-sided rational e^-x from alternating Taylor on y<=1/8 and outward squaring."""
        if x<0:raise ValueError('negative exp argument')
        if x==0:return Q(1),Q(1)
        k=0;y=x
        while y>Q(1,8):k+=1;y/=2
        t=Q(1); partial=Q(1);odd=None
        for j in range(1,17):
            t=-t*y/j
            partial+=t
            if j==15:odd=partial
        even=partial
        lo=floor_to(odd,self.scale);hi=ceil_to(even,self.scale)
        if not 0<lo<=hi<=1:raise ValueError('exponential interval invalid')
        for i in range(k):
            lo=floor_to(lo*lo,self.scale)
            hi=ceil_to(hi*hi,self.scale)
        assert 0<=lo<=hi<=1
        return lo,hi
    def kernel(self,R,r):
        if not (Q(0)<R<=r):raise ValueError('radial order')
        x=Q(1)-(R/r)**2
        return 1-self.sqrt_hi(x),1-self.sqrt_lo(x)
    def masses_on_shells(self,R,volume_mass_at,N=64):
        if not RMIN<=R<=RMAX:raise ValueError('radius outside mathematical domain')
        if R==RMAX:return volume_mass_at(R),volume_mass_at(R)
        low=high=volume_mass_at(R)
        # For B, mass at radial 120 represents integral inner to r; for S, it
        # includes the rmin inner cutoff and all exact source nodal integrals.
        for j in range(N):
            u=R+(RMAX-R)*Q(j*j,N*N)
            v=R+(RMAX-R)*Q((j+1)**2,N*N)
            mass=volume_mass_at(v)-volume_mass_at(u)
            if mass<0:raise ValueError('nonnegative mass shell violated')
            Kl,_=self.kernel(R,v)
            _,Kh=self.kernel(R,u)
            low+=mass*Kl
            high+=mass*Kh
        if not(0<=low<=high):raise ValueError('cylinder mass interval invalid')
        return low,min(high,volume_mass_at(RMAX))
    def disk_value(self,R,M,s,q,n=64):
        if not (R>0 and M>0 and s>0 and 0<q<=1):raise ValueError('disk scalar invalid')
        def J(t,upper):
            g2=1+(1/(q*q)-1)*4*t*t/(1+t*t)**2
            g=self.sqrt_lo(g2) if upper else self.sqrt_hi(g2)
            xx=R*g/s
            elo,ehi=self.exp_neg(xx)
            F=1-(1+xx)*(elo if upper else ehi)
            if not upper:F=max(Q(0),F)
            else:F=max(Q(0),F)
            return F/(g*g*(1+t*t))
        lo=hi=Q(0)
        for i in range(n):
            lo+=J(Q(i+1,n),False)
            hi+=J(Q(i,n),True)
        lo*=Q(4)*M/(PI_HIGH*q*n)
        hi*=Q(4)*M/(PI_LOW*q*n)
        if not(0<=lo<=hi):raise ValueError('disk interval invalid')
        if lo>M:raise ValueError('disk lower exceeds total exact mass')
        return lo,min(hi,M)

class SourceShadow:
    def __init__(self,radial,density):
        if len(radial)!=11520 or len(density)!=11520:raise ValueError('bad source nodal count')
        self.r=[Q.from_float(x) for x in radial]
        self.d=[Q.from_float(x) for x in density]
        if self.r[0]!=RMIN or self.r[-1]!=RMAX:raise ValueError('source support')
        if any(self.r[i]>=self.r[i+1] or self.d[i]<0 for i in range(11519)) or self.d[-1]<0:raise ValueError('source positivity')
        self.prefix=[Q(0)]
        for i in range(11519):
            self.prefix.append(self.prefix[-1]+self.integral_segment(self.r[i],self.r[i+1],self.d[i],self.d[i+1]))
    @staticmethod
    def integral_segment(u,v,ru,rv):
        mid=(u+v)/2;rm=(ru+rv)/2
        return (v-u)*(u*u*ru+4*mid*mid*rm+v*v*rv)/6
    @lru_cache(maxsize=20000)
    def volume_at(self,A):
        if A<=RMIN:return Q(0)
        if A>=RMAX:return self.prefix[-1]
        i=bisect_right(self.r,A)-1
        u=self.r[i];v=self.r[i+1]
        d=self.d[i]+(self.d[i+1]-self.d[i])*(A-u)/(v-u)
        return self.prefix[i]+self.integral_segment(u,A,self.d[i],d)

class Lens:
    def __init__(self,record,signrec,bits=42):
        self.id=record['lens_id']; self.E=Enclosure(bits)
        p=record['baryon_scalars'];self.p={k:Q.from_float(v) for k,v in p.items()}
        self.shadow=SourceShadow(record['radial_kpc'],record['density_msun_per_kpc3'])
        self.sigma_lo=fpair(signrec['left_strict_positive_exact_enclosure']['G4a_sigma_crit_enclosure_msun_per_kpc2'][0])
        self.sigma_hi=fpair(signrec['left_strict_positive_exact_enclosure']['G4a_sigma_crit_enclosure_msun_per_kpc2'][1])
        assert 0<self.sigma_lo<=self.sigma_hi
        self._Bcache={};self._Dcache={};self._Scache={}
    def primitive_B(self,r):
        M=self.p['bulge_mass_msun'];a=self.p['hernquist_a_kpc']
        return M*((r/(r+a))**2 - (RMIN/(RMIN+a))**2)
    def B(self,r,n=64):
        key=(r,n)
        if key not in self._Bcache:
            self._Bcache[key]=self.E.masses_on_shells(r,self.primitive_B,n)
        return self._Bcache[key]
    def D(self,r,n=64):
        key=(r,n)
        if key not in self._Dcache:
            p=self.p
            self._Dcache[key]=self.E.disk_value(r,p['disc_mass_msun'],p['disc_scale_kpc'],p['disc_q'],n)
        return self._Dcache[key]
    def S(self,A,n=64):
        key=(A,n)
        if key not in self._Scache:
            out=self.E.masses_on_shells(A,self.shadow.volume_at,n)
            self._Scache[key]=(4*PI_LOW*out[0],4*PI_HIGH*out[1])
        return self._Scache[key]
    def H(self,L,U,n=64):
        if not (RMIN<=L<U<=RMAX):raise ValueError('not one proper real-radius cell')
        b0=self.B(L,n)[0];b1=self.B(U,n)[1]
        d0=self.D(L,n)[0];d1=self.D(U,n)[1]
        p=self.p
        if min(b0,d0)<=0:raise ValueError('baryonic source mass lower not positive')
        q_vals=[(p['bulge_q']*b+p['disc_q']*d)/(b+d) for b in [b0,b1] for d in [d0,d1]]
        q0,q1=min(q_vals),max(q_vals)
        if not(Q(1,1000)<min(p['bulge_q'],p['disc_q']) and 0<q0<=q1<=1):raise ValueError('q corner or clipping bounds invalid')
        Alo=min(RMAX,L/self.E.sqrt_hi(q1))
        Ahi=min(RMAX,U/self.E.sqrt_lo(q0))
        assert Alo<=Ahi and Alo*Alo*q1<=L*L and (Ahi==RMAX or Ahi*Ahi*q0>=U*U)
        s0=self.S(Alo,n)[0];s1=self.S(Ahi,n)[1]
        lower=b0+d0+s0-PI_HIGH*self.sigma_hi*U*U
        upper=b1+d1+s1-PI_LOW*self.sigma_lo*L*L
        if lower>upper:raise ValueError('bad residual inclusion')
        return lower,upper,{'B_lower':b0,'B_upper':b1,'D_lower':d0,'D_upper':d1,'S_lower':s0,'S_upper':s1,'q_lower':q0,'q_upper':q1,'A_lower':Alo,'A_upper':Ahi}

# Source-independent derivative envelope, for extending local uniqueness to wider bands.
def _source_rho_at(src,r):
    if r<src.r[0] or r>src.r[-1]:return Q(0)
    if r==src.r[-1]:return src.d[-1]
    idx=bisect_right(src.r,r)-1
    return src.d[idx]+(src.d[idx+1]-src.d[idx])*(r-src.r[idx])/(src.r[idx+1]-src.r[idx])

class Derivative:
    def __init__(self,lens,nb=180,nd=70,ns=180):
        self.lens=lens;self.E=lens.E;self.nb=nb;self.nd=nd;self.ns=ns
        d=lens.shadow.d
        i=d.index(max(d))
        if not (0<i<len(d)-1 and all(d[j]<d[j+1] for j in range(i)) and all(d[j]>d[j+1] for j in range(i,len(d)-1))):
            raise ValueError('strict unimodal source rho not reverified')
        self.pk_idx=i
    def bulge_upper(self,L,U):
        e=self.E;p=self.lens.p;M=p['bulge_mass_msun'];a=p['hernquist_a_kpc']
        top=e.sqrt_hi(RMAX*RMAX-L*L);total=Q(0);n=self.nb
        for j in range(n):
            t0=top*Q(j*j,n*n);t1=top*Q((j+1)**2,n*n)
            r=e.sqrt_lo(L*L+t0*t0)
            total+=(t1-t0)/(r*(r+a)**3)
        return ceil_to(2*M*a*U*total,1000000)
    def disk_upper(self,L,U):
        e=self.E;p=self.lens.p;M=p['disc_mass_msun'];s=p['disc_scale_kpc'];q=p['disc_q']
        acc=Q(0);n=self.nd
        for j in range(n):
            t=Q(j,n)
            g=e.sqrt_lo(1+(1/(q*q)-1)*4*t*t/(1+t*t)**2)
            _,exphi=e.exp_neg(L*g/s)
            acc+=exphi/(1+t*t)
        return ceil_to(4*M*U*acc/(PI_LOW*q*s*s*n),1000000)
    def sigma_sup(self,Alo,Ahi):
        if not(Q(0)<Alo<=Ahi<RMAX):raise ValueError('sigma band out of domain')
        e=self.E;src=self.lens.shadow; top=e.sqrt_hi(RMAX*RMAX-Alo*Alo)
        n=self.ns;s=Q(0)
        pk_r=src.r[self.pk_idx];pk_d=src.d[self.pk_idx]
        for j in range(n):
            t0=top*Q(j*j,n*n);t1=top*Q((j+1)**2,n*n)
            rl=e.sqrt_lo(Alo*Alo+t0*t0)
            rh=e.sqrt_hi(Ahi*Ahi+t1*t1)
            if rl>RMAX:continue
            rlo=max(RMIN,rl);rhi=min(RMAX,rh)
            top_d=max(_source_rho_at(src,rlo),_source_rho_at(src,rhi))
            if rlo<=pk_r<=rhi:top_d=max(top_d,pk_d)
            s+=top_d*(t1-t0)
        return 2*s
    def Hprime_upper(self,L,U,mass_mesh=64):
        lens=self.lens;e=self.E;p=lens.p
        if not(RMIN<=L<U<RMAX):raise ValueError('derivative cell outside')
        blo=lens.B(L,mass_mesh)[0];bhi=lens.B(U,mass_mesh)[1]
        dlo=lens.D(L,mass_mesh)[0];dhi=lens.D(U,mass_mesh)[1]
        qb,qd=p['bulge_q'],p['disc_q']
        qv=[(qb*b+qd*d)/(b+d) for b in [blo,bhi] for d in [dlo,dhi]]
        qlo,qhi=min(qv),max(qv)
        Alo=L/e.sqrt_hi(qhi)
        Ahi=U/e.sqrt_lo(qlo)
        if not(RMIN<Alo<Ahi<RMAX):raise ValueError('derivative aperture band extends past source')
        bp=self.bulge_upper(L,U);dp=self.disk_upper(L,U)
        qp=ceil_to(abs(qb-qd)*(bp*dhi+bhi*dp)/(blo+dlo)**2,10**9)
        rt=e.sqrt_lo(qlo)
        Aprime=ceil_to(1/rt+U*qp/(2*qlo*rt),10**9)
        ssh=self.sigma_sup(Alo,Ahi)
        Sprime=ceil_to(2*PI_HIGH*Ahi*ssh*Aprime,1000000)
        crit=floor_to(2*PI_LOW*lens.sigma_lo*L,1000000)
        result=bp+dp+Sprime-crit
        return result,dict(Bp_upper=bp,Dp_upper=dp,Sp_upper=Sprime,crit_lower=crit,Alo=Alo,Ahi=Ahi,sigmaS_upper=ssh,Aprime_upper=Aprime)
