#!/usr/bin/env python3
"""Second arithmetic implementation: native NumPy source ops and independent sqrt floor.

It shares only the authenticated input parser with the producer. Calculations
and interval floor use separate code; no floating quadrature/Bessel values.
"""
from __future__ import annotations
import argparse
import json
from bisect import bisect_left
from fractions import Fraction
from math import isqrt
from pathlib import Path
import numpy as np
from float_bridge import read_locked,LENSES,sha

P=Fraction
BITS=120

def floor_sqrt_different(x):
    """Floor(sqrt(n/d)*2^BITS) via isqrt(n*d*2^(2BITS))//d."""
    if x<0:raise ValueError('negative')
    n,d=x.numerator,x.denominator
    bottom=isqrt((n*d) << (2*BITS))//d
    assert P(bottom,2**BITS)**2<=x<P(bottom+1,2**BITS)**2
    return P(bottom,2**BITS),P(bottom+1,2**BITS)

def rational_pl(rs,ms,A):
    if A<=rs[0]:return ms[0]
    if A>=rs[-1]:return ms[-1]
    j=bisect_left(rs,A)
    if rs[j]==A:return ms[j]
    l=j-1
    return (ms[l]*(rs[j]-A)+ms[j]*(A-rs[l]))/(rs[j]-rs[l])

def finite_node_interval(rows,qb,qd,pi,sigma,R):
    rs=[P.from_float(x[0]) for x in rows]
    B=[P.from_float(x[4]) for x in rows]
    D=[P.from_float(x[6]) for x in rows]
    S0=[P.from_float(x[5]) for x in rows]
    k=bisect_left(rs,R)
    if rs[k]!=R:raise ValueError('nodal evaluator requires stored R')
    Q=(qb*B[k]+qd*D[k])/(B[k]+D[k])
    lo,hi=floor_sqrt_different(Q)
    Alo=R/hi;Ahi=R/lo
    common=B[k]+D[k]-pi*sigma*R**2
    return common+rational_pl(rs,S0,Alo),common+rational_pl(rs,S0,Ahi)

def ceiling(x):return -((-x.numerator)//x.denominator)
def floor(x):return x.numerator//x.denominator

def check(receipt,saturation,h_archive):
    if receipt.get('schema')!='HIST001D_ORIGINAL_MARCH180_IEEE754_SAMPLED_H_POSTPROCESSING_AND_FINITE_PL_GAP_V1':raise ValueError('schema')
    if receipt.get('source_sampled_H_grid_values_replayed')!=1080 or receipt.get('source_sampled_roots_binary64_exact_replay_count')!=6:raise ValueError('replay totals')
    if receipt.get('physical_provider_admitted') is not False or receipt.get('empirical_validation')!='NOT_ESTABLISHED' or receipt.get('arbitrary_radius_original_March_source_theorem') is not False:raise ValueError('claim firewall')
    if len(receipt.get('lenses',[]))!=6 or [x['lens'] for x in receipt['lenses']]!=list(LENSES):raise ValueError('lens set')
    captures,qs,arrays,metadata,samples,finite,strict_rows,scale_rows=read_locked(saturation,h_archive)
    for c,q,rows,meta,pairs,old,rec in zip(captures,qs,arrays,metadata,samples,finite,receipt['lenses']):
        a=np.asarray(rows,dtype=np.float64)
        rad=a[:,0].copy();sig=float.fromhex(c['original_sigma_hex'])
        # Literal NumPy operator ordering from frozen March run_setA source.
        h=(a[:,4]+a[:,6]+a[:,7])-np.pi*rad**2*sig
        h_original=np.asarray([t[1] for t in pairs],dtype=np.float64)
        if not np.array_equal(h,h_original):raise ValueError('native NumPy differs from March archive')
        if not rec['all_180_archived_H_exactly_reproduced_from_final_stored_source_columns'] or not rec['source_float_root_exact_match_to_archived_binary64']:raise ValueError('false replay flag')
        inds=np.where(np.diff(np.sign(h_original)))[0]
        if len(inds)!=1:raise ValueError('unexpected sample topology')
        i=int(inds[0]); y0=float(h_original[i]);y1=float(h_original[i+1]);x0=float(rad[i]);x1=float(rad[i+1]);returned=float(x0-y0*(x1-x0)/(y1-y0))
        if returned.hex()!=rec['source_float_root_hex'] or returned!=meta['original_first_sign_change_root_kpc'] or i!=rec['source_crossing_index']:raise ValueError('root reproduction')
        if not rec['strict_original_6lens_portability_CSV_arcsec_reproduced'] or returned/float(scale_rows[c['lens_id']]['scale_kpc_per_arcsec'])!=float(strict_rows[c['lens_id']]['predicted_einstein_radius_arcsec']):raise ValueError('strict historical regression CSV')
        x0r,x1r=P.from_float(x0),P.from_float(x1)
        y0r,y1r=P.from_float(y0),P.from_float(y1)
        exact=(x0r*y1r-x1r*y0r)/(y1r-y0r)
        if ceiling(abs(P.from_float(returned)-exact)*10**18)!=rec['source_float_root_vs_exact_archived_sampled_PL_root_upper_atto_kpc']:raise ValueError('root rounding claim')
        pi=P.from_float(float.fromhex(c['original_pi4_float_hex']))/4
        sr=P.from_float(sig)
        ideal=[P.from_float(v[4])+P.from_float(v[6])+P.from_float(v[7])-pi*sr*P.from_float(v[0])**2 for v in rows]
        exact2=(x0r*ideal[i+1]-x1r*ideal[i])/(ideal[i+1]-ideal[i]);err_arith=max(abs(P.from_float(float(u))-v) for u,v in zip(h_original,ideal))
        if ceiling(err_arith*10**6)!=rec['max_exact_real_postprocessing_vs_binary64_archived_H_upper_micro_Msun']:raise ValueError('arith error')
        if ceiling(abs(P.from_float(returned)-exact2)*10**18)!=rec['source_float_root_vs_exact_stored_component_algebra_nodal_PL_root_upper_atto_kpc']:raise ValueError('ideal nodal root')
        qb,qd=P.from_float(float.fromhex(q['qb_hex'])),P.from_float(float.fromhex(q['qd_hex']))
        gmax=P(0);geo=P(0)
        for z,H,idealh in zip(rows,h_original,ideal):
            R=P.from_float(z[0]);lv,uv=finite_node_interval(rows,qb,qd,pi,sr,R)
            hreal=P.from_float(float(H))
            if not ((hreal>0 and lv>0) or (hreal<0 and uv<0)):raise ValueError('node sign')
            gmax=max(gmax,abs(hreal-lv),abs(hreal-uv));geo=max(geo,abs(idealh-lv),abs(idealh-uv))
        if ceiling(gmax*10**6)!=rec['max_source_archived_H_vs_finite_PL_node_upper_micro_Msun']:raise ValueError('node gap')
        if ceiling(geo*10**6)!=rec['max_frozen_geometric_Snode_vs_selected_PL_S0_upper_micro_Msun']:raise ValueError('geometric node gap')
        L,U=[P(z) for z in old['root_bracket']];source=P.from_float(returned)
        if source<L:sep=L-source;side='sampled_left_of_finite'
        elif source>U:sep=source-U;side='sampled_right_of_finite'
        else:raise ValueError('overlapping root definitions')
        if floor(sep*10**9)!=rec['sampled_float_vs_unique_finite_PL_root_separation_strict_lower_nano_kpc'] or rec['sampled_vs_finite_root_order']!=side:raise ValueError('root separation')
        if rec['original_floating_offgrid_source_error_bound_proved'] or rec['upstream_baryon_disk_shadow_projection_floating_error_proved'] or rec['reported_root_is_zero_of_offgrid_finite_PL_model']:raise ValueError('unsupported physical/source claim')
    return {'schema':'HIST001D_INDEPENDENT_NATIVE_NUMPY_AND_ALTERNATE_SQRT_FLOAT_BRIDGE_AUDIT_V1',
        'node_reproductions':1080,'source_returned_roots_reproduced':6,
        'max_node_float_gap_upper_micro_Msun':max(x['max_source_archived_H_vs_finite_PL_node_upper_micro_Msun'] for x in receipt['lenses']),
        'minimum_sample_to_finite_root_gap_lower_nano_kpc':min(x['sampled_float_vs_unique_finite_PL_root_separation_strict_lower_nano_kpc'] for x in receipt['lenses']),
        'independent_sqrt_approach':'INTEGER_ISQRT_NUMERATOR_TIMES_DENOMINATOR_DIVIDE_DENOMINATOR',
        'all_lens_source_array_exact_matches':True,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--saturation',type=Path,required=True);p.add_argument('--finite-H',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    ans=check(json.loads(a.receipt.read_text()),a.saturation,a.finite_H)
    a.out.write_text(json.dumps(ans,indent=2,sort_keys=True)+'\n')
    print('INDEPENDENT_NATIVE_CHECK_PASS',ans,flush=True)
