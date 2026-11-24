#!/usr/bin/env python3
"""Independent broad bounded-variation quadrature bound (deliberately loose).
Uses independent all180 signed enclosures and C3 independently audited GLOBAL sup.
No calls to the producer's BV routine or Bessel mass library.
"""
import json,io,zipfile,hashlib,struct
from fractions import Fraction as R
from pathlib import Path
from all180_independent import decode_ieee
ROOT=Path(__file__).resolve().parent
ALL_SHA='2e3c13ba68bbed98ef2c529a2e331b15c666d8927da22daf1be78d33a79f6391'
C3_SHA='725d7ba004d1bd54fb6be2838ca995fc5ba7ce45b54213f1926f0d78bd7e7f11'
SRC_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
def sha(x):return hashlib.sha256(x).hexdigest()
def ceil(x):return -((-x.numerator)//x.denominator)

def run():
    A=(ROOT/'all180_parent.zip').read_bytes();C=(ROOT/'c3_derivative_parent.zip').read_bytes()
    assert sha(A)==ALL_SHA and sha(C)==C3_SHA
    za=zipfile.ZipFile(io.BytesIO(A));zc=zipfile.ZipFile(io.BytesIO(C))
    parent=zipfile.ZipFile(io.BytesIO(za.read('inputs/frozen_smooth_shadow_gradient_parent.zip')))
    q=parent
    for _ in range(3):q=zipfile.ZipFile(io.BytesIO(q.read([f for f in q.namelist() if f.endswith('.zip')][0])))
    original=zipfile.ZipFile(io.BytesIO(q.read('inputs/original_source_46_frozen.zip')))
    lock=json.loads(q.read('inputs/original_46plus3_lock.json'))
    assert lock['original_46plus3_composite_sha256']==SRC_SHA
    for name,hash_ in lock['source_filenames_sha256'].items():assert sha(original.read('swells_pack_v2/'+name))==hash_
    for name,hash_ in lock['archived_negative_controls_sha256'].items():assert sha(q.read('inputs/negative_controls/'+name))==hash_
    receipts=json.loads(q.read('results/source180_capture.json'))['lenses']
    ceilings=json.loads(zc.read('results/independent_M2_M3_envelope.json'))['lenses']
    assert len(receipts)==len(ceilings)==6
    bound_producer=json.loads((ROOT/'all_aperture_bv_producer.json').read_text())['lenses']
    result=[]
    for a,b,base in zip(receipts,ceilings,bound_producer):
        assert a['lens_id']==b['lens_id']==base['lens_id']
        source=q.read('inputs/'+a['node_file']);assert sha(source)==a['node_sha256']
        rows=[[decode_ieee(source[j*64+k*8:j*64+(k+1)*8]) for k in range(8)] for j in range(180)]
        x=[v[0] for v in rows];weights=[v[1] for v in rows]
        assert all(x[j]<x[j+1] for j in range(179))
        assert all(w>0 for w in weights)
        signed=json.loads(za.read('results/independent_all180_'+a['lens_id'].replace('+','p')+'.json'))
        assert signed['source_sha256']==SRC_SHA
        ints=signed['signed_source_minus_smooth_Mprime_integer_intervals']
        assert len(ints)==180
        C4pi=decode_ieee(struct.pack('>d',float.fromhex('0x1.921fb54442d18p+3')))
        D=[C4pi*x[j]**2*rows[j][3] for j in range(180)]
        G=max(max(abs(D[j]-int(ints[j][0])),abs(D[j]-int(ints[j][1]))) for j in range(180))
        h=[x[j+1]-x[j] for j in range(179)];hmax=max(h);L=x[-1]-x[0]
        M2=int(b['independent_M2_cap_ceiling'])
        # Conservative: sup|g| <= max sampled g magnitude + (hmax/2) M2,
        # Var(g) <= L M2. For monotone 0<=phi<=1, Var(phi)<=1.
        h_bound= hmax/2 * (G + hmax*M2/2 + L*M2)
        idealw=[h[0]/2]+[(h[j-1]+h[j])/2 for j in range(1,179)]+[h[-1]/2]
        # Each pointwise g_j is at most G; use common bound even for weight delta.
        e_w=G*sum((abs(weights[j]-idealw[j]) for j in range(180)),R())
        upper=ceil(h_bound+e_w)
        assert upper>=base['all_real_smooth_candidate_K180_sampled_Mprime_vs_mathematical_continuum_abs_error_upper_integer_Msun']
        result.append({'lens_id':a['lens_id'],
                       'independent_global_M2_source_verified':True,
                       'independent_uniform_all_apertures_upper_integer_Msun':upper,
                       'source_node_sha256':a['node_sha256'],
                       'producer_tighter_cellwise_bound_contained':True,
                       'useful_root_scale_bound':False})
        print('INDEPENDENT_BV',a['lens_id'],'upper',upper,flush=True)
    out={'schema':'HIST001D_MARCH180_INDEPENDENT_GLOBAL_M2_BV_UPPER_V1',
         'lenses':result,'selected_smooth_acceleration_mass_only':True,
         'original_source':SRC_SHA,'all180_SHA256':ALL_SHA,'C3_SHA256':C3_SHA,
         'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
         'original_continuous_root_theorem_proved':False}
    dest=ROOT/'all_aperture_bv_independent.json';dest.write_bytes((json.dumps(out,sort_keys=True,indent=2)+'\n').encode())
    print('OUTPUT_SHA',sha(dest.read_bytes()))
if __name__=='__main__':run()
