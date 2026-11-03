#!/usr/bin/env python3
"""Original March D120 no-closure seam audit, nested SHA-locked protected data.

The original D120 119-segment float output, q circularization and original
March sampled H/root are replayed exactly from archived data. A separate
fixed-sample periodic-closure counterfactual is computed; no refit or physical
claim is authorized. Source-free pytest never loads the protected parents.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import struct
import sys
import zipfile
from pathlib import Path
from fractions import Fraction as F
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'reference'/'hist001d_original_float_bridge_candidate'))
from float_bridge import read_locked, float_sample_H  # noqa: E402
from seam_math import ff,seam_interval,exp_minus_alternating,integer_micro_interval,monotonicity_contract,floor,ceil  # noqa: E402

SAT_SHA='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
H_SHA='02c93bed1c2d5338972c192013270921264d00320b41d8d17ad44769b47dd7d6'
LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')

def sha(b):return hashlib.sha256(b).hexdigest()

def verify_manifest(zipfile_obj):
    meta=json.loads(zipfile_obj.read('MANIFEST_SHA256.json'))
    for f,expected in meta['files'].items():
        if sha(zipfile_obj.read(f))!=expected:raise ValueError('parent manifest '+f)

def d120_archive(sat_path):
    if sha(sat_path.read_bytes())!=SAT_SHA:raise ValueError('wrong saturation parent')
    with zipfile.ZipFile(sat_path) as z:
        verify_manifest(z)
        original=z.read('original_parent.zip')
    with zipfile.ZipFile(io.BytesIO(original)) as z:
        verify_manifest(z)
        frozen=z.read('inputs/frozen_source_parent.zip')
    with zipfile.ZipFile(io.BytesIO(frozen)) as z:
        verify_manifest(z)
        d120=z.read('inputs/original_march_D120_q_parent.zip')
    return d120

def num_crossing(r,H):
    k=np.where(np.diff(np.sign(H)))[0]
    if len(k)!=1 or not (H[k[0]]>0 and H[k[0]+1]<0):
        raise ValueError('no unique first sign change in sampled original model')
    j=int(k[0])
    x0,x1=float(r[j]),float(r[j+1]);y0,y1=float(H[j]),float(H[j+1])
    return j,float(x0-y0*(x1-x0)/(y1-y0))

def produce(sat_path,h_path,out_path):
    sat_path=Path(sat_path);h_path=Path(h_path);out_path=Path(out_path)
    if sha(h_path.read_bytes())!=H_SHA:raise ValueError('wrong finite-H parent')
    cap,qmeta,arrays,metas,samples,finite,strict_rows,scales=read_locked(sat_path,h_path)
    d120=d120_archive(sat_path)
    with zipfile.ZipFile(io.BytesIO(d120)) as z:
        verify_manifest(z)
        anglemeta=json.loads(z.read('results/source120_capture.json'))['lenses']
        if tuple(v['lens_id'] for v in anglemeta)!=LENSES:raise ValueError('source angle lens order')
        angles=[]
        for a in anglemeta:
            raw=z.read(a['angular_binary64_path'])
            if sha(raw)!=a['angular_node_sha256'] or len(raw)!=120*24:
                raise ValueError('angular source bytes invalid')
            angles.append(np.array(list(struct.iter_unpack('>ddd',raw)),dtype=np.float64))
    rec=[]
    for i,(c,q,rows,am,pairs,ang) in enumerate(zip(cap,qmeta,arrays,anglemeta,samples,angles)):
        lens=c['lens_id'];rr=np.asarray(rows,dtype=np.float64)
        R=rr[:,0];B=rr[:,4];S0=rr[:,5];D=rr[:,6];S=rr[:,7]
        theta,weights,alpha=ang.T
        if len(R)!=180 or len(theta)!=120 or not np.all(np.diff(theta)>0):raise ValueError('source dimensions')
        if not (theta[0]==0 and alpha[0]==1 and min(alpha)>0 and theta[-1]<2*np.pi):raise ValueError('source angles')
        # Frozen original mathematical 119-segment integration rule,
        # evaluated using the SAME NumPy operation order as the source.
        Rd=float.fromhex(am['Rd_hex']);sigma0=float.fromhex(am['sigma0_hex'])
        x=alpha[None,:]*R[:,None]/Rd
        inner=Rd**2/alpha[None,:]**2*(1-np.exp(-x)*(1+x))
        D_replayed=sigma0*np.trapezoid(inner,theta,axis=1)
        if not np.array_equal(D_replayed.view('uint64'),D.view('uint64')):
            raise ValueError('source D120 bitwise replay failed '+lens)
        qb=float.fromhex(am['qb_hex']);qd=float.fromhex(am['qd_hex'])
        denom=np.clip(B+D,1e-30,None)
        qeff=np.clip((qb*B+qd*D)/denom,1e-3,1.0)
        S_replayed=np.interp(R/np.sqrt(qeff),R,S0,left=S0[0],right=S0[-1])
        if not np.array_equal(S_replayed.view('uint64'),S.view('uint64')):
            raise ValueError('source circularized S replay failed '+lens)
        pi=np.pi;sigma=float.fromhex(c['original_sigma_hex'])
        H=np.asarray([float(float_sample_H(ff(b),ff(d),ff(s),ff(r),ff(pi),ff(sigma)))
                      for b,d,s,r in zip(B,D,S,R)])
        if not np.array_equal(H.view('uint64'),np.array([y for _,y in pairs]).view('uint64')):
            raise ValueError('source H original input check failed '+lens)
        k,root=num_crossing(R,H)
        expected=metas[i]['original_first_sign_change_root_kpc']
        if F.from_float(root)!=F.from_float(float(expected)):
            raise ValueError('source first crossing root changed '+lens)
        # Intentionally new periodic seam correction using exactly frozen
        # angular endpoints and first source angular step, NOT full integral.
        h=float(theta[1]-theta[0])
        seam=sigma0*h*(inner[:,0]+inner[:,-1])/2
        if not np.all(seam>0):raise ValueError('nonpositive seam for source R>0')
        D_120closed=D+seam
        q_new=np.clip((qb*B+qd*D_120closed)/np.clip(B+D_120closed,1e-30,None),1e-3,1.0)
        S_new=np.interp(R/np.sqrt(q_new),R,S0,left=S0[0],right=S0[-1])
        H_new=(B+D_120closed+S_new)-np.pi*R**2*sigma
        k_new,root_new=num_crossing(R,H_new)
        # Analytic rigorous exact fractions at the two crossing-cell endpoints.
        seam_bounds=[];pct_bounds=[]
        for j in (k,k+1):
            interval=seam_interval(ff(R[j]),ff(sigma0),ff(Rd),ff(h),ff(alpha[0]),ff(alpha[-1]),exp_minus_alternating)
            if not interval[0]>0:raise ValueError('seam interval lower <=0')
            seam_bounds.append(integer_micro_interval(interval))
            qd_source=ff(D[j])
            pct_bounds.append([floor(interval[0]*100*10**6/qd_source),ceil(interval[1]*100*10**6/qd_source)])
        if root_new<=root:raise ValueError('unexpected root shift sign; preserve rather than promote')
        if np.count_nonzero(rr[:,3]>0)!=180:raise ValueError('stored shadow density clipping active')
        n_original_arc=float(strict_rows[lens]['predicted_einstein_radius_arcsec'])
        scale=float(scales[lens]['scale_kpc_per_arcsec'])
        if root/scale!=n_original_arc:raise ValueError('strict output arcseconds')
        rec.append({
            'lens_id':lens,'original_180_node_sha256':c['node_sha256'],
            'source_120_angle_sha256':am['angular_node_sha256'],
            'source_D120_stored_binary64_exact_count':int(np.count_nonzero(D_replayed.view('uint64')==D.view('uint64'))),
            'source_circularized_shadow_stored_binary64_exact_count':int(np.count_nonzero(S_replayed.view('uint64')==S.view('uint64'))),
            'source_H_stored_binary64_exact_count':int(np.count_nonzero(H.view('uint64')==np.array([y for _,y in pairs]).view('uint64'))),
            'stored_shadow_density_strictly_positive_count':int(np.count_nonzero(rr[:,3]>0)),
            'stored_density_clip_floor_inactive_at_all_source_nodes':bool(np.all(rr[:,3]>0) and np.all(R*R>1e-12)),
            'source_kpc_per_arcsec_output_exact':True,
            'original_crossing_cell_index':k,'original_crossing_cell_R_hex':[R[k].hex(),R[k+1].hex()],
            'source_angular_periodic_seam_h_hex':h.hex(),
            'theta_first_hex':theta[0].hex(),'theta_last_hex':theta[-1].hex(),
            'a_first_hex':alpha[0].hex(),'a_last_hex':alpha[-1].hex(),
            'sigma0_hex':sigma0.hex(),'Rd_hex':Rd.hex(),
            'rigorous_exact_real_periodic_seam_at_crossing_endpoints_integer_micro_Msun':seam_bounds,
            'source_D120_stored_Msun_at_crossing_endpoints_hex':[D[k].hex(),D[k+1].hex()],
            'source_periodic_seam_percent_of_D_source_at_crossing_endpoints_integer_micro_percent':pct_bounds,
            'original_sampled_first_root_hex':root.hex(),
            'counterfactual_periodic_seam_sampled_first_root_hex':root_new.hex(),
            'counterfactual_root_shift_kpc_float':root_new-root,
            'counterfactual_new_crossing_index':k_new,
            'counterfactual_new_crossing_count':1,
            'new_disk_node_correction_positive':True,
            'seam_closure_not_original_source':True,
            'counterfactual_output_not_certified_root_shift':True,
        })
        print('SOURCE_D120',lens,'D,S,H 180/180','root',root,'shift',root_new-root,
              'seam_Msun_left',seam_bounds[0],flush=True)
    obj={
        'schema':'HIST001D_ORIGINAL_D120_PERIODIC_SEAM_SOURCE_LOCKED_DIAGNOSTIC_V1',
        'source_original_46plus3_sha256':'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a',
        'source_float_parent_sha256':'313b62e2c0f790684bd6ed6ff22431c2cce1f398d79fcc590971f8814ae4706e',
        'input_saturation_sha256':SAT_SHA,'input_finite_H_sha256':H_SHA,
        'frozen_D120_nodes_binary64_replayed':1080,
        'frozen_circularized_shadow_nodes_binary64_replayed':1080,
        'frozen_H_nodes_binary64_replayed':1080,
        'periodic_seam_term_analytic_positive_for_every_R_gt_zero':True,
        'periodic_seam_monotonicity_identity':monotonicity_contract(),
        'all_six_sampled_roots_with_periodic_seam_are_counterfactual_diagnostics_only':True,
        'full_azimuth_integral_error_certified':False,
        'historical_original_source_stencil_modified':False,
        'original_march_offgrid_physical_H_bound':False,
        'actual_original_March_SciPy_upstream_accuracy_proved':False,
        'physical_provider_admitted':False,
        'empirical_validation':'NOT_ESTABLISHED',
        'lenses':rec
    }
    out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_bytes((json.dumps(obj,indent=2,sort_keys=True)+'\n').encode())
    print('RECEIPT_SHA256',sha(out_path.read_bytes()))
    return obj

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--saturation',required=True,type=Path)
    p.add_argument('--finite-h',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    args=p.parse_args()
    produce(args.saturation,args.finite_h,args.out)
