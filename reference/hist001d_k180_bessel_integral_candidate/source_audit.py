#!/usr/bin/env python3
"""Authenticated source read and independent Bessel real-integral certificate.

Does not import old 512/608-bit special-function implementations. For ALL source
nodes or 24 crossing-neighborhood nodes plus endpoints, returns real-integral
Bessel F,F' and selected M,M' rigorous enclosures. Original data stay protected.
"""
from __future__ import annotations
import json,hashlib,zipfile,io,struct,argparse,time
from fractions import Fraction as Q
from pathlib import Path
from real_integral_bessel import selected_mass_prime, X
SAT_SHA='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
ORIG_PARENT_SHA='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
LENS=['J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720']
def sha(b):return hashlib.sha256(b).hexdigest()
def upper(x):return -(-x.numerator//x.denominator)
def lower(x):return x.numerator//x.denominator
def fraction_double(s):return Q.from_float(float.fromhex(s))
def open_inputs(saturation:bytes):
    if sha(saturation)!=SAT_SHA:raise ValueError('saturation source SHA mismatch')
    z=zipfile.ZipFile(io.BytesIO(saturation))
    parentbytes=z.read('original_parent.zip')
    if sha(parentbytes)!=ORIG_PARENT_SHA:raise ValueError('original source parent SHA mismatch')
    parent=zipfile.ZipFile(io.BytesIO(parentbytes))
    frozen=zipfile.ZipFile(io.BytesIO(parent.read('inputs/frozen_source_parent.zip')))
    originalD=zipfile.ZipFile(io.BytesIO(frozen.read('inputs/original_march_D120_q_parent.zip')))
    source=zipfile.ZipFile(io.BytesIO(originalD.read('inputs/original_march180_parent_v1r1.zip')))
    lock=json.loads(source.read('inputs/original_46plus3_lock.json'))
    if lock['original_46plus3_composite_sha256']!=SOURCE_SHA:raise ValueError('source composite mismatch')
    frozen_source=zipfile.ZipFile(io.BytesIO(source.read('inputs/original_source_46_frozen.zip')))
    for k,v in lock['source_filenames_sha256'].items():
        if sha(frozen_source.read('swells_pack_v2/'+k))!=v:raise ValueError('changed source file '+k)
    for k,v in lock['archived_negative_controls_sha256'].items():
        if sha(source.read('inputs/negative_controls/'+k))!=v:raise ValueError('negative control changed '+k)
    capture=json.loads(source.read('results/source180_capture.json'))['lenses']
    analytic=json.loads(parent.read('results/producer_analytic_source_gradient.json'))['lenses']
    old=zipfile.ZipFile(io.BytesIO(z.read('all180_parent.zip')))
    return source,capture,analytic,old

def audit_lens(src,c,a,prev,mode='crossing'):
    lens=c['lens_id']
    assert lens==a['lens_id']
    raw=src.read('inputs/'+c['node_file'])
    assert len(raw)==180*64 and sha(raw)==c['node_sha256']
    rows=list(struct.iter_unpack('>8d',raw))
    p={k:fraction_double(a['source_scalar_binary64_hex'][k]) for k in ('Mb','Md','a','Rd','delta','r0','n')}
    C=fraction_double(a['source_scalar_binary64_hex']['C4pi'])
    oldrec=json.loads(prev.read('results/all180_rational_'+lens.replace('+','p')+'.json'))
    assert oldrec['source_180_node_sha256']==c['node_sha256']
    # Source-selected root cell from the original all180 frozen-source crossing receipt,
    # NOT guessed from the node record's projection columns.
    cb=json.loads(prev.read('results/crossing_band_producer.json'))
    obj=next((q for q in cb['lenses'] if q['lens_id']==lens),None)
    if not obj or obj['source_original_node_sha256']!=c['node_sha256']:
        raise ValueError('crossing-cell source mismatch')
    ci=obj['original_March_sampled_crossing_edge_index']
    if type(ci) is not int or not 0<=ci<179:
        raise ValueError('invalid source crossing index')
    indices=list(range(180)) if mode=='all' else sorted({0,179,*[k for k in (ci-1,ci,ci+1,ci+2) if 0<=k<180]})
    out=[]
    for i in indices:
        rr=Q.from_float(rows[i][0])
        m,mp,meta=selected_mass_prime(rr,p)
        # archived source gradient C4pi*r²*rho; may be positive but not physical
        dsrc=C*rr**2*Q.from_float(rows[i][3])
        oldbounds=oldrec['source_gradient_minus_smooth_Mprime_interval_integer_msun_per_kpc'][i]
        diff=X(dsrc)-mp
        # Old signed source-minus-new-M' bounds use floor/ceil integer Msun/kpc
        ours=[lower(diff.lower()),upper(diff.upper())]
        if ours[0]<oldbounds[0] or ours[1]>oldbounds[1]:
            raise ValueError(f'new real-integral Mprime not inside old 512 derivation at {lens} node {i}: {ours} versus {oldbounds}')
        if mp.lower()<=0:
            raise ValueError(f'new Mprime positivity fails at {lens} node {i}')
        out.append({'index':i,'radius_binary64_hex':rows[i][0].hex(),
                    'Bessel_F_interval':[str(meta['F'].lower()),str(meta['F'].upper())],
                    'Bessel_Fprime_interval':[str(meta['Fp'].lower()),str(meta['Fp'].upper())],
                    'selected_M_interval':[str(m.lower()),str(m.upper())],
                    'selected_Mprime_interval':[str(mp.lower()),str(mp.upper())],
                    'source_grad_minus_independent_Mprime_integer_msun_per_kpc':ours,
                    'old_512_source_grad_minus_Mprime_integer_msun_per_kpc':oldbounds,
                    'grid_points_used':meta['grid_points'],
                    'trapezoid_K_upper_bound':str(meta['trapezoid_upper']),
                    'tail_K_upper_bound':str(meta['tail_upper'])})
    return {'lens_id':lens,'node_file_sha256':c['node_sha256'],'original_crossing_node_index':ci,
            'mode':mode,'evaluated_nodes':len(out),'nodes':out}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--all',action='store_true')
    ap.add_argument('--lens-index',type=int,default=-1)
    args=ap.parse_args()
    src,capture,analytic,old=open_inputs(Path(args.source).read_bytes())
    lindices=range(6) if args.lens_index<0 else [args.lens_index]
    started=time.time()
    rows=[]
    for j in lindices:
        rec=audit_lens(src,capture[j],analytic[j],old,'all' if args.all else 'crossing')
        rows.append(rec)
        print('BESSEL_INTEGRAL_CERT',rec['lens_id'],rec['evaluated_nodes'],'elapsed',round(time.time()-started,1),flush=True)
    report={'schema':'HIST001D_INDEPENDENT_K0K1_REAL_INTEGRAL_SOURCE_CERT_V1',
            'engine':'INFINITE_TRAPEZOID_STRIP_ANALYTIC_INTEGER_INTERVAL_512BITS_NO_K_BESSEL_SERIES',
            'source_saturation_SHA256':SAT_SHA,'source_original_46plus3_SHA256':SOURCE_SHA,
            'status':'MATHEMATICAL_SELECTED_MSTAR_ONLY_NONPROMOTING',
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'all180_nodes_certified':bool(args.all and all(q['evaluated_nodes']==180 for q in rows)),
            'all_six_lenses_in_this_receipt':len(rows)==6,
            'lenses':rows}
    data=(json.dumps(report,sort_keys=True,separators=(',',':'))+'\n').encode()
    Path(args.out).write_bytes(data)
    print('REPORT_SHA256',sha(data),'total_evaluations',sum(x['evaluated_nodes'] for x in rows),'elapsed',round(time.time()-started,1))
if __name__=='__main__':main()
