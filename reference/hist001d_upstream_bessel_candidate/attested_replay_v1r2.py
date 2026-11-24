#!/usr/bin/env python3
"""HIST-001D PR58 fail-closed historical K180 source/float-mass replay.

An independently trusted *whole-file* ZIP SHA-256 is the release authority.
The sealed historical source reproduces its 180-node density/float masses;
an independent exact-dyadic checker and adversarial QA are then executed
from authenticated source bytes in fresh isolated Python processes.

No certified arbitrary-input SciPy/libm ulps, continuum integration error,
physical Weyl lensing provider, blind validation or cosmology is inferred.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import zipfile

SCHEMA = 'HIST001D_BESSEL_SOURCE_GRADIENT_K180_PROTECTED_RELEASE_V1'
SOURCE_SHA = 'fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
SAT_SHA = '99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce'
ORIGINAL_RESULT_SHA = '4d56fce6b8f28675000585a31efea137c0a9b0c1a5fabd4e730346bbf49008e6'
INDEPENDENT_RESULT_SHA = '831db0aa6654fa46af88c31158fcf015fb209628f41b5ea01c7f4dac7204420a'
ADVERSARIAL_RESULT_SHA = '50f74d15b71af099056013b52abf6cbfe6c31f98f2534ec3e9c3960f7d7510e6'
LENSES = ('J0822+1828', 'J0915+4211', 'J0930+2855', 'J1021+2028', 'J1111+2234', 'J1135+3720')
PUBLIC = 'reference/hist001d_upstream_bessel_candidate/'
MASS_PREFIX = 'inputs/frozen_source_mass_'
ORIGINAL_FILES = (
    PUBLIC+'upstream_float_split.py',
    PUBLIC+'independent_stencil_check.py',
    PUBLIC+'adversarial_qa.py',
    PUBLIC+'verify_release.py',
    PUBLIC+'attested_replay_v1r2.py',
    'reference/hist001d_k180_saturation_candidate/all180_math.py',
    'reference/hist001d_k180_saturation_candidate/all180_independent.py',
)
RESULTS = {
    'results/upstream_float_split_v1.json': ORIGINAL_RESULT_SHA,
    'results/independent_stencil_check_v1.json': INDEPENDENT_RESULT_SHA,
    'results/adversarial_qa_v1.json': ADVERSARIAL_RESULT_SHA,
}
MAX_ZIP_SIZE = 24_000_000
MAX_MEMBERS = 48
MAX_DECOMPRESSED = 28_000_000


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def valid_digest(h: str) -> bool:
    return type(h) is str and re.fullmatch(r'[0-9a-f]{64}', h) is not None


def safe_path(name: str) -> bool:
    if (type(name) is not str or not name or '\\' in name or name.startswith('/')
        or ':' in name or any(ord(c) < 32 for c in name)):
        return False
    reserved = {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(1,10)),
                *(f'LPT{i}' for i in range(1,10))}
    for part in name.split('/'):
        if (part in ('', '.', '..') or part.rstrip(' .') != part or
            part.split('.')[0].upper() in reserved):
            return False
    return PurePosixPath(name).as_posix() == name


def check_member_inventory(z: zipfile.ZipFile) -> tuple[str,...]:
    members = z.infolist()
    if len(members) > MAX_MEMBERS or sum(m.file_size for m in members) > MAX_DECOMPRESSED:
        raise ValueError('UNRESOLVED: archive member count / uncompressed size budget exceeded')
    names = [m.filename for m in members]
    if (len(set(names)) != len(names) or
        len({n.casefold() for n in names}) != len(names) or
        not all(safe_path(n) for n in names)):
        raise ValueError('UNRESOLVED: duplicate, cross-platform alias, traversal, or unsafe ZIP member')
    for m in members:
        mode = m.external_attr >> 16
        typ = stat.S_IFMT(mode)
        if m.is_dir() or typ not in (0, stat.S_IFREG):
            raise ValueError('UNRESOLVED: directory/symlink/nonregular ZIP member')
        if m.flag_bits & 0x1:
            raise ValueError('UNRESOLVED: encrypted ZIP member not supported')
    if z.testzip() is not None:
        raise ValueError('UNRESOLVED: protected ZIP CRC check failed')
    return tuple(names)


def verify_release(archive: Path, external_sha: str) -> dict:
    if not valid_digest(external_sha):
        raise ValueError('UNRESOLVED: independent whole-ZIP SHA-256 authority is required')
    if not archive.is_file() or archive.stat().st_size > MAX_ZIP_SIZE:
        raise ValueError('UNRESOLVED: missing/oversized protected archive')
    if sha(archive.read_bytes()) != external_sha:
        raise ValueError('UNRESOLVED: independently pinned full ZIP SHA differs')
    with zipfile.ZipFile(archive) as z:
        names = check_member_inventory(z)
        if 'MANIFEST_SHA256.json' not in names:
            raise ValueError('UNRESOLVED: protected release manifest missing')
        manifest = json.loads(z.read('MANIFEST_SHA256.json'))
        if manifest.get('schema') != SCHEMA or manifest.get('release_version') != 'v1r2':
            raise ValueError('UNRESOLVED: wrong release identity/version')
        if manifest.get('claim_status') != 'SOURCE_CONDITIONAL_MATHEMATICAL_NONPROMOTING':
            raise ValueError('UNRESOLVED: unexpected mathematical claim scope')
        if (manifest.get('physical_provider_admitted') is not False or
            manifest.get('empirical_validation') != 'NOT_ESTABLISHED' or
            manifest.get('scientific_authority_promoted') is not False):
            raise ValueError('UNRESOLVED: forbidden scientific promotion')
        if (manifest.get('source_original_46plus3_sha256') != SOURCE_SHA or
            manifest.get('input_saturation_sha256') != SAT_SHA or
            manifest.get('source_execution_attested') is not True):
            raise ValueError('UNRESOLVED: wrong source lineage / source attestation')
        files = manifest.get('files')
        if type(files) is not dict or set(names) != set(files) | {'MANIFEST_SHA256.json'}:
            raise ValueError('UNRESOLVED: missing/extra untracked release members')
        if len(files) < 21:
            raise ValueError('UNRESOLVED: incomplete v1r2 archive')
        for name, h in files.items():
            if not safe_path(name) or not valid_digest(h) or sha(z.read(name)) != h:
                raise ValueError('UNRESOLVED: source/member SHA mismatch '+str(name))
        for name,h in {**RESULTS,'inputs/saturation_parent.zip':SAT_SHA}.items():
            if files.get(name) != h:
                raise ValueError('UNRESOLVED: original numerical/source parent changed '+name)
        for lens in LENSES:
            name = MASS_PREFIX+lens.replace('+','p')+'.be64'
            if name not in files or len(z.read(name)) != 180*8:
                raise ValueError('UNRESOLVED: protected binary64 mass sample missing or incomplete '+lens)
        for name in ORIGINAL_FILES + (
            'tests/historical/test_hist001d_upstream_bessel_mass_sourcefree.py',
            'tests/historical/test_hist001d_upstream_v1r2_attested.py',
            'docs/HIST001D_UPSTREAM_BESSEL_FLOAT_V1R2_ATTESTED_SCOPE.md',
        ):
            if name not in files:
                raise ValueError('UNRESOLVED: missing proof-critical source/test '+name)
        return manifest


def verify_extracted(archive: Path, root: Path, manifest: dict, exact_inventory: bool=True) -> int:
    if root.is_symlink():
        raise ValueError('UNRESOLVED: symlinked extracted source root')
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('UNRESOLVED: invalid extracted source root')
    if exact_inventory:
        if any(p.is_symlink() for p in root.rglob('*')):
            raise ValueError('UNRESOLVED: redirected executable/source path in extracted tree')
        present = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        if present != set(manifest['files']) | {'MANIFEST_SHA256.json'}:
            raise ValueError('UNRESOLVED: local extracted source has missing/extra files')
    with zipfile.ZipFile(archive) as z:
        if sha((root/'MANIFEST_SHA256.json').read_bytes()) != sha(z.read('MANIFEST_SHA256.json')):
            raise ValueError('UNRESOLVED: local manifest differs from protected ZIP')
        for name,h in manifest['files'].items():
            local=root/name
            if (not local.is_file() or local.is_symlink() or
                not local.resolve(strict=True).is_relative_to(root) or
                sha(local.read_bytes()) != h or local.read_bytes() != z.read(name)):
                raise ValueError('UNRESOLVED: local executable/data differs from authenticated ZIP '+name)
    return len(manifest['files'])


def _run(root: Path, script: str, args: list[str], budget: int, name: str) -> str:
    source = root/script
    # -I removes ambient PYTHONPATH and script directory: the only added script
    # directory is inside the freshly SHA-authenticated temporary source tree.
    boot = ('import sys,runpy; from pathlib import Path; '
            'p=Path(sys.argv[1]).resolve(); sys.argv=[str(p),*sys.argv[2:]]; '
            'sys.path.insert(0,str(p.parent)); runpy.run_path(str(p),run_name="__main__")')
    env={k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONHOME','PYTHONSTARTUP','PYTHONINSPECT')}
    env['PYTHONNOUSERSITE']='1'
    try:
        p=subprocess.run([sys.executable,'-I','-B','-OO','-c',boot,str(source),*args],
                         cwd=root,env=env,text=True,capture_output=True,timeout=budget,check=False)
    except subprocess.TimeoutExpired as exc:
        raise ValueError('UNRESOLVED: '+name+' exceeded execution budget') from exc
    if p.returncode:
        raise ValueError('UNRESOLVED: '+name+' failed (exit '+str(p.returncode)+'): '+p.stderr[-800:])
    return p.stdout


def replay(archive: Path, expected_sha: str, extracted_root: Path | None=None,
           budget_seconds: int=180, run_tests: bool=False) -> dict:
    if type(budget_seconds) is not int or budget_seconds < 1:
        raise ValueError('UNRESOLVED: zero or invalid source replay budget')
    archive=archive.resolve(strict=True)
    manifest=verify_release(archive,expected_sha)
    if extracted_root is not None:
        verify_extracted(archive,extracted_root,manifest,True)
    with tempfile.TemporaryDirectory(prefix='hist001d_pr58_attested_') as d:
        folder=Path(d)
        source=folder/'source';source.mkdir()
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                target=source/member.filename
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(z.read(member.filename))
        verified=verify_extracted(archive,source,manifest,True)
        work=folder/'replayed';work.mkdir()
        for name in ORIGINAL_FILES:
            if name.endswith(('upstream_float_split.py','all180_math.py','all180_independent.py')):
                dest=work/name;dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes((source/name).read_bytes())
        out=work/'results/upstream_float_split_v1.json'
        out.parent.mkdir(parents=True,exist_ok=True)
        stdout=_run(work,PUBLIC+'upstream_float_split.py',
                    ['--sat',str(source/'inputs/saturation_parent.zip'),'--out',str(out)],
                    budget_seconds,'historical 180-node original-source producer')
        lines=[line for line in stdout.splitlines() if '180/180 source density' in line]
        if len(lines)!=6 or any(not lines[i].startswith(LENSES[i]+' 180/180') for i in range(6)):
            raise ValueError('UNRESOLVED: original density replay not exactly six ordered 180-node lenses')
        if not out.is_file() or sha(out.read_bytes()) != ORIGINAL_RESULT_SHA:
            raise ValueError('UNRESOLVED: original source producer mathematical receipt differs')
        result=json.loads(out.read_bytes())
        if result.get('physical_provider_admitted') is not False or result.get('empirical_validation')!='NOT_ESTABLISHED':
            raise ValueError('UNRESOLVED: invalid producer science admission')
        for lens in LENSES:
            mass=MASS_PREFIX+lens.replace('+','p')+'.be64'
            if not (work/mass).is_file() or (work/mass).read_bytes() != (source/mass).read_bytes():
                raise ValueError('UNRESOLVED: original 180-node source-float mass differs '+lens)
        # Independent checker runs from authenticated source, with freshly
        # regenerated producer receipt and fresh mass binaries, not saved output.
        independent=work/'results/independent_stencil_check_v1.json'
        stdout2=_run(source,PUBLIC+'independent_stencil_check.py',
                     ['--sat',str(source/'inputs/saturation_parent.zip'), '--root',str(work),
                      '--receipt',str(out),'--out',str(independent)],budget_seconds,
                      'independent exact-dyadic 180-node stencil calculation')
        if ('INDEPENDENT_CHECK_PASS 6 '+INDEPENDENT_RESULT_SHA not in stdout2 or
            not independent.is_file() or sha(independent.read_bytes())!=INDEPENDENT_RESULT_SHA):
            raise ValueError('UNRESOLVED: independent 180-node arithmetic receipt differs')
        qa=work/'results/adversarial_qa_v1.json'
        stdout3=_run(source,PUBLIC+'adversarial_qa.py',
                     ['--sat',str(source/'inputs/saturation_parent.zip'),'--root',str(work),
                      '--receipt',str(out),'--out',str(qa)],budget_seconds,
                      'historical 26-case adversarial proof')
        if ('ADVERSARIAL 26 REJECTED '+ADVERSARIAL_RESULT_SHA not in stdout3 or
            not qa.is_file() or sha(qa.read_bytes())!=ADVERSARIAL_RESULT_SHA):
            raise ValueError('UNRESOLVED: historical adversarial receipt differs')
        if run_tests:
            boot=('import sys,pytest; sys.exit(pytest.main(sys.argv[1:]))')
            env={k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONSTARTUP','PYTHONHOME','PYTHONINSPECT')}
            env['PYTHONNOUSERSITE']='1'
            testpaths=[str(source/'tests/historical/test_hist001d_upstream_bessel_mass_sourcefree.py'),
                       str(source/'tests/historical/test_hist001d_upstream_v1r2_attested.py')]
            try:
                proc=subprocess.run([sys.executable,'-I','-B','-c',boot,*testpaths,'-q'],
                                    cwd=source,env=env,capture_output=True,text=True,timeout=budget_seconds)
            except subprocess.TimeoutExpired as exc:
                raise ValueError('UNRESOLVED: source-free tests exceeded budget') from exc
            if proc.returncode != 0 or 'passed' not in proc.stdout:
                raise ValueError('UNRESOLVED: source-free test suite failed: '+proc.stdout[-500:]+proc.stderr[-300:])
    return {
       'status':'CERTIFIED_CONDITIONAL_ORIGINAL_MARCH_K180_SOURCE_FLOAT_REPLAY',
       'independent_external_zip_sha256':expected_sha,
       'historical_original_source_composite_sha256':SOURCE_SHA,
       'historical_saturation_parent_sha256':SAT_SHA,
       'attested_manifest_members':verified,
       'source_shadow_density_nodes_bit_replayed':1080,
       'original_source_float_mass_binary64_samples_replayed':1080,
       'exact_dyadic_180_node_independent_checker_lenses':6,
       'historical_adversarial_mutations_rejected':26,
       'producer_result_sha256':ORIGINAL_RESULT_SHA,
       'independent_result_sha256':INDEPENDENT_RESULT_SHA,
       'adversarial_result_sha256':ADVERSARIAL_RESULT_SHA,
       'arbitrary_radius_scipy_ulp_certified':False,
       'continuous_radial_K180_error_certified':False,
       'source_physical_shadow_density_selected':False,
       'physical_provider_admitted':False,
       'empirical_validation':'NOT_ESTABLISHED',
       'scientific_authority_promoted':False,
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('--archive',type=Path)
    p.add_argument('--expected-sha256')
    p.add_argument('--extracted-root','--root',dest='extracted_root',type=Path)
    p.add_argument('--budget-seconds',type=int,default=180)
    p.add_argument('--with-tests',action='store_true')
    p.add_argument('--full',action='store_true',help='legacy compatibility; replay always source-connected')
    args=p.parse_args()
    try:
        if args.archive is None or args.expected_sha256 is None:
            raise ValueError('UNRESOLVED: --archive and externally supplied --expected-sha256 required')
        result=replay(args.archive,args.expected_sha256,args.extracted_root,args.budget_seconds,args.with_tests)
    except (ValueError,TypeError,KeyError,zipfile.BadZipFile,json.JSONDecodeError,OSError,RuntimeError,OverflowError) as exc:
        print(json.dumps({'status':'UNRESOLVED','reason':str(exc)},sort_keys=True))
        return 2
    print(json.dumps(result,sort_keys=True,indent=2))
    return 0

if __name__=='__main__':
    sys.exit(main())
