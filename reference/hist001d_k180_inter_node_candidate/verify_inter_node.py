#!/usr/bin/env python3
"""Independent Fraction-interval witness verifier for mathematical inter-node M_*'.

No imported K0/K1 implementation, X interval class, or producing subpanel arithmetic.
Relies on source-locked externally certified F,F' and M,M' endpoint enclosures.
Reconstructs F'' from I0,I1 positive-series enclosures and Wronskian.
No physical density or off-grid original SciPy error theorem.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,zipfile,io
from fractions import Fraction as Q
from pathlib import Path

SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
SAT_SHA='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'

def sha(b):return hashlib.sha256(b).hexdigest()
class R:
    __slots__=('l','u')
    def __init__(self,l,u=None):
        self.l=Q(l);self.u=self.l if u is None else Q(u)
        if self.l>self.u:raise ValueError('inverted witness interval')
    def __add__(self,x):
        x=I(x);return R(self.l+x.l,self.u+x.u)
    __radd__=__add__
    def __neg__(self):return R(-self.u,-self.l)
    def __sub__(self,x):return self+-I(x)
    def __rsub__(self,x):return I(x)-self
    def __mul__(self,x):
        x=I(x);a=[self.l*x.l,self.l*x.u,self.u*x.l,self.u*x.u];return R(min(a),max(a))
    __rmul__=__mul__
    def __truediv__(self,x):
        x=I(x)
        if x.l<=0<=x.u:raise ValueError('interval divisor contains 0')
        return self*R(1/x.u,1/x.l)
    def __rtruediv__(self,x):return I(x)/self
    def __pow__(self,n):
        if not isinstance(n,int) or n<0:raise ValueError('power nonnegative integer only')
        if n==0:return R(1)
        if n%2==1:return R(self.l**n,self.u**n)
        if self.l>=0:return R(self.l**n,self.u**n)
        if self.u<=0:return R(self.u**n,self.l**n)
        return R(0,max(abs(self.l),abs(self.u))**n)
    def __repr__(self):return f'R({float(self.l)},{float(self.u)})'
def I(x):return x if isinstance(x,R) else R(x)
def box(v):
    if not isinstance(v,list) or len(v)!=2:return (_ for _ in ()).throw(ValueError('two boundary strings required'))
    return R(Q(v[0]),Q(v[1]))
def floor(x):return x.numerator//x.denominator
def ceil(x):return -(-x.numerator//x.denominator)

def i_bessel_positive_series(y:Q,terms:int=160):
    """Independent exact-Fraction positive 0F1 series, rigorous geometric tail."""
    if y<=0 or terms<2:raise ValueError('positive y')
    z=y*y/4
    t0=s0=Q(1);t1=s1=y/2
    for k in range(1,terms):
        t0*=z/Q(k*k)
        t1*=z/Q(k*(k+1))
        s0+=t0;s1+=t1
    n=terms
    next0=t0*z/Q(n*n);next1=t1*z/Q(n*(n+1))
    ratio0=z/Q((n+1)*(n+1));ratio1=z/Q((n+1)*(n+2))
    if max(ratio0,ratio1)>=1:raise ValueError('I-series tail not contractive')
    return R(s0,s0+next0/(1-ratio0)),R(s1,s1+next1/(1-ratio1))

def independent_fpp(q,p):
    y=q['r']/(2*p['Rd']);J0,J1=i_bessel_positive_series(y)
    det=J0**2+J1**2
    K0=(J0*q['F']+J1/y)/det
    K1=(J0/y-J1*q['F'])/det
    if min(K0.l,K1.l)<=0 or q['F'].l<=0 or q['Fp'].u>=0:
        raise ValueError('Wronskian Bessel positivity failed')
    Fpp=4*q['F']-2*q['Fp']/y-2*J1*K1/(y*y)
    if Fpp.l<=0:raise ValueError('Wronskian Fpp positivity failed')
    # Cached Fpp must be consistent with an independently derived exact interval
    if q.get('Fpp') is not None and max(Fpp.l,q['Fpp'].l)>min(Fpp.u,q['Fpp'].u):
        raise ValueError('Fpp cached interval incompatible with Fraction derivation')
    return Fpp

def f_at_point(node,p):
    r=node['r'];y=r/(2*p['Rd'])
    B=p['Mb']*I(r)**2/I(r+p['a'])**2+p['Md']*I(y)**3*node['F']
    if B.l<=0:raise ValueError('invalid B')
    G=node['M']/B
    f=G/(p['delta']*(1+G))
    if f.l<=0 or f.u>=1:raise ValueError('out-of-range gate f')
    return f

def Msecond_envelope(left,right,p):
    r=R(left['r'],right['r']);y=r/(2*p['Rd']);delta=p['delta'];n=p['n']
    f0=f_at_point(left,p);f1=f_at_point(right,p)
    f=R(f0.l,f1.u)
    F=R(right['F'].l,left['F'].u)
    Fp=R(left['Fp'].l,right['Fp'].u)
    Fpp=R(right['Fpp_ind'].l,left['Fpp_ind'].u)
    B=p['Mb']*r**2/(r+p['a'])**2+p['Md']*y**3*F
    Bp=2*p['Mb']*p['a']*r/(r+p['a'])**3+p['Md']/(2*p['Rd'])*(3*y**2*F+y**3*Fp)
    Bpp=2*p['Mb']*p['a']*(p['a']-2*r)/(r+p['a'])**4+p['Md']/(2*p['Rd'])**2*(6*y*F+6*y**2*Fp+y**3*Fpp)
    G=delta*f/(1-delta*f)
    df=n*f*(1-f)/r
    ddf=n*f*(1-f)/(r*r)*(n*(1-2*f)-1)
    dG=delta*df/(1-delta*f)**2
    ddG=delta*ddf/(1-delta*f)**2+2*delta*delta*df*df/(1-delta*f)**3
    return Bpp*G+2*Bp*dG+B*ddG

def make_node(r,parts,p):
    q={'r':r,'F':box(parts['F']),'Fp':box(parts['Fp']),'Fpp':box(parts['Fpp']),'M':box(parts['M']),'Mp':box(parts['Mp'])}
    if min(q['F'].l,q['Fpp'].l,q['M'].l,q['Mp'].l)<=0 or q['Fp'].u>=0:raise ValueError('node sign failure')
    q['Fpp_ind']=independent_fpp(q,p)
    return q

def old_node(r,v,p):
    return make_node(r,{'F':v['Bessel_F_interval'],'Fp':v['Bessel_Fprime_interval'],'Fpp':v['independently_derived_Fpp_box'],'M':v['selected_M_interval'],'Mp':v['selected_Mprime_interval']},p)

def verify_lens(j,root:Path,extra_data=None):
    """Verify SHA-locked source-identity and all 179 cell dyadic coverage."""
    sat=(root/'inputs/saturation_parent_v1r1.zip').read_bytes()
    if sha(sat)!=SAT_SHA:raise ValueError('wrong saturation parent')
    z=zipfile.ZipFile(io.BytesIO(sat));parent=zipfile.ZipFile(io.BytesIO(z.read('original_parent.zip')))
    freeze=zipfile.ZipFile(io.BytesIO(parent.read('inputs/frozen_source_parent.zip')))
    D=zipfile.ZipFile(io.BytesIO(freeze.read('inputs/original_march_D120_q_parent.zip')))
    S=zipfile.ZipFile(io.BytesIO(D.read('inputs/original_march180_parent_v1r1.zip')))
    captures=json.loads(S.read('results/source180_capture.json'))['lenses']
    analytic=json.loads(parent.read('results/producer_analytic_source_gradient.json'))['lenses']
    cap=captures[j];a=analytic[j]
    raw=S.read('inputs/'+cap['node_file'])
    if sha(raw)!=cap['node_sha256']:raise ValueError('wrong original 180 nodes')
    arr=list(struct.iter_unpack('>8d',raw))
    prior=json.loads((root/f'results/lens_{j}.json').read_text())
    rec=prior['lenses'][0]
    if prior['source_original_46plus3_SHA256']!=SOURCE_SHA or rec['node_file_sha256']!=cap['node_sha256'] or rec['evaluated_nodes']!=180 or rec['lens_id']!=cap['lens_id']:
        raise ValueError('wrong prior Bessel certificate')
    p={k:Q.from_float(float.fromhex(a['source_scalar_binary64_hex'][k])) for k in ('Mb','Md','a','Rd','delta','r0','n')}
    if not (p['Mb']>0 and p['Md']>0 and p['Rd']>0 and p['a']>0 and p['delta']<1 and p['delta']>0 and p['n']>0 and p['r0']>0):raise ValueError('invalid model domain')
    def midpoint_parts(x):return {k:x[k] for k in ('F','Fp','Fpp','M','Mp')}
    # Independent Fpp for the 180 original nodes is reconstructed from F/Fp, not trusted from producer.
    originals=[]
    for idx,v in enumerate(rec['nodes']):
        rr=Q.from_float(arr[idx][0])
        if v['index']!=idx or v['radius_binary64_hex']!=arr[idx][0].hex():raise ValueError('bad original node alignment')
        q={'r':rr,'F':box(v['Bessel_F_interval']),'Fp':box(v['Bessel_Fprime_interval']),
           'M':box(v['selected_M_interval']),'Mp':box(v['selected_Mprime_interval'])}
        q['Fpp_ind']=independent_fpp({'r':rr,'F':q['F'],'Fp':q['Fp'],'Fpp':None},p)
        q['Fpp']=q['Fpp_ind']
        originals.append(q)
    out=json.loads((root/f'results/continuous_lens_{j}.json').read_text()) if extra_data is None else extra_data
    if out['lens_id']!=cap['lens_id'] or out['node_sha256']!=cap['node_sha256'] or not out['all_real_selected_Mprime_positive'] or out['unresolved'] or out['nodes']!=180 or out['physical_provider_admitted'] or out['empirical_validation']!='NOT_ESTABLISHED':
        raise ValueError('invalid claim or identity')
    mids={}
    for m in out['midpoints']:
        rr=Q(m['r'])
        if rr in mids or rr in (q['r'] for q in originals):raise ValueError('duplicated midpoint')
        mids[rr]=make_node(rr,midpoint_parts(m),p)
    points={q['r']:q for q in originals};points.update(mids)
    groups={k:[] for k in range(179)}
    for panel in out['panels']:
        k=panel['cell'];lo=Q(panel['lo']);hi=Q(panel['hi'])
        if k not in groups or lo not in points or hi not in points or not originals[k]['r']<=lo<hi<=originals[k+1]['r']:
            raise ValueError('panel source geometry/alignment')
        depth=panel['depth'];width=originals[k+1]['r']-originals[k]['r']
        if depth<0 or depth>out['maxdepth'] or hi-lo!=width/(2**depth):
            raise ValueError('non-dyadic panel')
        L,Rr=points[lo],points[hi]
        cellMpp=Msecond_envelope(L,Rr,p)
        c=max(abs(cellMpp.l),abs(cellMpp.u))
        val=min(L['Mp'].l,Rr['Mp'].l)-(hi-lo)*c/2
        upper=max(L['Mp'].u,Rr['Mp'].u)+(hi-lo)*c/2
        if not (val>0 and Q(panel['Mprime_lower_micro'],10**6)<=val and Q(panel['Mprime_upper_micro'],10**6)>=upper and Q(panel['Msecond_abs_ceil'])>=c):
            raise ValueError(f'panel false bound or positivity: lens {j} cell {k}')
        groups[k].append((lo,hi))
    for k,panels in groups.items():
        if not panels:raise ValueError('missing original cell')
        panels.sort()
        if panels[0][0]!=originals[k]['r'] or panels[-1][1]!=originals[k+1]['r'] or any(panels[i][1]!=panels[i+1][0] for i in range(len(panels)-1)):
            raise ValueError('gap or overlap in original radial cell')
    if len(out['panels'])!=out['accepted_panels'] or len(mids)!=out['extra_points']:
        raise ValueError('panel/point count not truthful')
    return {'lens_id':out['lens_id'],'radial_cells':179,'verified_subpanels':len(out['panels']),'midpoint_count':len(mids),'everywhere_positive':True}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);args=parser.parse_args()
    result=[verify_lens(i,args.root) for i in range(6)]
    report={'schema':'HIST001D_INDEPENDENT_FRACTION_REAL_RADIUS_WITNESS_VERIFIER_V1','all_pass':True,'results':result,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    target=args.root/'results/verify_independent.json'
    target.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print('VERIFIED',sum(x['verified_subpanels'] for x in result),'panels',sum(x['midpoint_count'] for x in result),'extra points',flush=True)
if __name__=='__main__':main()
