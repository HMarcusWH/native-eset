#!/usr/bin/env python3
"""Original March 180 node Bessel -> mass -> gradient source arithmetic audit.

Source-conditional and nonpromoting. This checks frozen source outputs and exact
rational arithmetic; it does NOT certify arbitrary-input SciPy/NumPy ulp bounds
nor the unsampled original physical lensing field.
"""
from __future__ import annotations
import json, io, zipfile, tempfile, sys, struct, hashlib, argparse
from pathlib import Path
from fractions import Fraction as F
import numpy as np
# The two inherited 512/608-bit arithmetic engines live in the exact parent public
# source tree; no private data is imported by this module at import time.
SIBLING=Path(__file__).resolve().parents[1]/'hist001d_k180_saturation_candidate'
if str(SIBLING) not in sys.path:sys.path.insert(0,str(SIBLING))
from all180_math import euler_gamma,source_mass,gate,Iv  # noqa: E402
from all180_independent import euler_gamma as gamma_independent,source_m_and_prime  # noqa: E402

PARENT_SHA='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
ORIGINAL_ZIP_SHA='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
sha=lambda x:hashlib.sha256(x).hexdigest()
def floor(q):return q.numerator//q.denominator
def ceil(q):return -((-q.numerator)//q.denominator)
def dyadic(x):return F.from_float(float(x))
def maxabs(q):return max(abs(q.low()),abs(q.high()))
def hull_micro(q):return [floor(q.low()*10**6),ceil(q.high()*10**6)]
def unsigned_micro(q):return ceil(maxabs(q)*10**6)
def rational_slope(xs,ys):
    if len(xs)!=len(ys) or len(xs)<3:raise ValueError('slope dimensions')
    if any(b<=a for a,b in zip(xs,xs[1:])):raise ValueError('mesh not increasing')
    D=[]
    for i in range(len(xs)):
        if i==0:di=(ys[1]-ys[0])/(xs[1]-xs[0])
        elif i==len(xs)-1:di=(ys[-1]-ys[-2])/(xs[-1]-xs[-2])
        else:
            hm=xs[i]-xs[i-1];hp=xs[i+1]-xs[i]
            di=(hp*(ys[i]-ys[i-1])/hm+hm*(ys[i+1]-ys[i])/hp)/(hm+hp)
        D.append(di)
    return D

def load(sat:Path):
    blob=sat.read_bytes()
    if sha(blob)!=PARENT_SHA:raise ValueError('saturation SHA mismatch')
    root=zipfile.ZipFile(io.BytesIO(blob));manifest=json.loads(root.read('MANIFEST_SHA256.json'))
    for path,h in manifest['files'].items():
        if sha(root.read(path))!=h:raise ValueError('saturation file hash '+path)
    original_parent=zipfile.ZipFile(io.BytesIO(root.read('original_parent.zip')))
    info=json.loads(original_parent.read('results/producer_analytic_source_gradient.json'))['lenses']
    all180=zipfile.ZipFile(io.BytesIO(root.read('all180_parent.zip')))
    certified=[]
    for a in info:
        f='results/all180_rational_'+a['lens_id'].replace('+','p')+'.json'
        certified.append(json.loads(all180.read(f)))
    f=zipfile.ZipFile(io.BytesIO(original_parent.read('inputs/frozen_source_parent.zip')))
    d=zipfile.ZipFile(io.BytesIO(f.read('inputs/original_march_D120_q_parent.zip')))
    s=zipfile.ZipFile(io.BytesIO(d.read('inputs/original_march180_parent_v1r1.zip')))
    lock=json.loads(s.read('inputs/original_46plus3_lock.json'))
    if lock['original_46plus3_composite_sha256']!=SOURCE_SHA:raise ValueError('source identity')
    source=s.read('inputs/original_source_46_frozen.zip')
    if sha(source)!=ORIGINAL_ZIP_SHA:raise ValueError('original ZIP identity')
    capture=json.loads(s.read('results/source180_capture.json'))['lenses']
    rows=[]
    for a in capture:
        raw=s.read('inputs/'+a['node_file'])
        if sha(raw)!=a['node_sha256'] or len(raw)!=180*64:raise ValueError('original node changed')
        rows.append(np.array(list(struct.iter_unpack('>8d',raw))))
    names=[x['lens_id'] for x in info]
    if names!=[x['lens_id'] for x in certified] or names!=[x['lens_id'] for x in capture] or len(names)!=6:raise ValueError('lens inventory')
    return lock,source,info,certified,capture,rows

def produce(sat,out):
    lock,src,infos,certs,captures,rows=load(sat)
    gamma=euler_gamma();gamma2=gamma_independent()
    result=[]
    with tempfile.TemporaryDirectory(prefix='hist001d-original-march-mass-') as td:
        with zipfile.ZipFile(io.BytesIO(src)) as z:
            for path,h in lock['source_filenames_sha256'].items():
                if sha(z.read('swells_pack_v2/'+path))!=h:raise ValueError('original source changed')
            for file_name in z.namelist():
                destination=(Path(td)/file_name).resolve()
                if not destination.is_relative_to(Path(td).resolve()):raise ValueError('unsafe protected source path')
            z.extractall(td)
        sys.path.insert(0,td)
        from swells_pack_v2.solv.baryons import J2141BaryonicModel
        from swells_pack_v2.solv.dmalane import epsilon_radius_proxy
        from swells_pack_v2.solv.shadow_density import compute_shadow_density
        from swells_pack_v2.solv.constants import G_KPC_KMS2_MSUN,FOUR_PI
        for info,cert,cap,mat in zip(infos,certs,captures,rows):
            pfloat={k:float.fromhex(v) for k,v in info['source_scalar_binary64_hex'].items()}
            pmath={k:dyadic(pfloat[k]) for k in ['Mb','Md','a','Rd','r0','n','delta']}
            R=mat[:,0];w=mat[:,1];stored_rho=mat[:,3]
            bary=J2141BaryonicModel(pfloat['Mb'],pfloat['a']*1.8153,pfloat['Md'],pfloat['Rd']*1.67835)
            bary.bulge_scale_kpc=pfloat['a'];bary.disk_scale_kpc=pfloat['Rd']
            gbar=bary.total_vbar(R)**2/R
            eps=epsilon_radius_proxy(R,pfloat['delta'],pfloat['r0'],pfloat['n'],epsilon_floor=0.05)
            gtot=gbar/eps
            mass_bary=np.where(R>0,gbar*R**2/G_KPC_KMS2_MSUN,0)
            mass_effective=np.where(R>0,gtot*R**2/G_KPC_KMS2_MSUN,0)
            mass_preclip=mass_effective-mass_bary
            mfloat=np.clip(mass_preclip,0,None)
            grad=np.gradient(mfloat,R)
            reproduced=compute_shadow_density(R,gbar,gtot,epsilon=eps,method='mass_difference_gradient')
            if not np.array_equal(reproduced.view(np.uint64),stored_rho.view(np.uint64)):
                raise ValueError('stored rho not bitwise reproduced: '+info['lens_id'])
            if not (np.all(eps>0.05) and np.all(eps<1.) and np.all(mass_preclip>0) and np.all(grad>0) and np.all(stored_rho>0)):
                raise ValueError('source clipping activated: '+info['lens_id'])
            raw_mass=b''.join(struct.pack('>d',float(x)) for x in mfloat)
            mass_rel='inputs/frozen_source_mass_'+info['lens_id'].replace('+','p')+'.be64'
            mass_path=out.parent.parent/mass_rel
            mass_path.parent.mkdir(exist_ok=True,parents=True)
            mass_path.write_bytes(raw_mass)
            x=[dyadic(a) for a in R];W=[dyadic(a) for a in w]
            m=[dyadic(a) for a in mfloat];C=dyadic(FOUR_PI)
            actual_d=[C*xx*xx*dyadic(rho) for xx,rho in zip(x,stored_rho)]
            ideal_d=rational_slope(x,m)
            residual=[a-b for a,b in zip(actual_d,ideal_d)]
            round_error=sum((wi*abs(v) for wi,v in zip(W,residual)),F())
            all180_micro=cert['stored_vs_ideal_stencil_absolute_upper_micro_msun_per_kpc']
            if len(all180_micro)!=180:raise ValueError('all180 per-node certificate count')
            inherited_bound=sum((wi*F(v,10**6) for wi,v in zip(W,all180_micro)),F())
            # The source Bessel analytic mass input belongs to the *original* source scalar values;
            # only 4 exact original sample nodes near each fitted crossing are re-enclosed here.
            sigma=pfloat['sigma_crit'];H=mat[:,4]+mat[:,6]+mat[:,7]-np.pi*R**2*sigma
            crossing=np.flatnonzero(np.diff(np.sign(H)))
            if len(crossing)!=1:raise ValueError('original sign chart not one crossing')
            j=int(crossing[0]); knots=list(range(max(0,j-1),min(180,j+3)))
            expected_knots=[j-1,j,j+1,j+2] if j>=1 else [0,1,2]
            if knots!=expected_knots:raise ValueError('crossing source window')
            m_int={};bary_int={};eps_int={};spot=[]
            for q in knots:
                M,_,(Fbes,_,_)=source_mass(x[q],pmath,gamma)
                M2,_=source_m_and_prime(x[q],pmath,gamma2)
                if M.high()<M2.lo() or M2.hi()<M.low():raise ValueError('512/608 Bessel mass intervals disjoint')
                y=x[q]/(2*pmath['Rd'])
                A=pmath['Mb']*Iv(x[q])**2/(x[q]+pmath['a'])**2+pmath['Md']*Iv(y)**3*Fbes
                g,_=gate(x[q],pmath['r0'],pmath['n'],pmath['delta'])
                e=1/(1+g)
                m_int[q]=M;bary_int[q]=A;eps_int[q]=e
                mdelta=Iv(m[q])-M;adelta=Iv(dyadic(mass_bary[q]))-A;edelta=Iv(dyadic(eps[q]))-e
                spot.append({'index':q,'R_hex':float(R[q]).hex(),
                      'source_Mshadow_hex':float(mfloat[q]).hex(),
                      'source_bary_acc_mass_hex':float(mass_bary[q]).hex(),
                      'source_epsilon_hex':float(eps[q]).hex(),
                      'source_Mshadow_minus_selected_math_interval_integer_micro_Msun':hull_micro(mdelta),
                      'source_bary_acc_mass_minus_selected_Bessel_math_interval_integer_micro_Msun':hull_micro(adelta),
                      'source_epsilon_minus_selected_math_interval_integer_femto':[floor(edelta.low()*10**15),ceil(edelta.high()*10**15)],
                      'independent_608bit_selected_Bessel_mass_interval_overlaps':True})
            # Component separation on the two crossing-cell density nodes
            grad_math=rational_slope([x[q] for q in knots],[m_int[q] for q in knots])
            crossing_rows=[]
            for target in [j,j+1]:
                loc=knots.index(target)
                upstream=ideal_d[target]-grad_math[loc]
                full=actual_d[target]-grad_math[loc]
                # The inherited upper bound was computed using the same mass law and source nodes
                if max(abs(full.low()),abs(full.high()))>F(all180_micro[target],10**6):
                    raise ValueError('source crossing 512-bit interval contradicts inherited all180 bound')
                crossing_rows.append({'index':target,
                    'stored_vs_ideal_sourcefloat_gradient_exact_integer_nano_Msun_per_kpc':
                     [floor(residual[target]*10**9),ceil(residual[target]*10**9)],
                    'sourcefloat_ideal_gradient_vs_selected_exact_gradient_integer_micro_Msun_per_kpc':hull_micro(upstream),
                    'total_stored_gradient_vs_selected_exact_gradient_integer_micro_Msun_per_kpc':hull_micro(full),
                    'inherited_independent_all180_bound_micro_Msun_per_kpc':all180_micro[target]})
            node={
                'lens_id':info['lens_id'],'original_node_sha256':cap['node_sha256'],
                'original_replayed_float_mass_binary_file':mass_rel,
                'original_replayed_float_mass_binary_sha256':sha(raw_mass),
                'original_180_shadow_density_bitwise_replay_count':180,
                'unclipped_positive_mass_gradient_density_nodes':180,
                'epsilon_floor_inactive_nodes':180,
                'source_epsilon_min_hex':float(np.min(eps)).hex(),
                'source_epsilon_max_hex':float(np.max(eps)).hex(),
                'rounding_only_stored_rho_vs_ideal_stencil_of_current_source_float_mass_all_apertures_micro_Msun_upper':ceil(round_error*10**6),
                'inherited_512bit_full_all180_source_vs_selected_math_stencil_all_apertures_micro_Msun_upper':ceil(inherited_bound*10**6),
                'upstream_sourcefloat_stencil_to_selected_ideal_math_stencil_all_apertures_triangle_micro_Msun_upper':ceil((inherited_bound+round_error)*10**6),
                'original_root_cell_index':j,
                'root_neighborhood_4_node_Bessel_gbar_gate_mass_replay':spot,
                'crossing_node_gradient_sourcefloat_vs_math_split':crossing_rows,
                'selected_mass_not_physical_source':True,
                'per_node_512bit_prior_certificate_reused':True,
            }
            result.append(node)
            print(info['lens_id'], '180/180 source density', 'rounding <=',node['rounding_only_stored_rho_vs_ideal_stencil_of_current_source_float_mass_all_apertures_micro_Msun_upper']/1e6,
                  'M_sun','inherited all <=',node['inherited_512bit_full_all180_source_vs_selected_math_stencil_all_apertures_micro_Msun_upper']/1e6,
                  'M_sun','crossing',j,flush=True)
        sys.path.remove(td)
    obj={'schema':'HIST001D_SOURCE_MARCH_BESSEL_FLOAT_MASS_GRADIENT_K180_COMPONENT_SPLIT_V1_NONPROMOTING',
         'source_original_46plus3_sha256':SOURCE_SHA,
         'input_saturation_sha256':PARENT_SHA,
         'source_scipy_version_replayed':__import__('scipy').__version__,
         'source_numpy_version_replayed':np.__version__,
         'all_source_shadow_density_nodes_reproduced_bitwise':1080,
         'all_epsilon_mass_gradient_density_clips_inactive_at_source_nodes':True,
         'inherited_exact_real_bessel_512bit_interval_all180_and_independent_spot_608bit':True,
         'source_rounding_split_applies_only_to_frozen_original_radii':True,
         'all_aperture_bound_applies_only_to_frozen_K180_mass_stencil_not_continuous_projection':True,
         'unseen_scipy_ulps_and_alternate_platforms_certified':False,
         'continuous_radii_Bessel_or_gradient_error_certified':False,
         'same_source_physical_density_or_Weyl_authorized':False,
         'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
         'lenses':result}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes((json.dumps(obj,sort_keys=True,indent=2)+'\n').encode())
    print('OUTPUT_SHA',sha(out.read_bytes()))
    return obj

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--sat',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    args=a.parse_args();produce(args.sat,args.out)
