#!/usr/bin/env python3
"""Strictly scoped targeted refinement of selected M* radial Peano bounds.

Selected historical acceleration-equivalent M*(r) ONLY; no physical density,
no original arbitrary-radius SciPy claim, no Einstein root count promotion.
All protected inputs are hashed and remain out of public GitHub.
"""
from __future__ import annotations
import argparse,hashlib,heapq,io,json,struct,sys,time,zipfile
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for module in ('hist001d_k180_bessel_integral_candidate',
               'hist001d_k180_inter_node_candidate','hist001d_k180_cancel_aware_candidate'):
    sys.path.insert(0,str(ROOT/'reference'/module))
from real_integral_bessel import X, selected_mass_prime  # noqa: E402
from inter_node_producer import makepoint,mpp_bound,cert_panel  # noqa: E402
from source_audit import open_inputs  # noqa: E402
from affine_kernel import kernel_integral  # noqa: E402
import signed_affine_producer as sp  # noqa: E402

CANCEL_SHA='639ee5973a59a63c14e63d59522c03d659de10dd6d7c195586de13e8186159c9'
INTER_SHA='63c4df7dcc4e5493fe9e2ea667ebb1a7d8ec418a8d03400096eb5fedf53d4691'
SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
EXTRAS=128
WITNESS_INDICES={0:(0,89,118,128),1:(0,61,128),2:(0,61,93,128),3:(0,92,114,128),4:(0,53,119,128),5:(0,83,107,128)}
LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')
_PARENT=None

def sha(raw):return hashlib.sha256(raw).hexdigest()
def floor(v):return v.numerator//v.denominator
def ceil(v):return -(-v.numerator//v.denominator)
def packed(v):return [str(v.lower()),str(v.upper())]

def load_parent():
    global _PARENT
    if _PARENT is not None:return _PARENT
    raw=(ROOT/'inputs'/'cancel_parent_v1.zip').read_bytes()
    if sha(raw)!=CANCEL_SHA:raise ValueError('protected cancellation-aware parent SHA')
    z=zipfile.ZipFile(io.BytesIO(raw))
    man=json.loads(z.read('MANIFEST_SHA256.json'))
    if man.get('physical_provider_admitted') is not False or man.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('prior claim guard')
    for path,digest in man['files'].items():
        if sha(z.read(path))!=digest:raise ValueError('protected parent member SHA '+path)
    inter=z.read('inputs/inter_node_parent_v1.zip')
    if sha(inter)!=INTER_SHA:raise ValueError('inter-node parent SHA')
    iz=zipfile.ZipFile(io.BytesIO(inter))
    sat=iz.read('inputs/saturation_parent_v1r1.zip');band=iz.read('inputs/crossing_band_parent_v1r2.zip')
    nodal=[json.loads(iz.read(f'results/lens_{j}.json')) for j in range(6)]
    radial=[json.loads(iz.read(f'results/continuous_lens_{j}.json')) for j in range(6)]
    bv=[json.loads(iz.read(f'results/bv_band_lens_{j}.json')) for j in range(6)]
    sp.PARENT_CACHE=(sat,band,nodal,radial,bv)
    prior=[json.loads(z.read(f'results/signed_lens_{j}.json')) for j in range(6)]
    assert len(prior)==6
    _PARENT=(z,prior,radial)
    return _PARENT

@dataclass
class Panel:
    a:F
    b:F
    pa:dict
    pb:dict
    mpp:X
    cap:int
    depth:int
    origin:int

def original(j):
    load_parent()
    sat,_,nodal,radial,_=sp.parent()
    source,captures,analytic,_=open_inputs(sat)
    cap=captures[j]
    if cap['lens_id']!=LENSES[j]:raise ValueError('lens sequence')
    raw=source.read('inputs/'+cap['node_file'])
    if sha(raw)!=cap['node_sha256'] or len(raw)!=180*64:raise ValueError('180 source node bytes')
    rows=list(struct.iter_unpack('>8d',raw))
    rec=nodal[j]['lenses'][0];rrec=radial[j]
    p={k:F.from_float(float.fromhex(analytic[j]['source_scalar_binary64_hex'][k])) for k in ('Mb','Md','a','Rd','delta','r0','n')}
    def box(v,key):return X(F(v[key][0]),F(v[key][1]))
    points={}
    for row,v in zip(rows,rec['nodes']):
        r=F.from_float(row[0]);points[r]=makepoint(r,box(v,'Bessel_F_interval'),box(v,'Bessel_Fprime_interval'),box(v,'selected_M_interval'),box(v,'selected_Mprime_interval'),p)
    for v in rrec['midpoints']:
        r=F(v['r']);points[r]=makepoint(r,box(v,'F'),box(v,'Fp'),box(v,'M'),box(v,'Mp'),p)
    panels=[]
    for k,item in enumerate(rrec['panels']):
        a,b=F(item['lo']),F(item['hi'])
        if a not in points or b not in points or not a<b:raise ValueError('missing initial radial endpoints')
        q=mpp_bound(points[a],points[b],p)
        c=ceil(max(abs(q.lower()),abs(q.upper())))
        if c>item['Msecond_abs_ceil']:raise ValueError('inherited radial curvature cap')
        panels.append(Panel(a,b,points[a],points[b],q,item['Msecond_abs_ceil'],0,k))
    if len(panels)!=rrec['accepted_panels'] or any(a.b!=b.a for a,b in zip(panels,panels[1:])):raise ValueError('radial geometry')
    return cap['lens_id'],cap['node_sha256'],p,panels

def W(Alo,Ahi,pan):
    return sp.weighted_curvature_kernel_upper(Alo,Ahi,pan.a,pan.b,12).upper()/2

def refine_lens(j,extras=EXTRAS):
    st=time.monotonic()
    z,prior,_=load_parent()
    lens,node_sha,p,originals=original(j)
    Alo,Ahi,meta=sp.get_band(j)
    old=prior[j]
    if old['lens']!=lens or old['original_180_source_node_sha256']!=node_sha or old['n']!=128:raise ValueError('old signed affine lens identity')
    queue=[];seq=0
    for pa in originals:
        heapq.heappush(queue,(-F(pa.cap)*W(Alo,Ahi,pa),seq,pa));seq+=1
    splits=[]
    for i in range(extras):
        _,_,pan=heapq.heappop(queue)
        mid=(pan.a+pan.b)/2
        M,Mp,aux=selected_mass_prime(mid,p)
        pt=makepoint(mid,aux['F'],aux['Fp'],M,Mp,p)
        splits.append({'origin':pan.origin,'a':str(pan.a),'b':str(pan.b),'mid':str(mid),
                       'depth':pan.depth+1,'F':packed(pt['F']),'Fp':packed(pt['Fp']),
                       'M':packed(pt['M']),'Mp':packed(pt['Mp'])})
        for a,b,pa,pb in ((pan.a,mid,pan.pa,pt),(mid,pan.b,pt,pan.pb)):
            mpp=mpp_bound(pa,pb,p)
            C=ceil(max(abs(mpp.lower()),abs(mpp.upper())))+1  # independent Fraction headroom, negligible in Msun
            lower,upper,_=cert_panel(pa,pb,p)
            if lower<=0:raise ValueError('refined real-radial Mprime positivity failed')
            child=Panel(a,b,pa,pb,mpp,C,pan.depth+1,pan.origin)
            heapq.heappush(queue,(-F(C)*W(Alo,Ahi,child),seq,child));seq+=1
        if (i+1)%32==0:print('MIDPOINTS',lens,i+1,'seconds',round(time.monotonic()-st,1),flush=True)
    leaves=sorted((entry[2] for entry in queue),key=lambda x:x.a)
    if len(leaves)!=len(originals)+extras or any(a.b!=b.a for a,b in zip(leaves,leaves[1:])):raise ValueError('broken radial coverage')
    per_root={}
    for leaf in leaves:
        per_root.setdefault(leaf.origin,[]).append(leaf)
    changed={k:v for k,v in per_root.items() if len(v)>1}
    Eabs=sum((F(t.cap)*W(Alo,Ahi,t) for t in leaves),F())
    prior_abs=old['independently_certifiable_symmetric_peano_remainder_ceiling_Msun']
    if Eabs>=prior_abs:raise ValueError('targeted Peano did not improve')
    print('CURVATURE',lens,'Eabs',float(Eabs),'old',prior_abs,'factor',float(prior_abs/Eabs),'seconds',round(time.monotonic()-st,1),flush=True)
    leaf_records=[{'origin':t.origin,'a':str(t.a),'b':str(t.b),'depth':t.depth,
                   'C_integer_Msecond_abs':t.cap,'signed_Msecond':packed(t.mpp),
                   'positive_Mprime_lower':str(min(t.pa['Mp'].lower(),t.pb['Mp'].lower())-(t.b-t.a)*t.cap/2),
                   'W_upper':str(W(Alo,Ahi,t))} for t in leaves]
    def evaluate(index):
        orig=old['point_values'][index]
        A=F(orig['A']);Q=X(F(orig['Q'][0]),F(orig['Q'][1]));L=X(F(orig['Plin'][0]),F(orig['Plin'][1]))
        for k in sorted(changed):
            base=originals[k]
            base_s=(base.pb['M']-base.pa['M'])/(base.b-base.a)
            L-=base_s*kernel_integral(A,base.a,base.b)
            for child in changed[k]:
                s=(child.pb['M']-child.pa['M'])/(child.b-child.a)
                L+=s*kernel_integral(A,child.a,child.b)
        dlow=Q.lower()-L.upper()-Eabs
        dhi=Q.upper()-L.lower()+Eabs
        return {'index':index,'A':str(A),'Q':packed(Q),'Lrefined':packed(L),
                'signed_D': [str(dlow),str(dhi)],'integer_D':[floor(dlow),ceil(dhi)],
                'strict_sign':1 if dlow>0 else (-1 if dhi<0 else 0)}
    anchors=[evaluate(k) for k in WITNESS_INDICES[j]]
    zeros=[];previous=None
    for point in anchors:
        if point['strict_sign']:
            if previous and previous['strict_sign']!=point['strict_sign']:
                zeros.append({'left_index':previous['index'],'right_index':point['index'],
                              'A_left':previous['A'],'A_right':point['A'],
                              'left_sign':previous['strict_sign'],'right_sign':point['strict_sign']})
            previous=point
    if not zeros:raise ValueError('no sign-reversal witness after refinement')
    if anchors[0]['index']!=0 or anchors[-1]['index']!=128:raise ValueError('aperture witnesses do not cover band ends')
    qbands=[]
    for aa,bb in zip(anchors,anchors[1:]):
        low=F(aa['Q'][0])-F(bb['Lrefined'][1])-Eabs
        high=F(bb['Q'][1])-F(aa['Lrefined'][0])+Eabs
        qbands.append([floor(low),ceil(high)])
    out={'schema':'HIST001D_SELECTED_MSTAR_TARGETED_PEANO_SIGN_REVERSALS_V1',
         'source_46plus3_sha256':SOURCE_SHA,'protected_cancel_parent_sha256':CANCEL_SHA,
         'protected_inter_node_parent_sha256':INTER_SHA,
         'lens':lens,'source_node_sha256':node_sha,'parent_signed_lens_sha256':sha(z.read(f'results/signed_lens_{j}.json')),
         'A_band':[str(Alo),str(Ahi)],'initial_radial_panels':len(originals),
         'added_integral_Bessel_midpoints':len(splits),'refined_radial_panels':len(leaves),
         'split_history':splits,'leaves':leaf_records,
         'E_symmetric_exact':str(Eabs),'E_symmetric_ceiling_integer_Msun':ceil(Eabs),
         'inherited_prior_symmetric_ceiling_integer_Msun':prior_abs,
         'anchors':anchors,'certified_zero_intervals':zeros,
         'certified_distinct_zero_lower_bound':len(zeros),
         'coarse_full_band_integer_enclosure_from_sparse_anchors':[min(a[0] for a in qbands),max(a[1] for a in qbands)],
         'positive_radial_Mstarprime_everywhere':True,
         'all_sign_definite_whole_band':False,'selected_smooth_quadrature_one_sign':False,
         'Einstein_residual_root_count_certified':False,'physical_provider_admitted':False,
         'empirical_validation':'NOT_ESTABLISHED',
         'mathematical_scope':'SELECTED_ACCELERATION_EQUIVALENT_MSTAR_ONLY'}
    print('RESULT',lens,'E',ceil(Eabs),'zeros>=',len(zeros),'aggregate',out['coarse_full_band_integer_enclosure_from_sparse_anchors'],'time',round(time.monotonic()-st,1),flush=True)
    return out

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--lens',type=int,required=True,choices=range(6));a.add_argument('--extra',type=int,default=EXTRAS);a.add_argument('--out',type=Path);args=a.parse_args()
    d=refine_lens(args.lens,args.extra)
    path=args.out or ROOT/'results'/f'targeted_lens_{args.lens}.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(d,sort_keys=True,separators=(',',':'))+'\n')
    print('OUTPUT_SHA256',sha(path.read_bytes()),flush=True)
