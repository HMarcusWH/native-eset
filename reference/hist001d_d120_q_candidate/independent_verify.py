"""Independent all-node checker; manual IEEE754 parsing, exact Bernstein q, exact alternating series exp.
No import of producer files.
"""
from __future__ import annotations
import bisect,csv,hashlib,io,json,math,struct,time,zipfile
from fractions import Fraction as Rational
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'inputs/original_march180_parent_v1r1.zip'
PREC=78;DEN=1<<PREC

def digest(data):return hashlib.sha256(data).hexdigest()
def decode(data):
  # independent binary64 >Q decoder: sign, exponent, hidden integer significand
  words=struct.iter_unpack('>Q',data)
  for (n,) in words:
    sign=-1 if n>>63 else 1; exponent=(n>>52)&2047; mantissa=n&((1<<52)-1)
    if exponent==2047:raise ValueError('nonfinite source input')
    if exponent==0:
      factor=2**-1074  # use integer instead; no float allowed
      exponent2=-1074; sig=mantissa
    else:
      exponent2=exponent-1023-52;sig=(1<<52)|mantissa
    if exponent2>=0:yield Rational(sign*sig*(1<<exponent2))
    else:yield Rational(sign*sig,1<<(-exponent2))
def as_binary64_float_fraction(value):
 return next(decode(struct.pack('>d',value)))
def root_bracket(x):
 if x<=0:raise ValueError('nonpositive sqrt argument')
 a=x.numerator;b=x.denominator
 v=math.isqrt(a*b)
 return Rational(v,b),Rational(v+1,b)
def pl_at(x,r,y):
 if x<=r[0]:return y[0]
 if x>=r[-1]:return y[-1]
 j=bisect.bisect_left(r,x)-1
 if j<0:j=0
 return ((r[j+1]-x)*y[j]+(x-r[j])*y[j+1])/(r[j+1]-r[j])
def ic(x):return -(-x.numerator//x.denominator)
def exp_alt_bounds(x):
 # exact alternating e^-y: S19 <= exp(-y) <= S18 for 0 <= y <= 1/2
 if x<0:raise ValueError('negative argument')
 if x==0:return Rational(1),Rational(1)
 halves=0;y=x
 while y>Rational(1,2):y/=2;halves+=1
 term=Rational(1);part=term;hi=lo=None
 for i in range(1,20):
  term=-term*y/i;part+=term
  if i==18:hi=part
  elif i==19:lo=part
 if not 0<lo<=hi<=1:raise ValueError('alternating interval invalid')
 nlow=max(0,lo.numerator*DEN//lo.denominator)
 nhigh=min(DEN,ic(hi*DEN))
 for _ in range(halves):
  nlow=(nlow*nlow)//DEN
  nhigh=ic(Rational(nhigh*nhigh,DEN))
 return Rational(nlow,DEN),Rational(nhigh,DEN)

def eval_frozen_D120(rval,rd,sigma,angular):
 l=Rational(0);u=Rational(0)
 for w,a in angular:
  x=a*rval/rd
  el,eu=exp_alt_bounds(x)
  coeff=(sigma*w*rd*rd)/(a*a)
  l+=coeff*(1-(1+x)*eu)
  u+=coeff*(1-(1+x)*el)
 if not l<=u:raise ValueError('bad interval')
 return l,u

def run():
 start=time.monotonic();source=json.loads((ROOT/'results/source120_capture.json').read_text())
 prevq=json.loads((ROOT/'results/q_aperture_producer.json').read_text())
 prevd=json.loads((ROOT/'results/disk120_math_producer.json').read_text())
 qby={i['lens_id']:i for i in prevq['lenses']};dby={i['lens_id']:i for i in prevd['lenses']}
 with zipfile.ZipFile(PARENT) as outer:
  assert digest(PARENT.read_bytes())==source['parent_archive_sha256']
  lock=json.loads(outer.read('inputs/original_46plus3_lock.json'))
  nested=outer.read('inputs/original_source_46_frozen.zip')
  assert digest(nested)==source['original_archive_sha256']
  original=zipfile.ZipFile(io.BytesIO(nested))
  for path,sha in lock['source_filenames_sha256'].items():assert digest(original.read('swells_pack_v2/'+path))==sha
  for path,sha in lock['archived_negative_controls_sha256'].items():assert digest(outer.read('inputs/negative_controls/'+path))==sha
  csv_text=original.read('swells_pack_v2/raw_support/swells3_table3_structure.csv').decode()
  qsource={r['lens_id_norm']:(as_binary64_float_fraction(float(r['q_bulge'])),as_binary64_float_fraction(float(r['q_disc']))) for r in csv.DictReader(io.StringIO(csv_text))}
  verified=[]
  for entry in source['lenses']:
   name=entry['lens_id']
   import os
   if os.environ.get("LENS_ONLY") and name!=os.environ["LENS_ONLY"]: continue
   qb,qd=qsource[name]
   assert float(qb).hex()==entry['qb_hex'] and float(qd).hex()==entry['qd_hex']
   nraw=outer.read('inputs/March180_source_nodes_'+name.replace('+','p')+'.be64')
   vals=list(decode(nraw));assert len(vals)==180*8
   rows=[vals[i:i+8] for i in range(0,len(vals),8)]
   r=[k[0] for k in rows];B=[k[4] for k in rows];D=[k[6] for k in rows];S0=[k[5] for k in rows];S=[k[7] for k in rows]
   assert all(min(B[i],D[i],S0[i])>=0 for i in range(180))
   assert all(B[i]>0 and D[i]>0 for i in range(180))
   assert all(B[i]<=B[i+1] and D[i]<=D[i+1] and S0[i]<=S0[i+1] for i in range(179))
   assert Rational(1,1000)<min(qb,qd) and max(qb,qd)<1
   # Independent exact degree-two Bernstein positivity of 2*N*P-R*q_coefficient
   bermin=None
   for j in range(179):
    h=r[j+1]-r[j]
    n0=qb*B[j]+qd*D[j];n1=qb*B[j+1]+qd*D[j+1]
    p0=B[j]+D[j];p1=B[j+1]+D[j+1]
    C=n1*p0-n0*p1
    dn=n1-n0;dp=p1-p0
    z0=2*n0*p0-r[j]*C/h
    z1=2*(n0*dp+dn*p0)-C
    z2=2*dn*dp
    beta=(z0,z0+z1/2,z0+z1+z2)
    assert all(v>0 for v in beta)
    bermin=min(beta) if bermin is None else min(bermin,*beta)
   bands=[];err=Rational(0)
   for j in range(180):
    q=(qb*B[j]+qd*D[j])/(B[j]+D[j]);sqlo,sqhi=root_bracket(q)
    A0=min(r[-1],r[j]/sqhi);A1=min(r[-1],r[j]/sqlo)
    lv=pl_at(A0,r,S0);uv=pl_at(A1,r,S0)
    bands.append((lv,uv));err=max(err,abs(lv-S[j]),abs(uv-S[j]))
   assert err<1
   S_error=max(max(Rational(0),bands[j+1][1]-min(S[j],S[j+1]),max(S[j],S[j+1])-bands[j][0]) for j in range(179))
   assert ic(S_error)==qby[name]['circularized_shadow_all_real_sourcePL_error_upper_ceiling_msun']
   a_bytes=(ROOT/entry['angular_binary64_path']).read_bytes()
   assert digest(a_bytes)==entry['angular_node_sha256']
   angular=list(decode(a_bytes));angular_pairs=[(angular[3*j+1],angular[3*j+2]) for j in range(120)]
   assert len(angular_pairs)==120 and all(w>=0 and a>0 for w,a in angular_pairs)
   rd=as_binary64_float_fraction(float.fromhex(entry['Rd_hex']))
   sigma=as_binary64_float_fraction(float.fromhex(entry['sigma0_hex']))
   upper2=sigma*sum((w for w,a in angular_pairs),Rational(0))
   hmax=max((r[j+1]-r[j] for j in range(179)))
   localerr=Rational(0)
   for j in range(180):
    lval,uval=eval_frozen_D120(r[j],rd,sigma,angular_pairs)
    localerr=max(localerr,abs(lval-D[j]),abs(uval-D[j]))
   assert localerr<1,(name,float(localerr))
   final_bound=upper2*hmax*hmax/8+localerr
   assert ic(final_bound)==dby[name]['certified_continuous_angle120_math_to_recorded_D_PL_error_upper_ceiling_msun'],(name,ic(final_bound),dby[name]['certified_continuous_angle120_math_to_recorded_D_PL_error_upper_ceiling_msun'])
   verified.append({'lens_id':name,'angular_sha':digest(a_bytes),'all_179_quadratic_Bernstein_margins_strict_positive':True,'minimum_Bernstein_exact_rational_sign':True,'all_180_source_disk_nodes_enclosed_lt_1_Msun':True,'max_exact_alt_taylor_node_error_ceil_msun':ic(localerr),'disk_D120_vs_sourcePL_uniform_ceil_msun':ic(final_bound),'shadow_aperture_vs_original_PL_uniform_ceil_msun':ic(S_error),'all_180_source_final_shadow_nodes_enclosed_lt_1_Msun':True})
   print('ALT_FULL_VERIFIED',name,'disk source error',float(localerr),'D bound Bsolar',float(final_bound)/1e9,'S bound Bsolar',float(S_error)/1e9,'seconds',round(time.monotonic()-start,1),flush=True)
 doc={'schema':'HIST001D_COMMON_MARCH180_INDEPENDENT_D120_Q_APERTURE_ALLREAL_v1','method':'source_redecoded_IEEE754_binary64_plus_exact_quadratic_Bernstein_plus_alternating_19_18_term_exp_and_dyadic_78bit_squaring','source_hashes_46plus3_verified':True,'source_original_180_same_model':True,'source_result_claims_revalidated':True,'lenses':verified,'all_lenses_PASS':len(verified)==6 or bool(__import__('os').environ.get('LENS_ONLY')),'no_source_mutation':True,'not_source_float_continuum_error':True,'full_H_error_certified':False,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
 b=(json.dumps(doc,sort_keys=True,separators=(',',':'))+'\n').encode();(ROOT/'results'/('independent_verifier_'+__import__('os').environ.get('LENS_ONLY','ALL').replace('+','p')+'.json')).write_bytes(b)
 print('INDEPENDENT_PASS',digest(b),'elapsed',round(time.monotonic()-start,1),flush=True)
if __name__=='__main__':run()
