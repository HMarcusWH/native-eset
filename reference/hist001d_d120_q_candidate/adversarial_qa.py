"""Tamper controls on externally SHA-pinned original-source bridge certificates.
This is integrity/claim QA, NOT independent mathematics.
"""
from __future__ import annotations
import copy,hashlib,json,zipfile,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'inputs/original_march180_parent_v1r1.zip'
sha=lambda x:hashlib.sha256(x).hexdigest()

def check(src,agg,docd,docq):
 if set(src)!={'schema','source_composite_lock','original_archive_sha256','parent_archive_sha256','lenses','source_mutated','new_D2d_11520_data_used','physical_provider_admitted','empirical_validation'}:raise ValueError('source schema drift')
 if src['source_composite_lock']!='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a':raise ValueError('source lock drift')
 if src['parent_archive_sha256']!='0a643e81a9ab542dce8f158bc5135d94478d9145ab33036aae5813907f3655a1':raise ValueError('parent drift')
 if src['source_mutated'] or src['new_D2d_11520_data_used'] or src['physical_provider_admitted'] or src['empirical_validation']!='NOT_ESTABLISHED':raise ValueError('source/claim forgery')
 if agg['source120_capture_sha256'] != sha((json.dumps(src,sort_keys=True,separators=(',',':'))+'\n').encode()):raise ValueError('receipt anchor mismatch')
 if agg['schema']!='HIST001D_COMMON180_D120_AND_Q_CIRCULARIZED_INDEPENDENT_6LENS_RECONCILIATION_v1':raise ValueError('false aggregate schema')
 if agg['parent_archive_sha256']!=src['parent_archive_sha256'] or not agg['uses_180_frozen_source_only'] or agg['full_original_source_continuum_error_proved'] or agg['physical_provider_admitted'] or agg['empirical_validation']!='NOT_ESTABLISHED':raise ValueError('false aggregate/model claim')
 if agg['cells_independent_q_Bernstein']!=1074 or agg['disk_source_knots_checked']!=1080 or len(agg['lens_records'])!=6:raise ValueError('false coverage')
 lsrc=[e['lens_id'] for e in src['lenses']];lags=[e['lens_id'] for e in agg['lens_records']]
 if lsrc!=lags or len(set(lags))!=6:raise ValueError('lens identity drift')
 if len(docd['lenses'])!=6 or len(docq['lenses'])!=6:raise ValueError('producer lens count')
 if docd['full_azimuth_angular_integral_certified'] or docd['actual_original_March_continuous_solver_error_certified'] or docd['D2d_11520_data_used'] or docd['physical_provider_admitted']:raise ValueError('false D claims')
 if docq['original_March_full_H_error_bounded'] or docq['new_11520_shadow_model_used'] or docq['physical_provider_admitted']:raise ValueError('false q claims')
 byq={x['lens_id']:x for x in docq['lenses']};byd={x['lens_id']:x for x in docd['lenses']}
 with zipfile.ZipFile(PARENT) as z:
  for sr,a in zip(src['lenses'],agg['lens_records']):
   name=sr['lens_id'];ang=(ROOT/sr['angular_binary64_path']).read_bytes()
   if sha(ang)!=sr['angular_node_sha256'] or a['angular_count']!=120 or a['node_count']!=180 or a['radial_cells']!=179:raise ValueError('angular/node drift')
   if not all(w>=0 and aa>0 for _,w,aa in struct.iter_unpack('>ddd',ang)):raise ValueError('bad angular data')
   raw=z.read('inputs/March180_source_nodes_'+name.replace('+','p')+'.be64')
   assert len(raw)==180*64
   if byq[name]['circularized_shadow_all_real_sourcePL_error_upper_ceiling_msun']!=a['q_circularized_shadow_PL_math_all_real_error_ceil_msun']:raise ValueError('shadow bound altered')
   if byd[name]['certified_continuous_angle120_math_to_recorded_D_PL_error_upper_ceiling_msun']!=a['disk_PL_math_all_real_error_ceil_msun']:raise ValueError('disk bound altered')
   if not byq[name]['all_real_aperture_unsaturated_strictly_increasing'] or byq[name]['coarse_aperture_derivative_positive_cells']!=179 or not byd[name]['disk_model_source_nodes_enclosed_to_lt_1_Msun']:raise ValueError('positivity/fidelity drift')
   if not a['min_q_aperture_guard_positive']:raise ValueError('q guard drift')
 return True

def run():
 files=['source120_capture.json','independent_six_lens_aggregate.json','disk120_math_producer.json','q_aperture_producer.json']
 src,agg,docd,docq=[json.loads((ROOT/'results'/f).read_text()) for f in files]
 check(src,agg,docd,docq)
 mods=[]
 def test(name,mutator):
  items=copy.deepcopy((src,agg,docd,docq));mutator(*items)
  # Self-rehashed JSON passes a naive local hash check; independent anchors/claims MUST refuse.
  outer=sha(json.dumps(items,sort_keys=True,separators=(',',':')).encode())
  try:check(*items)
  except (ValueError,KeyError,IndexError,AssertionError) as exc:mods.append({'name':name,'rejected':True,'reason':str(exc),'self_rehashed_sha256':outer})
  else:raise AssertionError('tamper accepted: '+name)
 test('source_lock_replaced',lambda s,a,d,q:s.__setitem__('source_composite_lock','f'*64))
 test('source_claim_physical',lambda s,a,d,q:s.__setitem__('physical_provider_admitted',True))
 test('source_false_11520',lambda s,a,d,q:s.__setitem__('new_D2d_11520_data_used',True))
 test('source_scalar_q_changed',lambda s,a,d,q:s['lenses'][0].__setitem__('qd_hex','0x1.0p-1'))
 test('source_schema_extra',lambda s,a,d,q:s.__setitem__('false_theorem',True))
 test('aggregate_false_h_error',lambda s,a,d,q:a.__setitem__('full_original_source_continuum_error_proved',True))
 test('aggregate_physics',lambda s,a,d,q:a.__setitem__('physical_provider_admitted',True))
 test('aggregate_missing_lens',lambda s,a,d,q:a['lens_records'].pop())
 test('aggregate_duplicate_lens',lambda s,a,d,q:a['lens_records'][1].__setitem__('lens_id',a['lens_records'][0]['lens_id']))
 test('aggregate_cell_count',lambda s,a,d,q:a.__setitem__('cells_independent_q_Bernstein',1073))
 test('aggregate_disk_lowered',lambda s,a,d,q:a['lens_records'][0].__setitem__('disk_PL_math_all_real_error_ceil_msun',a['lens_records'][0]['disk_PL_math_all_real_error_ceil_msun']-1))
 test('aggregate_shadow_lowered',lambda s,a,d,q:a['lens_records'][0].__setitem__('q_circularized_shadow_PL_math_all_real_error_ceil_msun',a['lens_records'][0]['q_circularized_shadow_PL_math_all_real_error_ceil_msun']-1))
 test('disk_full_angle_forgery',lambda s,a,d,q:d.__setitem__('full_azimuth_angular_integral_certified',True))
 test('disk_real_solver_claim',lambda s,a,d,q:d.__setitem__('actual_original_March_continuous_solver_error_certified',True))
 test('q_derivative_false',lambda s,a,d,q:q['lenses'][0].__setitem__('coarse_aperture_derivative_positive_cells',178))
 test('q_source_11520',lambda s,a,d,q:q.__setitem__('new_11520_shadow_model_used',True))
 assert len(mods)==16
 doc={'schema':'HIST001D_D120_Q_ORIGINAL_SOURCE_ARITHMETIC_ADVERSARIAL_QA_v1','alterations_checked':len(mods),'alterations_rejected':sum(x['rejected'] for x in mods),'cases':mods,'no_new_scientific_theorem_from_integrity_QA':True,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
 b=(json.dumps(doc,sort_keys=True,separators=(',',':'))+'\n').encode();(ROOT/'results/adversarial_qa.json').write_bytes(b)
 print('ADVERSARIAL_PASS',len(mods),sha(b))
if __name__=='__main__':run()
