"""Read-only source-locked historical March D120 angular nodes and source-knot results."""
import csv,hashlib,io,json,math,struct,zipfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'inputs/original_march180_parent_v1r1.zip'

def h(b):return hashlib.sha256(b).hexdigest()

def do():
 with zipfile.ZipFile(PARENT) as z:
  assert h(PARENT.read_bytes())=='0a643e81a9ab542dce8f158bc5135d94478d9145ab33036aae5813907f3655a1'
  data=z.read('inputs/original_source_46_frozen.zip'); assert h(data)=='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
  source=zipfile.ZipFile(io.BytesIO(data)); lock=json.loads(z.read('inputs/original_46plus3_lock.json'))
  for name,sha in lock['source_filenames_sha256'].items():assert h(source.read('swells_pack_v2/'+name))==sha
  for name,sha in lock['archived_negative_controls_sha256'].items(): assert h(z.read('inputs/negative_controls/'+name))==sha
  rows={r['lens_id']:r for r in csv.DictReader(io.StringIO(source.read('swells_pack_v2/cleaned/lens_set_A_run_fo_74bb5e.csv').decode()))}
  s={r['lens_id_norm']:r for r in csv.DictReader(io.StringIO(source.read('swells_pack_v2/raw_support/swells3_table3_structure.csv').decode()))}
  scale={r['lens_id']:r for r in csv.DictReader(io.StringIO(source.read('swells_pack_v2/cleaned/setA_scale_kpc_per_arcsec.csv').decode()))}
  theta=np.linspace(0.0,2*np.pi,120,endpoint=False)
  delta=np.diff(theta)
  w=np.zeros(120,dtype=np.float64);w[0]=delta[0]/2;w[-1]=delta[-1]/2;w[1:-1]=(delta[:-1]+delta[1:])/2
  assert len(w)==120 and np.all(w>=0)
  out=[]
  for lens_id,row in rows.items():
   md=10**float(row['logM_disc_chabrier_central']);dr=float(row['Re_disc_arcsec'])*float(scale[lens_id]['scale_kpc_per_arcsec']);rd=dr/1.67835
   qd=float(s[lens_id]['q_disc']);qb=float(s[lens_id]['q_bulge'])
   a=np.sqrt(np.cos(theta)**2+np.sin(theta)**2/qd**2)
   sig=md/(2*np.pi*qd*rd**2)
   original_rows=list(struct.iter_unpack('>8d',z.read('inputs/March180_source_nodes_'+lens_id.replace('+','p')+'.be64')))
   assert len(original_rows)==180
   Rs=np.array([v[0] for v in original_rows]); Ds=np.array([v[6] for v in original_rows])
   # Reconstruct the actual 120-angle source returned node results from unchanged mathematical formula and exact source floats.
   x=a[None,:]*Rs[:,None]/rd
   inner=rd**2/a[None,:]**2*(1-np.exp(-x)*(1+x))
   original_D_replay=sig*np.trapezoid(inner,theta,axis=1)
   assert np.array_equal(original_D_replay.view(np.uint64),Ds.view(np.uint64)), f'D120 historical node bytes differ: {lens_id}'
   data_bytes=b''.join(struct.pack('>ddd',float(th),float(wj),float(aj)) for th,wj,aj in zip(theta,w,a))
   path=ROOT/'inputs'/('disk120_frozen_'+lens_id.replace('+','p')+'.be64')
   path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data_bytes)
   out.append({'lens_id':lens_id,'qb_hex':qb.hex(),'qd_hex':qd.hex(),'Md_hex':md.hex(),'Rd_hex':rd.hex(),'sigma0_hex':sig.hex(),'angular_binary64_path':'inputs/'+path.name,'angular_node_sha256':h(data_bytes),'original_D_nodes_sha256':h(b''.join(struct.pack('>d',float(v)) for v in Ds)),'source_D_180_identical_binary64':True})
 doc={'schema':'HIST001D_D120_FROZEN_MARCH_ANGULAR_INPUT_CAPTURE_v1','source_composite_lock':lock['original_46plus3_composite_sha256'],'original_archive_sha256':h(data),'parent_archive_sha256':h(PARENT.read_bytes()),'lenses':out,'source_mutated':False,'new_D2d_11520_data_used':False,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
 (ROOT/'results').mkdir(exist_ok=True)
 (ROOT/'results/source120_capture.json').write_text(json.dumps(doc,sort_keys=True,separators=(',',':'))+'\n')
 print('SOURCE120_CAPTURE_PASS',len(out),h((ROOT/'results/source120_capture.json').read_bytes()))
if __name__=='__main__':do()
