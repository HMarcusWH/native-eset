"""Self-rehashed proof alterations must not change source/claim authority (NONPROMOTING)."""
import copy,hashlib,json,tempfile
from pathlib import Path
import independent_verify as ver
ROOT=Path(__file__).resolve().parent

def val(v):return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()

def run():
 baseline=json.loads(ver.PROOF.read_bytes());models=ver.load_models()
 assert ver.verify(baseline,models)['independent_verified_sign_cells']==1273
 rejected=[]
 tests={
  'missing_positive_leaf':lambda x: x['lenses'][0]['strict_sign_leaves'].pop(0),
  'duplicate_leaf':lambda x: x['lenses'][0]['strict_sign_leaves'].append(x['lenses'][0]['strict_sign_leaves'][0]),
  'flipped_sign':lambda x: x['lenses'][0]['strict_sign_leaves'][0].__setitem__(4,'NEG'),
  'shifted_index':lambda x: x['lenses'][2]['strict_sign_leaves'][20].__setitem__(3,999),
  'source_node_digest_altered':lambda x: x['lenses'][3]['source_input_hashes'].__setitem__('nodal_B_sha256','f'*64),
  'new_physical_claim':lambda x: x['claim_ceiling'].__setitem__('physical_provider_admitted',True),
  'new_empirical_claim':lambda x: x['claim_ceiling'].__setitem__('empirical_validation','VALIDATED'),
  'new_original_numeric_root_claim':lambda x: x['claim_ceiling'].__setitem__('original_full_continuum_root_uniqueness',True),
  'new_offgrid_source_claim':lambda x: x['claim_ceiling'].__setitem__('original_180_120_source_offgrid_numeric_error',True),
  'unsourced_extra_field':lambda x: x.__setitem__('true_theory_result',True),
  'altered_source_sha':lambda x: x.__setitem__('source_parent_zip_sha256','f'*64),
  'forged_root_derivative_cap':lambda x: x['lenses'][2].__setitem__('root_dH_strict_upper',{'num':'1','den':'1'}),
  'forged_strict_positive_bound':lambda x: x['lenses'][1].__setitem__('minimum_positive_cell_lower',{'num':'1000000000000000000000000000','den':'1'}),
  'forged_strict_negative_bound':lambda x: x['lenses'][0].__setitem__('maximum_negative_cell_upper',{'num':'-10000000000000000000000000000','den':'1'}),
  'fake_root_count':lambda x: x.__setitem__('strict_sign_leaf_count',1274),
  'shifted_root_guard':lambda x: x['lenses'][3].__setitem__('guard_left',{'num':'1','den':'1'}),
  'forged_refined_root':lambda x: x['lenses'][5].__setitem__('refined_root_left',{'num':'1','den':'1'}),
  'false_source_root':lambda x: x['lenses'][0].__setitem__('source_original_PL_root_exact',{'num':'2','den':'1'}),
  'wrong_lens_identity':lambda x: x['lenses'][4].__setitem__('lens','J0000+0000'),
  'edited_knot_error_claim':lambda x: x['lenses'][2].__setitem__('source_knot_difference_upper',{'num':'0','den':'1'}),
  'duplicate_cover_forgery':lambda x: x['lenses'][1]['strict_sign_leaves'].__setitem__(1,x['lenses'][1]['strict_sign_leaves'][0]),
  'wrong_controlling_model_id':lambda x: x.__setitem__('model','ORIGINAL_MARCH_CONTINUUM_ROOT_PROVED'),
 }
 for title,mutate in tests.items():
    v=copy.deepcopy(baseline);mutate(v)
    forged_hash=hashlib.sha256(val(v)).hexdigest() # Even fully rehashable outer wrappers are untrusted.
    try:ver.verify(v,models)
    except (AssertionError,ValueError,KeyError,TypeError,ZeroDivisionError,OverflowError) as ex:
       rejected.append({'case':title,'self_rehashed_outer_sha256':forged_hash,'rejected':True,'error':type(ex).__name__})
    else:raise RuntimeError('FORGED CLAIM ACCEPTED: '+title)
 # source-zip mutation even when a new ZIP digest is regenerated fails the independent external anchor
 old=ver.INPUT
 with tempfile.TemporaryDirectory() as td:
    copied=Path(td)/'repacked_original.zip';data=bytearray(old.read_bytes());data[-27]^=1;copied.write_bytes(data)
    ver.INPUT=copied
    try:
      try:ver.load_models()
      except (AssertionError,ValueError):
       rejected.append({'case':'source_zip_byte_changed','self_rehashed_outer_sha256':hashlib.sha256(data).hexdigest(),'rejected':True,'error':'SOURCE_SHA_LOCK'})
      else:raise RuntimeError('mutated source ZIP accepted')
    finally:ver.INPUT=old
 doc={'schema':'HIST001D_MARCH180_FROZEN_COMPONENT_COMPARATOR_ADVERSARIAL_QA_V1',
      'producer_sha256':ver.hashof(ver.PROOF.read_bytes()),'independent_verifier_source_sha256':ver.hashof(Path(ver.__file__).read_bytes()),
      'cases':rejected,'total_rejected':len(rejected),'all_rejected':True,
      'original_March_numeric_root_count_certified':False,'physical_provider_admitted':False,
      'empirical_validation':'NOT_ESTABLISHED'}
 out=val(doc);path=ROOT/'results'/'exact_defined_frozen180_comparator_qa.json';path.write_bytes(out)
 print('QA_REJECTED',len(rejected),'SHA256',hashlib.sha256(out).hexdigest())
if __name__=='__main__':run()
