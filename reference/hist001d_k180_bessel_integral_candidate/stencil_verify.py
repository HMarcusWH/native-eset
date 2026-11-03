#!/usr/bin/env python3
"""Independent exact-rational node-stencil contraction from separately generated real-integral boxes.

The verifier DOES NOT import the integral producer or special-function code.
It only trusts interval endpoints after archive SHA checking; re-runs
interval arithmetic with Fraction and IEEE754 bit decoding, and re-tests
positive frozen weights, complete 180-grid, and the derived all-A L1 bound.
"""
from __future__ import annotations
import zipfile,hashlib,io,json,struct,argparse
from pathlib import Path
from fractions import Fraction as Q
SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
SAT_SHA='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
PARENT_SHA='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
LENS=['J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720']
def digest(b):return hashlib.sha256(b).hexdigest()
def ceil(x):return -((-x.numerator)//x.denominator)
def parse64(b):
    bits=int.from_bytes(b,byteorder='big'); sign=-1 if bits>>63 else 1
    E=(bits>>52)&2047; m=bits&((1<<52)-1)
    if E==2047: raise ValueError('NaN and infinity disallowed')
    if E==0:e=1-1023-52
    else:m|=(1<<52);e=E-1023-52
    return Q(sign*m*(1<<e)) if e>=0 else Q(sign*m,1<<-e)

def parse_fraction_box(pair):
    if not isinstance(pair,list) or len(pair)!=2:raise ValueError('interval shape')
    a,b=Q(pair[0]),Q(pair[1]);
    if a>b:raise ValueError('interval inverted')
    return a,b

def scale_interval(k,interval):return (k*interval[0],k*interval[1]) if k>=0 else (k*interval[1],k*interval[0])
def plus(A,B):return (A[0]+B[0],A[1]+B[1])
def minus(A,B):return (A[0]-B[1],A[1]-B[0])
def maxabs(A):return max(abs(A[0]),abs(A[1]))

def verify(source_path,receipt_dir):
    raw=Path(source_path).read_bytes()
    if digest(raw)!=SAT_SHA:raise ValueError('protected saturation identity')
    z=zipfile.ZipFile(io.BytesIO(raw))
    pbytes=z.read('original_parent.zip')
    if digest(pbytes)!=PARENT_SHA:raise ValueError('protected original parent SHA')
    parent=zipfile.ZipFile(io.BytesIO(pbytes))
    aa=zipfile.ZipFile(io.BytesIO(parent.read('inputs/frozen_source_parent.zip')))
    bb=zipfile.ZipFile(io.BytesIO(aa.read('inputs/original_march_D120_q_parent.zip')))
    cc=zipfile.ZipFile(io.BytesIO(bb.read('inputs/original_march180_parent_v1r1.zip')))
    lock=json.loads(cc.read('inputs/original_46plus3_lock.json'))
    if lock['original_46plus3_composite_sha256']!=SOURCE_SHA:raise ValueError('source composite')
    source=json.loads(cc.read('results/source180_capture.json'))['lenses']
    analytic=json.loads(parent.read('results/producer_analytic_source_gradient.json'))['lenses']
    old=zipfile.ZipFile(io.BytesIO(z.read('all180_parent.zip')))
    out=[]
    for j,lens in enumerate(LENS):
        rec=json.loads((Path(receipt_dir)/f'lens_{j}.json').read_text())
        if len(rec['lenses'])!=1:raise ValueError('expected 1 lens per protected result')
        this=rec['lenses'][0]
        if rec.get('source_saturation_SHA256')!=SAT_SHA or rec.get('physical_provider_admitted') is not False or rec.get('empirical_validation')!='NOT_ESTABLISHED' or this['lens_id']!=lens or this['evaluated_nodes']!=180 or this['mode']!='all':raise ValueError('source/claim contract mismatch')
        cap=source[j]
        if cap['lens_id']!=lens or analytic[j]['lens_id']!=lens or cap['node_sha256']!=this['node_file_sha256']:raise ValueError('lens source mismatch')
        bb=cc.read('inputs/'+cap['node_file'])
        if len(bb)!=180*64 or digest(bb)!=cap['node_sha256']:raise ValueError('original binary64 hash mismatch')
        rawrows=[[parse64(bb[i*64+k*8:i*64+(k+1)*8]) for k in range(8)] for i in range(180)]
        rs=[r[0] for r in rawrows];ws=[r[1] for r in rawrows]
        if not all(rs[k]<rs[k+1] for k in range(179)) or not all(w>0 for w in ws):raise ValueError('source mesh/weight invalid')
        C=Q.from_float(float.fromhex(analytic[j]['source_scalar_binary64_hex']['C4pi']))
        masses=[];derivs=[]
        for i,n in enumerate(this['nodes']):
            if n['index']!=i or n['radius_binary64_hex']!=float(rs[i]).hex():raise ValueError('source row/index mismatch')
            ivM=parse_fraction_box(n['selected_M_interval']);ivP=parse_fraction_box(n['selected_Mprime_interval'])
            if ivP[0]<=0:raise ValueError('Mprime no longer strictly positive')
            # Integer reference is not the proof; it is checked as a consistency guard.
            ss=C*rs[i]**2*rawrows[i][3]
            delta=minus((ss,ss),ivP)
            old_bounds=n['old_512_source_grad_minus_Mprime_integer_msun_per_kpc']
            if delta[0]<old_bounds[0] or delta[1]>old_bounds[1]:raise ValueError('new independent derivative not contained by old certificate')
            masses.append(ivM);derivs.append(ivP)
        stencil=[]
        for i in range(180):
            if i==0: d=scale_interval(Q(1)/(rs[1]-rs[0]),minus(masses[1],masses[0]))
            elif i==179:d=scale_interval(Q(1)/(rs[-1]-rs[-2]),minus(masses[-1],masses[-2]))
            else:
                h0=rs[i]-rs[i-1];h1=rs[i+1]-rs[i]
                # Lagrange 3-point derivative, independent of producer weighted-secants formulation.
                terms=(scale_interval(-h1/(h0*(h0+h1)),masses[i-1]),
                       scale_interval((h1-h0)/(h0*h1),masses[i]),
                       scale_interval(h0/(h1*(h0+h1)),masses[i+1]))
                d=plus(plus(terms[0],terms[1]),terms[2])
            stencil.append(d)
        total=Q(0);maximum=Q(0);worst_idx=0
        stored_mass_diff=[];mass_width=Q(0)
        for i in range(180):
            Dstored=C*rs[i]**2*rawrows[i][3]
            discrepancy=minus((Dstored,Dstored),stencil[i])
            width=maxabs(discrepancy)
            total+=ws[i]*width
            if width>maximum:maximum=width;worst_idx=i
            if masses[i][1]-masses[i][0]>mass_width:mass_width=masses[i][1]-masses[i][0]
        oldreceipt=json.loads(old.read('results/all180_rational_'+lens.replace('+','p')+'.json'))
        inherited=ceil(sum((ws[i]*Q(oldreceipt['stored_vs_ideal_stencil_absolute_upper_micro_msun_per_kpc'][i],1000000) for i in range(180)),Q(0))*1000000)
        bound_micros=ceil(total*10**6)
        result={'lens_id':lens,'source_nodes':180,'node_file_sha256':cap['node_sha256'],
                'new_integral_K_all_aperture_source_to_ideal_stencil_bound_micro_Msun':bound_micros,
                'new_integral_K_all_aperture_source_to_ideal_stencil_bound_Msun':bound_micros/1e6,
                'inherited_512_integral_source_to_ideal_stencil_bound_micro_Msun':inherited,
                'new_bound_below_inherited_micro_ceiling':bound_micros<=inherited,
                'max_mass_interval_width_upper_integer_micro_Msun':ceil(mass_width*10**6),
                'max_nodal_gradient_residual_upper_integer_micro_Msun_per_kpc':ceil(maximum*10**6),
                'max_residual_index':worst_idx,
                'protected_result_SHA256':digest((Path(receipt_dir)/f'lens_{j}.json').read_bytes())}
        if not result['new_bound_below_inherited_micro_ceiling']:raise ValueError(f'new independent bound exceeds inherited old cap for {lens}: {bound_micros} vs {inherited}')
        out.append(result)
        print('INDEPENDENT_STENCIL',lens,'bound (micro Msun)',bound_micros,'inherited micro Msun',inherited,'masswidth (micro)',result['max_mass_interval_width_upper_integer_micro_Msun'],flush=True)
    return {'schema':'HIST001D_INDEPENDENT_K_REAL_INTEGRAL_ALL180_STENCIL_VERIFICATION_V1',
            'original_source_46plus3_sha256':SOURCE_SHA,'saturation_parent_sha256':SAT_SHA,
            'bound_uniform_all_A_ge0':True,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'six_lenses_all_180_nodes':True,'lenses':out}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--receipts-dir',required=True);ap.add_argument('--out',required=True)
    args=ap.parse_args();v=verify(args.source,args.receipts_dir)
    data=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode();Path(args.out).write_bytes(data)
    print('SUMMARY_SHA256',digest(data))
