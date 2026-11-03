#!/usr/bin/env python3
"""Protected HASH/CRC, independent witness, and optional clean full replay validator.

No source-only CI needs access to this protected artifact.
"""
import argparse,hashlib,json,sys,tempfile,zipfile,subprocess
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def verify(archive,full=False):
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('ZIP CRC failure')
        files=z.namelist()
        if len(files)!=len(set(files)):raise ValueError('duplicate names')
        if any(x.startswith('/') or '\\' in x or '..' in Path(x).parts for x in files):raise ValueError('unsafe ZIP path')
        manifest=json.loads(z.read('MANIFEST_SHA256.json'))
        if manifest.get('schema')!='HIST001D_MARCH180_SIGNED_STENCIL_VS_CONTINUUM_SOURCE_PROTECTED_V1':raise ValueError('release schema')
        if sorted(files)!=sorted(['MANIFEST_SHA256.json']+list(manifest['files'])):raise ValueError('unexpected or missing entry')
        for name,h in manifest['files'].items():
            if sha(z.read(name))!=h:raise ValueError('bad SHA '+name)
        expected={
         'inputs/upstream_float_k180_v1.zip':'d853e4184a570bb1de508658a53ac83eb2d12244b0b14699c14c314448cac5e5',
         'inputs/fixed_A_interval_v1r1.zip':'54eeec715a8f2b9514b88d7806cef84cb90aea54cdada0e0c11bf9489362051e',
         'inputs/crossing_bands_v1r2.zip':'cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77'}
        for name,h in expected.items():
            if manifest['files'][name]!=h:raise ValueError('incorrect parent '+name)
        res=json.loads(z.read('results/signed_stencil_decomposition_v1.json'))
        qa=json.loads(z.read('results/adversarial_signed_bias_v1.json'))
        independent=json.loads(z.read('results/independent_signed_bias_v1.json'))
        if (res['physical_provider_admitted'] is not False or res['empirical_validation']!='NOT_ESTABLISHED' or
                res['all_six_bandwise_bias_positive'] is not True or res['all_six_pointwise_bias_positive'] is not True or
                res['all_six_fixed_A_quadrature_remainder_sign_resolved'] is not True or len(res['lenses'])!=6 or
                qa['all_rejected'] is not True or len(qa['cases'])!=39 or
                independent['all_lenses_passed'] is not True or len(independent['lenses'])!=6):
            raise ValueError('unsupported result / QA status')
        with tempfile.TemporaryDirectory(prefix='hist001d-signed-stencil-release-') as t:
            wd=Path(t)
            for name in files:
                target=wd/name;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(z.read(name))
            ref=wd/'reference/hist001d_k180_signed_stencil_candidate'
            inputs=['--upstream',str(wd/'inputs/upstream_float_k180_v1.zip'),
                    '--point',str(wd/'inputs/fixed_A_interval_v1r1.zip'),
                    '--band',str(wd/'inputs/crossing_bands_v1r2.zip')]
            # Independently check every saved numerical inequality and original source identity.
            result=wd/'independent_replay.json'
            subprocess.run([sys.executable,str(ref/'verify_signed_bias.py'),*inputs,
                            '--receipt',str(wd/'results/signed_stencil_decomposition_v1.json'),
                            '--out',str(result)],check=True,cwd=wd)
            if result.read_bytes()!=z.read('results/independent_signed_bias_v1.json'):
                raise ValueError('independent replay bytes differ')
            if full:
                prod=wd/'producer_replay.json'
                subprocess.run([sys.executable,str(ref/'finite_difference_bias.py'),*inputs,
                                '--out',str(prod)],check=True,cwd=wd)
                if prod.read_bytes()!=z.read('results/signed_stencil_decomposition_v1.json'):
                    raise ValueError('producer byte replay differs')
                qaout=wd/'qa_replay.json'
                subprocess.run([sys.executable,str(ref/'adversarial_signed_bias.py'),*inputs,
                                '--receipt',str(prod),'--out',str(qaout)],check=True,cwd=wd)
                if qaout.read_bytes()!=z.read('results/adversarial_signed_bias_v1.json'):
                    raise ValueError('adversarial QA byte replay differs')
                subprocess.run([sys.executable,'-m','pytest','-q',str(wd/'tests/historical/test_hist001d_k180_signed_stencil_source_free.py')],check=True,cwd=wd)
    print('SIGNED_STENCIL_RELEASE_PASS', 'full' if full else 'quick', 'sha',sha(Path(archive).read_bytes()),'files',len(files),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--full',action='store_true')
    a=ap.parse_args();verify(a.archive,a.full)
