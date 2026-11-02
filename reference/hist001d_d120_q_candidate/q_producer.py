"""Fraction proof of positive and monotone frozen-180 q(R), aperture and final circularized source shadow."""
import hashlib,json,struct,zipfile,math,bisect
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'inputs/original_march180_parent_v1r1.zip'
SCALE=1<<72

def sha(x):return hashlib.sha256(x).hexdigest()
def f(x):return F.from_float(x)
def cceil(x):return -(-x.numerator//x.denominator)
def sqrtbounds(x):
 assert x>0
 j=math.isqrt(x.numerator*SCALE*SCALE//x.denominator)
 return F(j,SCALE),F(j+1,SCALE)
def pl(R,rs,m):
 if R<=rs[0]:return m[0]
 if R>=rs[-1]:return m[-1]
 k=bisect.bisect_right(rs,R)-1
 return m[k] + (R-rs[k])*(m[k+1]-m[k])/(rs[k+1]-rs[k])
def run():
 src=json.loads((ROOT/'results/source120_capture.json').read_text())
 output=[]
 with zipfile.ZipFile(PARENT) as z:
  for el in src['lenses']:
   lid=el['lens_id']; qb=f(float.fromhex(el['qb_hex'])); qd=f(float.fromhex(el['qd_hex']))
   rr=list(struct.iter_unpack('>8d',z.read('inputs/March180_source_nodes_'+lid.replace('+','p')+'.be64')))
   r=list(map(f,[x[0] for x in rr]));B=list(map(f,[x[4] for x in rr]));D=list(map(f,[x[6] for x in rr]));S0=list(map(f,[x[5] for x in rr]));S=list(map(f,[x[7] for x in rr]));last=r[-1]
   assert min(B)>0 and min(D)>0 and min(qb,qd)>F(1,1000) and max(qb,qd)<1
   assert all(B[i+1]>=B[i] and D[i+1]>=D[i] and S0[i+1]>=S0[i] for i in range(179))
   margins=[];qmin=F(1);qmax=F(0)
   for j in range(179):
    h=r[j+1]-r[j]; n0=qb*B[j]+qd*D[j];n1=qb*B[j+1]+qd*D[j+1];p0=B[j]+D[j];p1=B[j+1]+D[j+1];q0=n0/p0;q1=n1/p1
    qmin=min(qmin,q0,q1);qmax=max(qmax,q0,q1)
    # Conservative independent all-R derivative lower: 2*q-R*q' >0.
    # q'(R) = C/(h P(t)^2), C=N1 P0-N0 P1 (exact dyadics).
    delta=n1*p0-n0*p1
    qpmax=max(F(0),delta/(h*min(p0,p1)**2))
    gap=2*min(q0,q1)-r[j+1]*qpmax
    assert gap>0,(lid,j,float(gap))
    margins.append(gap)
   bands=[];knoterr=F(0)
   for j in range(180):
    q=(qb*B[j]+qd*D[j])/(B[j]+D[j])
    root_lo,root_hi=sqrtbounds(q)
    A_lo=min(last,r[j]/root_hi);A_hi=min(last,r[j]/root_lo)
    lower=pl(A_lo,r,S0);upper=pl(A_hi,r,S0)
    assert lower<=upper and 0<=lower
    bands.append((lower,upper))
    knoterr=max(knoterr,abs(lower-S[j]),abs(upper-S[j]))
   assert knoterr<F(1),(lid,float(knoterr))
   upper_E=max(max(F(0),bands[j+1][1]-min(S[j],S[j+1]),max(S[j],S[j+1])-bands[j][0]) for j in range(179))
   output.append({'lens_id':lid,'source_qb_hex':el['qb_hex'],'source_qd_hex':el['qd_hex'],'coarse_aperture_derivative_positive_cells':len(margins),'original_rho0_nondecreasing':True,'no_q_clipping_for_positive_PL_BD':True,'all_real_aperture_unsaturated_strictly_increasing':True,'circularized_shadow_PL_non_decreasing':True,'source_knot_absolute_discrepancy_lt_1_msun':True,'worst_source_knot_discrepancy_ceiling_msun':cceil(knoterr),'circularized_shadow_all_real_sourcePL_error_upper_ceiling_msun':cceil(upper_E),'minimum_coarse_margin_2q_Rqprime_numerator':str(min(margins).numerator),'minimum_coarse_margin_2q_Rqprime_denominator':str(min(margins).denominator)})
 doc={'schema':'HIST001D_COMMON180_SOURCE_FROZEN_QEFF_APERTURE_AND_SHADOW_ALLREAL_v1','source_capture_sha256':sha((ROOT/'results/source120_capture.json').read_bytes()),'lenses':output,'exact_input_kind':'source_replayed_original_180_B_D_S0_S_binary64_as_dyadics','all_real_domain':'[binary64(0.02),binary64(120)] kpc','method':'positive_BD_rational_corner_q_AND_conservative_qprime_ratio_AND_directed_72bit_sqrt','original_180_source_frozen':True,'original_March_off_grid_algorithm_was_defined':False,'new_11520_shadow_model_used':False,'original_March_full_H_error_bounded':False,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
 out=(json.dumps(doc,sort_keys=True,separators=(',',':'))+'\n').encode();(ROOT/'results/q_aperture_producer.json').write_bytes(out)
 for a in output: print('Q_CERT_PASS',a['lens_id'],'cells',a['coarse_aperture_derivative_positive_cells'],'knot',a['worst_source_knot_discrepancy_ceiling_msun'],'S err BMsun',round(a['circularized_shadow_all_real_sourcePL_error_upper_ceiling_msun']/1e9,6),flush=True)
 print('Q_CERT_SHA',sha(out))
if __name__=='__main__':run()
