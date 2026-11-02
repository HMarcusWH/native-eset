#!/usr/bin/env python3
"""Rigorous but very conservative all-aperture quadrature error candidate.
Conditional on independently archived exact-real smooth M2 cell bounds.
DOES NOT claim a useful root-scale error bound.
"""
import zipfile,io,json,struct,hashlib
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
C3_SHA='725d7ba004d1bd54fb6be2838ca995fc5ba7ce45b54213f1926f0d78bd7e7f11'
ALL180_SHA='2e3c13ba68bbed98ef2c529a2e331b15c666d8927da22daf1be78d33a79f6391'
PARENT_SHA='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
def sha(x):return hashlib.sha256(x).hexdigest()
def ceil(x):return -((-x.numerator)//x.denominator)

def calculate():
    rawc=(ROOT/'c3_derivative_parent.zip').read_bytes()
    rawa=(ROOT/'all180_parent.zip').read_bytes()
    assert sha(rawc)==C3_SHA and sha(rawa)==ALL180_SHA
    c3=zipfile.ZipFile(io.BytesIO(rawc));all180=zipfile.ZipFile(io.BytesIO(rawa))
    m2s=json.loads(c3.read('results/source_bound_M2_M3_rational_producer.json'))
    assert m2s['source_sha256']==SOURCE and len(m2s['lenses'])==6
    par=all180.read('inputs/frozen_smooth_shadow_gradient_parent.zip')
    assert sha(par)==PARENT_SHA
    z=zipfile.ZipFile(io.BytesIO(par))
    for _ in range(3):z=zipfile.ZipFile(io.BytesIO(z.read([x for x in z.namelist() if x.endswith('.zip')][0])))
    locked=json.loads(z.read('inputs/original_46plus3_lock.json'))
    assert locked['original_46plus3_composite_sha256']==SOURCE
    original=zipfile.ZipFile(io.BytesIO(z.read('inputs/original_source_46_frozen.zip')))
    for path,h in locked['source_filenames_sha256'].items():assert sha(original.read('swells_pack_v2/'+path))==h
    for path,h in locked['archived_negative_controls_sha256'].items():assert sha(z.read('inputs/negative_controls/'+path))==h
    origin=json.loads(z.read('results/source180_capture.json'))['lenses']
    assert len(origin)==6
    source4pi=Q.from_float(float.fromhex('0x1.921fb54442d18p+3'))
    out=[]
    for l,c in zip(origin,m2s['lenses']):
        assert l['lens_id']==c['lens_id']
        tag=l['lens_id'].replace('+','p')
        q=json.loads(all180.read('results/all180_rational_'+tag+'.json'))
        assert q['original_46plus3_source_composite_sha256']==SOURCE
        raw=z.read('inputs/'+l['node_file'])
        assert sha(raw)==l['node_sha256']==q['source_180_node_sha256']
        row=list(struct.iter_unpack('>8d',raw))
        R=[Q.from_float(x[0]) for x in row]; W=[Q.from_float(x[1]) for x in row]
        assert len(row)==180 and all(R[i]<R[i+1] for i in range(179)) and all(w>0 for w in W)
        h=[R[i+1]-R[i] for i in range(179)]
        cells=list(map(int,c['M2_by_cell_upper_ceil']))
        assert len(cells)==179 and all(y>=0 for y in cells)
        sigma=q['source_gradient_minus_smooth_Mprime_interval_integer_msun_per_kpc']
        assert len(sigma)==180
        D=[source4pi*R[i]**2*Q.from_float(row[i][3]) for i in range(180)]
        G=[max(abs(D[i]-sigma[i][0]),abs(D[i]-sigma[i][1])) for i in range(180)]
        Gcells=[max(G[i],G[i+1])+h[i]*cells[i]/2 for i in range(179)]
        e_kernel=max((h[i]*Gcells[i] for i in range(179)))/2
        e_curv=sum((h[i]**2*cells[i] for i in range(179)),Q())/2
        wmath=[h[0]/2]+[(h[i-1]+h[i])/2 for i in range(1,179)]+[h[-1]/2]
        e_weights=sum((abs(W[i]-wmath[i])*G[i] for i in range(180)),Q())
        E=e_kernel+e_curv+e_weights
        out.append({'lens_id':l['lens_id'],'source_180_node_sha256':l['node_sha256'],
                    'all_real_smooth_candidate_K180_sampled_Mprime_vs_mathematical_continuum_abs_error_upper_integer_Msun':ceil(E),
                    'kernel_BV_contribution_integer_Msun':ceil(e_kernel),
                    'derivative_M2_variation_contribution_integer_Msun':ceil(e_curv),
                    'source_weight_vs_exact_mesh_contribution_micro_Msun':ceil(e_weights*1_000_000),
                    'physical_continuum_source_admitted':False,
                    'scientifically_useful_root_error_bound':False})
        print('BV_SRC',l['lens_id'],'E=',ceil(E),'M_sun','weight delta micro=',ceil(e_weights*1_000_000),flush=True)
    output={'schema':'HIST001D_MARCH180_SELECTED_SMOOTH_MSH_ALL_APERTURE_BV_CONSERVATIVE_BOUND_V1',
            'lenses':out,'source_46plus3_sha256':SOURCE,'C3_sha256':C3_SHA,'all180_sha256':ALL180_SHA,
            'underlying_theorem':'bounded_variation_trapezoid_error_h_over_2_times_total_variation',
            'source_specific_M2_cell_bounds_authority':'conditional_c3_external_math_candidate',
            'selected_math_smooth_mass_only':True,'valid_apertures':'all_real_A_ge_0',
            'original_source_true_physical_continuum_bound_proved':False,
            'useful_full_March_H_root_error_proved':False,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    dest=ROOT/'all_aperture_bv_producer.json';dest.write_bytes((json.dumps(output,sort_keys=True,indent=2)+'\n').encode())
    print('OUTPUT_SHA',sha(dest.read_bytes()))
    return output
if __name__=='__main__':calculate()
