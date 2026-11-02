#!/usr/bin/env python3
"""Reexecute historical 46+3 source from protected nested ZIP to capture its exact 180 source arrays.
This script never changes the original source; NONPROMOTING HISTORICAL NUMERICAL EVIDENCE.
"""
from __future__ import annotations
import io, json, hashlib, tempfile, zipfile, os, sys, struct
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(v):return b''.join(struct.pack('>d',float(x)) for x in v)

def capture(source_root):
    sys.path.insert(0,str(source_root))
    from swells_pack_v2.solv.baryons import J2141BaryonicModel
    from swells_pack_v2.solv.cosmology import FlatLCDM
    from swells_pack_v2.solv.gate_struct import A0_MPS2,compute_transition_radius_kpc,extract_gate_features_from_values
    from swells_pack_v2.solv.dmalane import build_gate_components,epsilon_from_config
    from swells_pack_v2.solv.run_setA_port_cand import _build_anchor,_candidate_gate_config,_load_tables,_projection_matrix,_trapz_weights
    from swells_pack_v2.solv.run_j2141_axisym_lens import hernquist_density,projected_disk_mass_exponential,apply_shadow_projection_mode
    from swells_pack_v2.solv.shadow_density import compute_shadow_density
    source=source_root/'swells_pack_v2'; anchor,_=_build_anchor(source)
    cfg=_candidate_gate_config(anchor,candidate_name='ra0_gated_geometry_sigmoid_reg_v2')
    data=_load_tables(source)
    radii=np.linspace(.02,120.,180,dtype=np.float64)
    w=_trapz_weights(radii)
    K=_projection_matrix(radii)
    cosmo=FlatLCDM(70.,.3)
    report=[]
    with zipfile.ZipFile(ROOT/'inputs/march_180_grid.zip') as z:
        for _,row in data.iterrows():
            lid=str(row['lens_id'])
            Mb=10**row['logM_bulge_chabrier_central'];Md=10**row['logM_disc_chabrier_central']
            bre=row['Re_bulge_arcsec']*row['scale_kpc_per_arcsec'];dr50=row['Re_disc_arcsec']*row['scale_kpc_per_arcsec']
            qb=float(row['q_bulge']);qd=float(row['q_disc'])
            model=J2141BaryonicModel(Mb,bre,Md,dr50)
            features=extract_gate_features_from_values(Mb,bre,Md,dr50,qb,qd,ra0_kpc=compute_transition_radius_kpc(model,a0_mps2=A0_MPS2))
            gbar=model.total_vbar(radii)**2/radii
            comps=build_gate_components(cfg,features=features,anchor=anchor)
            eps=epsilon_from_config(radii,gbar,cfg,features=features,anchor=anchor)
            rho_s=compute_shadow_density(radii,gbar,gbar/eps,epsilon=eps,method=comps.get('shadow_density_method','mass_difference_gradient'))
            rho_b=hernquist_density(radii,Mb,bre/1.8153)
            B=K.dot(rho_b)
            D=np.array([projected_disk_mass_exponential(R,Md,dr50/1.67835,qd,ntheta=120) for R in radii],dtype=np.float64)
            S0=K.dot(rho_s)
            mode={'shadow_projection':'baryon_structure_circularized','disk_axis_ratio_q':qd,'bulge_axis_ratio_q':qb}
            S=apply_shadow_projection_mode(radii,S0,mode,B,D,dict(mode))
            sigma=cosmo.sigma_crit_msun_per_kpc2(float(row['z_deflector']),float(row['z_source']))
            H=B+D+S-np.pi*radii**2*sigma
            old=z.read('sampled_binary64/'+lid.replace('+','p')+'.R_H_be64.bin')
            oldH=[pair[1] for pair in struct.iter_unpack('>dd',old)]
            assert len(oldH)==len(radii) and blob(H)==blob(oldH), 'original solver sampled residual mismatch '+lid
            assert np.all(np.isfinite(rho_s)) and np.all(rho_s>=0) and np.all(rho_b>0)
            assert np.all(np.isfinite(S0))
            path=ROOT/'inputs'/('March180_source_nodes_'+lid.replace('+','p')+'.be64')
            with path.open('wb') as f:
                for data_row in zip(radii,w,rho_b,rho_s,B,S0,D,S,strict=True):
                    f.write(struct.pack('>8d',*map(float,data_row)))
            report.append({'lens_id':lid,'node_file':path.name,'node_sha256':sha(path.read_bytes()),'number_of_nodes':180,'min_shadow_density':float(min(rho_s)),'max_shadow_density':float(max(rho_s)),'bulge_density_sha256':sha(blob(rho_b)),'shadow_density_sha256':sha(blob(rho_s)),'shadow_180_grid_source_is_nonnegative':True,'identical_original_H_180_nodes':True,'source_s0_non_decreasing_num':bool(np.all(np.diff(S0)>=0)),'source_s0_min_delta':float(min(np.diff(S0))),'source_s0_max_delta':float(max(np.diff(S0))),'original_pi4_float_hex':float(4*np.pi).hex(),'original_sigma_hex':float(sigma).hex(),'radial_support':[radii[0].hex(),radii[-1].hex()]})
            print('SOURCE180_CAPTURE_PASS',lid,'rho_sha',sha(blob(rho_s)),'s0 node jump_max',max(np.diff(S0)),flush=True)
    return report

def main():
    lock=json.loads((ROOT/'inputs/original_46plus3_lock.json').read_bytes())
    src=(ROOT/'inputs/original_source_46_frozen.zip').read_bytes()
    assert sha(src)=='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
    assert lock['original_46plus3_composite_sha256']=='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
    with zipfile.ZipFile(io.BytesIO(src)) as sourcez:
        assert sourcez.testzip() is None
        assert len(lock['source_filenames_sha256'])==46
        for path,pin in lock['source_filenames_sha256'].items():
            assert sha(sourcez.read('swells_pack_v2/'+path))==pin
        assert len(lock['archived_negative_controls_sha256'])==3
        for path,pin in lock['archived_negative_controls_sha256'].items():
            assert sha((ROOT/'inputs/negative_controls'/path).read_bytes())==pin
        with tempfile.TemporaryDirectory(prefix='march180-source-') as tmp:
            sourcez.extractall(tmp)
            report=capture(Path(tmp))
    doc={'schema':'HIST001D_MARCH_180_FROZEN_SOURCE_NODAL_RHO_AND_STENCIL_V1','source_lock_sha256':lock['original_46plus3_composite_sha256'],'model':'HISTORICAL_ESET3_4_MARCH_REG_V2_180x120','lenses':report,'claims':{'source_shadow_grid_locked':True,'no_new_11520_density':True,'continuum_source_equivalence_claimed':False,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}}
    raw=(json.dumps(doc,sort_keys=True,separators=(',',':'))+'\n').encode()
    (ROOT/'results/source180_capture.json').write_bytes(raw)
    print('CAPTURE_LEDGER',sha(raw))
if __name__=='__main__': main()
