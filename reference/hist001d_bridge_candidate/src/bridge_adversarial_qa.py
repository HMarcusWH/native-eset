#!/usr/bin/env python3
"""Fail-closed mutation checks: original external inputs and alleged proof result values.
Does not promote numerical source equations or physical lensing.
"""
import copy,hashlib,json,shutil,tempfile,zipfile
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import bridge_independent
sha=lambda b:hashlib.sha256(b).hexdigest()
ORIG=json.loads((ROOT/'results/bridge_discrepancy_producer.json').read_bytes())

changes=[
 ('first_model_identity',lambda x:x['lenses'][0].__setitem__('lens_id','J_FAKE')),
 ('last_model_identity',lambda x:x['lenses'][-1].__setitem__('lens_id','J_FAKE')),
 ('claimed_lower_bound_inflation',lambda x:x['lenses'][0].__setitem__('max_certified_endpoint_difference_floor_msun',str(int(x['lenses'][0]['max_certified_endpoint_difference_floor_msun'])+1000))),
 ('claimed_exact_bound_reduction',lambda x:x['lenses'][1]['max_certified_endpoint_difference_lower_exact_msun'].__setitem__('num','1')),
 ('wrong_best_side',lambda x:x['lenses'][1].__setitem__('max_endpoint_with_strict_disjoint_interval','LEFT')),
 ('forged_numeric_root',lambda x:x['lenses'][2]['march_interpolant_unique_root_kpc'].__setitem__('num','900')), 
 ('wrong_separation',lambda x:x['lenses'][3]['guaranteed_root_position_separation_lower_kpc'].__setitem__('num','0')),
 ('wrong_exact_query_radius',lambda x:x['lenses'][3]['exact_endpoint_discrepancies'][0]['R_exact_kpc'].__setitem__('num','1')),
 ('wrong_march_y',lambda x:x['lenses'][4]['exact_endpoint_discrepancies'][1]['march_H_exact_interpolated_msun'].__setitem__('num','1')),
 ('wrong_endpoint_interval',lambda x:x['lenses'][4]['exact_endpoint_discrepancies'][0].__setitem__('disposition','INTERVALS_OVERLAP')),
 ('wrong_numerical_cell',lambda x:x['lenses'][5]['exact_endpoint_discrepancies'][0].__setitem__('grid_left_index',999)),
 ('false_continuum_error',lambda x:x['claims'].__setitem__('March_180x120_continuum_discretization_error_certified',True)),
 ('false_continuum_root',lambda x:x['claims'].__setitem__('original_March_continuum_root_count_certified',True)),
 ('false_uniform_upper',lambda x:x['claims'].__setitem__('uniform_upper_error_bound_between_models',True)),
 ('false_physical_provider',lambda x:x['claims'].__setitem__('physical_Weyl_provider_admitted',True)),
]

def main():
    successes=[]
    with tempfile.TemporaryDirectory(prefix='hist001d_bridge_QA_') as d:
        d=Path(d)
        for title,mutator in changes:
            record=copy.deepcopy(ORIG)
            mutator(record)
            path=d/(title+'.json')
            # Self-rehashed canonical JSON still must not pass independent full replay.
            b=(json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode()
            path.write_bytes(b)
            try:bridge_independent.validate_producer(ROOT,path)
            except Exception:successes.append({'attack':title,'rehashed_sha256':sha(b),'verdict':'REJECTED'})
            else:raise RuntimeError('FORGED WITNESS PASSED: '+title)
        for name in ('march_180_grid.zip','proxy_narrow.zip'):
            fake=d/name
            raw=bytearray((ROOT/'inputs'/name).read_bytes())
            raw[127]^=1
            fake.write_bytes(raw)
            # No automatic pin rewriting; original external SHA remains mandatory.
            with tempfile.TemporaryDirectory(dir=d) as dd:
                target=Path(dd)
                (target/'inputs').mkdir()
                for n in ('march_180_grid.zip','proxy_narrow.zip'):
                    shutil.copy2((ROOT/'inputs'/n) if n!=name else fake,target/'inputs'/n)
                try:bridge_independent.derive(target)
                except Exception:successes.append({'attack':'source_ZIP_tamper_'+name,'rehashed_sha256':sha(raw),'verdict':'REJECTED'})
                else:raise RuntimeError('TAMPERED SOURCE PASSED: '+name)
    rep={'schema':'HIST001D_G4B1C_BRIDGE_ADVERSARIAL_QA_V1','status':'ALL_TAMPERED_EVIDENCE_REJECTED_SCOPED',
         'count':len(successes),'tests':successes,
         'claims':{'standalone_math_and_input_integrity_ONLY':True,'physical_provider_admitted':False,'empirical_validation':False}}
    raw=(json.dumps(rep,sort_keys=True,separators=(',',':'))+'\n').encode()
    (ROOT/'results/bridge_adversarial_qa.json').write_bytes(raw)
    print('ADVERSARIAL_QA_PASS',len(successes),sha(raw))
if __name__=='__main__':main()
