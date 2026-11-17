#!/usr/bin/env python3
"""Separate dyadic rational checker for six original source crossing-cell K180 envelopes.

Original 180 samples and independent signed all-node source-vs-smooth intervals;
no import of the crossing-band producer or its sqrt function.
"""
from __future__ import annotations
import io,json,struct,hashlib,zipfile,math
from pathlib import Path
from fractions import Fraction as F
from all180_independent import read_source,decode_ieee
P=Path(__file__).resolve().parent

def updiv(a,b):return -(-a//b)
def ceil(v):return -(-v.numerator//v.denominator)

def sqrt_upper(v:F,bits=184):
    if v<0:raise ValueError('square root positive')
    numerator=v.numerator << (2*bits)
    t=numerator//v.denominator
    j=math.isqrt(t)
    if j*j*v.denominator!=numerator:j+=1
    val=F(j,1<<bits)
    if val*val<v:raise ValueError('upper sqrt guard failed')
    return val

def sqrt_lower(v:F,bits=184):
    if v<0:raise ValueError('negative sqrt argument')
    j=math.isqrt((v.numerator << (2*bits))//v.denominator)
    val=F(j,1<<bits)
    if val*val>v:raise ValueError('lower sqrt guard failed')
    return val

def check():
    z3,cap,sm=read_source()
    hzip=zipfile.ZipFile(io.BytesIO(z3.read('inputs/march_180_grid.zip')))
    producer=json.loads((P/'results/crossing_band_producer.json').read_text())
    if len(producer['lenses'])!=6:raise ValueError('missing six source lens proof')
    rows=[]
    for c,s,p in zip(cap['lenses'],sm['lenses'],producer['lenses']):
        if c['lens_id']!=s['lens_id'] or c['lens_id']!=p['lens_id']:raise ValueError('source mismatch')
        lid=c['lens_id'];tag=lid.replace('+','p')
        payload=z3.read('inputs/'+c['node_file'])
        if hashlib.sha256(payload).hexdigest()!=c['node_sha256']:raise ValueError('original source node array changed')
        arr=[[decode_ieee(payload[i*64+8*j:i*64+8*(j+1)]) for j in range(8)] for i in range(180)]
        if not all(r[4]>0 and r[6]>0 and r[1]>0 for r in arr):raise ValueError('original source B/D projection cone')
        binH=hzip.read(f'sampled_binary64/{tag}.R_H_be64.bin')
        H=[(decode_ieee(binH[i*16:i*16+8]),decode_ieee(binH[i*16+8:i*16+16])) for i in range(180)]
        if len(H)!=len(arr) or any(x[0]!=y[0] for x,y in zip(H,arr)):
            raise ValueError('original sampled R identity')
        edges=[i for i in range(179) if H[i][1]*H[i+1][1]<0]
        if len(edges)!=1 or any(x[1]==0 for x in H):raise ValueError('historical sign-change source premise')
        j=edges[0]
        def parse_hex(h):return decode_ieee(struct.pack('>d',float.fromhex(h)))
        qmin=min(parse_hex(s['source_scalar_binary64_hex']['qb']),parse_hex(s['source_scalar_binary64_hex']['qd']))
        if not qmin>0:raise ValueError('positive baryonic axis ratio')
        A_hi=min(F(120),sqrt_upper(H[j+1][0]**2/qmin,bits=184))
        cert=json.loads((P/'results'/f'independent_all180_{tag}.json').read_text())
        dif=cert['signed_source_minus_smooth_Mprime_integer_intervals']
        if cert['node_sha256']!=c['node_sha256'] or len(dif)!=180:
            raise ValueError('missing independent signed 180 source intervals')
        value=F()
        for node,d in zip(arr,dif):
            ring,weight=node[0],node[1]
            if weight<=0:raise ValueError('source negative quadrature weight')
            if ring<=A_hi:phi=F(1)
            else:
                u=1-A_hi*A_hi/(ring*ring)
                if not 0<u<=1:raise ValueError('aperture upper guard')
                phi=1-sqrt_lower(u,bits=184)
            if not 0<=phi<=1:raise ValueError('cylinder kernel factor')
            value+=weight*max(abs(d[0]),abs(d[1]))*phi
        upper=ceil(value)
        if upper>p['certified_frozen_K180_shadow_density_substitution_crossing_cell_upper_integer_msun']:
            raise ValueError('producer understated original source K180 crossing band')
        rows.append({'lens_id':lid,'source_cell_index':j,'independent_K180_crossing_cell_upper_integer_msun':upper,'producer_bound_accepted':True})
    report={'schema':'HIST001D_SOURCE_MARCH180_CROSSING_K180_INDEPENDENT_RATIONAL_CHECK_V1',
        'original_source_46plus3_sha256':'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a',
        'six_original_source_crossing_cells':6,
        'all_source_rows_and_nodal_signed_interval_inputs_reverified':True,
        'physical_provider_admitted':False,'original_full_H_or_root_count_proved':False,
        'lenses':rows}
    out=P/'results/crossing_band_independent.json'
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print('INDEPENDENT_CROSSING_CELL_KERNEL_PASS',rows)
    print('SHA256',hashlib.sha256(out.read_bytes()).hexdigest())
    return report

if __name__=='__main__':check()
