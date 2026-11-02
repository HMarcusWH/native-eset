import json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED_PARENT='0a643e81a9ab542dce8f158bc5135d94478d9145ab33036aae5813907f3655a1'
sha=lambda b:hashlib.sha256(b).hexdigest()

def run():
 src=json.loads((ROOT/'results/source120_capture.json').read_text());q=json.loads((ROOT/'results/q_aperture_producer.json').read_text());d=json.loads((ROOT/'results/disk120_math_producer.json').read_text())
 orig_names=[x['lens_id'] for x in src['lenses']]
 assert len(orig_names)==6 and len(set(orig_names))==6
 assert len(q['lenses'])==len(d['lenses'])==6
 assert sha((ROOT/'inputs/original_march180_parent_v1r1.zip').read_bytes())==EXPECTED_PARENT
 rec=[]
 for name in orig_names:
  fq=next(x for x in q['lenses'] if x['lens_id']==name);fd=next(x for x in d['lenses'] if x['lens_id']==name)
  path=ROOT/'results'/('independent_verifier_'+name.replace('+','p')+'.json')
  ind=json.loads(path.read_bytes())
  assert ind['source_hashes_46plus3_verified'] and len(ind['lenses'])==1
  fi=ind['lenses'][0]
  assert fi['lens_id']==name
  assert fi['disk_D120_vs_sourcePL_uniform_ceil_msun']==fd['certified_continuous_angle120_math_to_recorded_D_PL_error_upper_ceiling_msun']
  assert fi['shadow_aperture_vs_original_PL_uniform_ceil_msun']==fq['circularized_shadow_all_real_sourcePL_error_upper_ceiling_msun']
  assert fi['all_179_quadratic_Bernstein_margins_strict_positive']
  assert fi['all_180_source_disk_nodes_enclosed_lt_1_Msun']
  assert fi['all_180_source_final_shadow_nodes_enclosed_lt_1_Msun']
  rec.append({'lens_id':name,'node_count':180,'angular_count':120,'radial_cells':179,'disk_PL_math_all_real_error_ceil_msun':fi['disk_D120_vs_sourcePL_uniform_ceil_msun'],'q_circularized_shadow_PL_math_all_real_error_ceil_msun':fi['shadow_aperture_vs_original_PL_uniform_ceil_msun'],'min_q_aperture_guard_positive':True,'independent_per_lens_receipt_sha256':sha(path.read_bytes())})
 doc={'schema':'HIST001D_COMMON180_D120_AND_Q_CIRCULARIZED_INDEPENDENT_6LENS_RECONCILIATION_v1','parent_archive_sha256':EXPECTED_PARENT,'source120_capture_sha256':sha((ROOT/'results/source120_capture.json').read_bytes()),'q_producer_sha256':sha((ROOT/'results/q_aperture_producer.json').read_bytes()),'disk_producer_sha256':sha((ROOT/'results/disk120_math_producer.json').read_bytes()),'lens_records':rec,'cells_independent_q_Bernstein':6*179,'disk_source_knots_checked':6*180,'independent_binary64_decode':True,'disk_exponential_alternating_exact_rational':True,'uses_180_frozen_source_only':True,'all_real_claim_scope':'SOURCE_FROZEN_120_ANGLE_IDEAL_MATH_D_VS_ORIGINAL_RECORDED_PL_AND_180_SOURCE_PL_BD_Q_EFF_S0_CIRCULARIZED','full_original_source_continuum_error_proved':False,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED','merged_release':False}
 raw=(json.dumps(doc,sort_keys=True,separators=(',',':'))+'\n').encode()
 (ROOT/'results/independent_six_lens_aggregate.json').write_bytes(raw)
 print('SIX_LENS_AGGREGATE_PASS',sha(raw))
 for x in rec:print(x['lens_id'],x['disk_PL_math_all_real_error_ceil_msun'],x['q_circularized_shadow_PL_math_all_real_error_ceil_msun'])
if __name__=='__main__':run()
