"""Source-locked materialization of previously verified interval inputs only (protected)."""
import sys,json,hashlib
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'reference/hist001d_k180_targeted_candidate'))
from targeted_refine import original
import signed_affine_producer as sp
OUT=ROOT/'results'

def data_for(j):
 lens,nodehash,p,initial=original(j)
 rec=json.loads((ROOT/'results'/f'targeted_lens_{j}.json').read_text())
 pts={}
 for q in initial:pts[q.a]=q.pa;pts[q.b]=q.pb
 def interval(q):return [str(q.lower()),str(q.upper())]
 for q in rec['split_history']:
  a,b,mid=F(q['a']),F(q['b']),F(q['mid'])
  if mid!=(a+b)/2:raise ValueError('split midpoint')
  pts[mid]={'M':sp.X(F(q['M'][0]),F(q['M'][1])),
            'Mp':sp.X(F(q['Mp'][0]),F(q['Mp'][1]))}
 leaves=[]
 for q in rec['leaves']:
  a,b=F(q['a']),F(q['b']);pa,pb=pts[a],pts[b]
  leaves.append(dict(a=str(a),b=str(b),M_a=interval(pa['M']),M_b=interval(pb['M']),
                     Mp_a=interval(pa['Mp']),Mp_b=interval(pb['Mp']),C=int(q['C_integer_Msecond_abs']),origin=int(q['origin'])))
 _,_,nodes,_=sp.endpoints(j)
 obj={'schema':'HIST001D_SOURCE_LOCKED_MSTAR_KNOT_AUDIT_INPUTS_V1','lens':lens,
  'original_180_node_sha256':nodehash,'protected_parent_sha256':'23251d6c5a153e8cb149143f7fcf25f02c21097e6f625b3c46fdb9645fef96e1',
  'source_46plus3_sha256':'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a',
  'A_band':rec['A_band'],'Peano_symmetric_exact':rec['E_symmetric_exact'],
  'nodes':[{'r':str(r),'w':str(w),'Mp':interval(mp)} for r,w,mp in nodes],
  'leaves':leaves,'selected_mathematical_mass_only':True,
  'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
 assert len(obj['nodes'])==180 and len(leaves)==rec['refined_radial_panels']
 path=OUT/f'inputs_lens_{j}.json';path.write_text(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n')
 print('INPUT',lens,len(leaves),hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--lens',type=int,choices=range(6))
 args=parser.parse_args()
 for j in ([args.lens] if args.lens is not None else range(6)):data_for(j)
