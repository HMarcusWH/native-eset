"""Source-frozen March 180-grid component-interpolant: exact rational interval witness.
No claim of original source off-grid floating implementation, continuous physical mass, Weyl, or empirical admission.
"""
from __future__ import annotations
import bisect, hashlib, io, json, math, struct, zipfile
from fractions import Fraction as F
from pathlib import Path
import numpy as np

PARENT = Path(__file__).resolve().parent/'inputs'/'original_march_D120_q_parent.zip'
EXPECTED_SHA='8178dfb07aa4c070b5f10e7de2c1e4130ffe777efb08d57382f4aae9cfcd4132'
FROZEN_LOCK='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'

def hexsha(x): return hashlib.sha256(x).hexdigest()
def frac(v): return F.from_float(float(v))
def sqrt_box(value:F, bits=64):
    assert value>=0
    n=value.numerator;d=value.denominator; base=1<<bits
    k=math.isqrt((n*base*base)//d)
    return F(k,base),F(k+1,base)
def ceil_frac(x:F):return -(-x.numerator//x.denominator)
class Lens:
    def __init__(self,lid,rows,sigma,qb,qd,source_H):
        self.lid=lid;self.r=[frac(x[0]) for x in rows]
        self.B=[frac(x[4]) for x in rows];self.D=[frac(x[6]) for x in rows]
        self.S0=[frac(x[5]) for x in rows];self.S=[frac(x[7]) for x in rows]
        self.T=[frac(t) for t in np.pi*np.array([x[0] for x in rows])**2*sigma]
        self.qb=frac(qb);self.qd=frac(qd);self.original_H=[frac(h) for h in source_H]
        assert len(self.r)==len(self.T)==180
        assert all(self.r[i]<self.r[i+1] for i in range(179))
        assert all(self.B[i]>0 and self.D[i]>0 and self.S0[i]>=0 for i in range(180))
        assert all(self.B[i]<=self.B[i+1] and self.D[i]<=self.D[i+1] and self.S0[i]<=self.S0[i+1] and self.T[i]<self.T[i+1] for i in range(179))
        self.h=[self.r[i+1]-self.r[i] for i in range(179)]
        self.bs=[(self.B[i+1]-self.B[i])/self.h[i] for i in range(179)]
        self.ds=[(self.D[i+1]-self.D[i])/self.h[i] for i in range(179)]
        self.ts=[(self.T[i+1]-self.T[i])/self.h[i] for i in range(179)]
        self.ss=[(self.S0[i+1]-self.S0[i])/self.h[i] for i in range(179)]
        self.n0=[self.qb*self.B[i]+self.qd*self.D[i] for i in range(180)]
        self.p0=[self.B[i]+self.D[i] for i in range(180)]
        self.cert_inputs={"lens_id":self.lid,"r_sha256":hexsha(b''.join(struct.pack('>d',float(v)) for v in self.r)),"nodal_B_sha256":hexsha(b''.join(struct.pack('>d',float(v)) for v in self.B)),"nodal_D_sha256":hexsha(b''.join(struct.pack('>d',float(v)) for v in self.D)),"nodal_S0_sha256":hexsha(b''.join(struct.pack('>d',float(v)) for v in self.S0)),"nodal_T_sha256":hexsha(b''.join(struct.pack('>d',float(v)) for v in self.T)),"original_H_sha256":hexsha(b''.join(struct.pack('>d',float(v)) for v in self.original_H))}
    def lin(self,values,i,x):return values[i]+(x-self.r[i])*(values[i+1]-values[i])/self.h[i]
    def pl(self,values,x):
        if x<=self.r[0]:return values[0]
        if x>=self.r[-1]:return values[-1]
        i=bisect.bisect_right(self.r,x)-1
        return self.lin(values,i,x)
    def q(self,i,x):return self.lin(self.n0,i,x)/self.lin(self.p0,i,x)
    def A_box(self,i,l,u,bits=56):
        ql=self.q(i,l);qu=self.q(i,u);qmin=min(ql,qu);qmax=max(ql,qu)
        # A bounded by interval arithmetic on R and q, with no reliance on monotonicity of A.
        sl,_=sqrt_box(1/qmax,bits);_,su=sqrt_box(1/qmin,bits)
        return min(self.r[-1],l*sl),min(self.r[-1],u*su),qmin,qmax
    def S_box(self,i,l,u,bits=56):
        alo,ahi,qmin,qmax=self.A_box(i,l,u,bits)
        return self.pl(self.S0,alo),self.pl(self.S0,ahi),alo,ahi,qmin,qmax
    def H_box(self,i,l,u,bits=56):
        slo,shi,*_=self.S_box(i,l,u,bits)
        return self.lin(self.B,i,l)+self.lin(self.D,i,l)+slo-self.lin(self.T,i,u), self.lin(self.B,i,u)+self.lin(self.D,i,u)+shi-self.lin(self.T,i,l)
    def H_point(self,i,x,bits=72):return self.H_box(i,x,x,bits)
    def dH_upper(self,i,l,u,bits=56):
        slo,shi,alo,ahi,qmin,qmax=self.S_box(i,l,u,bits)
        # The possible raw-shadow slopes at all A in [alo,ahi] with capped plateau.
        ia=max(0,bisect.bisect_right(self.r,alo)-1)
        ib=min(178,bisect.bisect_left(self.r,ahi))
        # no need to be sharp: including slopes of an extra adjacent bin is safe
        sslope=max(self.ss[max(0,ia):min(179,max(ia+1,ib))],default=F(0))
        p_left=self.lin(self.p0,i,l);p_right=self.lin(self.p0,i,u)
        N_left=self.lin(self.n0,i,l);N_right=self.lin(self.n0,i,u)
        # q' exact = (N'P - NP')/P²; sign constant on each radial cell
        C=self.n0[i+1]*self.p0[i]-self.n0[i]*self.p0[i+1]
        qprime_max=max(F(0),-C)/(self.h[i]*min(p_left,p_right)**2)
        _,one_over_sqrt=sqrt_box(1/qmin,bits)
        Aprime_up=one_over_sqrt*(1+u*qprime_max/(2*qmin))
        derivative_ub=self.bs[i]+self.ds[i]+sslope*Aprime_up-self.ts[i]
        return derivative_ub

def load():
    data=PARENT.read_bytes();assert hexsha(data)==EXPECTED_SHA
    z=zipfile.ZipFile(io.BytesIO(data));assert z.testzip() is None
    parent_bytes=z.read('inputs/original_march180_parent_v1r1.zip');assert hexsha(parent_bytes)=='0a643e81a9ab542dce8f158bc5135d94478d9145ab33036aae5813907f3655a1'
    z2=zipfile.ZipFile(io.BytesIO(parent_bytes));assert z2.testzip() is None
    lock=json.loads(z2.read('inputs/original_46plus3_lock.json'))
    assert lock['original_46plus3_composite_sha256']==FROZEN_LOCK
    src_bytes=z2.read('inputs/original_source_46_frozen.zip');assert hexsha(src_bytes)=='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
    src=zipfile.ZipFile(io.BytesIO(src_bytes)); assert src.testzip() is None
    for p,s in lock['source_filenames_sha256'].items():assert hexsha(src.read('swells_pack_v2/'+p))==s
    for p,s in lock['archived_negative_controls_sha256'].items():assert hexsha(z2.read('inputs/negative_controls/'+p))==s
    sourcecap=json.loads(z2.read('results/source180_capture.json'))
    angularcap=json.loads(z.read('results/source120_capture.json'))
    g=zipfile.ZipFile(io.BytesIO(z2.read('inputs/march_180_grid.zip')))
    lenses=[]
    for cap in angularcap['lenses']:
        lid=cap['lens_id'];file='inputs/March180_source_nodes_'+lid.replace('+','p')+'.be64'
        rows=list(struct.iter_unpack('>8d',z2.read(file)))
        oldgrid=list(struct.iter_unpack('>dd',g.read('sampled_binary64/'+lid.replace('+','p')+'.R_H_be64.bin')))
        sc=next(t for t in sourcecap['lenses'] if t['lens_id']==lid)
        assert hexsha(z2.read(file))==sc['node_sha256']
        assert all(x[0]==y[0] for x,y in zip(rows,oldgrid))
        sigma=float.fromhex(sc['original_sigma_hex'])
        q_b=float.fromhex(cap['qb_hex']);q_d=float.fromhex(cap['qd_hex'])
        model=Lens(lid,rows,sigma,q_b,q_d,[x[1] for x in oldgrid])
        # Proof source node correspondence via Python/Numpy (not a mathematical proof of float errors).
        rad=np.array([r[0] for r in rows]);B=np.array([x[4] for x in rows]);D=np.array([x[6] for x in rows]);S=np.array([x[7] for x in rows]);T=np.pi*rad**2*sigma
        assert np.array_equal((B+D+S-T).view(np.uint64),np.array([x[1] for x in oldgrid]).view(np.uint64))
        q=(q_b*B+q_d*D)/(B+D)
        A=np.minimum(rad[-1],rad/np.sqrt(q))
        S0=np.array([x[5] for x in rows]);
        assert np.max(abs(np.interp(A,rad,S0)-S))<1
        lenses.append(model)
    return lenses

if __name__=='__main__':
    for l in load():
        print(l.lid,l.cert_inputs)
