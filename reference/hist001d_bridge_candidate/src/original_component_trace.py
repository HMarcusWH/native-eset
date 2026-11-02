#!/usr/bin/env python3
"""Diagnostics ONLY; rebuild original unchanged March output components, record exact float64 arrays.
No source changes, refit, continuum/physical inference, or new numerical-error theorem.
"""
from __future__ import annotations
import sys,os,json,hashlib,struct
from pathlib import Path
from fractions import Fraction as F
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PREV=Path(os.environ['HIST001_ORIGINAL_SOURCE_CONTEXT'])
sys.path.insert(0,str(PREV))
from swells_pack_v2.solv.baryons import J2141BaryonicModel
from swells_pack_v2.solv.cosmology import FlatLCDM
from swells_pack_v2.solv.gate_struct import A0_MPS2,compute_transition_radius_kpc,extract_gate_features_from_values
from swells_pack_v2.solv.dmalane import build_gate_components,epsilon_from_config
from swells_pack_v2.solv.run_setA_port_cand import _build_anchor,_candidate_gate_config,_load_tables,_projection_matrix
from swells_pack_v2.solv.run_j2141_axisym_lens import hernquist_density, projected_disk_mass_exponential,apply_shadow_projection_mode
from swells_pack_v2.solv.shadow_density import compute_shadow_density

def sha(b):return hashlib.sha256(b).hexdigest()
def asblob(x):return b''.join(struct.pack('>d',float(y)) for y in x)
source=PREV/'swells_pack_v2'; a,_=_build_anchor(source)
cfg=_candidate_gate_config(a,candidate_name='ra0_gated_geometry_sigmoid_reg_v2')
table=_load_tables(source);r=np.linspace(0.02,120.,180);K=_projection_matrix(r);cosmo=FlatLCDM(70.,.3)
output=[];coefficients=[]
for _,row in table.iterrows():
    lid=row['lens_id']; bmass=10**row['logM_bulge_chabrier_central'];dmass=10**row['logM_disc_chabrier_central']
    bre=row['Re_bulge_arcsec']*row['scale_kpc_per_arcsec']; dr50=row['Re_disc_arcsec']*row['scale_kpc_per_arcsec']
    qb=float(row['q_bulge']);qd=float(row['q_disc'])
    model=J2141BaryonicModel(bmass,bre,dmass,dr50)
    features=extract_gate_features_from_values(bmass,bre,dmass,dr50,qb,qd,ra0_kpc=compute_transition_radius_kpc(model,a0_mps2=A0_MPS2))
    gbar=model.total_vbar(r)**2/r;comps=build_gate_components(cfg,features=features,anchor=a)
    eps=epsilon_from_config(r,gbar,cfg,features=features,anchor=a);gtot=gbar/eps
    rho=compute_shadow_density(r,gbar,gtot,epsilon=eps,method=comps.get('shadow_density_method','mass_difference_gradient'))
    B=K.dot(hernquist_density(r,bmass,bre/1.8153))
    D=np.array([projected_disk_mass_exponential(R,dmass,dr50/1.67835,qd,ntheta=120) for R in r],dtype=np.float64)
    S0=K.dot(np.nan_to_num(rho,nan=0.0))
    mode={'shadow_projection':'baryon_structure_circularized','disk_axis_ratio_q':qd,'bulge_axis_ratio_q':qb}
    S=apply_shadow_projection_mode(r,S0,mode,B,D,dict(mode))
    sigma=cosmo.sigma_crit_msun_per_kpc2(float(row['z_deflector']),float(row['z_source']))
    coefficients.append({'lens_id':lid,'source_sigma_crit_float64_hex':float(sigma).hex(),'source_pi_float64_hex':float(np.pi).hex(),'z_lens_float64_hex':float(row['z_deflector']).hex(),'z_source_float64_hex':float(row['z_source']).hex()})
    target=np.pi*r**2*sigma; H=B+D+S-target
    prior=(PREV/'sampled_binary64'/f'{lid.replace("+","p")}.R_H_be64.bin').read_bytes()
    previous=np.array([q[1] for q in struct.iter_unpack('>dd',prior)],dtype=np.float64)
    matches=asblob(H)==asblob(previous)
    if not matches:
       print('SOURCE_COMPONENT_REPRO_NOT_IDENTICAL',lid,'maxdiff',np.max(np.abs(H-previous)),flush=True)
       raise RuntimeError('SOURCE NUMERIC IDENTITY DIFFERED - do not use as source trace')
    path=ROOT/'inputs'/('march_components_'+lid.replace('+','p')+'.bin')
    with path.open('wb') as f:
        for tup in zip(r,B,D,S,target,H):f.write(struct.pack('>6d',*map(float,tup)))
    output.append({'lens_id':lid,'component_archive_member':path.relative_to(ROOT).as_posix(),'component_file_SHA256':sha(path.read_bytes()),
      'component_reassembles_original_H_byte_exact':True,'same_original_180_grid_H':True,
      'original_rho_density_sha256':sha(asblob(np.asarray(rho,dtype=np.float64))),
      'original_bulge_numeric_Hernquist_K180':True,
      'original_disk_numeric_omitted_endpoint_120_angles':True,
      'shadow_180grid_baryon_structure_circularized':True,
      'target_uses_source_returned_numpy_pi_Sigma_crit':True})
    print('COMPONENT_IDENTITY_OK',lid,sha(path.read_bytes()),flush=True)
report={'schema':'HIST001D_SOURCE_REPLAY_MATCHING_ORIGINAL_180_SAMPLE_COMPONENT_TRACE_DIAGNOSTIC_V1',
 'original_source_composite_lock':'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a',
 'lenses':output,
 'claims':{'original_finite_computation_component_trace_only':True,
          'physical_mass_continuum_error_certified':False,'no_source_refit':True,
          'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}}
raw=(json.dumps(report,sort_keys=True,separators=(',',':'))+'\n').encode()
(ROOT/'results/original_180_component_trace.json').write_bytes(raw)
print('TRACE_PASS',sha(raw))
coef_raw=(json.dumps({'schema':'HIST001D_ORIGINAL_MARCH_SOURCE_TARGET_FLOAT64_COEFFICIENT_V1','lenses':coefficients,'math_target_not_observation':True},sort_keys=True,separators=(',',':'))+'\n').encode()
(ROOT/'results/source_target_coefficient_witness.json').write_bytes(coef_raw)
print('TARGET_COEFFICIENT_PASS',sha(coef_raw))
