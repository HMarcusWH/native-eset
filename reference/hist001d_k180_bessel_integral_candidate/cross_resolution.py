#!/usr/bin/env python3
"""Cross-resolution integral Bessel, exact Wronskian and optional mpmath diagnostic."""
import json,hashlib,argparse
from pathlib import Path
from fractions import Fraction as Q
import real_integral_bessel as B
from source_audit import open_inputs, SAT_SHA

def calc(source):
    src,cap,ana,old=open_inputs(Path(source).read_bytes())
    res=[]
    for j in range(6):
        p={k:Q.from_float(float.fromhex(ana[j]['source_scalar_binary64_hex'][k])) for k in ('Mb','Md','a','Rd','delta','r0','n')}
        parent=json.loads(old.read('results/crossing_band_producer.json'))['lenses']
        cell=next(x['original_March_sampled_crossing_edge_index'] for x in parent if x['lens_id']==cap[j]['lens_id'])
        import struct
        raw=src.read('inputs/'+cap[j]['node_file'])
        x=list(struct.iter_unpack('>8d',raw))
        for i in [cell]:
            r=Q.from_float(x[i][0]);y=r/(2*p['Rd'])
            B.H=Q(1,32)
            f32,p32,_=B.F_and_prime(y)
            a,b=B.I0I1(y);c,d,_=B.K0K1_integral(y)
            wr=a*d+b*c
            target=Q(1)/y
            if not wr.lower()<=target<=wr.upper():raise ValueError('Wronskian failed (1/32)')
            B.H=Q(1,64)
            f64,p64,_=B.F_and_prime(y)
            a,b=B.I0I1(y);c,d,_=B.K0K1_integral(y)
            wr=a*d+b*c
            if not wr.lower()<=target<=wr.upper():raise ValueError('Wronskian failed (1/64)')
            if not (f64.lower()<=f32.upper() and f32.lower()<=f64.upper()):raise ValueError('F boxes disjoint')
            if not (p64.lower()<=p32.upper() and p32.lower()<=p64.upper()):raise ValueError('Fprime boxes disjoint')
            res.append({'lens_id':cap[j]['lens_id'],'index':i,
                        'I0K1_plus_I1K0_contains_exact_inverse_y_on_both_grids':True,
                        'F_two_grid_intersection':True,'Fprime_two_grid_intersection':True,
                        'two_grid_step_h':['1/32','1/64']})
    return {'schema':'HIST001D_BESSEL_INTEGRAL_TWO_RESOLUTIONS_AND_WRONSKIAN_V1',
            'source_saturation_sha256':SAT_SHA,'two_grid_cross_checks':len(res),
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'checks':res}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
    args=p.parse_args();o=calc(args.source)
    Path(args.out).write_text(json.dumps(o,sort_keys=True,indent=2)+'\n')
    print('CROSS_GRID_WRONSKIAN',len(o['checks']),'SHA256',hashlib.sha256(Path(args.out).read_bytes()).hexdigest())
