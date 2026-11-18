#!/usr/bin/env python3
"""Constructive non-identifiability of a smooth physical radial density from nodes alone.
The bump does NOT satisfy the separately chosen smooth historical mass law.
"""
import io,zipfile,json,struct,hashlib
from fractions import Fraction as F
from pathlib import Path
from conservation_identity import bump_integral_coefficient
ROOT=Path(__file__).resolve().parent
PARENT='3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
SOURCE='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
def sha(b):return hashlib.sha256(b).hexdigest()

def build():
    data=(ROOT/'original_parent.zip').read_bytes();assert sha(data)==PARENT
    z=zipfile.ZipFile(io.BytesIO(data))
    for _ in range(3):z=zipfile.ZipFile(io.BytesIO(z.read([x for x in z.namelist() if x.endswith('.zip')][0])))
    lock=json.loads(z.read('inputs/original_46plus3_lock.json'))
    assert lock['original_46plus3_composite_sha256']==SOURCE
    orig=zipfile.ZipFile(io.BytesIO(z.read('inputs/original_source_46_frozen.zip')))
    for name,h in lock['source_filenames_sha256'].items():assert sha(orig.read('swells_pack_v2/'+name))==h
    for name,h in lock['archived_negative_controls_sha256'].items():assert sha(z.read('inputs/negative_controls/'+name))==h
    c=json.loads(z.read('results/source180_capture.json'))['lenses'][0]
    rows=list(struct.iter_unpack('>8d',z.read('inputs/'+c['node_file'])))
    assert len(rows)==180 and rows[0][0]>0
    a,b=F.from_float(rows[0][0]),F.from_float(rows[1][0])
    C=F.from_float(float.fromhex('0x1.921fb54442d18p+3'))
    cf=bump_integral_coefficient(a,b,C)
    assert cf>0
    target=F(1_000_000_000)
    amplitude=target/cf
    assert amplitude>0 and amplitude*cf==target
    # The polynomial bump ((r-a)*(b-r))^4 has support (a,b),
    # vanishes with first three derivatives at endpoints and every source node,
    # and adds target mass exactly when A>=b.
    data={
      'schema':'HIST001D_SOURCE_NODE_ONLY_SMOOTH_DENSITY_NONIDENTIFIABILITY_WITNESS_V1',
      'original_source_sha256':SOURCE,'original_captured_source_node_sha256':c['node_sha256'],
      'source_lens_id':c['lens_id'],
      'source_first_gap_exact_dyadic':[str(a),str(b)],
      'bump_C3_nonnegative_support_only_first_node_gap':True,
      'bump_definition':'lambda * ((r-a)*(b-r))^4 on (a,b); zero elsewhere',
      'bump_projected_K180_node_values_unchanged':True,
      'target_aperture':'A>=b (including original A=120 kpc)',
      'continuum_projected_mass_difference_exact_Msun':str(amplitude*cf),
      'unit_amplitude_projected_mass_coefficient_fraction':str(cf),
      'chosen_lambda_exact_fraction':str(amplitude),
      'node_only_data_cannot_certify_finite_uniform_continuum_projection_upper':True,
      'selected_smooth_Msh_law_preserved_by_bump':False,
      'physical_density_source_admitted':False,
      'original_continuous_root_theorem_proved':False,
      'empirical_validation':'NOT_ESTABLISHED'
    }
    out=ROOT/'node_only_nonidentifiability.json';out.write_bytes((json.dumps(data,indent=2,sort_keys=True)+'\n').encode())
    print('WITNESS exact mass addition',amplitude*cf,'first gap [float]',float(a),float(b),'sha',sha(out.read_bytes()))
    return data
if __name__=='__main__':build()
