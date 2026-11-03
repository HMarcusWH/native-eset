#!/usr/bin/env python3
"""Independent real-integral K certificate for ALL REAL radii between March nodes.
Conditional mathematical M_star, NOT physical density; fail closed.
"""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
import json,sys,time,struct
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'reference/hist001d_k180_bessel_integral_candidate'))
from real_integral_bessel import X,I0I1,selected_mass_prime
from source_audit import open_inputs,sha

def absmax(v):return max(abs(v.lower()),abs(v.upper()))
def ceilq(x):return -(-x.numerator//x.denominator)
def floorq(x):return x.numerator//x.denominator
def packed(x):return [str(x.lower()),str(x.upper())]

def makepoint(r,F,Fp,M,Mp,p):
    y=r/(2*p['Rd']);I0,I1=I0I1(y);det=I0*I0+I1*I1
    K0=(I0*F+I1/y)/det;K1=(I0/y-I1*F)/det
    if min(F.lower(),K0.lower(),K1.lower())<=0 or Fp.upper()>=0:
        raise ValueError('non-positive Bessel interval')
    Fpp=4*F-2*Fp/y-2*I1*K1/(y*y)
    if Fpp.lower()<=0 or Mp.lower()<=0:raise ValueError('Bessel/Fsecond/Mprime positivity failed')
    return dict(r=r,F=F,Fp=Fp,Fpp=Fpp,M=M,Mp=Mp)

def gate_f(node,p):
    r=node['r'];y=r/(2*p['Rd'])
    B=p['Mb']*X(r)**2/X(r+p['a'])**2 +p['Md']*X(y)**3*node['F']
    if B.lower()<=0:raise ValueError('bad acceleration denominator')
    G=node['M']/B
    f=G/(p['delta']*(1+G))
    if f.lower()<=0 or f.upper()>=1:raise ValueError('bad gate source interval')
    return f

def mpp_bound(a,b,p):
    lo,hi=a['r'],b['r'];delta,n=p['delta'],p['n']
    f=X(gate_f(a,p).lower(),gate_f(b,p).upper())
    r=X(lo,hi);y=r/(2*p['Rd'])
    F=X(b['F'].lower(),a['F'].upper());Fp=X(a['Fp'].lower(),b['Fp'].upper())
    Fpp=X(b['Fpp'].lower(),a['Fpp'].upper())
    B=p['Mb']*r**2/(r+p['a'])**2+p['Md']*y**3*F
    Bp=2*p['Mb']*p['a']*r/(r+p['a'])**3+p['Md']/(2*p['Rd'])*(3*y*y*F+y**3*Fp)
    Bpp=2*p['Mb']*p['a']*(p['a']-2*r)/(r+p['a'])**4+p['Md']/(2*p['Rd'])**2*(6*y*F+6*y*y*Fp+y**3*Fpp)
    G=delta*f/(1-delta*f)
    fp=n*f*(1-f)/r
    fpp=n*f*(1-f)/(r*r)*(n*(1-2*f)-1)
    Gp=delta*fp/(1-delta*f)**2
    Gpp=delta*fpp/(1-delta*f)**2+2*delta*delta*fp*fp/(1-delta*f)**3
    return Bpp*G+2*Bp*Gp+B*Gpp

def cert_panel(a,b,p):
    mpp=mpp_bound(a,b,p); curv=absmax(mpp)
    delta=(b['r']-a['r'])*curv/2
    return min(a['Mp'].lower(),b['Mp'].lower())-delta,max(a['Mp'].upper(),b['Mp'].upper())+delta,curv

def run_lens(j,maxdepth=14):
    src,caps,analytic,_=open_inputs((ROOT/'inputs/saturation_parent_v1r1.zip').read_bytes())
    rfile=ROOT/f'results/lens_{j}.json';rec=json.loads(rfile.read_text())['lenses'][0]
    if rec['node_file_sha256']!=caps[j]['node_sha256'] or rec['lens_id']!=caps[j]['lens_id'] or rec['mode']!='all' or rec['evaluated_nodes']!=180:
        raise ValueError('inherited independent integral node identity failure')
    arr=list(struct.iter_unpack('>8d',src.read('inputs/'+caps[j]['node_file'])))
    p={k:Q.from_float(float.fromhex(analytic[j]['source_scalar_binary64_hex'][k])) for k in ('Mb','Md','a','Rd','delta','r0','n')}
    nodes=[]
    for i,(v,row) in enumerate(zip(rec['nodes'],arr)):
        def x(name):return X(Q(v[name][0]),Q(v[name][1]))
        if v['index']!=i or v['radius_binary64_hex']!=row[0].hex():raise ValueError('archived nodal radius/index mismatch')
        nodes.append(makepoint(Q.from_float(row[0]),x('Bessel_F_interval'),x('Bessel_Fprime_interval'),x('selected_M_interval'),x('selected_Mprime_interval'),p))
    if len(nodes)!=180:raise ValueError('180 source nodes required')
    points={x['r']:x for x in nodes};midpoints=[];panels=[];unresolved=[]
    st=time.monotonic()
    def check(k,a,b,depth):
        l,u,c=cert_panel(a,b,p)
        if l>0:
            panels.append(dict(cell=k,lo=str(a['r']),hi=str(b['r']),depth=depth,Mprime_lower_micro=floorq(l*10**6),Mprime_upper_micro=ceilq(u*10**6),Msecond_abs_ceil=ceilq(c)))
        elif depth<maxdepth:
            r=(a['r']+b['r'])/2
            if r not in points:
                M,Mp,aux=selected_mass_prime(r,p)
                q=makepoint(r,aux['F'],aux['Fp'],M,Mp,p)
                points[r]=q
                midpoints.append(dict(cell=k,r=str(r),F=packed(q['F']),Fp=packed(q['Fp']),Fpp=packed(q['Fpp']),M=packed(q['M']),Mp=packed(q['Mp'])))
            mid=points[r]
            check(k,a,mid,depth+1);check(k,mid,b,depth+1)
        else:
            unresolved.append(dict(cell=k,lo=str(a['r']),hi=str(b['r']),depth=depth,Mprime_lower_micro=floorq(l*10**6)))
    for i in range(179):
        check(i,nodes[i],nodes[i+1],0)
        if i%30==0:print('PROGRESS',j,i,'midpoint',len(midpoints),'panels',len(panels),'unresolved',len(unresolved),'seconds',round(time.monotonic()-st,1),flush=True)
    complete=(not unresolved and panels[0]['lo']==str(nodes[0]['r']) and panels[-1]['hi']==str(nodes[-1]['r']) and all(Q(a['hi'])==Q(b['lo']) for a,b in zip(panels,panels[1:])))
    obj=dict(schema='HIST001D_SELECTED_MSTAR_REAL_INTEGRAL_BESSEL_INTER_NODE_MPRIME_V1',lens_id=caps[j]['lens_id'],node_sha256=caps[j]['node_sha256'],all_real_selected_Mprime_positive=complete,nodes=180,accepted_panels=len(panels),extra_points=len(midpoints),panels=panels,midpoints=midpoints,unresolved=unresolved,
    source_scope='SELECTED_HISTORICAL_ACCELERATION_EQUIVALENT_MSTAR_NOT_PHYSICAL',physical_provider_admitted=False,empirical_validation='NOT_ESTABLISHED',maxdepth=maxdepth)
    dest=ROOT/'results'/f'continuous_lens_{j}.json';dest.write_text(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n')
    print('DONE',j,'pass',complete,'panels',len(panels),'newpoints',len(midpoints),'unresolved',len(unresolved),'SHA',sha(dest.read_bytes()),'seconds',round(time.monotonic()-st,1),flush=True)
    return obj
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--lens',type=int,choices=range(6),required=True);a.add_argument('--maxdepth',type=int,default=14);opts=a.parse_args();run_lens(opts.lens,opts.maxdepth)
