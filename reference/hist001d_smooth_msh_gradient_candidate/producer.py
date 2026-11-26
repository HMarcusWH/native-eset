#!/usr/bin/env python3
"""Frozen March source -> mathematically analytic mass-gradient sensitivity.

Numerical DIAGNOSTIC, not rigorous Bessel interval computation, physical
matter density or original historical off-grid solver root theorem.
"""
from __future__ import annotations
import csv, hashlib, io, json, math, struct, sys, tempfile, zipfile
from pathlib import Path
import numpy as np
from smooth_math import source_mass_and_analytic_gradient

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT/'inputs/frozen_source_parent.zip'
PARENT_SHA = '82a840767c61e1b6a838bbf3cf105d1b4ff5b854a883dfacd219e8e2b1bb67bf'
ORIGINAL_SHA = '283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
SOURCE_LOCK = 'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'

def h(b): return hashlib.sha256(b).hexdigest()
def output(doc, filename):
    p=ROOT/'results'/filename
    p.parent.mkdir(exist_ok=True,parents=True)
    p.write_bytes((json.dumps(doc,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode())
    return h(p.read_bytes())

def original_source_context():
    # Caller opens archive; all nested source-file SHA pins are independent.
    root=zipfile.ZipFile(PARENT)
    if h(PARENT.read_bytes())!=PARENT_SHA or root.testzip() is not None: raise ValueError('original parent identity/CRC')
    z1=zipfile.ZipFile(io.BytesIO(root.read('inputs/original_march_D120_q_parent.zip')))
    z2=zipfile.ZipFile(io.BytesIO(z1.read('inputs/original_march180_parent_v1r1.zip')))
    source_bytes=z2.read('inputs/original_source_46_frozen.zip')
    if h(source_bytes)!=ORIGINAL_SHA: raise ValueError('46-file frozen source ZIP changed')
    source=zipfile.ZipFile(io.BytesIO(source_bytes))
    lock=json.loads(z2.read('inputs/original_46plus3_lock.json'))
    if lock.get('original_46plus3_composite_sha256')!=SOURCE_LOCK: raise ValueError('source lock modified')
    if len(lock['source_filenames_sha256'])!=46 or len(lock['archived_negative_controls_sha256'])!=3:
        raise ValueError('46+3 inventory changed')
    for path,sha in lock['source_filenames_sha256'].items():
        if h(source.read('swells_pack_v2/'+path))!=sha: raise ValueError('source file changed: '+path)
    for path,sha in lock['archived_negative_controls_sha256'].items():
        if h(z2.read('inputs/negative_controls/'+path))!=sha: raise ValueError('negative control changed: '+path)
    return root,z1,z2,source,source_bytes

def compute():
    root,z1,z2,src,source_bytes=original_source_context()
    archive=json.loads(z2.read('results/source180_capture.json'))
    if archive['source_lock_sha256']!=SOURCE_LOCK or len(archive['lenses'])!=6:
        raise ValueError('original lens inventory changed')
    # Reexecute actual ORIGINAL source functions in a disposable source copy.
    with tempfile.TemporaryDirectory(prefix='hist001d-analytic-source-') as temp:
        base=Path(temp)
        for item in src.infolist():
            if item.is_dir(): continue
            dest=base/item.filename
            if not dest.resolve().is_relative_to(base.resolve()): raise ValueError('unsafe source path')
            dest.parent.mkdir(exist_ok=True,parents=True)
            dest.write_bytes(src.read(item))
        sys.dont_write_bytecode=True
        sys.path.insert(0,str(base))
        from swells_pack_v2.solv.run_setA_port_cand import _build_anchor,_load_tables,_candidate_gate_config,_projection_matrix
        from swells_pack_v2.solv.baryons import J2141BaryonicModel
        from swells_pack_v2.solv.gate_struct import A0_MPS2,compute_transition_radius_kpc,extract_gate_features_from_values
        from swells_pack_v2.solv.dmalane import build_gate_components,epsilon_from_config
        from swells_pack_v2.solv.shadow_density import compute_shadow_density
        from swells_pack_v2.solv.run_j2141_axisym_lens import apply_shadow_projection_mode
        from swells_pack_v2.solv.constants import G_KPC_KMS2_MSUN
        pack=base/'swells_pack_v2';anchor,_=_build_anchor(pack)
        cfg=_candidate_gate_config(anchor,'ra0_gated_geometry_sigmoid_reg_v2')
        rows={str(z['lens_id']):z for _,z in _load_tables(pack).iterrows()}
        original_H_zip=zipfile.ZipFile(io.BytesIO(z2.read('inputs/march_180_grid.zip')))
        output_rows=[]
        for L in archive['lenses']:
            lid=L['lens_id'];tag=lid.replace('+','p')
            if lid not in rows: raise ValueError('lens order mismatch')
            arr_bytes=z2.read('inputs/'+L['node_file'])
            if h(arr_bytes)!=L['node_sha256']: raise ValueError('original nodal source identity changed')
            nod=np.array(list(struct.iter_unpack('>8d',arr_bytes)),dtype='float64')
            R=np.ascontiguousarray(nod[:,0]);w=nod[:,1];rho_original=nod[:,3]
            B,S0,D,S=nod[:,4],nod[:,5],nod[:,6],nod[:,7]
            if len(R)!=180 or not np.all(np.diff(R)>0):raise ValueError('original 180 radials changed')
            oldH=np.array([y for x,y in struct.iter_unpack('>dd',original_H_zip.read(f'sampled_binary64/{tag}.R_H_be64.bin'))])
            sigma=float.fromhex(L['original_sigma_hex'])
            if (B+D+S-np.pi*R**2*sigma).tobytes()!=oldH.tobytes():
                raise ValueError('original source H knot identity not reproduced')
            row=rows[lid]
            Mb=float(10**row['logM_bulge_chabrier_central']);Md=float(10**row['logM_disc_chabrier_central'])
            bre=float(row['Re_bulge_arcsec']*row['scale_kpc_per_arcsec'])
            dr50=float(row['Re_disc_arcsec']*row['scale_kpc_per_arcsec'])
            qb=float(row['q_bulge']);qd=float(row['q_disc'])
            bary=J2141BaryonicModel(Mb,bre,Md,dr50)
            feat=extract_gate_features_from_values(Mb,bre,Md,dr50,qb,qd,
                     ra0_kpc=compute_transition_radius_kpc(bary,a0_mps2=A0_MPS2))
            comps=build_gate_components(cfg,features=feat,anchor=anchor)
            n=float(comps['n']);r0=float(comps['r0_kpc']);delta=float(comps['delta_epsilon'])
            if comps['shadow_density_method']!='mass_difference_gradient':
                raise ValueError('unapproved shadow model')
            vbar=bary.total_vbar(R);gbar=vbar**2/R
            eps=epsilon_from_config(R,gbar,cfg,features=feat,anchor=anchor)
            gradient_source=compute_shadow_density(R,gbar,gbar/eps,epsilon=eps,method='mass_difference_gradient')
            err=np.abs(gradient_source-rho_original)/np.maximum(rho_original,1.)
            # SciPy/NumPy vector routines can differ 1-2 ULP between vector layouts.
            if np.max(err)>2e-14:raise ValueError('original gradient replay beyond roundoff tolerance')
            Msm, Mprime=source_mass_and_analytic_gradient(R,Mb=Mb,Md=Md,a=float(bary.bulge_scale_kpc),
                 Rd=float(bary.disk_scale_kpc),delta=delta,r0=r0,n=n)
            C4pi=float(4*np.pi)
            rho_smooth=np.clip(Mprime/(C4pi*R*R),0,None)
            if not (np.all(rho_smooth>0) and np.all(np.isfinite(rho_smooth))):
                raise ValueError('analytic candidate positive at frozen nodes required')
            # Preserve the entire original radial quadrature and original B,D,q.
            K=_projection_matrix(R)
            S0_new=K.dot(rho_smooth)
            lens_cfg={'shadow_projection':'baryon_structure_circularized','disk_axis_ratio_q':qd,
                      'bulge_axis_ratio_q':qb}
            S_new=apply_shadow_projection_mode(R,S0_new,lens_cfg,B,D,lens_cfg)
            H_new=B+D+S_new-np.pi*R**2*sigma
            oldedges=np.flatnonzero(np.diff(np.sign(oldH)))
            newedges=np.flatnonzero(np.diff(np.sign(H_new)))
            if len(oldedges)!=1:raise ValueError('original historical sign chart changed')
            def first_root(hh,edge):
                i=int(edge)
                return float(R[i]-hh[i]*(R[i+1]-R[i])/(hh[i+1]-hh[i]))
            oldroot=first_root(oldH,oldedges[0])
            newroots=[first_root(H_new,j) for j in newedges]
            samples=[0,1,2,max(0,int(oldedges[0])),min(179,int(oldedges[0])+1),90,179]
            sampled=[{'index':j,'radius_kpc':float(R[j]),
                      'rho_source':float(rho_original[j]),'rho_analytic_derivative':float(rho_smooth[j])}
                     for j in sorted(set(samples))]
            numeric_profile=b''.join(struct.pack('>5d',*values) for values in
                     zip(R,Msm,Mprime,rho_smooth,H_new,strict=True))
            filename=f'analytic_gradient_{tag}.be64'
            (ROOT/'inputs'/filename).write_bytes(numeric_profile)
            output_rows.append({
                'lens_id':lid, 'original_180_nodal_sha256':h(arr_bytes),
                'analytic_profile_file':'inputs/'+filename,
                'analytic_profile_sha256':h(numeric_profile),
                'source_scalar_binary64_hex':{'Mb':Mb.hex(),'Md':Md.hex(),'a':float(bary.bulge_scale_kpc).hex(),
                    'Rd':float(bary.disk_scale_kpc).hex(),'delta':delta.hex(),'r0':r0.hex(),'n':n.hex(),
                    'qb':qb.hex(),'qd':qd.hex(),'sigma_crit':sigma.hex(),'C4pi':C4pi.hex()},
                'epsilon_branch_no_node_clip':bool(np.all(eps>0.05)&np.all(eps<1.0)),
                'smooth_density_positive_AT_SOURCE_NODES_ONLY':True,
                'source_gradient_relative_replay_difference_max':float(np.max(err)),
                'first_node_original_density':float(rho_original[0]),
                'first_node_analytic_derivative_density':float(rho_smooth[0]),
                'first_node_source_over_analytic_ratio':float(rho_original[0]/rho_smooth[0]),
                'median_absolute_relative_density_change_at_180_nodes':float(np.median(abs(rho_original-rho_smooth)/rho_smooth)),
                'old_original_sampled_root_kpc':oldroot,
                'new_replacement_density_sampled_root_kpc':newroots,
                'new_sampled_sign_change_count':len(newedges),
                'max_abs_original_H_vs_diagnostic_H_node_msun':float(np.max(abs(H_new-oldH))),
                'max_abs_original_vs_diagnostic_spherical_shadow_node_msun':float(np.max(abs(S0_new-S0))),
                'selected_node_examples':sampled
            })
        result={'schema':'HIST001D_SOURCE_ANALYTIC_MSH_DERIVATIVE_V1_NONPROMOTING_DIAGNOSTIC',
                'source_lock_sha256':SOURCE_LOCK,'parent_source_archive_sha256':PARENT_SHA,
                'original_math_model':'HISTORICAL_ESET3_4_MARCH_REGV2_180x120',
                'distinct_new_diagnostic':'ANALYTICALLY_DIFFERENTIATED_ACCEL_EQUIVALENT_SHADOW_MASS_AT_ORIGINAL_RADII',
                'lenses':output_rows,'proved_uniform_gradient_error':False,
                'certified_M2_M3_derivative_suprema':False,
                'original_numerical_continuum_root_uniqueness':False,
                'physical_Weyl':False,'empirical_validation':'NOT_ESTABLISHED',
                'source_11520_proxy_substituted':False}
        result_sha=output(result,'producer_analytic_source_gradient.json')
        print('SOURCE_ANALYTIC_GRADIENT_DIAGNOSTIC_PASS',len(output_rows),result_sha,flush=True)
        for L in output_rows:
            print('FIRST_NODE',L['lens_id'],f"ratio={L['first_node_source_over_analytic_ratio']:.9g}",
                  'old_root',f"{L['old_original_sampled_root_kpc']:.9f}",
                  'new_first_sample_root',L['new_replacement_density_sampled_root_kpc'],flush=True)
        sys.path.remove(str(base))
        return result_sha

if __name__=='__main__':compute()
