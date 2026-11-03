#!/usr/bin/env python3
"""Independent exact-rational arithmetic/coverage review for source-defined full-H PL witness.

Uses a separate integer-sqrt enclosure (isqrt(n*d)/d), reconstructed
PL/q and analytic derivative inequalities. Does NOT independently rederive
or certify the selected M* Bessel interval system.
"""
from __future__ import annotations
import argparse,json,bisect
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
from full_h_finite_source import load_source,LENSES

def ff(x):return F.from_float(x)
def from_pair(pair):return F(int(pair[0]),int(pair[1]))
def floor(x):return x.numerator//x.denominator
def ceil(x):return -((-x.numerator)//x.denominator)
def sqrt_bnd(x):
    if x<0:raise ValueError('negative sqrt')
    n,d=x.numerator,x.denominator
    k=isqrt(n*d)
    return F(k,d),F(k+(k*k!=n*d),d)

class CheckLens:
    def __init__(self,record,rows,qmeta,cap):
        self.name=cap['lens_id']
        self.r=[ff(x[0]) for x in rows];self.B=[ff(x[4]) for x in rows]
        self.D=[ff(x[6]) for x in rows];self.S0=[ff(x[5]) for x in rows];self.S=[ff(x[7]) for x in rows]
        self.qb=ff(float.fromhex(qmeta['qb_hex']));self.qd=ff(float.fromhex(qmeta['qd_hex']))
        self.sigma=ff(float.fromhex(cap['original_sigma_hex']))
        self.pi=ff(float.fromhex(cap['original_pi4_float_hex']))/4
        self.k=record['root_cell_index']
        if len(self.r)!=180 or any(self.r[i]>=self.r[i+1] for i in range(179)):
            raise ValueError('mesh')
        if any(x<=0 for x in self.B+self.D) or any(self.S0[i]>self.S0[i+1] for i in range(179)):
            raise ValueError('source monotonic inputs')
    def interp(self,x,y):
        if y<=self.r[0]:return x[0]
        if y>=self.r[-1]:return x[-1]
        i=bisect.bisect_right(self.r,y)-1
        return x[i]+(x[i+1]-x[i])*(y-self.r[i])/(self.r[i+1]-self.r[i])
    def q(self,x):
        B=self.interp(self.B,x);D=self.interp(self.D,x)
        return (self.qb*B+self.qd*D)/(B+D)
    def aa(self,x):
        a,b=sqrt_bnd(self.q(x))
        return x/b,x/a
    def value(self,x):
        a,b=self.aa(x)
        base=self.interp(self.B,x)+self.interp(self.D,x)-self.pi*self.sigma*x*x
        return base+self.interp(self.S0,a),base+self.interp(self.S0,b)
    def whole_panel(self,L,U,j):
        if not self.r[j]<=L<U<=self.r[j+1]:raise ValueError('global cell')
        a,_=self.aa(L);_,b=self.aa(U)
        low=self.interp(self.B,L)+self.interp(self.D,L)+self.interp(self.S0,a)-self.pi*self.sigma*U*U
        high=self.interp(self.B,U)+self.interp(self.D,U)+self.interp(self.S0,b)-self.pi*self.sigma*L*L
        return low,high
    def derivative_upper(self,L,U):
        j=self.k;R0,R1=self.r[j:j+2];h=R1-R0
        P0=self.B[j]+self.D[j];P1=self.B[j+1]+self.D[j+1]
        N0=self.qb*self.B[j]+self.qd*self.D[j];N1=self.qb*self.B[j+1]+self.qd*self.D[j+1]
        dP=(P1-P0)/h
        def p(x):return P0+dP*(x-R0)
        det=(N1*P0-N0*P1)/h
        qmin=min(self.q(L),self.q(U))
        qp_neg=max(F(0),-det/min(p(L),p(U))**2)
        qsqrt,_=sqrt_bnd(qmin)
        aprime=(1+U*qp_neg/(2*qmin))/qsqrt
        Al,_=self.aa(L);_,Au=self.aa(U)
        ms=[(self.S0[z+1]-self.S0[z])/(self.r[z+1]-self.r[z]) for z in range(179) if self.r[z]<=Au and self.r[z+1]>=Al]
        if not ms:raise ValueError('empty S0 slopes')
        return dP+max(ms)*aprime-2*self.pi*self.sigma*L
    def global_aperture_monotone(self):
        for j in range(179):
            L,U=self.r[j:j+2];h=U-L
            P0=self.B[j]+self.D[j];P1=self.B[j+1]+self.D[j+1]
            N0=self.qb*self.B[j]+self.qd*self.D[j];N1=self.qb*self.B[j+1]+self.qd*self.D[j+1]
            C=(N1*P0-N0*P1)/h
            qlo=min(N0/P0,N1/P1)
            qp_upper=max(F(0),C/min(P0,P1)**2)
            assert 2*qlo-U*qp_upper>0

def check_coverage(leaves,L,U,kind):
    if not leaves:raise ValueError('empty '+kind)
    spans=sorted(leaves,key=lambda t:t[0])
    if spans[0][0]!=L or spans[-1][1]!=U:raise ValueError('boundary mismatch '+kind)
    for i,(x,y) in enumerate(spans):
        if not x<y:raise ValueError('zero/reverse subband')
        if i and spans[i-1][1]!=x:raise ValueError('gap/overlap '+kind)

def verify(finite,source,diag,band):
    R=json.loads(Path(finite).read_text())
    caps,qs,rows,env,diagnostics=load_source(source,diag)
    B=json.loads(Path(band).read_text())
    if R['schema']!='HIST001D_MARCH180_SOURCE_CONSISTENT_FINITE_FULL_H_CROSSING_CELL_V1' or B['all_six_crossing_aperture_bands_positive'] is not True:
        raise ValueError('wrong artifact schema')
    if R['physical_provider_admitted'] or R['empirical_validation']!='NOT_ESTABLISHED':raise ValueError('promoted claim')
    if len(R['lenses'])!=len(B['lenses'])!=6:raise ValueError('missing lens')
    countglobal=0;countderiv=0
    for i,entry in enumerate(R['lenses']):
        if entry['lens']!=LENSES[i] or B['lenses'][i]['lens']!=LENSES[i]:raise ValueError('wrong lens')
        e=CheckLens(entry,rows[i],qs[i],caps[i]);e.global_aperture_monotone()
        k=e.k;lo,hi=e.r[k:k+2]
        if from_pair(entry['R_left_n_over_d'])!=lo or from_pair(entry['R_right_n_over_d'])!=hi:raise ValueError('source R endpoints')
        l, u=e.value(lo),e.value(hi)
        if not l[0]>0 or not u[1]<0:raise ValueError('nonbracketed finite H')
        if floor(l[0])!=entry['source_H_at_left_lower_Msun'] or ceil(u[1])!=entry['source_H_at_right_upper_Msun']:
            raise ValueError('source endpoint enclosure mismatch')
        sa=e.value(from_pair(entry['sampled_root_n_over_d']))
        if not (sa[0]>0 or sa[1]<0):raise ValueError('archived sampled root not separated')
        for j in range(179):
            if j==k:continue
            pieces=[x for x in entry['global_sign_subbands'] if x['source_R_cell']==j]
            spans=[(from_pair(x['L_n_over_d']),from_pair(x['U_n_over_d'])) for x in pieces]
            check_coverage(spans,e.r[j],e.r[j+1],'whole-H source cell')
            for spec,(L,U) in zip(pieces,spans):
                pmin,pmax=e.whole_panel(L,U,j)
                if j<k:
                    if spec['sign']!='positive' or not pmin>0 or floor(pmin)<spec['lower_or_upper_integer_Msun']:
                        raise ValueError('positive global source H witness')
                else:
                    if spec['sign']!='negative' or not pmax<0 or ceil(pmax)>spec['lower_or_upper_integer_Msun']:
                        raise ValueError('negative global source H witness')
                countglobal+=1
        if entry['global_sign_unknown_subbands'] or entry['global_offgrid_other_cells_unknown']:
            raise ValueError('unresolved global subband')
        slopes=entry['fractional_derivative_leaves']
        spans=[(F(int(x['L'][0]),int(x['L'][1])),F(int(x['U'][0]),int(x['U'][1]))) for x in slopes]
        check_coverage(spans,lo,hi,'crossing-cell derivative')
        for spec,(L,U) in zip(slopes,spans):
            upper=e.derivative_upper(L,U)
            if upper>=0 or ceil(upper)>spec['Hprime_upper_integer_ceiling_Msun_per_kpc']:
                raise ValueError('finite H monotonicity witness')
            countderiv+=1
        a,b=map(F,entry['root_bracket'])
        if not lo<a<b<hi or b-a>=F(1,10**8):raise ValueError('root bracket width')
        if e.value(a)[0]<=0 or e.value(b)[1]>=0:raise ValueError('root bracket signs')
        gap=B['lenses'][i]['minimum_gap_lower_floor_Msun']
        prior=env[i]['component_bounds'][1]['source_node_max_anchor_gap_upper_exact']
        nodal=F(int(prior['n']),int(prior['d']))
        if not 0<=nodal<1 or gap<1_000_000:raise ValueError('no whole-band H shadow gap')
        if B['lenses'][i]['original_180_source_node_sha256']!=caps[i]['node_sha256']:
            raise ValueError('source mismatch band archive')
        if not B['lenses'][i]['status']=='PASS_POSITIVE_FOR_ENTIRE_APERTURE_BAND':raise ValueError('band proof not pass')
    return {'status':'PASS_CONDITIONAL_EXACT_RATIONAL_FINITE_H_WITNESS',
            'global_sign_leaves':countglobal,'crossing_derivative_leaves':countderiv,
            'lenses':6,'full_selected_smooth_global_root_uniqueness_proved':False,
            'empirical_validation':'NOT_ESTABLISHED','physical_provider_admitted':False}

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    for p in ['finite','source','diag','band']:
        ap.add_argument('--'+p,type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    output=verify(a.finite,a.source,a.diag,a.band)
    a.out.write_text(json.dumps(output,sort_keys=True,indent=2)+'\n')
    print(output)
