#!/usr/bin/env python3
"""Independent rational e^(+y) series recheck of D120 seam source-bound receipt.

Data authentication is inherited from the separately source-locked historical
float-bridge reader. This tests a *different* exponential inequality from the
producer; it is not an independent physical provider or special-function engine.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import struct
import sys
import zipfile
from fractions import Fraction as F
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'reference'/'hist001d_original_float_bridge_candidate'))
from float_bridge import read_locked  # noqa: E402
from seam_math import ff,seam_interval,exp_minus_positive,integer_micro_interval,floor,ceil  # noqa: E402

LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')
SCHEMA='HIST001D_ORIGINAL_D120_PERIODIC_SEAM_SOURCE_LOCKED_DIAGNOSTIC_V1'
SOURCE='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
SAT='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
H='02c93bed1c2d5338972c192013270921264d00320b41d8d17ad44769b47dd7d6'


def sha(b):return hashlib.sha256(b).hexdigest()

def check_structure(rec):
    if not isinstance(rec,dict) or rec.get('schema')!=SCHEMA:raise ValueError('wrong seam schema')
    if rec.get('source_original_46plus3_sha256')!=SOURCE:raise ValueError('wrong source')
    if rec.get('input_saturation_sha256')!=SAT or rec.get('input_finite_H_sha256')!=H:raise ValueError('wrong input parent')
    if rec.get('source_float_parent_sha256')!='313b62e2c0f790684bd6ed6ff22431c2cce1f398d79fcc590971f8814ae4706e':raise ValueError('wrong source float lineage')
    for f in ('frozen_D120_nodes_binary64_replayed','frozen_circularized_shadow_nodes_binary64_replayed','frozen_H_nodes_binary64_replayed'):
        if rec.get(f)!=1080:raise ValueError('incorrect original source node count '+f)
    if rec.get('periodic_seam_term_analytic_positive_for_every_R_gt_zero') is not True:raise ValueError('monotonic positive source')
    if 'd seam/dR' not in rec.get('periodic_seam_monotonicity_identity',''):raise ValueError('missing derivative identity')
    if rec.get('all_six_sampled_roots_with_periodic_seam_are_counterfactual_diagnostics_only') is not True:raise ValueError('counterfactual scope')
    for key in ('full_azimuth_integral_error_certified','historical_original_source_stencil_modified','original_march_offgrid_physical_H_bound','actual_original_March_SciPy_upstream_accuracy_proved','physical_provider_admitted'):
        if rec.get(key) is not False:raise ValueError('forbidden promotion '+key)
    if rec.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('empirical promotion')
    ls=rec.get('lenses')
    if not isinstance(ls,list) or len(ls)!=6 or [x.get('lens_id') for x in ls]!=list(LENSES):raise ValueError('missing/duplicated/misaligned lenses')
    for x in ls:
        for k in ('source_D120_stored_binary64_exact_count','source_circularized_shadow_stored_binary64_exact_count','source_H_stored_binary64_exact_count'):
            if x.get(k)!=180:raise ValueError('node mismatch '+x['lens_id']+' '+k)
        if x.get('source_kpc_per_arcsec_output_exact') is not True:raise ValueError('strict output mismatch')
        if x.get('stored_shadow_density_strictly_positive_count')!=180 or x.get('stored_density_clip_floor_inactive_at_all_source_nodes') is not True:raise ValueError('false zero-clip status')
        if x.get('new_disk_node_correction_positive') is not True:raise ValueError('counterfactual source positive flag')
        if x.get('seam_closure_not_original_source') is not True:raise ValueError('old-source conflation')
        if x.get('counterfactual_output_not_certified_root_shift') is not True:raise ValueError('false root certificate')
        if x.get('counterfactual_new_crossing_count')!=1:raise ValueError('counterfactual numerical crossing')
        if not 0<=x.get('original_crossing_cell_index',-1)<179:raise ValueError('R-cell index')
        bs=x.get('rigorous_exact_real_periodic_seam_at_crossing_endpoints_integer_micro_Msun')
        ps=x.get('source_periodic_seam_percent_of_D_source_at_crossing_endpoints_integer_micro_percent')
        if not (isinstance(bs,list) and isinstance(ps,list) and len(bs)==len(ps)==2):raise ValueError('seam bound count')
        for a,b in zip(bs,ps):
            if not (isinstance(a,list) and len(a)==2 and all(type(q) is int for q in a) and 0<a[0]<=a[1]):raise ValueError('seam sign')
            if not (isinstance(b,list) and len(b)==2 and all(type(q) is int for q in b) and 0<b[0]<=b[1]):raise ValueError('seam percent sign')
        if not isinstance(x.get('counterfactual_root_shift_kpc_float'),(int,float)) or x['counterfactual_root_shift_kpc_float']<=0:raise ValueError('root shift flagged')
        if x.get('counterfactual_new_crossing_index') not in range(179):raise ValueError('new crossing index')
    return True


def verify_source_math(rec, saturation, finite_h):
    check_structure(rec)
    captures,_,rows,meta,pairs,_,_,_=read_locked(Path(saturation),Path(finite_h))
    # Independent access to the original D120 source-angle bytes.
    with zipfile.ZipFile(saturation) as z:orig=z.read('original_parent.zip')
    with zipfile.ZipFile(io.BytesIO(orig)) as z:froz=z.read('inputs/frozen_source_parent.zip')
    with zipfile.ZipFile(io.BytesIO(froz)) as z:d120=z.read('inputs/original_march_D120_q_parent.zip')
    with zipfile.ZipFile(io.BytesIO(d120)) as z:
        angular_source=json.loads(z.read('results/source120_capture.json'))['lenses']
        by_lens={m['lens_id']:(m,z.read(m['angular_binary64_path'])) for m in angular_source}
    for a,raw_nodes,lens in zip(captures,rows,rec['lenses']):
        name=a['lens_id']
        angles_metadata,raw=by_lens[name]
        angle=list(struct.iter_unpack('>ddd',raw))
        if len(angle)!=120 or sha(raw)!=angles_metadata['angular_node_sha256'] or lens['source_120_angle_sha256']!=sha(raw):raise ValueError('source angle identity')
        if lens['original_180_node_sha256']!=a['node_sha256']:raise ValueError('source 180 identity')
        k=lens['original_crossing_cell_index']
        h=ff(angle[1][0]-angle[0][0])
        s0=ff(float.fromhex(angles_metadata['sigma0_hex']))
        rd=ff(float.fromhex(angles_metadata['Rd_hex']))
        alpha0=ff(angle[0][2]);alphalast=ff(angle[-1][2])
        if lens['source_angular_periodic_seam_h_hex']!=float(h).hex():raise ValueError('angular seam geometry')
        if lens['a_first_hex']!=float(alpha0).hex() or lens['a_last_hex']!=float(alphalast).hex():raise ValueError('angular endpoint geometry')
        if lens['theta_last_hex']!=angle[-1][0].hex():raise ValueError('theta last')
        if lens['sigma0_hex']!=float(s0).hex() or lens['Rd_hex']!=float(rd).hex():raise ValueError('disk constant')
        Rband=[ff(raw_nodes[k][0]),ff(raw_nodes[k+1][0])]
        if lens['original_crossing_cell_R_hex']!=[float(r).hex() for r in Rband]:raise ValueError('R-band source identity')
        for i,R in enumerate(Rband):
            iv=seam_interval(R,s0,rd,h,alpha0,alphalast,exp_minus_positive)
            stored=lens['rigorous_exact_real_periodic_seam_at_crossing_endpoints_integer_micro_Msun'][i]
            alt=integer_micro_interval(iv)
            if stored[0]>alt[0] or stored[1]<alt[1]:
                raise ValueError('independent exponential bound not enclosed '+name)
            d=ff(raw_nodes[k+i][6])
            pct=[floor(100*10**6*iv[0]/d),ceil(100*10**6*iv[1]/d)]
            saved_pct=lens['source_periodic_seam_percent_of_D_source_at_crossing_endpoints_integer_micro_percent'][i]
            if saved_pct[0]>pct[0] or saved_pct[1]<pct[1]:raise ValueError('independent percent enclosure '+name)
        if lens['source_D120_stored_Msun_at_crossing_endpoints_hex']!=[raw_nodes[k][6].hex(),raw_nodes[k+1][6].hex()]:raise ValueError('disk node source')
        if any(row[3]<=0 or row[0]**2<=1e-12 for row in raw_nodes):raise ValueError('stored rho or radial floor')
        # Independent numerical assembly verifies the exact recorded counterfactual,
        # rather than trusting a positive root-shift flag.
        r=np.array([row[0] for row in raw_nodes]);B=np.array([row[4] for row in raw_nodes]);D=np.array([row[6] for row in raw_nodes]);S0=np.array([row[5] for row in raw_nodes]);
        alpha=np.array([a[2] for a in angle]);Rd=float(rd);sig0=float(s0);step=float(h)
        x=np.multiply.outer(r,alpha)/Rd
        fun=Rd**2/(alpha[None,:]**2)*(1-np.exp(-x)*(1+x))
        seam_array=sig0*step*(fun[:,0]+fun[:,-1])/2
        alternative_D=D+seam_array
        qb=float.fromhex(angles_metadata['qb_hex']);qd=float.fromhex(angles_metadata['qd_hex'])
        qeff=np.clip((qb*B+qd*alternative_D)/np.clip(B+alternative_D,1e-30,None),1e-3,1.0)
        alternative_S=np.interp(r/np.sqrt(qeff),r,S0,left=S0[0],right=S0[-1])
        sigma=float.fromhex(a['original_sigma_hex'])
        alt_H=(B+alternative_D+alternative_S)-np.pi*r**2*sigma
        indices=np.flatnonzero((alt_H[:-1]>0)&(alt_H[1:]<0))
        if len(indices)!=1 or int(indices[0])!=lens['counterfactual_new_crossing_index']:raise ValueError('new crossing count/index')
        j=int(indices[0]);root_new=float(r[j]-alt_H[j]*(r[j+1]-r[j])/(alt_H[j+1]-alt_H[j]))
        if root_new.hex()!=lens['counterfactual_periodic_seam_sampled_first_root_hex']:raise ValueError('counterfactual source root mismatch')
        source_root=float(meta[LENSES.index(name)]['original_first_sign_change_root_kpc'])
        if root_new-source_root!=lens['counterfactual_root_shift_kpc_float']:raise ValueError('counterfactual root displacement mismatch')
        if lens['original_sampled_first_root_hex']!=str(meta[LENSES.index(name)]['original_first_sign_change_root_kpc'].__float__().hex()):raise ValueError('original sampled root mismatch')
        print('INDEPENDENT_POSITIVE_EXP_CERT',name,flush=True)
    return True

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--saturation',type=Path,required=True)
    p.add_argument('--finite-h',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True)
    a=p.parse_args()
    verify_source_math(json.loads(a.receipt.read_text()),a.saturation,a.finite_h)
    print('INDEPENDENT_SEAM_OK')
