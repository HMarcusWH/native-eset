#!/usr/bin/env python3
"""Source-conditional selected-M* full-H endpoint sign enclosures.

No physical lensing or global smooth-H uniqueness claim. The selected mathematical
M* derivative-positive certificate, source finite B/D/q and earlier interval
Bessel engine are imported under SHA manifest checks; no independent Bessel
reimplementation is implied by this script.
"""
from __future__ import annotations
import argparse,hashlib,json,sys,time,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
REFERENCES=HERE.parent
if not (REFERENCES/'hist001d_k180_root_aperture_candidate').is_dir():
    REFERENCES=HERE.parent/'reference'  # support local protected clean extraction
sys.path.insert(0,str(REFERENCES/'hist001d_k180_root_aperture_candidate'))
sys.path.insert(0,str(REFERENCES/'hist001d_k180_crossing_band_candidate'))
from root_aperture_certifier import load_external,Lens,euler_gamma  # noqa: E402
from crossing_band_certifier import q_source_metadata  # noqa: E402
from full_h_finite_source import FiniteLens,ff,floor,ceil,SOURCE_SHA,LENSES  # noqa: E402

def sha(b):return hashlib.sha256(b).hexdigest()

def verify_selected_derivative_audit(release,source_node_sha,i):
    with zipfile.ZipFile(release) as z:
        manifest=json.loads(z.read('MANIFEST_SHA256.json'))
        for key,digest in manifest['files'].items():
            if sha(z.read(key))!=digest:raise ValueError('derivative release manifest mismatch '+key)
        entry=json.loads(z.read(f'results/selected_mass_prime_{i}.json'))
    if (entry['lens']!=LENSES[i] or
            entry['source_180_node_sha256']!=source_node_sha or
            entry['selected_mathematical_Mstar_prime_positive_everywhere'] is not True or
            entry['unresolved_cells']!=0 or
            entry['physical_density_source_admitted'] is not False):
        raise ValueError('selected Mprime mathematical positivity not supported')
    return entry

def execute(i,source,diag,release,out,bisects=16):
    capture,infos,arrays=load_external(source)
    qmeta=q_source_metadata(source)
    diagnostics=json.loads(diag.read_text())['lens_results']
    derivative=verify_selected_derivative_audit(release,capture[i]['node_sha256'],i)
    gamma=euler_gamma()
    c=capture[i];q=qmeta[i];dd=diagnostics[i]
    fl=FiniteLens(c['lens_id'],arrays[i],ff(float.fromhex(q['source_qb_hex'])),ff(float.fromhex(q['source_qd_hex'])),
                  ff(float.fromhex(c['original_sigma_hex'])),ff(float.fromhex(c['original_pi4_float_hex'])))
    _,left,right=fl.source_cell(ff(dd['sampled_R_root_kpc']))
    selected=Lens(c,infos[i],arrays[i],gamma)
    lowerA=fl.A_box(left)[0];upperA=fl.A_box(right)[1]
    baseleft=fl.pl(fl.B,left)+fl.pl(fl.D,left)-fl.Cpi*fl.sigma*left*left
    baseright=fl.pl(fl.B,right)+fl.pl(fl.D,right)-fl.Cpi*fl.sigma*right*right
    start=time.monotonic()
    p_lo,err_lo,nlo=selected.continuous(lowerA,bisections=bisects)
    p_hi,err_hi,nhi=selected.continuous(upperA,bisections=bisects)
    Hlo=floor(baseleft+p_lo.low());Hhi=ceil(baseright+p_hi.high())
    if Hlo<=0 or Hhi>=0:raise ValueError('selected smooth endpoint sign inconclusive')
    result={'schema':'HIST001D_SELECTED_MSMOOTH_FULL_H_SOURCE_CELL_ENDPOINT_SIGNS_V1',
            'lens':fl.name,'source_46plus3_sha256':SOURCE_SHA,'node_sha256':c['node_sha256'],
            'selected_Mprime_all_real_positive_certificate':True,
            'selected_Mprime_positive_dyadic_cells':derivative['all_real_verified_positive_dyadic_cells'],
            'R_cell_left_binary64_hex':float(left).hex(),
            'R_cell_right_binary64_hex':float(right).hex(),
            'A_left_exact_rational_lower':[str(lowerA.numerator),str(lowerA.denominator)],
            'A_right_exact_rational_upper':[str(upperA.numerator),str(upperA.denominator)],
            'selected_P_left_integer_Msun_lower':floor(p_lo.low()),
            'selected_P_right_integer_Msun_upper':ceil(p_hi.high()),
            'H_selected_left_integer_Msun_lower':Hlo,
            'H_selected_right_integer_Msun_upper':Hhi,
            'integration_bisections_per_endpoint':bisects,
            'selected_continuum_H_has_root_in_source_cell':True,
            'selected_continuum_global_root_uniqueness_proved':False,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED'}
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(fl.name,'H lower(left)',Hlo,'H upper(right)',Hhi,
          'integration cells',nlo,nhi,'seconds',round(time.monotonic()-start,1),flush=True)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',type=int,choices=range(6),required=True)
    for name in ['source','diag','release','out']:
        ap.add_argument('--'+name,required=True,type=Path)
    ap.add_argument('--bisects',type=int,default=16)
    a=ap.parse_args()
    execute(a.index,a.source,a.diag,a.release,a.out,a.bisects)
