#!/usr/bin/env python3
"""Source-bound nonpromoting HIST-001D PR59 signed March K180 replay.

Authoritative input is an independently supplied SHA-256 of the *whole ZIP*.
Internal manifest hashes are necessary for inventory integrity but cannot
by themselves authenticate edited executable code. The independent verifier,
producer and historical QA execute from a freshly extracted source tree,
under isolated Python with assertions stripped, and their outputs are compared
byte-for-byte with separate immutable historical result SHA locks.

This is a conditional exact-rational K180/math-continuum comparator, NOT a
physical Weyl lensing provider, model validation or original off-grid solver.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, stat, subprocess, sys, tempfile, zipfile
from pathlib import Path, PurePosixPath

PUBLIC = 'reference/hist001d_k180_signed_stencil_candidate/'
SCHEMA = 'HIST001D_MARCH180_SIGNED_STENCIL_VS_CONTINUUM_SOURCE_PROTECTED_V1'
SOURCE = 'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
PARENT_SHA = {
 'inputs/upstream_float_k180_v1.zip':'d853e4184a570bb1de508658a53ac83eb2d12244b0b14699c14c314448cac5e5',
 'inputs/fixed_A_interval_v1r1.zip':'54eeec715a8f2b9514b88d7806cef84cb90aea54cdada0e0c11bf9489362051e',
 'inputs/crossing_bands_v1r2.zip':'cec7a5dccb210a89ad4a674f74b328639bbf2d287d038c491f88b964fa8aca77',
}
RESULT_SHA = {
 'results/signed_stencil_decomposition_v1.json':'0c6b6013e0245b1c4d8bc867b8dc70d99aac9714b53e3903fd019b1776bfea3b',
 'results/independent_signed_bias_v1.json':'de237c9050add37249af309da6cc1d8a09c0b25bbc227060043a2d9413e08847',
 'results/adversarial_signed_bias_v1.json':'3198a89ca9140345cd345e803090ffd6c3e6628e9fd2c7a3f48ece2f6fe266be',
}
# Source hash authority is bound to this public source-only review script.
# Patched mathematical producer/checker SHA are populated at release sealing.
CRITICAL_SOURCE_SHA = {
 PUBLIC+'finite_difference_bias.py':'5eb8cf55b8001ea7878574a8e5020a5aa8f26b8be56f73c5df0ad5d0e10f318f',
 PUBLIC+'verify_signed_bias.py':'78444465bd866e57e0c7cd39c5a2f9155e8b9bc00a4bf572045c1d51dde81664',
 PUBLIC+'adversarial_signed_bias.py':'46960754429e76e383863c7213407ba9f58a4e34ac3cbde0b9598944db28f6b3',
}
LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')
MAX_ZIP_BYTES=22_000_000
MAX_MEMBERS=25
MAX_TOTAL_BYTES=26_000_000
EXPECTED_MEMBER_COUNT=18


def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def is_sha(value:object)->bool:return type(value) is str and re.fullmatch(r'[0-9a-f]{64}',value) is not None

def safe_path(name:object)->bool:
    if (type(name) is not str or not name or name.startswith('/') or '\\' in name
        or ':' in name or any(ord(c)<32 for c in name)):
        return False
    reserved={'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),*(f'LPT{i}' for i in range(1,10))}
    for part in name.split('/'):
        if (part in ('', '.', '..') or part.rstrip(' .')!=part or
            part.split('.')[0].upper() in reserved):return False
    return PurePosixPath(name).as_posix()==name

def inspect_members(z:zipfile.ZipFile)->tuple[str,...]:
    members=z.infolist()
    if len(members)!=EXPECTED_MEMBER_COUNT or len(members)>MAX_MEMBERS or sum(x.file_size for x in members)>MAX_TOTAL_BYTES:
        raise ValueError('UNRESOLVED: protected release membership/decompressed byte budget')
    names=[x.filename for x in members]
    if (len(names)!=len(set(names)) or len({n.casefold() for n in names})!=len(names)
        or not all(safe_path(n) for n in names)):
        raise ValueError('UNRESOLVED: duplicate, traversal, cross-platform alias or unsafe ZIP filename')
    for member in members:
        mode=member.external_attr>>16
        if (member.is_dir() or stat.S_IFMT(mode) not in (0,stat.S_IFREG)
            or member.flag_bits & 1):
            raise ValueError('UNRESOLVED: symlink, directory, nonregular or encrypted ZIP member')
    if z.testzip() is not None:raise ValueError('UNRESOLVED: ZIP member CRC failed')
    return tuple(names)

def inspect_archive(archive:Path,external_sha:str)->dict:
    if not is_sha(external_sha):
        raise ValueError('UNRESOLVED: independently supplied whole-ZIP SHA-256 required')
    if not archive.is_file() or archive.stat().st_size>MAX_ZIP_BYTES:
        raise ValueError('UNRESOLVED: protected release missing/oversized')
    if sha(archive.read_bytes())!=external_sha:
        raise ValueError('UNRESOLVED: protected release failed external whole-ZIP SHA-256 lock')
    with zipfile.ZipFile(archive) as z:
        names=inspect_members(z)
        if 'MANIFEST_SHA256.json' not in names:
            raise ValueError('UNRESOLVED: protected manifest missing')
        mf=json.loads(z.read('MANIFEST_SHA256.json'))
        if (mf.get('schema')!=SCHEMA or mf.get('version')!=2 or mf.get('release_version')!='v1r2'
            or mf.get('claim_status')!='NONPROMOTING'):
            raise ValueError('UNRESOLVED: wrong release schema/version/claim status')
        if (mf.get('original_46plus3_source_sha256')!=SOURCE or
            mf.get('physical_provider_admitted') is not False or
            mf.get('empirical_validation')!='NOT_ESTABLISHED' or
            mf.get('scientific_authority_promoted') is not False or
            mf.get('source_execution_attested') is not True):
            raise ValueError('UNRESOLVED: invalid source/claim lineage')
        files=mf.get('files')
        if type(files) is not dict or set(names)!=set(files)|{'MANIFEST_SHA256.json'}:
            raise ValueError('UNRESOLVED: missing or extra SHA-untracked source/data')
        if len(files)!=EXPECTED_MEMBER_COUNT-1:
            raise ValueError('UNRESOLVED: incomplete release source inventory')
        for path,digest in files.items():
            if not safe_path(path) or not is_sha(digest) or sha(z.read(path))!=digest:
                raise ValueError('UNRESOLVED: release member SHA mismatch '+str(path))
        for path,digest in {**PARENT_SHA,**RESULT_SHA,**CRITICAL_SOURCE_SHA}.items():
            if files.get(path)!=digest:
                raise ValueError('UNRESOLVED: wrong protected parent/result/critical proof source '+path)
        if Path(__file__).resolve(strict=True).read_bytes() != z.read(PUBLIC+'attested_replay_v1r2.py'):
            raise ValueError('UNRESOLVED: executing attestor is not the whole-release authenticated attestor')
        required={PUBLIC+f for f in ('finite_difference_bias.py','verify_signed_bias.py','adversarial_signed_bias.py',
                                     'verify_release.py','attested_replay_v1r2.py')}
        required |= {'tests/historical/test_hist001d_k180_signed_stencil_source_free.py',
                     'tests/historical/test_hist001d_signed_stencil_v1r2_failclosed.py',
                     'docs/HIST001D_SIGNED_STENCIL_V1R2_FAILCLOSED_SCOPE.md'}
        if not required.issubset(files):raise ValueError('UNRESOLVED: missing critical executable/test/scope member')
        return mf

def inspect_extracted(archive:Path,root:Path,manifest:dict,exact_inventory:bool=True)->int:
    if root.is_symlink():raise ValueError('UNRESOLVED: symlinked source extraction root')
    root=root.resolve(strict=True)
    if not root.is_dir():raise ValueError('UNRESOLVED: expected directory root')
    if exact_inventory:
        if any(x.is_symlink() for x in root.rglob('*')):
            raise ValueError('UNRESOLVED: symlink in extracted source')
        observed={x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file()}
        if observed!=set(manifest['files'])|{'MANIFEST_SHA256.json'}:
            raise ValueError('UNRESOLVED: extracted source inventory differs from authenticated release')
    with zipfile.ZipFile(archive) as z:
        if (root/'MANIFEST_SHA256.json').read_bytes()!=z.read('MANIFEST_SHA256.json'):
            raise ValueError('UNRESOLVED: local manifest changed')
        for path,h in manifest['files'].items():
            local=root/path
            if (not local.is_file() or local.is_symlink()
                or not local.resolve(strict=True).is_relative_to(root)
                or sha(local.read_bytes())!=h or local.read_bytes()!=z.read(path)):
                raise ValueError('UNRESOLVED: edited local executable/data does not match signed release '+path)
    return len(manifest['files'])

def _run(script:Path,work_dir:Path,args:list[str],budget:int,label:str)->str:
    bootstrap=('import sys,runpy;from pathlib import Path;'
               'p=Path(sys.argv[1]).resolve();sys.argv=[str(p),*sys.argv[2:]];'
               'sys.path.insert(0,str(p.parent));runpy.run_path(str(p),run_name="__main__")')
    env={k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONHOME','PYTHONINSPECT','PYTHONSTARTUP')}
    env['PYTHONNOUSERSITE']='1'
    try:
        r=subprocess.run([sys.executable,'-I','-B','-OO','-c',bootstrap,str(script),*args],
                         text=True,capture_output=True,cwd=work_dir,env=env,timeout=budget,check=False)
    except subprocess.TimeoutExpired as exc:
        raise ValueError('UNRESOLVED: '+label+' exceeded execution budget') from exc
    if r.returncode:
        raise ValueError('UNRESOLVED: '+label+' exited '+str(r.returncode)+': '+r.stderr[-700:])
    return r.stdout

def replay(archive:Path,external_sha:str,extracted_root:Path|None=None,budget_seconds:int=180)->dict:
    if type(budget_seconds) is not int or budget_seconds<1:
        raise ValueError('UNRESOLVED: invalid or zero execution budget')
    archive=archive.resolve(strict=True)
    mf=inspect_archive(archive,external_sha)
    if extracted_root is not None:inspect_extracted(archive,extracted_root,mf,True)
    with tempfile.TemporaryDirectory(prefix='hist001d_pr59_attested_') as d:
        tmp=Path(d);source=tmp/'source';source.mkdir()
        with zipfile.ZipFile(archive) as z:
            for item in z.infolist():
                target=source/item.filename
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(z.read(item.filename))
        n=inspect_extracted(archive,source,mf,True)
        out=tmp/'new';out.mkdir()
        base=['--upstream',str(source/'inputs/upstream_float_k180_v1.zip'),
              '--point',str(source/'inputs/fixed_A_interval_v1r1.zip'),
              '--band',str(source/'inputs/crossing_bands_v1r2.zip')]
        result=out/'signed_stencil_decomposition_v1.json'
        a=_run(source/PUBLIC/'finite_difference_bias.py',source,base+['--out',str(result)],budget_seconds,'original source-bound mathematical producer')
        if 'COMPLETE 6 ' not in a or not result.is_file() or sha(result.read_bytes())!=RESULT_SHA['results/signed_stencil_decomposition_v1.json']:
            raise ValueError('UNRESOLVED: signed K180 mathematical producer differs')
        data=json.loads(result.read_bytes())
        if (len(data.get('lenses',[]))!=6 or tuple(x.get('lens') for x in data['lenses'])!=LENSES
            or data.get('physical_provider_admitted') is not False or data.get('empirical_validation')!='NOT_ESTABLISHED'):
            raise ValueError('UNRESOLVED: unexpected source-conditional six lens claim')
        independent=out/'independent_signed_bias_v1.json'
        output=_run(source/PUBLIC/'verify_signed_bias.py',source,base+['--receipt',str(result),'--out',str(independent)],budget_seconds,'independent exact-rational bisection verifier')
        if ('PASS_INDEPENDENT 6 '+RESULT_SHA['results/independent_signed_bias_v1.json'] not in output
            or not independent.is_file() or sha(independent.read_bytes())!=RESULT_SHA['results/independent_signed_bias_v1.json']):
            raise ValueError('UNRESOLVED: independent proof arithmetic did not reproduce sealed output')
        qa=out/'adversarial_signed_bias_v1.json'
        stdout=_run(source/PUBLIC/'adversarial_signed_bias.py',source,base+['--receipt',str(result),'--out',str(qa)],budget_seconds,'original adversarial negative suite')
        if ('QA_REJECTED 39 SHA '+RESULT_SHA['results/adversarial_signed_bias_v1.json'] not in stdout
            or not qa.is_file() or sha(qa.read_bytes())!=RESULT_SHA['results/adversarial_signed_bias_v1.json']):
            raise ValueError('UNRESOLVED: original 39 adversarial claims were not rejected')
        # Explicitly exclude changes from the protected source/result to publicly
        # deployed physical equations. The matched archives and results are the scope.
        return {'status':'CERTIFIED_CONDITIONAL_HISTORICAL_SIGNED_K180_MATHEMATICAL_REPLAY',
                'external_whole_archive_sha256':external_sha,
                'historical_source_sha256':SOURCE,
                'attested_manifest_source_members':n,
                'source_lenses':6,'independent_exact_rational_lenses':6,
                'original_adversarial_mutations_rejected':39,
                'source_parent_zip_shas':PARENT_SHA,
                'result_receipt_shas':RESULT_SHA,
                'independent_Bessel_special_function_engine_reproduced':False,
                'native_physical_Weyl_provider_admitted':False,
                'physical_provider_admitted':False,
                'empirical_validation':'NOT_ESTABLISHED',
                'scientific_authority_promoted':False}

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument('--archive',type=Path)
    p.add_argument('--expected-sha256')
    p.add_argument('--extracted-root',type=Path)
    p.add_argument('--budget-seconds',type=int,default=180)
    args=p.parse_args()
    try:
        if args.archive is None or args.expected_sha256 is None:
            raise ValueError('UNRESOLVED: --archive and independently pinned --expected-sha256 are mandatory')
        result=replay(args.archive,args.expected_sha256,args.extracted_root,args.budget_seconds)
    except (ValueError,TypeError,KeyError,OSError,RuntimeError,zipfile.BadZipFile,json.JSONDecodeError,OverflowError) as exc:
        print(json.dumps({'status':'UNRESOLVED','reason':str(exc)},sort_keys=True));return 2
    print(json.dumps(result,indent=2,sort_keys=True));return 0
if __name__=='__main__':sys.exit(main())
