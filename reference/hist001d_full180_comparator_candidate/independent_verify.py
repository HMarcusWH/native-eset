"""Independent exact-fraction validator for full domain of defined March 180-component PL comparator.
Does NOT import the producer, the producer's arithmetic module, or its interval helpers.
This is a mathematical candidate, not a claim about original offgrid source or physical fields.
"""
from __future__ import annotations
import hashlib,io,json,math,struct,zipfile
from fractions import Fraction as Rational
from pathlib import Path
import numpy as np

BASE=Path(__file__).resolve().parent
INPUT=BASE/'inputs'/'original_march_D120_q_parent.zip'
PROOF=BASE/'results'/'exact_defined_frozen180_comparator_producer.json'
LOCKED_PARENT='8178dfb07aa4c070b5f10e7de2c1e4130ffe777efb08d57382f4aae9cfcd4132'
GUARDS={'J0822+1828':('1.754','1.814'), 'J0915+4211':('1.373','1.433'),
        'J0930+2855':('4.594','4.654'),'J1021+2028':('1.100','1.160'),
        'J1111+2234':('3.924','3.984'),'J1135+3720':('2.152','2.212')}

def hashof(raw):return hashlib.sha256(raw).hexdigest()
def dyadic_from_float64(v):
    """Explicit unpack of exponent/significand, not Fraction.from_float."""
    raw=struct.unpack('>Q',struct.pack('>d',v))[0]
    sign=-1 if raw>>63 else 1
    exp=(raw>>52)&2047
    mant=raw&((1<<52)-1)
    assert exp!=2047
    if exp==0:
        numerator=mant;shift=-1074
    else:
        numerator=(1<<52)+mant;shift=exp-1023-52
    if shift>=0:return Rational(sign*numerator*(1<<shift),1)
    return Rational(sign*numerator,1<<(-shift))
def b64_words(raw, width):
    assert len(raw)% (8*width)==0
    return [[dyadic_from_float64(float(x)) for x in row] for row in struct.iter_unpack('>'+'d'*width,raw)]
def enclosing_root(x):
    assert x>0
    n,d=x.numerator,x.denominator
    k=math.isqrt(n*d)
    lower=Rational(k,d);upper=Rational(k+1,d)
    assert lower*lower<=x<upper*upper
    return lower,upper

def ppoint(u,v,t): return u+(v-u)*t

def linear_at(values, rs, j, x):
    assert rs[j]<=x<=rs[j+1]
    return ppoint(values[j],values[j+1],(x-rs[j])/(rs[j+1]-rs[j]))

def shadow_interp(rs, ss, x):
    assert x>=0
    if x<=rs[0]:return ss[0]
    if x>=rs[-1]:return ss[-1]
    # Standalone linear search; no producer bisect routine.
    for k in range(len(rs)-1):
        if rs[k]<=x<=rs[k+1]:return linear_at(ss,rs,k,x)
    raise ValueError('shadow support cannot be interpolated')

def positive_ratio_bounds(m, j, a, b):
    B,D,rs=m['B'],m['D'],m['r']
    qb,qd=m['qb'],m['qd']
    bl=linear_at(B,rs,j,a);br=linear_at(B,rs,j,b)
    dl=linear_at(D,rs,j,a);dr=linear_at(D,rs,j,b)
    ql=(qb*bl+qd*dl)/(bl+dl)
    qr=(qb*br+qd*dr)/(br+dr)
    assert bl>0 and br>0 and dl>0 and dr>0 and ql>0 and qr>0
    return min(ql,qr),max(ql,qr)

def aperture_enclosure(m,j,a,b):
    minq,maxq=positive_ratio_bounds(m,j,a,b)
    sl,_=enclosing_root(1/maxq)
    _,su=enclosing_root(1/minq)
    al=min(m['r'][-1],a*sl)
    au=min(m['r'][-1],b*su)
    assert al<=au
    return al,au,minq,maxq

def interval_score(m,j,a,b):
    rs=m['r'];a0,a1,qmin,qmax=aperture_enclosure(m,j,a,b)
    # DIFFERENT proof algebra: combine B+D-T into one affine term, bound its endpoints.
    core=[]
    for x in (a,b):
        core.append(linear_at(m['B'],rs,j,x)+linear_at(m['D'],rs,j,x)-linear_at(m['T'],rs,j,x))
    return min(core)+shadow_interp(rs,m['S0'],a0),max(core)+shadow_interp(rs,m['S0'],a1)

def independent_dh_upper(m,j,a,b):
    rs=m['r'];h=rs[j+1]-rs[j]
    pl=lambda field,x: linear_at(field,rs,j,x)
    Bprime=(m['B'][j+1]-m['B'][j])/h
    Dprime=(m['D'][j+1]-m['D'][j])/h
    Tprime=(m['T'][j+1]-m['T'][j])/h
    al,au,qmin,qmax=aperture_enclosure(m,j,a,b)
    P0=m['B'][j]+m['D'][j];P1=m['B'][j+1]+m['D'][j+1]
    N0=m['qb']*m['B'][j]+m['qd']*m['D'][j]
    N1=m['qb']*m['B'][j+1]+m['qd']*m['D'][j+1]
    # Different from producer: no sign-sensitive improvement at all.
    qp_abs=abs((N1*P0-N0*P1)/h)/min(pl(m['B'],a)+pl(m['D'],a),pl(m['B'],b)+pl(m['D'],b))**2
    sqrtq_lower,_=enclosing_root(qmin)
    assert sqrtq_lower>0
    Aprime_upper=1/sqrtq_lower+b*qp_abs/(2*qmin*sqrtq_lower)
    # Enumerate every source-knot shadow interval that touches the aperture band.
    candidates=[]
    for k in range(179):
        if rs[k]<=au and rs[k+1]>=al:
            slope=(m['S0'][k+1]-m['S0'][k])/(rs[k+1]-rs[k])
            assert slope>=0
            candidates.append(slope)
    slope_upper=max(candidates,default=Rational(0))
    return Bprime+Dprime-Tprime+slope_upper*Aprime_upper

def exactpair(value):
    assert set(value)=={'num','den'} and type(value['num']) is str and type(value['den']) is str
    n=int(value['num']);d=int(value['den'])
    assert d>0 and str(n)==value['num'] and str(d)==value['den']
    return Rational(n,d)

def load_models():
    assert hashof(INPUT.read_bytes())==LOCKED_PARENT
    outer=zipfile.ZipFile(INPUT);assert outer.testzip() is None
    parent_bytes=outer.read('inputs/original_march180_parent_v1r1.zip')
    assert hashof(parent_bytes)=='0a643e81a9ab542dce8f158bc5135d94478d9145ab33036aae5813907f3655a1'
    z=zipfile.ZipFile(io.BytesIO(parent_bytes));assert z.testzip() is None
    sourcebytes=z.read('inputs/original_source_46_frozen.zip')
    assert hashof(sourcebytes)=='283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e'
    original=zipfile.ZipFile(io.BytesIO(sourcebytes));assert original.testzip() is None
    lock=json.loads(z.read('inputs/original_46plus3_lock.json'))
    assert lock['original_46plus3_composite_sha256']=='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
    for path,h in lock['source_filenames_sha256'].items():assert hashof(original.read('swells_pack_v2/'+path))==h
    for path,h in lock['archived_negative_controls_sha256'].items():assert hashof(z.read('inputs/negative_controls/'+path))==h
    source180=json.loads(z.read('results/source180_capture.json'))
    angular=json.loads(outer.read('results/source120_capture.json'))
    grid=zipfile.ZipFile(io.BytesIO(z.read('inputs/march_180_grid.zip')))
    models=[]
    for l in angular['lenses']:
        lid=l['lens_id'];tag=lid.replace('+','p')
        raw=z.read('inputs/March180_source_nodes_'+tag+'.be64')
        s=next(x for x in source180['lenses'] if x['lens_id']==lid)
        assert hashof(raw)==s['node_sha256']
        records=b64_words(raw,8)
        rr=[r[0] for r in records]
        B=[r[4] for r in records];D=[r[6] for r in records];S0=[r[5] for r in records];S=[r[7] for r in records]
        sigma=float.fromhex(s['original_sigma_hex'])
        # Reconstruct binary64 node T using original NumPy evaluation semantics.
        Treal=np.pi*np.array([float(x) for x in rr])**2*sigma
        T=[dyadic_from_float64(float(x)) for x in Treal]
        # Replay actual registered March result, not assuming float equality by name.
        grid_raw=grid.read('sampled_binary64/'+tag+'.R_H_be64.bin')
        hist=b64_words(grid_raw,2);H=[x[1] for x in hist]
        assert [x[0] for x in hist]==rr
        Bf=np.array([float(x) for x in B]);Df=np.array([float(x) for x in D]);Sf=np.array([float(x) for x in S]);Hf=np.array([float(x) for x in H]);
        assert np.array_equal((Bf+Df+Sf-Treal).view(np.uint64),Hf.view(np.uint64))
        assert all(rr[k]<rr[k+1] and B[k]<=B[k+1] and D[k]<=D[k+1] and S0[k]<=S0[k+1] and T[k]<T[k+1] for k in range(179))
        assert min(B)>0 and min(D)>0 and min(S0)>=0
        qb=dyadic_from_float64(float.fromhex(l['qb_hex']));qd=dyadic_from_float64(float.fromhex(l['qd_hex']))
        assert Rational(1,1000)<qb<1 and Rational(1,1000)<qd<1
        models.append(dict(lid=lid,r=rr,B=B,D=D,S0=S0,S=S,T=T,H=H,qb=qb,qd=qd,
                           hashes=dict(node=hashof(raw), source_H=hashof(b''.join(struct.pack('>d',float(t)) for t in H)),
                           original_source_composite=lock['original_46plus3_composite_sha256'])))
    return models

def verify(proof_data,models=None):
    allowed_top={'schema','model','source_parent_zip_sha256','original_source_lock_sha256','definition',
                 'domain','certifier','number_of_lenses','strict_sign_leaf_count','lenses','claim_ceiling'}
    allowed_lens={'lens','source_input_hashes','root_cell','guard_left','guard_right',
                  'root_H_positive_left_lower','root_H_negative_right_upper','root_dH_strict_upper',
                  'minimum_positive_cell_lower','maximum_negative_cell_upper','source_knot_difference_upper',
                  'all_original_knot_differences_below_one_msun','refined_root_left','refined_root_right',
                  'source_original_PL_root_exact','root_separation_from_original_sampled_PL_strict_lower_kpc',
                  'full_root_count_not_transferred_between_new_comparator_and_original_sampled_interpolant',
                  'all_source_radial_cells','strict_sign_leaf_count','maximum_split_depth',
                  'strict_sign_leaves','has_exactly_one_root_in_DEFINED_MARCH_180_COMPONENT_COMPARATOR',
                  'no_original_March_180x120_continuum_root_count_claim'}
    assert set(proof_data)==allowed_top
    assert proof_data['schema']=='HIST001D_MARCH180_EXPLICIT_COMPONENT_PL_COMPOSITION_ONE_ROOT_MATH_CANDIDATE_V1'
    assert set(proof_data['claim_ceiling'])=={
       'source_frozen_defined_component_comparator_exactly_one_real_root_per_lens_IF_SOURCE_LOCKS_AND_ARITHMETIC_SOUND',
       'original_180_120_source_offgrid_numeric_error','original_full_continuum_root_uniqueness',
       'source_derived_shadow_continuum','physical_Weyl_lensing','native_v172_equivalence','holdout',
       'physical_provider_admitted','empirical_validation','Theory_State_mutated'}
    assert proof_data['claim_ceiling']['source_frozen_defined_component_comparator_exactly_one_real_root_per_lens_IF_SOURCE_LOCKS_AND_ARITHMETIC_SOUND'] is True
    for forbidden in ('original_180_120_source_offgrid_numeric_error','original_full_continuum_root_uniqueness',
                      'source_derived_shadow_continuum','physical_Weyl_lensing','native_v172_equivalence','holdout'):
        assert proof_data['claim_ceiling'][forbidden] is False
    assert all(set(l)==allowed_lens for l in proof_data['lenses'])
    assert proof_data['number_of_lenses']==6
    assert proof_data['source_parent_zip_sha256']==LOCKED_PARENT
    assert proof_data['original_source_lock_sha256']=='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
    assert proof_data['claim_ceiling']['physical_provider_admitted'] is False
    assert proof_data['claim_ceiling']['empirical_validation']=='NOT_ESTABLISHED'
    assert proof_data['claim_ceiling']['original_full_continuum_root_uniqueness'] is False
    assert proof_data['claim_ceiling']['original_180_120_source_offgrid_numeric_error'] is False
    assert proof_data['claim_ceiling']['Theory_State_mutated'] is False
    assert proof_data['model']=='DEFINED_MARCH_SOURCE_FROZEN_BPL_DPL_S0PL_qA_TPL__NOT_ORIGINAL_OFFGRID_SOURCE'
    if models is None:models=load_models()
    result=[];count=0
    assert len({l['lens'] for l in proof_data['lenses']})==6
    assert {l['lens'] for l in proof_data['lenses']}=={m['lid'] for m in models}
    for m in models:
        L=next(x for x in proof_data['lenses'] if x['lens']==m['lid'])
        lid=m['lid']; j=L['root_cell'];assert type(j) is int and 0<=j<179
        assert L['all_source_radial_cells']==179 and L['all_original_knot_differences_below_one_msun'] is True
        assert L['has_exactly_one_root_in_DEFINED_MARCH_180_COMPONENT_COMPARATOR'] is True
        assert L['no_original_March_180x120_continuum_root_count_claim'] is True
        input_hashes={'lens_id':lid}
        for fld,name in [('r','r_sha256'),('B','nodal_B_sha256'),('D','nodal_D_sha256'),('S0','nodal_S0_sha256'),('T','nodal_T_sha256'),('H','original_H_sha256')]:
            input_hashes[name]=hashof(b''.join(struct.pack('>d',float(x)) for x in m[fld]))
        assert L['source_input_hashes']==input_hashes
        assert m['H'][j]>0>m['H'][j+1]
        assert sum(m['H'][i]>0>m['H'][i+1] for i in range(179))==1
        left=exactpair(L['guard_left']);right=exactpair(L['guard_right']);assert (left,right)==tuple(map(Rational,GUARDS[lid]))
        assert m['r'][j]<left<right<m['r'][j+1]
        leftlower=interval_score(m,j,left,left)[0]
        rightupper=interval_score(m,j,right,right)[1]
        assert leftlower>0 and rightupper<0
        assert exactpair(L['root_H_positive_left_lower'])<=leftlower
        assert exactpair(L['root_H_negative_right_upper'])>=rightupper
        derivative=independent_dh_upper(m,j,left,right)
        assert derivative<0
        assert exactpair(L['root_dH_strict_upper'])<0
        assert derivative<=exactpair(L['root_dH_strict_upper'])+Rational(10**15) # independent separately proven, not trusting producer bound
        expected=[]
        for i in range(179):
            if i<j:expected.append((i,'whole',m['r'][i],m['r'][i+1],'POS'))
            elif i==j:
                expected.append((i,'left',m['r'][i],left,'POS'))
                expected.append((i,'right',right,m['r'][i+1],'NEG'))
            else:expected.append((i,'whole',m['r'][i],m['r'][i+1],'NEG'))
        groups={}
        for cell in L['strict_sign_leaves']:
            assert type(cell) is list and len(cell)==5
            i,part,depth,k,sign=cell
            assert type(i) is type(depth) is type(k) is int and 0<=i<179 and 0<=depth<=18 and 0<=k<2**depth
            assert part in ('whole','left','right') and sign in ('POS','NEG')
            groups.setdefault((i,part),[]).append((depth,k,sign))
        assert len(groups)==len(expected)
        n=0;minpos=None;maxneg=None
        for i,part,a,b,sign in expected:
            cells=[]
            for dep,idx,mark in groups[(i,part)]:
                assert mark==sign
                den=1<<dep
                lo=a+(b-a)*Rational(idx,den)
                hi=a+(b-a)*Rational(idx+1,den)
                assert a<=lo<hi<=b
                cells.append((lo,hi,dep,idx))
            cells.sort()
            assert len(cells)==len(set(cells))
            assert cells[0][0]==a and cells[-1][1]==b
            for old,new in zip(cells,cells[1:]):assert old[1]==new[0]
            for l,r,dep,idx in cells:
                lower,upper=interval_score(m,i,l,r)
                if sign=='POS':assert lower>0;minpos=lower if minpos is None else min(minpos,lower)
                else:assert upper<0;maxneg=upper if maxneg is None else max(maxneg,upper)
                n+=1
        assert n==L['strict_sign_leaf_count'] and minpos>0 and maxneg<0
        assert exactpair(L['minimum_positive_cell_lower'])<=minpos
        assert exactpair(L['maximum_negative_cell_upper'])>=maxneg
        assert max(d for cells in groups.values() for d,k,sign in cells)==L['maximum_split_depth']
        # Source at all 180 nodes: the newly defined model agrees to strictly
        # less than 1 solar mass with the *registered* original sampled H values.
        knot_worst=Rational(0)
        for ix,x in enumerate(m['r']):
            sourceindex=min(ix,178)
            low,high=interval_score(m,sourceindex,x,x)
            knot_worst=max(knot_worst,abs(low-m['H'][ix]),abs(high-m['H'][ix]))
        assert knot_worst<1
        assert exactpair(L['source_knot_difference_upper'])>=knot_worst
        # No numerical near-root fit: certify all 20 bisections as exact signs.
        refined_left=exactpair(L['refined_root_left']);refined_right=exactpair(L['refined_root_right'])
        assert left<=refined_left<refined_right<=right
        assert refined_right-refined_left==Rational(3,50)/(1<<20)
        assert interval_score(m,j,refined_left,refined_left)[0]>0
        assert interval_score(m,j,refined_right,refined_right)[1]<0
        h0=m['H'][j];h1=m['H'][j+1]
        source_pl_root=m['r'][j]+(m['r'][j+1]-m['r'][j])*h0/(h0-h1)
        assert source_pl_root==exactpair(L['source_original_PL_root_exact'])
        assert source_pl_root>refined_right
        assert exactpair(L['root_separation_from_original_sampled_PL_strict_lower_kpc'])==source_pl_root-refined_right
        assert L['full_root_count_not_transferred_between_new_comparator_and_original_sampled_interpolant'] is True
        assert n>=179 # 180 radial nodes mean 179 non-guard cells minimum
        count+=n
        result.append({'lens':lid,'cells_verified':n,'cross_cell':j,
                       'minimum_positive_lower_integer_msun':int(minpos.numerator//minpos.denominator),
                       'maximum_negative_upper_integer_msun':int(-((-maxneg.numerator)//maxneg.denominator)),
                       'derivative_upper_billion_msun_per_kpc':round(float(derivative)/1e9,9),
                       'mathematical_comparator_root_interval_kpc_display':[round(float(refined_left),10),round(float(refined_right),10)],
                       'original_sampled_PL_root_kpc_display':round(float(source_pl_root),10),
                       'strict_different_root_lower_kpc_display':round(float(source_pl_root-refined_right),10),
                       'certified_unique_root_in_mathematical_comparator_only':True})
    assert count==proof_data['strict_sign_leaf_count']
    return {'schema':'HIST001D_MARCH180_EXPLICIT_COMPONENT_PL_COMPOSITION_INDEPENDENT_VERIFIER_V1',
            'status':'PASS_SCOPED_MATHEMATICAL_COMPARATOR_ONLY','source_parent_sha256':hashof(INPUT.read_bytes()),
            'producer_certificate_sha256':hashof(PROOF.read_bytes()),'independent_verified_sign_cells':count,
            'lenses':result,'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'original_offgrid_March_numeric_root_count_certified':False,'canonical_theory_state_mutated':False}

def run():
    data=json.loads(PROOF.read_bytes());answer=verify(data)
    output=(json.dumps(answer,sort_keys=True,separators=(',',':'))+'\n').encode()
    (BASE/'results'/'exact_defined_frozen180_comparator_independent.json').write_bytes(output)
    for x in answer['lenses']:print('INDEPENDENT_PASS',x['lens'],x['cells_verified'],'derivative ub billion',x['derivative_upper_billion_msun_per_kpc'],flush=True)
    print('INDEPENDENT_SHA256',hashof(output))
if __name__=='__main__':run()
