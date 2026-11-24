#!/usr/bin/env python3
"""Independent 608-bit rational source readback and saturation-endpoint verifier.
Uses all180_independent.py reference implementation, not producer arithmetic.
"""
import zipfile,io,hashlib,json,struct
from pathlib import Path
from fractions import Fraction as Q
from all180_independent import source_m_and_prime,euler_gamma,decode_ieee
ROOT=Path(__file__).resolve().parent
EXPECTED_PARENT='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
EXPECTED_SOURCE='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
def sha(b):return hashlib.sha256(b).hexdigest()
def ceil(q):return -((-q.numerator)//q.denominator)
def floor(q):return q.numerator//q.denominator

def inspect():
    parent=(ROOT/'original_parent.zip').read_bytes()
    assert sha(parent)==EXPECTED_PARENT
    z0=zipfile.ZipFile(io.BytesIO(parent))
    z1=zipfile.ZipFile(io.BytesIO(z0.read('inputs/frozen_source_parent.zip')))
    z2=zipfile.ZipFile(io.BytesIO(z1.read('inputs/original_march_D120_q_parent.zip')))
    z3=zipfile.ZipFile(io.BytesIO(z2.read('inputs/original_march180_parent_v1r1.zip')))
    orig=zipfile.ZipFile(io.BytesIO(z3.read('inputs/original_source_46_frozen.zip')))
    lock=json.loads(z3.read('inputs/original_46plus3_lock.json'))
    assert lock['original_46plus3_composite_sha256']==EXPECTED_SOURCE
    for k,s in lock['source_filenames_sha256'].items():assert sha(orig.read('swells_pack_v2/'+k))==s
    for k,s in lock['archived_negative_controls_sha256'].items():assert sha(z3.read('inputs/negative_controls/'+k))==s
    capt=json.loads(z3.read('results/source180_capture.json'))['lenses']
    sm=json.loads(z0.read('results/producer_analytic_source_gradient.json'))['lenses']
    earlier=json.loads((ROOT/'endpoint_saturation_producer.json').read_text())
    assert len(capt)==len(sm)==len(earlier['lenses'])==6
    gamma=euler_gamma()
    answers=[]
    for a,b,baseline in zip(capt,sm,earlier['lenses']):
        assert a['lens_id']==b['lens_id']==baseline['lens_id']
        bytes_=z3.read('inputs/'+a['node_file']);assert sha(bytes_)==a['node_sha256']
        # decode by manual binary64 integer bits, never producer Fraction.from_float
        table=[[decode_ieee(bytes_[j*64+i*8:j*64+(i+1)*8]) for i in range(8)] for j in range(180)]
        R=[x[0] for x in table];W=[x[1] for x in table]
        def unhex(h):return decode_ieee(struct.pack('>d',float.fromhex(h)))
        params={k:unhex(b['source_scalar_binary64_hex'][k]) for k in ('Mb','Md','a','Rd','delta','r0','n')}
        C=unhex(b['source_scalar_binary64_hex']['C4pi'])
        assert all(R[j]<R[j+1] for j in range(179))
        assert all(w>0 for w in W) and all(x[3]>=0 for x in table)
        # independent Bessel/reduced-power endpoint source model
        m0,_=source_m_and_prime(R[0],params,gamma)
        mN,_=source_m_and_prime(R[-1],params,gamma)
        DM=mN-m0
        assert DM.lo()>0
        # built independently by rational products and single exact sum (not source s0)
        Qorig=sum((W[j]*C*R[j]*R[j]*table[j][3] for j in range(180)),Q())
        diff=Qorig-DM
        # independently compare with original source final mass record
        S0_src=table[-1][5]
        d2=S0_src-DM
        # producer bound MUST cover independent interval
        cap=baseline['source_specific_K180_vs_smooth_M_endpoints_absolute_error_upper_milli_Msun']
        cap2=baseline['original_source_S0_at_Rmax_vs_smooth_M_endpoints_absolute_error_upper_milli_Msun']
        assert diff.lo()>=-Q(cap,1000) and diff.hi()<=Q(cap,1000)
        assert d2.lo()>=-Q(cap2,1000) and d2.hi()<=Q(cap2,1000)
        # hard, independently check useful scientific finite statement
        assert diff.lo()>-Q(1,10) and diff.hi()<Q(1,10)
        assert d2.lo()>-Q(1,10) and d2.hi()<Q(1,10)
        out={'lens_id':a['lens_id'],
             'recorded_binary64_original_S0_and_source_nodes_reauthenticated':True,
             'saturated_aperture_exact_source_model':True,
             'independent_K180_minus_continuum_mass_interval_micro_Msun':[floor(diff.lo()*1_000_000),ceil(diff.hi()*1_000_000)],
             'independent_reported_S0_minus_continuum_mass_interval_micro_Msun':[floor(d2.lo()*1_000_000),ceil(d2.hi()*1_000_000)],
             'independent_K180_absolute_error_upper_milli_Msun':ceil(diff.err()*1000),
             'independent_original_S0_absolute_error_upper_milli_Msun':ceil(d2.err()*1000),
             'producer_bound_includes_independent_interval':True}
        answers.append(out)
        print('INDEPENDENT',a['lens_id'],'error bound',out['independent_K180_absolute_error_upper_milli_Msun']/1000,'Msun',flush=True)
    result={'schema':'HIST001D_MARCH180_SATURATED_K180_SELECTED_MSH_INDEPENDENT_V1',
            'original_source_sha256':EXPECTED_SOURCE,'parent_sha256':EXPECTED_PARENT,'lenses':answers,
            'global_uniform_aperture_quadrature_error_proved':False,
            'general_floating_operation_error_proved':False,'continuous_physical_density_admitted':False,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    resultfile=ROOT/'endpoint_saturation_independent.json'
    resultfile.write_bytes((json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    print('OUTPUT_SHA',sha(resultfile.read_bytes()))
    return result
if __name__=='__main__':inspect()
