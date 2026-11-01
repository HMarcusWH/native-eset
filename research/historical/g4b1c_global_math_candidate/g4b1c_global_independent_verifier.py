#!/usr/bin/env python3
"""Independent exact-Q all-real finite-proxy root-count crosscheck.

DOES NOT import producer, source adapter, mathematical lib or their witnesses as
computed authority; independently decodes frozen source ZIP and original 46+3,
rebuilds source nodal integrals using antiderivatives (not Simpson), uses cubic
radial/t meshes (not quadratic), separate Taylor/π bounds, and recomputes all
positive-H and negative-Hprime leaf enclosures. Still mathematical candidate.
"""
from __future__ import annotations
import sys,hashlib,io,json,zipfile,struct,math,bisect
from fractions import Fraction as Q
from pathlib import Path
from functools import lru_cache
ROOT=Path(__file__).resolve().parent
EXPECTED_PRODUCER_SHA='97f2146f48c2c7fa3af5d8cb021f68fef0e28e5ce5544d3113e3166c43b53b99'
SOURCE_SHA={
 'source_nodal.zip':'804fd8e26b208c9837638ceee90998843e29b484aa3e5ca794dd5d81b3988973',
 'prepeak_v5.json':'f499ee992b762f6da5e774d95b00588e96cf9ee17e4bcaa4bda7ad30628b5963',
 'narrow_signs_v1.json':'5f74321ad4140640e56bf0a9a3147817879c52c40f4e91eab6487d0b61c36899',
 'narrow_uniqueness_v1.json':'2d5d797329d9dd77c4bd3e5c5c3d385edf79e1147f332554d70a735d87eb1d06',
 'narrow_uniqueness_independent_v1.json':'6b47c9a013f522be52ffe4afad09a03eb797ddb2b7fffaafbca29996ec82ef84',
 'inner_v3.json':'8a3f7da5288080aa1e575e31cbb72dd114dc1668ad258639674916307bfed0ac',
 'outer_v4.json':'c8e4af053bc4765dd119337ab5da302cd42a73d9eb52015909ccceb68dffe5ac'}
IDS=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')
RMIN=Q.from_float(.02);RMAX=Q(120)
MAGIC=b'native-eset-g4b1b-exact-binary64-nodal-pairs-v1\0'
PARAMS=('bulge_mass_msun','hernquist_a_kpc','disc_mass_msun','disc_scale_kpc','bulge_q','disc_q')

def bad(message):raise ValueError(message)
def sha(x):return hashlib.sha256(x).hexdigest()
def f(x):
 if set(x)!={'num','den'}:bad('noncanonical rational keyset')
 a,b=x['num'],x['den'];v=Q(int(a),int(b))
 if str(v.numerator)!=a or str(v.denominator)!=b:bad('noncanonical rational digits')
 return v
def pq(x):return {'num':str(x.numerator),'den':str(x.denominator)}
def flo(x,n=1):return Q((x.numerator*n)//x.denominator,n)
def cei(x,n=1):return -flo(-x,n)

def arctan_inv(q,terms):
 acc=Q(0); power=Q(1,q)
 for k in range(terms):
  acc+=(power/(2*k+1))*(1 if k%2==0 else -1)
  power/=q*q
 return acc
PILO=16*arctan_inv(5,10)-4*arctan_inv(239,9)
PIHI=16*arctan_inv(5,9)-4*arctan_inv(239,10)
if not (Q(3)<PILO<PIHI<Q(22,7)):bad('Machin pi bounds')

# 44-bit rational directed sqrt; producer used 34-bit Q.
SCALE=1<<44
def sqrt_lower(value):
 if value<0:bad('negative sqrt input')
 digit=math.isqrt((value.numerator*SCALE*SCALE)//value.denominator)
 return Q(digit,SCALE)
def sqrt_upper(value):
 v=sqrt_lower(value);return v if v*v==value else v+Q(1,SCALE)

def exp_bounds(x):
 """19th/20th alternating Taylor on <=1/16, explicit directed 44-bit squaring."""
 if x<0:bad('negative exponent')
 if x==0:return Q(1),Q(1)
 t=x;k=0
 while t>Q(1,16):t/=2;k+=1
 partial=term=Q(1);lower=None
 for i in range(1,21):
  term*= -t/i;partial+=term
  if i==19:lower=partial
 lower=flo(lower,SCALE);upper=cei(partial,SCALE)
 if not 0<lower<=upper<=1:bad('alternating exponential bounds invalid')
 for _ in range(k):
  lower=flo(lower*lower,SCALE);upper=cei(upper*upper,SCALE)
 return lower,upper

def source_decode():
 for fn,expected in SOURCE_SHA.items():
  if sha((ROOT/'input'/fn).read_bytes())!=expected:bad('SHA source/proof mismatch '+fn)
 def load(fn):return json.loads((ROOT/'input'/fn).read_bytes())
 pre=load('prepeak_v5.json');sign=load('narrow_signs_v1.json');narrow=load('narrow_uniqueness_v1.json');ind=load('narrow_uniqueness_independent_v1.json');inner=load('inner_v3.json');outer=load('outer_v4.json')
 with zipfile.ZipFile(ROOT/'input/source_nodal.zip') as z:
  if z.testzip() is not None:bad('original zip bad CRC')
  lock=json.loads(z.read('evidence/source_lock_46plus3.json'))
  ledger=json.loads(z.read('evidence/six_lens_nodal_provenance.json'))
  if sha(z.read('evidence/six_lens_nodal_provenance.json'))!='4b5746051babaadb0ad61aa61a857ff78a61fd6ac9676cd5513d51273c597701':bad('external ledger SHA changed')
  raw=z.read('source/dma_swells_benchmark_pack_v2_frozen_exact.zip')
  if sha(raw)!='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e':bad('original source zip changed')
  if lock['original_46plus3_composite_sha256']!='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a':bad('original source SHA authority')
  if len(lock['source_filenames_sha256'])!=46 or len(lock['archived_negative_controls_sha256'])!=3:bad('46+3 original inventory')
  with zipfile.ZipFile(io.BytesIO(raw)) as o:
   for path,dig in lock['source_filenames_sha256'].items():
    if sha(o.read('swells_pack_v2/'+path))!=dig:bad('original 46 file SHA changed')
  for path,dig in lock['archived_negative_controls_sha256'].items():
   if sha(z.read('negative_controls/'+path))!=dig:bad('3 original negatives SHA changed')
  if ledger['lens_ids']!=list(IDS) or len(ledger['lens_records'])!=6:bad('source lens order')
  records=[]
  for lid,row in zip(IDS,ledger['lens_records']):
   if row['lens_id']!=lid:bad('lens row drift')
   bytes_=z.read('nodes/'+lid.replace('+','p')+'.radius_density_interleaved_be64.bin')
   if len(bytes_)!=184320:bad('node record count')
   digest=sha(MAGIC+struct.pack('>I',11520)+bytes_)
   if digest!=row['exact_d2d_source_11520_nodal_digest']:bad('source node exact SHA changed')
   pairs=list(struct.iter_unpack('>dd',bytes_))
   r=[Q.from_float(t[0]) for t in pairs];d=[Q.from_float(t[1]) for t in pairs]
   if len(r)!=11520 or r[0]!=RMIN or r[-1]!=RMAX or any(r[i]>=r[i+1] or d[i]<0 for i in range(11519)) or d[-1]<0:bad('source nodes not ordered/positive')
   scalars={k:Q.from_float(float.fromhex(row['original_baryon_scales_and_q_binary64_hex'][k])) for k in PARAMS}
   records.append({'id':lid,'r':r,'d':d,'s':scalars,'digest':digest})
 return records,pre,sign,narrow,ind,inner,outer

class ExactProfile:
 def __init__(self,record):
  self.r=record['r'];self.d=record['d'];self.p=record['s'];self.pk_idx=self.d.index(max(self.d))
  self.cumulative=[Q(0)]
  for j in range(len(self.r)-1):
   self.cumulative.append(self.cumulative[-1]+self.segment(j,self.r[j],self.r[j+1]))
  if any(self.d[i]>=self.d[i+1] for i in range(self.pk_idx)) or any(self.d[i]<=self.d[i+1] for i in range(self.pk_idx,len(self.d)-1)):
   bad('source profile 3D uniqueness sign not reconfirmed')
 @staticmethod
 def poly_int(a,b,ma,intercept):return ma*(b**4-a**4)/4+intercept*(b**3-a**3)/3
 def segment(self,i,a,b):
  r0,r1=self.r[i:i+2];v0,v1=self.d[i:i+2]
  slope=(v1-v0)/(r1-r0)
  return self.poly_int(a,b,slope,v0-slope*r0)
 @lru_cache(maxsize=10000)
 def interior(self,t):
  if t<=RMIN:return Q(0)
  if t>=RMAX:return self.cumulative[-1]
  i=bisect.bisect_right(self.r,t)-1
  return self.cumulative[i]+self.segment(i,self.r[i],t)
 def rho_at(self,r):
  if r<RMIN or r>RMAX:return Q(0)
  if r==RMAX:return self.d[-1]
  i=bisect.bisect_right(self.r,r)-1
  return self.d[i]+(self.d[i+1]-self.d[i])*(r-self.r[i])/(self.r[i+1]-self.r[i])
 def rho_max(self,a,b):
  if a>RMAX:return Q(0)
  a=max(RMIN,a);b=min(RMAX,b)
  if b<a:return Q(0)
  y=max(self.rho_at(a),self.rho_at(b))
  peak=self.r[self.pk_idx]
  if a<=peak<=b:y=max(y,self.d[self.pk_idx])
  return y

class Alt:
 def __init__(self,profile,sigma0,sigma1):
  self.pro=profile;self.pp=profile.p;self.sig0=sigma0;self.sig1=sigma1
  self.bcache={};self.dcache={};self.scache={}
 def bulge_primitive(self,t):
  p=self.pp;M,a=p['bulge_mass_msun'],p['hernquist_a_kpc']
  return M*(t*t/(t+a)**2-RMIN*RMIN/(RMIN+a)**2)
 def cylinder_interval(self,A,cumulative,n):
  if A==RMAX:return cumulative(RMAX),cumulative(RMAX)
  if not RMIN<A<RMAX:bad('invalid cylinder aperture')
  inside=cumulative(A);lo=hi=inside
  for j in range(n):
   u=A+(RMAX-A)*Q(j**3,n**3);v=A+(RMAX-A)*Q((j+1)**3,n**3)
   moment=cumulative(v)-cumulative(u)
   if moment<0:bad('negative cylindrical mass element')
   lo+=moment*(1-sqrt_upper(1-(A/v)**2))
   hi+=moment*(1-sqrt_lower(1-(A/u)**2))
  if not 0<=lo<=hi:bad('bad cylinder mass bound')
  return lo,min(hi,cumulative(RMAX))
 def B(self,R,n=70):
  key=(R,n)
  if key not in self.bcache:self.bcache[key]=self.cylinder_interval(R,self.bulge_primitive,n)
  return self.bcache[key]
 def D(self,R,n=70):
  key=(R,n)
  if key in self.dcache:return self.dcache[key]
  p=self.pp;M,s,q=p['disc_mass_msun'],p['disc_scale_kpc'],p['disc_q']
  def integrand(t,above):
   k=1+(1/(q*q)-1)*4*t*t/(1+t*t)**2
   g=sqrt_lower(k) if above else sqrt_upper(k)
   x=R*g/s
   left,right=exp_bounds(x)
   v=1-(1+x)*(left if above else right)
   return max(Q(0),v)/(g*g*(1+t*t))
  low=high=Q(0)
  for j in range(n):
   low+=integrand(Q(j+1,n),False)
   high+=integrand(Q(j,n),True)
  low*=4*M/(PIHI*q*n);high*=4*M/(PILO*q*n)
  if not 0<=low<=high or low>M:bad('disk bounds invalid')
  self.dcache[key]=(low,min(high,M));return self.dcache[key]
 def S(self,A,n=70):
  key=(A,n)
  if key not in self.scache:
   a,b=self.cylinder_interval(A,self.pro.interior,n)
   self.scache[key]=(4*PILO*a,4*PIHI*b)
  return self.scache[key]
 def bounds_and_aperture(self,L,U,n):
  b0=self.B(L,n)[0];b1=self.B(U,n)[1];d0=self.D(L,n)[0];d1=self.D(U,n)[1]
  q0s=[(self.pp['bulge_q']*b+self.pp['disc_q']*d)/(b+d) for b in (b0,b1) for d in (d0,d1)]
  qlo,qhi=min(q0s),max(q0s)
  Alo=L/sqrt_upper(qhi);Ahi=U/sqrt_lower(qlo)
  if not(Q(1,1000)<min(self.pp['bulge_q'],self.pp['disc_q']) and 0<qlo<=qhi<=1 and RMIN<Alo<=Ahi<RMAX and Alo*Alo*qhi<=L*L and Ahi*Ahi*qlo>=U*U):bad('aperture guard fails')
  return b0,b1,d0,d1,qlo,qhi,Alo,Ahi
 def H_low(self,L,U,n=70):
  b0,b1,d0,d1,qlo,qhi,Alo,Ahi=self.bounds_and_aperture(L,U,n)
  return b0+d0+self.S(Alo,n)[0]-PIHI*self.sig1*U*U
 def Bprime_upper(self,L,U,N=200):
  p=self.pp;M,a=p['bulge_mass_msun'],p['hernquist_a_kpc']
  end=sqrt_upper(RMAX*RMAX-L*L);total=Q(0)
  for j in range(N):
   x=end*Q(j**3,N**3);y=end*Q((j+1)**3,N**3)
   rr=sqrt_lower(L*L+x*x)
   total+=(y-x)/(rr*(rr+a)**3)
  return cei(2*M*a*U*total,1000000)
 def Dprime_upper(self,L,U,N=90):
  p=self.pp;M,s,q=p['disc_mass_msun'],p['disc_scale_kpc'],p['disc_q'];sum_=Q(0)
  for j in range(N):
   t=Q(j,N)
   g=sqrt_lower(1+(1/(q*q)-1)*4*t*t/(1+t*t)**2)
   elo,ehi=exp_bounds(L*g/s)
   sum_+=ehi/(1+t*t)
  return cei(4*M*U*sum_/(PILO*q*s*s*N),1000000)
 def sigma_max(self,Alo,Ahi,N=165):
  end=sqrt_upper(RMAX*RMAX-Alo*Alo);total=Q(0)
  for j in range(N):
   lo=end*Q(j**3,N**3);hi=end*Q((j+1)**3,N**3)
   rlo=sqrt_lower(Alo*Alo+lo*lo)
   rhi=sqrt_upper(Ahi*Ahi+hi*hi)
   total+=(hi-lo)*self.pro.rho_max(rlo,rhi)
  return 2*total
 def Hprime_upper(self,L,U,n=72):
  b0,b1,d0,d1,qlo,qhi,Alo,Ahi=self.bounds_and_aperture(L,U,n)
  bp=self.Bprime_upper(L,U);dp=self.Dprime_upper(L,U)
  qp=cei(abs(self.pp['bulge_q']-self.pp['disc_q'])*(bp*d1+b1*dp)/(b0+d0)**2,10**9)
  rt=sqrt_lower(qlo)
  Aprime=cei(1/rt+U*qp/(2*qlo*rt),10**9)
  su=self.sigma_max(Alo,Ahi)
  sprime=cei(2*PIHI*Ahi*su*Aprime,1000000)
  crit=flo(2*PILO*self.sig0*L,1000000)
  return bp+dp+sprime-crit

def structural_preflight(cand):
 """Quick fail-closed graph/domain/claim check BEFORE expensive source integrals.

 This is NOT a second mathematical proof; full kernel recomputation follows.
 """
 if cand.get('schema')!='HIST001_G4B1C_GLOBAL_FINITE_PROXY_SIX_SINGLE_REAL_ROOT_CANDIDATE_v1' or cand.get('status')!='NEW_LOCAL_UNREVIEWED_CONDITIONAL_GLOBAL_FINITE_PROXY_ROOT_COUNT_CANDIDATE':bad('candidate schema/status drift')
 if cand.get('model_identity')!='EXACT_MATHEMATICAL_FINITE_D2D_SOURCE_NODAL_PROXY_ONLY_NOT_MARCH_180X120' or cand.get('frozen_original_march_46plus3_sha')!='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a':bad('candidate model/source type drift')
 if cand.get('antecedents')!=SOURCE_SHA or cand.get('claims')!={'global_exactly_one_REAL_ROOT_per_lens_conditional_ON_FINITE_PROXY_and_ANTECEDENT_THEOREMS':True,'independent_original_march_180x120_all_real_root_count_proved':False,'external_mathematical_peer_review_completed':False,'physical_same_source_Weyl_admitted':False,'Native_v172_field_equivalence_proved':False,'heldout_observational_validation':'NOT_ESTABLISHED','physical_provider_admitted':False,'canonical_theory_state_mutated':False}:bad('claim/antecedent altered')
 if len(cand.get('lenses',[]))!=6:bad('lens count is not six')
 source_narrow=json.loads((ROOT/'input/narrow_signs_v1.json').read_bytes())['lenses']
 source_pre=json.loads((ROOT/'input/prepeak_v5.json').read_bytes())['lenses']
 for lid,rec,s,p in zip(IDS,cand['lenses'],source_narrow,source_pre,strict=True):
  if rec.get('lens_id')!=lid:bad('lens name/order changed')
  if not (rec.get('all_R_rmin_to_120_contiguous_proof_groups') is True and rec.get('exactly_one_mathematical_finite_proxy_real_zero_on_full_domain_conditional') is True and rec.get('original_March_numerical_root_count')=='NOT_ESTABLISHED' and rec.get('physical_provider_admitted') is False):bad('per-lens scientific claim or root count altered')
  if not(rec.get('inner_positive_to')==p['inner_strict_positive_until_exact'] and rec.get('outer_negative_from')==p['outer_strict_negative_from_exact'] and rec.get('narrow_unique_L')==s['rational_bracket_radius']['lower'] and rec.get('narrow_unique_U')==s['rational_bracket_radius']['upper']):bad('source bands changed')
  pivot=f(rec['pivot']);Lw=f(rec['inner_positive_to']);Ln=f(rec['narrow_unique_L']);Un=f(rec['narrow_unique_U']);Uw=f(rec['outer_negative_from'])
  if not(RMIN<Lw<=pivot<Ln<Un<Uw<RMAX):bad('global exact interval ordering false')
  left=rec.get('strict_positive_left_cover',[]);der=rec.get('strict_negative_derivative_corridor_cover',[])
  if len(left)!=rec.get('left_positive_cell_count') or len(der)!=rec.get('derivative_corridor_cell_count') or len(left)>100 or len(der)>100:bad('proof cell count changed')
  current=Lw
  for row in left:
   if set(row)!={'L','U','H_lower_floor_msun'}:bad('left leaf key changed')
   a=f(row['L']);b=f(row['U'])
   if a!=current or not current<b<=pivot or int(row['H_lower_floor_msun'])<=0:bad('left prefix root exclusion cell not contiguous/positive')
   current=b
  if current!=pivot:bad('left positivity prefix missing cells')
  for region,start,stop in (('LEFT_DECREASING',pivot,Ln),('RIGHT_DECREASING',Un,Uw)):
   current=start
   for row in [z for z in der if z['region']==region]:
    if set(row)!={'region','L','U','Hprime_upper_ceil_msun_per_kpc'}:bad('derivative leaf key changed')
    a=f(row['L']);b=f(row['U'])
    if current!=a or not a<b<=stop or int(row['Hprime_upper_ceil_msun_per_kpc'])>=0:bad('derivative sign/interval cover failed')
    current=b
   if current!=stop:bad('derivative corridor missing cells')
  if any(z.get('region') not in ('LEFT_DECREASING','RIGHT_DECREASING') for z in der):bad('unknown derivative cells')

def independent_replay(candidate_path=None,expected_sha=None):
 candidate_path=Path(candidate_path) if candidate_path is not None else ROOT/'G4b1c_Global_Six_Lens_Exactly_One_Finite_Proxy_Real_Root_Candidate_v1.json'
 expected_sha=expected_sha or EXPECTED_PRODUCER_SHA
 producer_bytes=candidate_path.read_bytes()
 if sha(producer_bytes)!=expected_sha:bad('candidate producer SHA mismatch')
 candidate=json.loads(producer_bytes)
 structural_preflight(candidate)
 if candidate['schema']!='HIST001_G4B1C_GLOBAL_FINITE_PROXY_SIX_SINGLE_REAL_ROOT_CANDIDATE_v1' or candidate['status']!='NEW_LOCAL_UNREVIEWED_CONDITIONAL_GLOBAL_FINITE_PROXY_ROOT_COUNT_CANDIDATE':bad('candidate schema/status drift')
 if candidate['model_identity']!='EXACT_MATHEMATICAL_FINITE_D2D_SOURCE_NODAL_PROXY_ONLY_NOT_MARCH_180X120' or candidate['frozen_original_march_46plus3_sha']!='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a':bad('candidate model/source type drift')
 if candidate['antecedents']!=SOURCE_SHA or candidate['claims']!={'global_exactly_one_REAL_ROOT_per_lens_conditional_ON_FINITE_PROXY_and_ANTECEDENT_THEOREMS':True,'independent_original_march_180x120_all_real_root_count_proved':False,'external_mathematical_peer_review_completed':False,'physical_same_source_Weyl_admitted':False,'Native_v172_field_equivalence_proved':False,'heldout_observational_validation':'NOT_ESTABLISHED','physical_provider_admitted':False,'canonical_theory_state_mutated':False}:bad('claim/antecedent altered')
 records,pre,sign,narrow,ind,inner,outer=source_decode()
 report=[]
 for rec,pp,ss,n,nn,ins,outs,src in zip(records,pre['lenses'],sign['lenses'],narrow['lenses'],ind['lenses'],inner['lenses'],outer['lenses'],candidate['lenses'],strict=True):
  lid=rec['id']
  if not all(w['lens_id']==lid for w in (pp,ss,n,nn,ins,outs,src)):bad('lens name/order changed')
  if not(src['source_nodal_sha256']==rec['digest']==pp['source_nodal_sha256']==ss['source_nodal_digest']==n['source_nodal_sha256']==nn['source_nodal_sha256']):bad('source nodal sha mismatch')
  Lw=f(pp['inner_strict_positive_until_exact']);Uw=f(pp['outer_strict_negative_from_exact']);Ln=f(ss['rational_bracket_radius']['lower']);Un=f(ss['rational_bracket_radius']['upper']);pivot=f(src['pivot'])
  if not(RMIN<Lw<=pivot<Ln<Un<Uw<RMAX and Un-Ln==Q(1,10)):bad('coverage domain invalid')
  if not(Lw==f(ins['new_disk_assisted_positive_to'])==f(src['inner_positive_to']) and Uw==f(outs['new_certified_negative_from_exact'])==f(src['outer_negative_from'])):bad('old inner/outer certificates not attached')
  if not(ins['entire_real_Rmin_to_new_T_strict_H_positive_conditional'] and outs['entire_real_outer_band_strict_negative'] and ss['IVT_at_least_one_zero_in_open_bracket_conditional'] and n['Hprime_strict_negative_every_real_R_in_bracket'] and nn['independent_strict_all_real_derivative_negative']):bad('missing essential strict antecedent')
  if not(Ln==f(src['narrow_unique_L']) and Un==f(src['narrow_unique_U'])):bad('source root interval mismatch')
  alt=Alt(ExactProfile(rec),f(ss['left_strict_positive_exact_enclosure']['G4a_sigma_crit_enclosure_msun_per_kpc2'][0]),f(ss['left_strict_positive_exact_enclosure']['G4a_sigma_crit_enclosure_msun_per_kpc2'][1]))
  left=src['strict_positive_left_cover'];der=src['strict_negative_derivative_corridor_cover']
  if len(left)!=src['left_positive_cell_count'] or len(der)!=src['derivative_corridor_cell_count'] or len(left)>100 or len(der)>100:bad('bad proof cell budget')
  if set(src)!={'lens_id','source_nodal_sha256','inner_positive_to','outer_negative_from','narrow_unique_L','narrow_unique_U','pivot','strict_positive_left_cover','strict_negative_derivative_corridor_cover','left_positive_cell_count','derivative_corridor_cell_count','all_R_rmin_to_120_contiguous_proof_groups','exactly_one_mathematical_finite_proxy_real_zero_on_full_domain_conditional','original_March_numerical_root_count','physical_provider_admitted'}:bad('unknown per-lens claim key')
  t=Lw; min_H=None
  for leaf in left:
   a,b=f(leaf['L']),f(leaf['U'])
   if set(leaf)!={'L','U','H_lower_floor_msun'} or a!=t or not a<b<=pivot or int(leaf['H_lower_floor_msun'])<=0:bad('left positive proof invalid or gaps')
   exact_low=alt.H_low(a,b,n=72)
   if exact_low<=0 or Q(int(leaf['H_lower_floor_msun']))>flo(exact_low):bad('independent direct H lower did not prove claimed positive margin: '+lid+': '+str(float(a)))
   if min_H is None or exact_low<min_H:min_H=exact_low
   t=b
  if t!=pivot:bad('strict left-positive coverage does not reach pivot')
  leftD=[z for z in der if z['region']=='LEFT_DECREASING'];rightD=[z for z in der if z['region']=='RIGHT_DECREASING']
  if len(leftD)+len(rightD)!=len(der):bad('unknown derivative interval group')
  mder=None
  for group,start,stop in ((leftD,pivot,Ln),(rightD,Un,Uw)):
   t=start
   for row in group:
    a,b=f(row['L']),f(row['U'])
    if set(row)!={'region','L','U','Hprime_upper_ceil_msun_per_kpc'} or a!=t or not a<b<=stop or int(row['Hprime_upper_ceil_msun_per_kpc'])>=0:bad('derivative coverage gap / negative witness altered')
    v=alt.Hprime_upper(a,b,n=76)
    if v>=0 or Q(int(row['Hprime_upper_ceil_msun_per_kpc']))<cei(v):bad('independent derivative/margin failed: '+lid+' '+str(float(a))+' '+str(float(b))+'  '+'{:.3f}'.format(float(v)/1e9))
    if mder is None or v>mder:mder=v
    t=b
   if t!=stop:bad('derivative corridor not to required exact endpoint')
  if not src['all_R_rmin_to_120_contiguous_proof_groups'] or not src['exactly_one_mathematical_finite_proxy_real_zero_on_full_domain_conditional'] or src['original_March_numerical_root_count']!='NOT_ESTABLISHED' or src['physical_provider_admitted'] is not False:bad('producer lens claims')
  report.append({'lens_id':lid,'external_exact_source_node_digest':rec['digest'],'independently_positive_H_cells':len(left),'independently_negative_Hprime_cells':len(der),'independent_min_left_H_lower_floor_msun':str(flo(min_H)) if min_H is not None else 'NOT_REQUIRED_BY_MONOTONICITY','independent_least_negative_Hprime_upper_ceil_msun_per_kpc':str(cei(mder)),'all_real_R_0p02_to120_exact_single_proxy_root_conditional':True})
 return {'schema':'HIST001D_G4B1C_GLOBAL_FINITE_PROXY_ROOT_COUNT_INDEPENDENT_RECHECK_V1','status':'PASS_SCOPED_INDEPENDENT_EXACT_RATIONAL_MATHEMATICAL_CANDIDATE_NOT_PEER_REVIEWED',
 'source_input_sha256':SOURCE_SHA,'candidate_producer_sha256':expected_sha,
 'independent_method':'original binary64 source ZIP and 46+3 digest; exact primitive linear density r^2 moments; cubic-partition alternate cylinder, disk and t-derivative enclosures; 44-bit directed roots, 19/20-term alternating exponential range reduction and distinct pi series',
 'lenses':report,'claims':{'conditional_full_DOMAIN_one_root_per_lens_for_THIS_defined_FINITE_PROXY':True,'original_March_180x120_real_root_count_certified':False,'independent_math_peer_review_completed':False,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED','canonical_theory_state_mutated':False}}

def main():
 result=independent_replay()
 raw=(json.dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf-8')
 fn=ROOT/'G4b1c_Independent_Global_Root_Count_Exact_Rational_Verifier_v1.json';fn.write_bytes(raw)
 print(json.dumps({'output':str(fn),'sha256':sha(raw),'independent_positive_H_cells':sum(k['independently_positive_H_cells'] for k in result['lenses']),'independent_negative_Hprime_cells':sum(k['independently_negative_Hprime_cells'] for k in result['lenses']),'worst_Hprime_bound':[(k['lens_id'],k['independent_least_negative_Hprime_upper_ceil_msun_per_kpc']) for k in result['lenses']]},indent=2))
if __name__=='__main__':main()
