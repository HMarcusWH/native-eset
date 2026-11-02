#!/usr/bin/env python3
"""Independent mathematical-source derivative spot audit.

No import from producer.py or smooth_math.py. Independent special.iv/kv and
ivp/kvp path plus mp.diff of the full Bessel MASS function at selected knots.
These are numerical high-precision comparisons, NOT validated interval bounds.
"""
from __future__ import annotations
import hashlib,io,json,math,struct,zipfile
from fractions import Fraction
from pathlib import Path
import numpy as np
from scipy import special
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'inputs/frozen_source_parent.zip'

def h(b):return hashlib.sha256(b).hexdigest()
def exact_mpf_float(v):
    f=Fraction.from_float(float(v))
    return mp.mpf(f.numerator)/mp.mpf(f.denominator)
def run():
    p=json.loads((ROOT/'results/producer_analytic_source_gradient.json').read_text())
    assert p['schema']=='HIST001D_SOURCE_ANALYTIC_MSH_DERIVATIVE_V1_NONPROMOTING_DIAGNOSTIC'
    assert len(p['lenses'])==6 and not p['proved_uniform_gradient_error'] and not p['physical_Weyl']
    assert not p['source_11520_proxy_substituted'] and not p['original_numerical_continuum_root_uniqueness']
    assert h(PARENT.read_bytes())==p['parent_source_archive_sha256']
    with zipfile.ZipFile(PARENT) as z0,zipfile.ZipFile(io.BytesIO(z0.read('inputs/original_march_D120_q_parent.zip'))) as z1,zipfile.ZipFile(io.BytesIO(z1.read('inputs/original_march180_parent_v1r1.zip'))) as z2:
        frozen=zipfile.ZipFile(io.BytesIO(z2.read('inputs/original_source_46_frozen.zip')))
        locks=json.loads(z2.read('inputs/original_46plus3_lock.json'))
        assert len(locks['source_filenames_sha256'])==46 and len(locks['archived_negative_controls_sha256'])==3
        assert locks['original_46plus3_composite_sha256']==p['source_lock_sha256']
        for name,sha in locks['source_filenames_sha256'].items():
            assert h(frozen.read('swells_pack_v2/'+name))==sha
        for name,sha in locks['archived_negative_controls_sha256'].items():
            assert h(z2.read('inputs/negative_controls/'+name))==sha
        source=json.loads(z2.read('results/source180_capture.json'))
        auth={t['lens_id']:t for t in source['lenses']}
        assert list(auth)==[t['lens_id'] for t in p['lenses']]
        mp.mp.dps=55
        report=[]
        for model in p['lenses']:
            lid=model['lens_id'];item=auth[lid]
            b=z2.read('inputs/'+item['node_file'])
            assert h(b)==model['original_180_nodal_sha256']==item['node_sha256']
            arr=np.array(list(struct.iter_unpack('>8d',b)))
            r=arr[:,0];w=arr[:,1];source_rho=arr[:,3];B=arr[:,4];S0_source=arr[:,5];D=arr[:,6]
            name=ROOT/model['analytic_profile_file']
            assert h(name.read_bytes())==model['analytic_profile_sha256']
            prof=np.array(list(struct.iter_unpack('>5d',name.read_bytes())))
            assert prof.shape==(180,5) and np.array_equal(r.view(np.uint64),prof[:,0].view(np.uint64))
            hexa=model['source_scalar_binary64_hex']
            Mb,Md,a,Rd,delta,r0,n=[float.fromhex(hexa[k]) for k in ('Mb','Md','a','Rd','delta','r0','n')]
            qb,qd,sigma,C=[float.fromhex(hexa[k]) for k in ('qb','qd','sigma_crit','C4pi')]
            assert C==float(4*math.pi) and 0<delta<=0.95 and r0>0 and n>0
            yy=r/(2*Rd)
            # Distinct Bessel APIs + derivative (ivp,kvp), rather than producer recurrence.
            i0=special.iv(0,yy);i1=special.iv(1,yy)
            k0=special.kv(0,yy);k1=special.kv(1,yy)
            F=i0*k0-i1*k1
            Fp=(special.ivp(0,yy)*k0+i0*special.kvp(0,yy)
                -special.ivp(1,yy)*k1-i1*special.kvp(1,yy))
            M=Mb*r*r/(r+a)**2+Md*yy**3*F
            Mp=2*Mb*a*r/(r+a)**3+Md/(2*Rd)*(3*yy**2*F+yy**3*Fp)
            f=r**n/(r**n+r0**n);fp=n*r**(n-1)*r0**n/(r**n+r0**n)**2
            ep=1-delta*f
            analytic_M=M*delta*f/ep
            analytic_Mp=Mp*delta*f/ep+M*delta*fp/ep**2
            analytic_rho=np.maximum(analytic_Mp/(C*r*r),0)
            rel=np.abs(analytic_rho-prof[:,3])/np.maximum(np.abs(prof[:,3]),1.e-10)
            if not np.all(np.isfinite(rel)) or np.max(rel)>4e-7: raise AssertionError('independent Bessel derivative does not enclose producer numerical result')
            # Independent projector uses monotone positive cylinder kernel, not K.dot.
            R=r[:,None];rr=r[None,:]
            inside=np.broadcast_to(rr**2,R.shape[:-1]+rr.shape[1:])
            outside=rr*(rr-np.sqrt(np.maximum(rr*rr-R*R,0)))
            kernel=np.where(rr<=R,inside,outside)
            s0=np.sum(C*(w*analytic_rho)[None,:]*kernel,axis=1)
            qeff=np.clip((qb*B+qd*D)/(B+D),1e-3,1.)
            aperture=r/np.sqrt(qeff)
            s=np.interp(aperture,r,s0,left=s0[0],right=s0[-1])
            hn=B+D+s-math.pi*r*r*sigma
            max_h_mismatch=np.max(abs(hn-prof[:,4]))
            if max_h_mismatch>1.0: raise AssertionError('independent projected H differs materially')
            edges=np.flatnonzero(np.diff(np.sign(hn)))
            assert len(edges)==model['new_sampled_sign_change_count']
            if edges.size:
                roots=[float(r[i]-hn[i]*(r[i+1]-r[i])/(hn[i+1]-hn[i])) for i in edges]
                assert max(abs(a-b) for a,b in zip(roots,model['new_replacement_density_sampled_root_kpc']))<1e-10
            else:roots=[]
            # Independently differentiate direct Bessel-defined scalar mass in 55 dps.
            mMb,mMd,ma,mRd,mdelta,mr0,mn=[exact_mpf_float(v) for v in (Mb,Md,a,Rd,delta,r0,n)]
            def mass(rr):
                y=rr/(2*mRd)
                f=rr**mn/(rr**mn+mr0**mn)
                ff=mp.besseli(0,y)*mp.besselk(0,y)-mp.besseli(1,y)*mp.besselk(1,y)
                Mb_eff=mMb*rr**2/(rr+ma)**2+mMd*y**3*ff
                return Mb_eff*mdelta*f/(1-mdelta*f)
            iroot=int(np.searchsorted(r,model['old_original_sampled_root_kpc']))
            ids=sorted(set([0,1,2,max(0,iroot-1),iroot,90,179]))
            spots=[]
            for idx in ids:
                deriv=mp.diff(mass,exact_mpf_float(r[idx]))
                rho=float(deriv)/(C*r[idx]*r[idx])
                # A numerical cross-check; not a rigorous bound on Bessel functions.
                relative=abs(rho-prof[idx,3])/max(abs(rho),1e-30)
                if relative>2e-6: raise AssertionError('55-dps Bessel derivative disagrees with producer')
                spots.append({'index':idx,'relative_producer_vs_mp':relative,
                     'source_over_high_precision_smooth_density':float(source_rho[idx]/rho),
                     'mp_smooth_density_msun_kpc3':rho})
            first=spots[0]['source_over_high_precision_smooth_density']
            assert first>4e6
            report.append({'lens_id':lid,'all_180_nodes_bessel_recurrence_rel_discrepancy_max':float(np.max(rel)),
                'independent_projection_max_H_difference_msun':float(max_h_mismatch),
                'independent_new_roots_sampled_kpc':roots,
                'mp_spot_checks':spots,'first_source_over_mp_ratio':first,
                'all_180_smooth_gradient_source_accuracy_proved':False,
                'continuous_root_count_established':False})
        doc={'schema':'HIST001D_INDEPENDENT_BESSEL_MP_SOURCE_DERIVATIVE_DIAGNOSTIC_V1',
             'source_lock_sha256':p['source_lock_sha256'],
             'producer_result_sha256':h((ROOT/'results/producer_analytic_source_gradient.json').read_bytes()),
             'lenses':report, 'independent_mpmath_special_function_spots':True,
             'global_Bessel_interval_error_certified':False,
             'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
        raw=(json.dumps(doc,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
        (ROOT/'results/independent_mp_check.json').write_bytes(raw)
        print('INDEPENDENT_MP_SOURCE_DERIVATIVE_DIAGNOSTIC_PASS',len(report),h(raw),flush=True)
        return h(raw)
if __name__=='__main__':run()
