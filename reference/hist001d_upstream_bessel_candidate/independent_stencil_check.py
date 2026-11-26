#!/usr/bin/env python3
"""Independent exact-dyadic arithmetic for protected 180-node float mass.

No producer, NumPy, SciPy, Bessel or source imports. Only binary64 input bytes
in explicitly protected archives are consumed. Does not prove continuum error.
"""
from __future__ import annotations
import hashlib, io, json, struct, zipfile, argparse
from pathlib import Path
from fractions import Fraction as Q
PARENT_SHA='99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
SOURCE_SHA='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
LENSES=['J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720']
sha=lambda v:hashlib.sha256(v).hexdigest()
def ceil(v):return -((-v.numerator)//v.denominator)
def decode(b:bytes)->Q:
    if len(b)!=8:raise ValueError('invalid binary64 length')
    u=int.from_bytes(b,'big');sgn=-1 if u>>63 else 1
    exponent=(u>>52)&2047;mant=u&((1<<52)-1)
    if exponent==2047:raise ValueError('NaN/Inf forbidden')
    if exponent==0:n=mant;shift=-1074
    else:n=mant+(1<<52);shift=exponent-1075
    return Q(sgn*n*(2**shift)) if shift>=0 else Q(sgn*n,2**(-shift))
def source_stencil(xs,ms):
    if len(xs)!=180 or len(ms)!=180:raise ValueError('required 180 original knots')
    if any(xs[i]>=xs[i+1] for i in range(179)):raise ValueError('not ordered')
    y=[]
    for i in range(180):
        if i==0:y.append((ms[1]-ms[0])/(xs[1]-xs[0]))
        elif i==179:y.append((ms[-1]-ms[-2])/(xs[-1]-xs[-2]))
        else:
            hm=xs[i]-xs[i-1];hp=xs[i+1]-xs[i]
            a=-hp/(hm*(hm+hp))
            b=(hp-hm)/(hm*hp)
            c=hm/(hp*(hm+hp))
            y.append(a*ms[i-1]+b*ms[i]+c*ms[i+1])
    return y

def check(sat_path:Path,root:Path,expected:dict):
    if expected.get('schema')!='HIST001D_SOURCE_MARCH_BESSEL_FLOAT_MASS_GRADIENT_K180_COMPONENT_SPLIT_V1_NONPROMOTING':raise ValueError('schema')
    if expected.get('source_original_46plus3_sha256')!=SOURCE_SHA:raise ValueError('source provenance')
    if expected.get('all_source_shadow_density_nodes_reproduced_bitwise')!=1080:raise ValueError('node count')
    if expected.get('continuous_radii_Bessel_or_gradient_error_certified') is not False:raise ValueError('claim inflation')
    if expected.get('physical_provider_admitted') is not False or expected.get('empirical_validation')!='NOT_ESTABLISHED':raise ValueError('physical/empirical claim')
    if len(expected.get('lenses',[]))!=6 or [x['lens_id'] for x in expected['lenses']]!=LENSES:raise ValueError('lens inventory')
    raw=sat_path.read_bytes()
    if sha(raw)!=PARENT_SHA:raise ValueError('protected parent hash')
    sat=zipfile.ZipFile(io.BytesIO(raw))
    if sat.testzip() is not None:raise ValueError('parent CRC')
    parent=zipfile.ZipFile(io.BytesIO(sat.read('original_parent.zip')))
    s=zipfile.ZipFile(io.BytesIO(parent.read('inputs/frozen_source_parent.zip')))
    d=zipfile.ZipFile(io.BytesIO(s.read('inputs/original_march_D120_q_parent.zip')))
    march=zipfile.ZipFile(io.BytesIO(d.read('inputs/original_march180_parent_v1r1.zip')))
    caps=json.loads(march.read('results/source180_capture.json'))['lenses']
    all180=zipfile.ZipFile(io.BytesIO(sat.read('all180_parent.zip')))
    if [x['lens_id'] for x in caps]!=LENSES:raise ValueError('original lens order')
    results=[]
    for a,c in zip(expected['lenses'],caps):
        rawrow=march.read('inputs/'+c['node_file'])
        if sha(rawrow)!=c['node_sha256'] or c['node_sha256']!=a['original_node_sha256']:raise ValueError('node hash')
        if len(rawrow)!=180*64:raise ValueError('node dimensions')
        original=[[decode(rawrow[i*64+j*8:i*64+(j+1)*8]) for j in range(8)] for i in range(180)]
        r=[v[0] for v in original];w=[v[1] for v in original];rho=[v[3] for v in original]
        if min(w)<=0 or min(rho)<=0:raise ValueError('weight/rho positivity')
        path=a['original_replayed_float_mass_binary_file']
        correct='inputs/frozen_source_mass_'+a['lens_id'].replace('+','p')+'.be64'
        if path!=correct:raise ValueError('mass file path')
        raw_mass=(root/path).read_bytes()
        if len(raw_mass)!=180*8 or sha(raw_mass)!=a['original_replayed_float_mass_binary_sha256']:raise ValueError('source float mass file')
        mass=[decode(raw_mass[i*8:i*8+8]) for i in range(180)]
        if min(mass)<=0:raise ValueError('source shadow mass positivity')
        G=source_stencil(r,mass)
        C=decode(struct.pack('>d',float.fromhex('0x1.921fb54442d18p+3')))
        capsum=sum((w[i]*abs(C*r[i]**2*rho[i]-G[i]) for i in range(180)),Q())
        upper=ceil(capsum*10**6)
        if upper!=a['rounding_only_stored_rho_vs_ideal_stencil_of_current_source_float_mass_all_apertures_micro_Msun_upper']:
            raise ValueError('incorrect roundoff bound '+a['lens_id'])
        rec=json.loads(all180.read('results/all180_rational_'+a['lens_id'].replace('+','p')+'.json'))
        old_bound=rec['stored_vs_ideal_stencil_absolute_upper_micro_msun_per_kpc']
        if len(old_bound)!=180:raise ValueError('old bound length')
        inherited=sum((w[i]*Q(int(old_bound[i]),10**6) for i in range(180)),Q())
        inh=ceil(inherited*10**6)
        if inh!=a['inherited_512bit_full_all180_source_vs_selected_math_stencil_all_apertures_micro_Msun_upper']:
            raise ValueError('inherited all-node bound invalid')
        if ceil((capsum+inherited)*10**6)!=a['upstream_sourcefloat_stencil_to_selected_ideal_math_stencil_all_apertures_triangle_micro_Msun_upper']:
            raise ValueError('triangle decomposition invalid')
        if a['unclipped_positive_mass_gradient_density_nodes']!=180 or a['epsilon_floor_inactive_nodes']!=180:
            raise ValueError('clip status')
        j=a['original_root_cell_index']
        if j not in (1,2,3,5,6):raise ValueError('crossing index')
        if [q['index'] for q in a['crossing_node_gradient_sourcefloat_vs_math_split']] != [j,j+1]:
            raise ValueError('crossing-node identity')
        results.append({'lens_id':a['lens_id'],'rounding_upper_micro_Msun':upper,'inherited_math_upper_micro_Msun':inh})
    return {'schema':'HIST001D_INDEPENDENT_EXACT_FLOAT_GRADIENT_NODE_CHECK_V1',
            'source_sha256':SOURCE_SHA,'lenses':results,'all_1080_nodes_checked':True,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}

if __name__=='__main__':
    arg=argparse.ArgumentParser();arg.add_argument('--sat',type=Path,required=True);arg.add_argument('--root',type=Path,required=True);arg.add_argument('--receipt',type=Path,required=True);arg.add_argument('--out',type=Path,required=True)
    ns=arg.parse_args()
    obj=check(ns.sat,ns.root,json.loads(ns.receipt.read_bytes()))
    ns.out.parent.mkdir(parents=True,exist_ok=True)
    ns.out.write_bytes((json.dumps(obj,sort_keys=True,indent=2)+'\n').encode())
    print('INDEPENDENT_CHECK_PASS',len(obj['lenses']),sha(ns.out.read_bytes()))
