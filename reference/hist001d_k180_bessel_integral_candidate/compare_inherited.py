#!/usr/bin/env python3
"""Reproduce exact-box overlap with authenticated inherited 512-bit K logarithmic series.

This step imports the *protected prior* SHA-locked math module ONLY for comparison.
The new real-integral engine never imports or calls it to calculate its own boxes.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile,importlib.util,tempfile,struct
from pathlib import Path
from fractions import Fraction as Q
from source_audit import open_inputs, SAT_SHA

def sha(x):return hashlib.sha256(x).hexdigest()
def run(source,receipts_dir):
    raw=Path(source).read_bytes()
    if sha(raw)!=SAT_SHA:raise ValueError('source archive invalid')
    src,caps,analytic,oldall=open_inputs(raw)
    oldcode=zipfile.ZipFile(io.BytesIO(raw)).read('all180_math.py')
    with tempfile.TemporaryDirectory(prefix='hist001d_prior_') as d:
        modpath=Path(d)/'old_512_math.py';modpath.write_bytes(oldcode)
        spec=importlib.util.spec_from_file_location('old_512_math',modpath)
        ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
        gamma=ref.euler_gamma()
        count=0
        prior_cross=json.loads(oldall.read('results/crossing_band_producer.json'))['lenses']
        for j,cap in enumerate(caps):
            lens=cap['lens_id']
            params={k:Q.from_float(float.fromhex(analytic[j]['source_scalar_binary64_hex'][k])) for k in ('Mb','Md','a','Rd','delta','r0','n')}
            ci=next(x['original_March_sampled_crossing_edge_index'] for x in prior_cross if x['lens_id']==lens)
            source_rows=list(struct.iter_unpack('>8d',src.read('inputs/'+cap['node_file'])))
            receipt=json.loads((Path(receipts_dir)/f'lens_{j}.json').read_text())['lenses'][0]['nodes']
            for i in sorted({0,179,*[k for k in (ci-1,ci,ci+1,ci+2) if 0<=k<180]}):
                r=Q.from_float(source_rows[i][0]);M,Mp,_=ref.source_mass(r,params,gamma)
                newM=(Q(receipt[i]['selected_M_interval'][0]),Q(receipt[i]['selected_M_interval'][1]))
                newMp=(Q(receipt[i]['selected_Mprime_interval'][0]),Q(receipt[i]['selected_Mprime_interval'][1]))
                if newM[0]>M.high() or M.low()>newM[1]:raise ValueError(f'M intervals disjoint {lens} {i}')
                if newMp[0]>Mp.high() or Mp.low()>newMp[1]:raise ValueError(f'Mprime intervals disjoint {lens} {i}')
                count+=1
    return {'schema':'HIST001D_INTEGRAL_VS_PRIOR_512_POWER_SERIES_OVERLAP_V1',
            'source_saturation_SHA256':SAT_SHA,'old_logarithmic_Bessel_source_sha256':sha(oldcode),
            'both_M_and_Mprime_overlap_count':count,'physical_provider_admitted':False,
            'empirical_validation':'NOT_ESTABLISHED'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--receipts-dir',required=True);ap.add_argument('--out',required=True)
    a=ap.parse_args();result=run(a.source,a.receipts_dir)
    out=Path(a.out);dat=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode();out.write_bytes(dat)
    print('PRIOR_POWER_SERIES_OVERLAP',result['both_M_and_Mprime_overlap_count'],'SHA',sha(dat))
