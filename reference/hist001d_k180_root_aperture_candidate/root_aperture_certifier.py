#!/usr/bin/env python3
"""Candidate, data-dependent *fixed diagnostic A* March K180/selected-continuum enclosure.

Every finite source radius, trapezoid weight, sampled shadow density and fitted
scalar is the exact rational interpretation of the frozen historical binary64.
The original data remain in an external SHA-locked protected ZIP, not GitHub.

This code has NO claim to physical Weyl lensing, all-A root-band accuracy,
original March floating H uncertainty, actual source-law admissibility,
empirical validation or original March root uniqueness.
"""
from __future__ import annotations
import argparse
import hashlib
import heapq
import io
import json
import struct
import sys
import time
import zipfile
from fractions import Fraction as Q
from math import isqrt
from pathlib import Path

SATURATION_CODE = Path(__file__).resolve().parents[1] / 'hist001d_k180_saturation_candidate'
if str(SATURATION_CODE) not in sys.path:
    sys.path.insert(0, str(SATURATION_CODE))
from all180_math import Iv, SCALE, bessel_F_Fp, gate, euler_gamma  # noqa: E402

SOURCE_SHA = 'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
PARENT_SHA = '3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18'
DIAGNOSTIC_SHA = '298a467e6ceab5c48ced00e08ac2fdb1082627eebedb6340139021f090430812'
LENSES = ('J0822+1828', 'J0915+4211', 'J0930+2855', 'J1021+2028', 'J1111+2234', 'J1135+3720')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def floor(q: Q) -> int:
    return q.numerator // q.denominator


def ceil(q: Q) -> int:
    return -((-q.numerator) // q.denominator)


def sqrt_outward(x: Iv) -> Iv:
    """Certified fixed-point interval sqrt, no floating square roots."""
    if x.l < 0:
        raise ValueError('sqrt of negative interval')
    lo = isqrt(x.l * SCALE)
    hi = isqrt(x.u * SCALE)
    if hi * hi != x.u * SCALE:
        hi += 1
    return Iv(lo, hi, raw=True)


def projected_u(A: Q, r: Q) -> Iv:
    if A <= 0 or r <= 0:
        raise ValueError('positive A and radius required')
    if r <= A:
        return Iv(0)
    return sqrt_outward(Iv(1) - Iv(A / r) ** 2)


def cylinder_phi(A: Q, r: Q) -> Iv:
    if A < 0 or r <= 0:
        raise ValueError('nonnegative A and positive r')
    return Iv(1) if r <= A else Iv(1) - projected_u(A, r)


def load_external(path: Path):
    """Rehash original sources, negative controls and 180-node raw arrays.

    Expects the versioned v1 or v1r1 saturation archive. Rejects substituted
    11,520-node data, changed source laws and missing source locks.
    """
    if not path.is_file():
        raise ValueError('external source archive missing')
    with zipfile.ZipFile(path) as outer:
        m = json.loads(outer.read('MANIFEST_SHA256.json'))
        if m['schema'] != 'HIST001D_MARCH180_K180_SATURATION_SOURCE_INTEGRITY_V1':
            raise ValueError('unsupported external scientific scope')
        if m.get('physical_provider_admitted') is not False or m.get('empirical_validation') != 'NOT_ESTABLISHED':
            raise ValueError('unrecognized physical claim')
        for name, expected in m['files'].items():
            if sha(outer.read(name)) != expected:
                raise ValueError(f'external manifest mismatch: {name}')
        parent = outer.read('original_parent.zip')
        if sha(parent) != PARENT_SHA:
            raise ValueError('wrong original source parent')
    with zipfile.ZipFile(io.BytesIO(parent)) as p:
        capture_parent = p.read('inputs/frozen_source_parent.zip')
        info = json.loads(p.read('results/producer_analytic_source_gradient.json'))['lenses']
    with zipfile.ZipFile(io.BytesIO(capture_parent)) as p:
        march_d120 = p.read('inputs/original_march_D120_q_parent.zip')
    with zipfile.ZipFile(io.BytesIO(march_d120)) as p:
        original_180 = p.read('inputs/original_march180_parent_v1r1.zip')
    with zipfile.ZipFile(io.BytesIO(original_180)) as source:
        lock = json.loads(source.read('inputs/original_46plus3_lock.json'))
        if lock['original_46plus3_composite_sha256'] != SOURCE_SHA:
            raise ValueError('wrong original 46+3 source composite')
        with zipfile.ZipFile(io.BytesIO(source.read('inputs/original_source_46_frozen.zip'))) as src:
            for name, expected in lock['source_filenames_sha256'].items():
                if sha(src.read('swells_pack_v2/' + name)) != expected:
                    raise ValueError('original March source file changed')
        for name, expected in lock['archived_negative_controls_sha256'].items():
            if sha(source.read('inputs/negative_controls/' + name)) != expected:
                raise ValueError('negative control changed')
        capture = json.loads(source.read('results/source180_capture.json'))['lenses']
        arrays = []
        for lens in capture:
            data = source.read('inputs/' + lens['node_file'])
            if len(data) != 180 * 8 * 8 or sha(data) != lens['node_sha256']:
                raise ValueError('changed six-by-180 frozen node data')
            arrays.append(list(struct.iter_unpack('>8d', data)))
    if tuple(x['lens_id'] for x in capture) != LENSES or tuple(x['lens_id'] for x in info) != LENSES:
        raise ValueError('wrong six-lens source order')
    return capture, info, arrays


class Lens:
    def __init__(self, capture, source_info, rows, gamma):
        self.name = capture['lens_id']
        s = source_info['source_scalar_binary64_hex']
        self.p = {k: Q.from_float(float.fromhex(s[k])) for k in ('Mb','Md','a','Rd','delta','r0','n')}
        self.C4pi = Q.from_float(float.fromhex(s['C4pi']))
        self.r = [Q.from_float(z[0]) for z in rows]
        self.w = [Q.from_float(z[1]) for z in rows]
        self.rho = [Q.from_float(z[3]) for z in rows]
        if len(self.r)!=180 or any(self.r[i]>=self.r[i+1] for i in range(179)):
            raise ValueError('not original increasing 180-node source mesh')
        if self.r[-1] != 120 or any(x <= 0 for x in self.w) or any(x < 0 for x in self.rho):
            raise ValueError('source mesh / clipped density / weight violation')
        self.gamma = gamma
        self.cache = {}

    def point(self, r: Q):
        if r in self.cache:
            return self.cache[r]
        p=self.p; y=r/(2*p['Rd'])
        F,Fp,(i0,i1,k0,k1)=bessel_F_Fp(y,self.gamma)
        Fpp=4*F-2*Fp/Iv(y)-2*i1*k1/Iv(y*y)
        B=p['Mb']*Iv(r)**2/(Iv(r+p['a'])**2)+p['Md']*Iv(y)**3*F
        Bp=2*p['Mb']*p['a']*Iv(r)/(Iv(r+p['a'])**3)+p['Md']/(2*p['Rd'])*(3*Iv(y)**2*F+Iv(y)**3*Fp)
        G,Gp=gate(r,p['r0'],p['n'],p['delta'])
        M=B*G
        Mp=Bp*G+B*Gp
        if F.low()<=0 or Fp.high()>=0 or Fpp.low()<=0 or M.low()<0:
            raise ValueError('Bessel/Stieltjes sign interval failure')
        ans=(M,Mp,F,Fp,Fpp,G)
        self.cache[r]=ans
        return ans

    def derivatives(self, lo: Q, hi: Q):
        """All-real cell enclosures using complete monotonicity of F(y).

        For y>0, F=I0 K0-I1 K1 = (2/pi)*integral_0^pi
        K0(2 y sin(t))*sin(t)^2 dt. K0 has a positive Laplace
        representation, so F>0, F'<0, F''>0, F'''<0.
        Thus endpoint outward F/F'/F'' intervals enclose every real y
        in the entire cell. No finite sampling monotonicity assumption.
        """
        if not 0<lo<hi:
            raise ValueError('strictly positive ordered real source cell')
        v0,v1=self.point(lo),self.point(hi);p=self.p
        F=Iv(v1[2].low(),v0[2].high())
        Fp=Iv(v0[3].low(),v1[3].high())
        Fpp=Iv(v1[4].low(),v0[4].high())
        r=Iv(lo,hi);y=r/(2*p['Rd'])
        B=p['Mb']*r**2/(r+p['a'])**2+p['Md']*y**3*F
        Bp=2*p['Mb']*p['a']*r/(r+p['a'])**3+p['Md']/(2*p['Rd'])*(3*y*y*F+y**3*Fp)
        Bpp=2*p['Mb']*p['a']*(p['a']-2*r)/(r+p['a'])**4 + p['Md']/(2*p['Rd'])**2*(6*y*F+6*y*y*Fp+y**3*Fpp)
        G=Iv(v0[5].low(),v1[5].high())
        delta,n=p['delta'],p['n']
        f0=v0[5]/(delta*(1+v0[5]));f1=v1[5]/(delta*(1+v1[5]))
        f=Iv(f0.low(),f1.high())
        if f.low()<=0 or f.high()>=1 or (1-delta*f).low()<=0:
            raise ValueError('gate range failed')
        fp=n*f*(1-f)/r
        fpp=n*f*(1-f)/(r*r)*(n*(1-2*f)-1)
        Gp=delta*fp/(1-delta*f)**2
        Gpp=delta*fpp/(1-delta*f)**2 + 2*delta**2*fp**2/(1-delta*f)**3
        Mp=Bp*G+B*Gp
        Mpp=Bpp*G+2*Bp*Gp+B*Gpp
        return Mp,Mpp

    def cell(self, A: Q, lo: Q, hi: Q):
        u0,u1=projected_u(A,lo),projected_u(A,hi)
        du=u1-u0
        if du.low()<=0:
            raise ValueError('transformed mesh monotonicity')
        M0,M1=self.point(lo)[0],self.point(hi)[0]
        Mp,Mpp=self.derivatives(lo,hi)
        rv=Iv(lo,hi);uv=Iv(u0.low(),u1.high())
        rup=rv**3*uv/Iv(A*A)
        rpu=rv**3*(1+2*uv*uv)/(Iv(A*A)*(1-uv*uv))
        fpp_bound=Mpp.bound_abs()*rup.bound_abs()**2+Mp.bound_abs()*rpu.bound_abs()
        error=du.high()**3*fpp_bound/12
        trap=du*(M0+M1)/2
        return trap-Iv(error),trap+Iv(error),error

    def continuous(self, A: Q, *, bisections: int=120):
        a,b=self.r[0],self.r[-1]
        if not a<A<b:
            raise ValueError('fixed diagnostic aperture strictly inside original source support')
        knots=[A]+[r for r in self.r if A<r<b]+[b]
        cells={};heap=[]
        def add(lo,hi):
            value=self.cell(A,lo,hi)
            cells[(lo,hi)]=value
            heapq.heappush(heap,(-value[2],lo,hi))
        for lo,hi in zip(knots,knots[1:]):add(lo,hi)
        for _ in range(bisections):
            while heap:
                neg,lo,hi=heapq.heappop(heap)
                if (lo,hi) in cells and cells[(lo,hi)][2]==-neg:
                    break
            else:
                raise ValueError('empty interval refinement queue')
            cells.pop((lo,hi))
            mid=(lo+hi)/2
            add(lo,mid);add(mid,hi)
        integral=Iv(0)
        for lower,upper,_ in cells.values():
            integral=integral+Iv(lower.low(),upper.high())
        boundary=self.point(b)[0]*(1-projected_u(A,b))-self.point(a)[0]
        return boundary+integral,sum((v[2] for v in cells.values()),Q()),len(cells)

    def frozen_discrete(self,A:Q):
        result=Iv(0)
        for r,w,rho in zip(self.r,self.w,self.rho):
            result=result+Iv(w*self.C4pi*r*r*rho)*cylinder_phi(A,r)
        return result


def load_apertures(path: Path):
    raw=path.read_bytes()
    if sha(raw)!=DIAGNOSTIC_SHA:
        raise ValueError('wrong historical diagnostic SHA')
    data=json.loads(raw)
    if data['original_source_46plus3_sha256']!=SOURCE_SHA or data['original_source_parent_sha256']!=PARENT_SHA:
        raise ValueError('wrong source diagnostic')
    if data['original_March_H_error_or_root_count_certified'] or data['physical_provider_admitted']:
        raise ValueError('diagnostic has an unadmitted claim')
    entries=data['lens_results']
    if len(entries)!=6 or tuple(v['lens'] for v in entries)!=LENSES or any(not v['not_a_rigorous_interval_certificate'] for v in entries):
        raise ValueError('wrong six-lens diagnostic')
    return entries


def run(external_zip:Path, aperture_json:Path, bisections:int=120):
    if bisections<0 or bisections>100000:
        raise ValueError('invalid refinement steps')
    source_hash=sha(external_zip.read_bytes())
    capture,info,arrays=load_external(external_zip)
    apertures=load_apertures(aperture_json)
    gamma=euler_gamma()
    output=[]
    for c,sm,rows,d in zip(capture,info,arrays,apertures):
        lens=Lens(c,sm,rows,gamma)
        A_float=d['circularized_aperture_kpc']
        if type(A_float) is not float or not A_float>0:
            raise ValueError('aperture is not a finite binary64 diagnostic')
        A=Q.from_float(A_float)
        t=time.monotonic()
        P,err,ncells=lens.continuous(A,bisections=bisections)
        Qf=lens.frozen_discrete(A)
        D=Qf-P
        result={
          'lens':lens.name,
          'aperture_selected_diagnostic_binary64_hex':A_float.hex(),
          'selected_diagnostic_only_not_entire_band':True,
          'source_k180_interval_integer_Msun':[floor(Qf.low()),ceil(Qf.high())],
          'selected_continuum_interval_integer_Msun':[floor(P.low()),ceil(P.high())],
          'Q_March_minus_P_selected_continuum_interval_integer_Msun':[floor(D.low()),ceil(D.high())],
          'signed_positive_discrepancy_proven_for_this_A':D.low()>0,
          'trapezoid_remainder_sum_integer_Msun_upper':ceil(err),
          'integration_cells':ncells,
          'original_source_180_nodes_sha256':c['node_sha256'],
        }
        print(lens.name,'fixed diagnostic A',A_float.hex(),'strict sign',D.low()>0,
              'D integer enclosure',result['Q_March_minus_P_selected_continuum_interval_integer_Msun'],
              'cells',ncells,'seconds_diagnostic',round(time.monotonic()-t,2),flush=True)
        output.append(result)
    return {
      'schema':'HIST001D_ORIGINAL_MARCH180_ROOT_APERTURE_SELECTED_SMOOTH_CONTINUUM_FIXED_DIAGNOSTIC_INTERVAL_V1',
      'date':'2026-11-02',
      'external_saturation_archive_sha256':source_hash,
      'original_source_parent_sha256':PARENT_SHA,
      'original_46plus3_source_sha256':SOURCE_SHA,
      'diagnostic_A_input_sha256':DIAGNOSTIC_SHA,
      'arithmetic':'exact-rational outward 512-bit inherited Bessel source and sqrt; all-real F derivative intervals; transformed composite trapezoid remainder',
      'no_11520_node_replacement':True,
      'all_six_positive_fixed_A':all(x['signed_positive_discrepancy_proven_for_this_A'] for x in output),
      'original_off_grid_H_root_count_proved':False,
      'all_aperture_bands_proved':False,
      'selected_smooth_mathematical_mass_not_ESET_physical_source':True,
      'physical_provider_admitted':False,
      'empirical_validation':'NOT_ESTABLISHED',
      'lenses':output,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--external-zip',type=Path,required=True,help='protected source-bound candidate ZIP; never commit to public GitHub')
    parser.add_argument('--diagnostic-json',type=Path,required=True,help='external SHA-locked six diagnostic apertures, not a full root-band certificate')
    parser.add_argument('--bisections',type=int,default=120)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    result=run(args.external_zip,args.diagnostic_json,args.bisections)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    if not result['all_six_positive_fixed_A']:
        raise SystemExit('UNKNOWN / sign not certified on all diagnostic apertures')
    print('OUTPUT_SHA256',sha(args.out.read_bytes()))

if __name__=='__main__':main()
