#!/usr/bin/env python3
"""Nonpromoting exact-rational historical March180 PL full-H bridge.

Identifies a *mathematically specified off-grid extension* of the original
stored March finite source (NOT the original source's sampled-root return).
All 8-by-180 stored binary64 values and q_b/q_d/Sigma/C4pi are exact fractions.
Uses outward fixed-point rational square-root enclosures only; no SciPy.

H_PL_source(R)=B_PL(R)+D_PL(R)+S0_PL(A(R)) - Cpi*sigma*R**2,
q(R)=(q_b B_PL+q_d D_PL)/(B_PL+D_PL), A=R/sqrt(q(R)).

One-sided derivative proofs split the original root-containing source R-cell
into dyadic subcells; no discontinuity or differentiability through A=r_j
is assumed. The same H at source samples differs from the recorded rounded
S values by bounded operation-level floating-point arithmetic.
"""
from __future__ import annotations
import argparse,bisect,hashlib,io,json,struct,zipfile
from fractions import Fraction as F
from math import isqrt
from pathlib import Path

SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
TOP_PARENT_SHA='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')
BITS=112

def sha(b):return hashlib.sha256(b).hexdigest()
def ff(x):return F.from_float(x)
def floor(x):return x.numerator//x.denominator
def ceil(x):return -((-x.numerator)//x.denominator)

def sqrt_rational_bounds(x:F, bits=112):
    if x<0:raise ValueError('negative square root')
    n=x.numerator<<(2*bits)
    a=isqrt(n//x.denominator)
    low=F(a,1<<bits)
    high=F(a if a*a*x.denominator==n else a+1,1<<bits)
    assert low*low<=x<=high*high
    return low,high

class FiniteLens:
    def __init__(self, name, rows, qb, qd, sigma, C4pi):
        self.name=name
        self.rows=rows
        self.r=[ff(z[0]) for z in rows]
        self.B=[ff(z[4]) for z in rows]
        self.S0=[ff(z[5]) for z in rows]
        self.D=[ff(z[6]) for z in rows]
        self.S=[ff(z[7]) for z in rows]
        self.qb=qb;self.qd=qd;self.sigma=sigma;self.Cpi=C4pi/4
        if len(rows)!=180 or len(set(self.r))!=180 or any(self.r[i]>=self.r[i+1] for i in range(179)):
            raise ValueError('original 180 mesh invalid')
        if any(z<=0 for z in self.B+self.D) or any(self.S0[i]>self.S0[i+1] for i in range(179)):
            raise ValueError('nonpositive baryon or nonmonotonic S0 source')
        if min(qb,qd,sigma,C4pi)<=0:raise ValueError('source scalar positivity')

    def pl(self, vals,R):
        if R<=self.r[0]:return vals[0]
        if R>=self.r[-1]:return vals[-1]
        i=bisect.bisect_right(self.r,R)-1
        return vals[i]+(vals[i+1]-vals[i])*(R-self.r[i])/(self.r[i+1]-self.r[i])

    def q(self,R):
        B=self.pl(self.B,R);D=self.pl(self.D,R)
        return (self.qb*B+self.qd*D)/(B+D)

    def A_box(self,R):
        q=self.q(R);lo,hi=sqrt_rational_bounds(q,BITS)
        if lo<=0:raise ValueError('unbounded A')
        return R/hi,R/lo

    def source_H_box(self,R):
        Alo,Ahi=self.A_box(R)
        if not 0<Alo<=Ahi:raise ValueError('A nonpositive or reversed')
        s0=self.pl(self.S0,Alo);s1=self.pl(self.S0,Ahi)
        target=self.Cpi*self.sigma*R*R
        base=self.pl(self.B,R)+self.pl(self.D,R)-target
        return base+s0,base+s1

    def nodal_archived_H(self,i):
        R=self.r[i]
        return self.B[i]+self.D[i]+self.S[i]-self.Cpi*self.sigma*R*R

    def source_cell(self,original_reported_root):
        k=bisect.bisect_right(self.r,original_reported_root)-1
        if not 0<=k<179 or not self.r[k]<original_reported_root<self.r[k+1]:
            raise ValueError('reported root not strictly in 180 source interval')
        return k,self.r[k],self.r[k+1]

    def h_derivative_upper(self,L,U,k):
        """Exact rational upper bound on derivative on [L,U] in R-cell k.

        On subbands where A crosses a source radius, take max of BOTH PL
        shadow slopes; no illegal derivative through the A-knot is used.
        """
        R0,R1=self.r[k:k+2]
        if not R0<=L<U<=R1:raise ValueError('R cell domain')
        h=R1-R0;B0,B1=self.B[k:k+2];D0,D1=self.D[k:k+2]
        P0=B0+D0;P1=B1+D1;N0=self.qb*B0+self.qd*D0;N1=self.qb*B1+self.qd*D1
        dP=(P1-P0)/h; C=(N1*P0-N0*P1)/h
        def P(R):return P0+dP*(R-R0)
        qL=self.q(L);qU=self.q(U);qmin=min(qL,qU)
        if qmin<=0:raise ValueError('negative q')
        plower=min(P(L),P(U));qpneg=max(F(0),-C/(plower*plower))
        sqlo,_=sqrt_rational_bounds(qmin,BITS)
        # q'(R) has the same sign as C; dropping negative q' correction
        # when C>=0 is a mathematically conservative upper bound.
        Aprime_upper=(1+U*qpneg/(2*qmin))/sqlo
        A_l,_=self.A_box(L);_,A_u=self.A_box(U)
        if not self.r[0]<A_l<A_u<self.r[-1]:raise ValueError('aperture band')
        slopes=[(self.S0[j+1]-self.S0[j])/(self.r[j+1]-self.r[j])
                 for j in range(179) if self.r[j]<=A_u and self.r[j+1]>=A_l]
        if not slopes:raise ValueError('missing shadow slope')
        Slope=max(slopes)
        upper=dP+Slope*Aprime_upper-2*self.Cpi*self.sigma*L
        return upper,{'Pderiv':str(dP),'max_shadow_slope':str(Slope),'Aprime_upper':str(Aprime_upper)}

    def certify_cell_decreasing(self,k,R0,R1,max_depth=16):
        leaves=[];unknown=[]
        def go(L,U,d):
            high,dbg=self.h_derivative_upper(L,U,k)
            rec={'L':(str(L.numerator),str(L.denominator)),'U':(str(U.numerator),str(U.denominator)),
                 'depth':d,'Hprime_upper_integer_ceiling_Msun_per_kpc':ceil(high)}
            if high<0:
                leaves.append(rec);return
            if d>=max_depth:
                unknown.append(rec);return
            T=(L+U)/2
            go(L,T,d+1);go(T,U,d+1)
        go(R0,R1,0)
        return leaves,unknown

    def root_bracket(self,L,U,iterations=34):
        a,b=self.source_H_box(L);c,d=self.source_H_box(U)
        if a<=0 or d>=0:raise ValueError('H does not bracket crossing')
        for _ in range(iterations):
            t=(L+U)/2
            hlo,hhi=self.source_H_box(t)
            if hlo>0:L=t
            elif hhi<0:U=t
            else:break
        return L,U

    def q_monotonic_global(self):
        """Strict A'(R)>0 on all original source R cells with exact Q."""
        margins=[]
        for j in range(179):
            R0,R1=self.r[j:j+2];h=R1-R0
            P0=self.B[j]+self.D[j];P1=self.B[j+1]+self.D[j+1]
            N0=self.qb*self.B[j]+self.qd*self.D[j]
            N1=self.qb*self.B[j+1]+self.qd*self.D[j+1]
            q0=N0/P0;q1=N1/P1
            C=(N1*P0-N0*P1)/h
            qpmax=max(F(0),C/min(P0,P1)**2)
            margin=2*min(q0,q1)-R1*qpmax
            if margin<=0:raise ValueError('A(R) nonmonotone source cell')
            margins.append(margin)
        return min(margins)

    def global_sign_interval(self,L,U,k):
        """Enclose H(R) throughout [L,U] using nondecreasing B,D,S0,A,T.

        This is an *interval sign test*, not a derivative assertion.
        """
        if not self.r[k]<=L<U<=self.r[k+1]:raise ValueError('not one R cell')
        if self.B[k+1]<self.B[k] or self.D[k+1]<self.D[k]:
            raise ValueError('source baryonic mass not monotone')
        Al,_=self.A_box(L);_,Au=self.A_box(U)
        lo=self.pl(self.B,L)+self.pl(self.D,L)+self.pl(self.S0,Al)-self.Cpi*self.sigma*U*U
        hi=self.pl(self.B,U)+self.pl(self.D,U)+self.pl(self.S0,Au)-self.Cpi*self.sigma*L*L
        return lo,hi

    def certify_global_exclusion(self,crossing_cell,max_depth=22):
        signed=[];unknown=[]
        def go(L,U,k,d,required_sign):
            low,high=self.global_sign_interval(L,U,k)
            if required_sign=='positive' and low>0:
                signed.append((k,d,'positive',floor(low),L,U));return
            if required_sign=='negative' and high<0:
                signed.append((k,d,'negative',ceil(high),L,U));return
            if d>=max_depth:
                unknown.append((k,d,'unknown',floor(low),ceil(high),L,U));return
            t=(L+U)/2
            go(L,t,k,d+1,required_sign);go(t,U,k,d+1,required_sign)
        for k in range(179):
            if k==crossing_cell:continue
            need='positive' if k<crossing_cell else 'negative'
            go(self.r[k],self.r[k+1],k,0,need)
        return signed,unknown

    def sampled_crossings(self):
        H=[self.nodal_archived_H(i) for i in range(180)]
        return [(i, 'positive_to_negative' if H[i]>0 and H[i+1]<0 else 'other')
                for i in range(179) if H[i]*H[i+1]<0]


def load_source(path:Path,diag_path:Path):
    """Use nested original SHA+manifest source; fail on any substituted inputs."""
    with zipfile.ZipFile(path) as outer:
        man=json.loads(outer.read('MANIFEST_SHA256.json'))
        if man.get('schema')!='HIST001D_MARCH180_K180_SATURATION_SOURCE_INTEGRITY_V1':raise ValueError('outer manifest schema')
        for name,digest in man['files'].items():
            if sha(outer.read(name))!=digest:raise ValueError('outer manifest mismatch '+name)
        parent=outer.read('original_parent.zip')
    if sha(parent)!=TOP_PARENT_SHA:raise ValueError('original parent mismatch')
    with zipfile.ZipFile(io.BytesIO(parent)) as a:
        f=a.read('inputs/frozen_source_parent.zip')
    with zipfile.ZipFile(io.BytesIO(f)) as b:
        d=b.read('inputs/original_march_D120_q_parent.zip')
    with zipfile.ZipFile(io.BytesIO(d)) as c:
        qmeta=json.loads(c.read('results/source120_capture.json'))['lenses']
        rad=c.read('inputs/original_march180_parent_v1r1.zip')
    with zipfile.ZipFile(io.BytesIO(rad)) as e:
        cap=json.loads(e.read('results/source180_capture.json'))['lenses']
        if len(cap)!=len(qmeta)!=6:raise ValueError('six lenses expected')
        lock=json.loads(e.read('inputs/original_46plus3_lock.json'))
        if lock['original_46plus3_composite_sha256']!=SOURCE_SHA:raise ValueError('original source lock mismatch')
        src=e.read('inputs/original_source_46_frozen.zip')
        with zipfile.ZipFile(io.BytesIO(src)) as source:
            for key,digest in lock['source_filenames_sha256'].items():
                if sha(source.read('swells_pack_v2/'+key))!=digest:raise ValueError('original source content '+key)
        rows=[]
        for c0 in cap:
            bb=e.read('inputs/'+c0['node_file'])
            if sha(bb)!=c0['node_sha256'] or len(bb)!=180*64:raise ValueError('180 source node hash mismatch')
            rows.append(list(struct.iter_unpack('>8d',bb)))
        nodal=json.loads(e.read('results/frozen_stencil_all_real_envelope_producer.json'))
    with open(diag_path) as fd:dig=json.load(fd)
    if [x['lens_id'] for x in cap]!=list(LENSES) or [x['lens_id'] for x in qmeta]!=list(LENSES):
        raise ValueError('source lens alignment')
    if [x['lens'] for x in dig['lens_results']]!=list(LENSES):raise ValueError('diagnostic lens alignment')
    return cap,qmeta,rows,nodal['lenses'],dig['lens_results']

def execute(source,diag,out,*,depth=16,root_steps=34):
    cap,qmeta,rows,nodal,diagnostics=load_source(source,diag)
    result=[]
    for i in range(6):
        c=cap[i];q=qmeta[i];raw=rows[i]
        lens=FiniteLens(c['lens_id'],raw,ff(float.fromhex(q['qb_hex'])),ff(float.fromhex(q['qd_hex'])),
                        ff(float.fromhex(c['original_sigma_hex'])),ff(float.fromhex(c['original_pi4_float_hex'])))
        r_reported=ff(diagnostics[i]['sampled_R_root_kpc'])
        k,L,U=lens.source_cell(r_reported)
        crossings=lens.sampled_crossings()
        signL=lens.source_H_box(L);signU=lens.source_H_box(U)
        sample_H=lens.source_H_box(r_reported)
        if signL[0]<=0 or signU[1]>=0:raise ValueError('source H endpoint bracket')
        derivative_leaves,unknown=lens.certify_cell_decreasing(k,L,U,max_depth=depth)
        q_margin=lens.q_monotonic_global()
        signs,sign_unknown=lens.certify_global_exclusion(k,max_depth=22)
        bracket=(None,None) if unknown else lens.root_bracket(L,U,iterations=root_steps)
        p=nodal[i]['component_bounds'][1]
        if p['component']!='SHADOW_SPHERICAL_K180':raise ValueError('wrong node proof component')
        gap=F(int(p['source_node_max_anchor_gap_upper_exact']['n']),int(p['source_node_max_anchor_gap_upper_exact']['d']))
        if not 0<=gap<1:raise ValueError('missing rigorous nodal Q/S0 bridge')
        r={'lens':lens.name,'root_cell_index':k,
           'sampled_root_n_over_d':[str(r_reported.numerator),str(r_reported.denominator)],
           'R_left_n_over_d':[str(L.numerator),str(L.denominator)],
           'R_right_n_over_d':[str(U.numerator),str(U.denominator)],
           'archived_nodal_sign_crossings':crossings,
           'q_aperture_monotonic_179_source_cells':q_margin>0,
           'global_offgrid_PL_source_other_cells_excluded':not bool(sign_unknown),
           'global_offgrid_other_cells_signed_subbands':len(signs),
           'global_offgrid_other_cells_unknown':len(sign_unknown),
           'global_sign_summary':{'positive_subbands':sum(v[2]=='positive' for v in signs),'negative_subbands':sum(v[2]=='negative' for v in signs),
                                  'worst_positive_lower_integer_msun':min([v[3] for v in signs if v[2]=='positive'],default=None),
                                  'worst_negative_upper_integer_msun':max([v[3] for v in signs if v[2]=='negative'],default=None)},
           'source_H_at_left_lower_Msun':floor(signL[0]),'source_H_at_right_upper_Msun':ceil(signU[1]),
           'source_H_at_original_sample_root_interval_integer_Msun':[floor(sample_H[0]),ceil(sample_H[1])],
           'original_sample_root_is_not_root_of_this_offgrid_finite_model':sample_H[0]>0 or sample_H[1]<0,
           'H_source_strictly_decreasing_full_root_cell':not bool(unknown),
           'derivative_certified_subcells':len(derivative_leaves),'derivative_unresolved':len(unknown),
           'worst_derivative_upper_integer_Msun_per_kpc':max(x['Hprime_upper_integer_ceiling_Msun_per_kpc'] for x in derivative_leaves) if derivative_leaves else None,
           'root_bracket':[str(bracket[0]),str(bracket[1])] if bracket[0] is not None else None,
           'root_bracket_rounded':[float(bracket[0]),float(bracket[1])] if bracket[0] is not None else None,
           'maximum_nodal_S0_vs_Q_upper_fraction':[str(gap.numerator),str(gap.denominator)],
           'fractional_derivative_leaves':derivative_leaves,
           'global_sign_subbands':[{'source_R_cell':j,'depth':d,'sign':sign,
                                    'lower_or_upper_integer_Msun':n,
                                    'L_n_over_d':[str(L.numerator),str(L.denominator)],
                                    'U_n_over_d':[str(U.numerator),str(U.denominator)]}
                                   for j,d,sign,n,L,U in signs],
           'fractional_derivative_unknown':unknown,
           'global_sign_unknown_subbands':[{'source_R_cell':j,'depth':d,'sign':sign,
                                            'L_n_over_d':[str(L.numerator),str(L.denominator)],
                                            'U_n_over_d':[str(U.numerator),str(U.denominator)]}
                                           for j,d,sign,_,_,L,U in sign_unknown],
           'no_original_offgrid_source_run_claim':True,
           'no_physical_source_or_continuum_root_claim':True}
        result.append(r)
        print(lens.name,'nodal crossings',crossings,'strictly decreasing',not bool(unknown),
              'leaves',len(derivative_leaves),'unknown',len(unknown),'H ends',r['source_H_at_left_lower_Msun'],r['source_H_at_right_upper_Msun'],
              'root bracket',r['root_bracket_rounded'],'global_h_exclusion',not bool(sign_unknown),'global_subbands',len(signs),'unknown',len(sign_unknown),flush=True)
    receipt={'schema':'HIST001D_MARCH180_SOURCE_CONSISTENT_FINITE_FULL_H_CROSSING_CELL_V1',
            'original_source_sha256':SOURCE_SHA,
            'source_model':'EXACT_BINARY64_ORIGINAL_GRID_PL_B_D_S0_AND_QEFF_PL_EXTENSION',
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'continuous_real_root_count_proved':False,'math_selected_source_root_theorem_proved':False,
            'lenses':result}
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--diag',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--depth',type=int,default=16)
    a=ap.parse_args()
    execute(a.source,a.diag,a.out,depth=a.depth)
