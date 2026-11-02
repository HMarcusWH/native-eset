"""Exact-dyadic algebra with Decimal.exp correctly-rounded explicit ulp enclosure.
Mathematical frozen-original-angle D120; NOT exact source floating evaluation.
"""
import math,json,zipfile,struct,hashlib,time
from fractions import Fraction as F
from pathlib import Path
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'inputs/original_march180_parent_v1r1.zip'
PREC=58

def sha(b):return hashlib.sha256(b).hexdigest()
def ff(h):return F.from_float(float.fromhex(h))
def decimal_exact_interval(x):
 with localcontext() as ctx:
  ctx.prec=PREC;ctx.rounding=ROUND_FLOOR
  lo=Decimal(x.numerator)/Decimal(x.denominator)
 with localcontext() as ctx:
  ctx.prec=PREC;ctx.rounding=ROUND_CEILING
  hi=Decimal(x.numerator)/Decimal(x.denominator)
 return lo,hi

def exp_negative_interval(x):
 assert x>=0
 if x==0:return F(1),F(1)
 lo,hi=decimal_exact_interval(x)
 with localcontext() as ctx:
  ctx.prec=PREC;ctx.rounding='ROUND_HALF_EVEN'
  el=(-hi).exp();eu=(-lo).exp()
  ul=Decimal(1).scaleb(el.adjusted()-PREC+1)
  uu=Decimal(1).scaleb(eu.adjusted()-PREC+1)
  return F(max(Decimal(0),el-ul)),F(eu+uu)

def ideal_disk_at_r(R,sig,rd,angles):
 lo=F(0);hi=F(0)
 rd2=rd*rd
 for w,a in angles:
  x=a*R/rd;elo,ehi=exp_negative_interval(x)
  coef=sig*w*rd2/(a*a)
  lo+=coef*(1-(1+x)*ehi)
  hi+=coef*(1-(1+x)*elo)
 assert lo<=hi and hi>0
 return lo,hi

def ceilF(x):return -(-x.numerator//x.denominator)
def out():
 source=json.loads((ROOT/'results/source120_capture.json').read_text())
 with zipfile.ZipFile(PARENT) as z:
  doc=[]
  for lens in source['lenses']:
   l=lens['lens_id'];s=ff(lens['Rd_hex']);sig=ff(lens['sigma0_hex']);Md=ff(lens['Md_hex']);a_data=(ROOT/lens['angular_binary64_path']).read_bytes()
   assert sha(a_data)==lens['angular_node_sha256']
   angles=[(F.from_float(w),F.from_float(a)) for _,w,a in struct.iter_unpack('>ddd',a_data)]
   assert len(angles)==120 and all(w>=0 and a>0 for w,a in angles)
   arr=list(struct.iter_unpack('>8d',z.read('inputs/March180_source_nodes_'+l.replace('+','p')+'.be64')))
   r=[F.from_float(v[0]) for v in arr];d=[F.from_float(v[6]) for v in arr]
   assert all(r[i]<r[i+1] for i in range(179))
   assert all(d[i]>0 for i in range(180))
   cap= sig*sum(w for w,a in angles)
   hmax=max(r[i+1]-r[i] for i in range(179))
   theory_error=cap*hmax*hmax/8
   worst=F(0);minsource_gap=F(10**40)
   t=time.time()
   for i,(R,ds) in enumerate(zip(r,d)):
    low,up=ideal_disk_at_r(R,sig,s,angles)
    diff=max(abs(low-ds),abs(up-ds))
    worst=max(diff,worst)
    minsource_gap=min(minsource_gap,ds-low,up-ds)
    if i in (0,30,90,179): print('DISK_NODE_CHECK',l,i,'interval_diff Msolar',float(diff),flush=True)
   assert worst<F(1),f'disk source-node discrepancy >=1 Msun for {l}: {float(worst)}'
   print('DISK_DONE',l,'knot err max',float(worst),'C2',float(cap),'interpol err GMsun',float(theory_error)/1e9,'elapsed',round(time.time()-t,2),flush=True)
   doc.append({'lens_id':l,'angular_source_sha256':lens['angular_node_sha256'],'original_D_sha256':lens['original_D_nodes_sha256'],'disk_evaluation_exact_model':'SOURCE_FROZEN_119_TRAPEZOID_SEGMENT_WEIGHTS_AND_A_FLOATS_MATH_EXP','angular_node_count':120,'original_disk_180_source_nodes_are_binary64_replayed':True,'disk_model_source_nodes_enclosed_to_lt_1_Msun':True,'certified_knot_error_integer_ceiling_msun':ceilF(worst),'certified_continuous_angle120_math_to_recorded_D_PL_error_upper_ceiling_msun':ceilF(theory_error+worst),'pure_interpolation_curvature_error_upper_msun':str(theory_error.numerator)+'/'+str(theory_error.denominator),'mathematical_C2_upper_msun_per_kpc2':str(cap.numerator)+'/'+str(cap.denominator),'numeric_error_absolute_vs_original_D120_same_floats_plus_interpolation_only':False,'max_r_step':str(hmax.numerator)+'/'+str(hmax.denominator)})
 rootdoc={'schema':'HIST001D_D120_ORIGINAL_FROZEN_ANGULAR_SOURCE_MATH_INTERPOLATION_ENCLOSURE_v1','lenses':doc,'method':'exact_rationals_and_decimal_exp_correctly_rounded_with_1ulp_outward_guard','source_capture_sha256':sha((ROOT/'results/source120_capture.json').read_bytes()),'source_finite_N180':True,'Ntheta':120,'omitted_last_angle_gap_is_retained':True,'full_azimuth_angular_integral_certified':False,'all_R_disk_math_to_recorded_node_PL_bound':True,'actual_original_March_continuous_solver_error_certified':False,'D2d_11520_data_used':False,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
 out=(json.dumps(rootdoc,sort_keys=True,separators=(',',':'))+'\n').encode()
 (ROOT/'results/disk120_math_producer.json').write_bytes(out)
 print('DISK_MATH_CERT_PASS',sha(out))

if __name__=='__main__':out()
