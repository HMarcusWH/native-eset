#!/usr/bin/env python3
"""Source-data-independent adversarial schema/claim mutations."""
from __future__ import annotations
import copy,json
from pathlib import Path
from inter_node_claim_guard import validate,LENSES,SOURCE_SHA

def synthetic():
    inter=[];bv=[]
    for i,name in enumerate(LENSES):
        panels=[{'cell':k,'lo':str(k),'hi':str(k+1),'depth':0,'Mprime_lower_micro':1,
                 'Mprime_upper_micro':100,'Msecond_abs_ceil':3} for k in range(179)]
        inter.append({'schema':'HIST001D_SELECTED_MSTAR_REAL_INTEGRAL_BESSEL_INTER_NODE_MPRIME_V1',
          'lens_id':name,'node_sha256':str(i)*64,'source_scope':'SELECTED_HISTORICAL_ACCELERATION_EQUIVALENT_MSTAR_NOT_PHYSICAL',
          'all_real_selected_Mprime_positive':True,'nodes':180,'accepted_panels':179,'extra_points':0,
          'unresolved':[],'panels':panels,'midpoints':[],
          'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'})
        bv.append({'lens':name,'accepted_original_radial_cells':179,'accepted_subpanels':179,
         'source_scope':'SELECTED_MSTAR_ONLY_NOT_PHYSICAL_SOURCE','useful_for_full_root_gap':False,
         'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
         'uniform_band_derivative_sampled_trap_vs_mathematical_continuum_error_ceiling_Msun':2,
         'uniform_band_error_kernel_variation_ceiling_Msun':1,
         'uniform_band_error_Mprime_variation_ceiling_Msun':1,
         'uniform_band_original_weight_rounding_ceiling_micro_Msun':0,
         'P_mathematical_continuum_all_A_band_integer_Msun_enclosure':[1,3]})
    meta={'source_original_46plus3_sha256':SOURCE_SHA,'physical_provider_admitted':False,
          'empirical_validation':'NOT_ESTABLISHED','global_ideal_K180_vs_continuum_root_error_proved':False,
          'smooth_model_physical_Weyl_provider_admitted':False,
          'selected_Mstar_prime_all_real_positive':True,'all_six_root_band_BV_bounds_certified':True,
          'useful_for_original_March_root_gap':False,'parent_sha_lock_byte_counts':[100,200]}
    return inter,bv,meta

def run():
    baseline=synthetic();assert validate(*baseline)
    trials=[]
    def mutation(label,f):
        x=copy.deepcopy(baseline);f(*x)
        try:validate(*x)
        except (ValueError,KeyError,TypeError,IndexError):trials.append({'label':label,'status':'REJECTED'});return
        raise AssertionError('accepted unsafe mutation '+label)
    mutation('omit-lens',lambda i,b,m:i.pop())
    mutation('extra-lens',lambda i,b,m:i.append(copy.deepcopy(i[0])))
    mutation('swap-lens',lambda i,b,m:i[0].update(lens_id=i[1]['lens_id']))
    mutation('wrong-bv-lens',lambda i,b,m:b[0].update(lens='other'))
    mutation('forged-source',lambda i,b,m:m.update(source_original_46plus3_sha256='0'*64))
    mutation('physical-provider',lambda i,b,m:m.update(physical_provider_admitted=True))
    mutation('scientific-validation',lambda i,b,m:m.update(empirical_validation='VALIDATED'))
    mutation('false-continuum-root',lambda i,b,m:m.update(global_ideal_K180_vs_continuum_root_error_proved=True))
    mutation('false-Weyl',lambda i,b,m:m.update(smooth_model_physical_Weyl_provider_admitted=True))
    mutation('failed-real-positivity',lambda i,b,m:m.update(selected_Mstar_prime_all_real_positive=False))
    mutation('failed-BV',lambda i,b,m:m.update(all_six_root_band_BV_bounds_certified=False))
    mutation('false-root-usefulness',lambda i,b,m:m.update(useful_for_original_March_root_gap=True))
    mutation('zero-parent-bytes',lambda i,b,m:m.update(parent_sha_lock_byte_counts=[0,200]))
    mutation('missing-parent',lambda i,b,m:m.update(parent_sha_lock_byte_counts=[200]))
    mutation('wrong-inter-schema',lambda i,b,m:i[0].update(schema='not certified'))
    mutation('unresolved-panel',lambda i,b,m:i[0].update(unresolved=[{'cell':0}]))
    mutation('missing-cell',lambda i,b,m:i[0]['panels'].pop())
    mutation('duplicate-cell-index',lambda i,b,m:i[0]['panels'][0].update(cell=1))
    mutation('negative-lower',lambda i,b,m:i[0]['panels'][0].update(Mprime_lower_micro=-1))
    mutation('zero-lower',lambda i,b,m:i[0]['panels'][0].update(Mprime_lower_micro=0))
    mutation('inverted-interval',lambda i,b,m:i[0]['panels'][0].update(Mprime_upper_micro=0))
    mutation('negative-curvature',lambda i,b,m:i[0]['panels'][0].update(Msecond_abs_ceil=-1))
    mutation('wrong-panel-count',lambda i,b,m:i[0].update(accepted_panels=999))
    mutation('wrong-midpoint-count',lambda i,b,m:i[0].update(extra_points=1))
    mutation('forged-nodal-hash',lambda i,b,m:i[0].update(node_sha256='bad'))
    mutation('physical-inter',lambda i,b,m:i[0].update(physical_provider_admitted=True))
    mutation('physical-BV',lambda i,b,m:b[0].update(physical_provider_admitted=True))
    mutation('false-BV-physical',lambda i,b,m:b[0].update(useful_for_full_root_gap=True))
    mutation('trivial-BV',lambda i,b,m:b[0].update(uniform_band_derivative_sampled_trap_vs_mathematical_continuum_error_ceiling_Msun=0))
    mutation('negative-continuum',lambda i,b,m:b[0].update(P_mathematical_continuum_all_A_band_integer_Msun_enclosure=[-1,3]))
    mutation('inverted-continuum',lambda i,b,m:b[0].update(P_mathematical_continuum_all_A_band_integer_Msun_enclosure=[4,3]))
    mutation('wrong-BV-count',lambda i,b,m:b[0].update(accepted_subpanels=0))
    result={'schema':'HIST001D_INTER_NODE_ADVERSARIAL_QA_V1','count':len(trials),'all_rejected':True,'cases':trials,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    return result

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);a=p.parse_args()
    obj=run();dest=a.root/'results/adversarial_qa.json'
    dest.write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
    print('ADVERSARIAL_REJECTED',obj['count'])
if __name__=='__main__':main()
