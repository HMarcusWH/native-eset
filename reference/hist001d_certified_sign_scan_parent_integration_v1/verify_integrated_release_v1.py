"""Fail-closed independent clean-extraction verification of HIST001D source-bound scanner.

Public source only: protected source arrays and receipts stay in an optional,
access-controlled 6-parent release ZIP. No claim about physical Weyl lensing,
original March arbitrary-input floating-point sign topology, or validation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT_SHA="252d502a1a6607751c5604de221767a10ff6f28e253b0c92d4988773e65ebb29"
GLOBAL_SHA="ee677eea7f2f7bcf5c90347f5c54658988090340d888870c7e60071263693fff"
SCANNER_SHA="73943c3fbb1cafd504f3e5d6d3d1d2855553144e18b24952f19ef0150cd63038"
SOURCE_SHA="fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
PARENT_BRACKET="HIST001D_GUARDED_BINARY64_ROOT_BRACKETING_FULL_v1_2026_11_07_NONPROMOTING.zip"
PARENT_GLOBAL="HIST001D_SOURCE_CONNECTED_K180_D120_KNOT_SAFE_GLOBAL_ROOTS_v1_2026_11_06_FULL_NONPROMOTING.zip"


def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def canonical(obj)->bytes:return (json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')


def check_zip(archive:Path):
    if archive.is_symlink() or not archive.is_file():raise ValueError('unsafe source archive path')
    with zipfile.ZipFile(archive) as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or 'MANIFEST_SHA256.json' not in names:
            raise ValueError('duplicate or missing release inventory')
        if z.testzip() is not None:raise ValueError('zip CRC invalid')
        for info in z.infolist():
            p=PurePosixPath(info.filename)
            if info.filename.startswith('/') or '\\' in info.filename or '..' in p.parts or ((info.external_attr>>16)&0o170000)==0o120000:
                raise ValueError('unsafe archive path/symlink')
            if info.file_size>15_000_000:raise ValueError('unexpected oversized archive member')
        manifest=json.loads(z.read('MANIFEST_SHA256.json'))
        files=manifest.get('files',{})
        if (manifest.get('schema')!='HIST001D_SOURCE_BOUND_SIGN_COVERAGE_RELEASE_V1' or
            manifest.get('nonpromoting') is not True or
            set(files)|{'MANIFEST_SHA256.json'}!=set(names)):
            raise ValueError('release manifest schema or source inventory mismatch')
        for name,record in files.items():
            b=z.read(name)
            if sha(b)!=record['sha256'] or len(b)!=record['size_bytes']:
                raise ValueError('release member digest mismatch: '+name)
        for path,h in [('parents/'+PARENT_BRACKET,ROOT_SHA),
                       ('parents/'+PARENT_GLOBAL,GLOBAL_SHA),
                       ('parents/scanner_source_only_v0_1.zip',SCANNER_SHA)]:
            if sha(z.read(path))!=h:
                raise ValueError('immutable parent archive SHA mismatch: '+path)
        att=json.loads(z.read('SOURCE_IDENTITY.json'))
        if (att.get('original_source_46plus3_sha256')!=SOURCE_SHA or
            att.get('physical_provider_admitted') is not False or
            att.get('scientific_authority_promoted') is not False or
            att.get('global_uniqueness_full_producer_regenerated') is not False or
            att.get('empirical_validation')!='NOT_ESTABLISHED'):
            raise ValueError('scientific authority was promoted')
        saved=json.loads(z.read('results/source_bound_coverage.json'))
        from hashlib import sha256
        if (saved.get('status')!='CERTIFIED_CONDITIONAL' or
            len(saved.get('lens_results',[]))!=6 or
            saved.get('physical_provider_admitted') is not False or
            saved.get('empirical_validation')!='NOT_ESTABLISHED'):
            raise ValueError('unadmitted scientific result in release')
        audit=json.loads(z.read('results/global_independent_audit.json'))
        if audit.get('status')!='PASS_SOURCE_BOUND_INDEPENDENT_1400_PANEL_REPLAY':
            raise ValueError('missing independent global checker')
        bad=json.loads(z.read('results/protected_adversarial_audit.json'))
        if (bad.get('status')!='PASS_SCOPED_NONPROMOTING' or
            not all(x.get('rejected_or_unresolved') for x in bad.get('cases',[])) or
            bad.get('adversarial_check_count')!=len(bad.get('cases',[]))):
            raise ValueError('adversarial audit incomplete')
        return {'status':'PASS_ARCHIVE_INTEGRITY_AND_NONPROMOTION',
                'files_checked':len(files),'size_bytes':archive.stat().st_size,
                'zip_sha256':sha(archive.read_bytes())}


def safe_extract(archive:Path,dest:Path):
    with zipfile.ZipFile(archive) as z:
        if len(z.namelist())!=len(set(z.namelist())) or z.testzip() is not None:
            raise ValueError('corrupt embedded archive')
        for info in z.infolist():
            pp=PurePosixPath(info.filename)
            if info.filename.startswith('/') or '\\' in info.filename or '..' in pp.parts or ((info.external_attr>>16)&0o170000)==0o120000:
                raise ValueError('unsafe nested archived path')
        z.extractall(dest)


def subprocess_run(argv:list[str],*,cwd:Path|None=None,env:dict|None=None,timeout:int=250):
    p=subprocess.run([sys.executable,*argv],cwd=cwd,env=env,text=True,capture_output=True,timeout=timeout)
    if p.returncode!=0:
        raise RuntimeError('subprocess failed '+str(argv[:3])+': '+p.stderr[-900:]+p.stdout[-900:])
    return p.stdout.strip(),p.stderr.strip()


def test_release(archive:Path, full:bool=False):
    result={'schema':'HIST001D_SOURCE_BOUND_SIGN_COVERAGE_CLEAN_REPLAY_AUDIT_V1',
            'archive_integrity':check_zip(archive),
            'full_source_bound_replay_requested':full,
            'root_source_replayed':False,
            'independent_global_1400_panels_replayed':False,
            'all_12_new_endpoint_guards_replayed':False,
            'adversarial_receipt_regenerated':False,
            'global_theorem_full_producer_replayed':False,
            'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
            'scientific_authority_promoted':False}
    if not full:
        result['status']='SOURCE_ARCHIVE_AND_SCOPE_ONLY_PASS';return result
    with tempfile.TemporaryDirectory(prefix='hist001d_protected_clean_replay_') as tmp:
        w=Path(tmp)
        safe_extract(archive,w)
        source=w/'source'; parents=w/'parents'; extracted=w/'engine'
        bracket=parents/PARENT_BRACKET;globalzip=parents/PARENT_GLOBAL
        root=extracted/'root'; globaldir=extracted/'global'; scanner=extracted/'scanner'
        for x in (root,globaldir,scanner):x.mkdir(parents=True,exist_ok=True)
        safe_extract(bracket,root)
        safe_extract(globalzip,globaldir)
        safe_extract(parents/'scanner_source_only_v0_1.zip',scanner)
        scan_dir=scanner/'hist001d_certified_sign_scan_v0_1'
        if not scan_dir.is_dir():raise ValueError('missing scanner v0.1 source root')
        env=os.environ.copy()
        env.update(HIST001D_ENGINE_DIR=str(root.resolve()),
                   HIST001D_PARENT_DIR=str(parents.resolve()),
                   HIST001D_ROOT_ZIP=str(bracket.resolve()),
                   HIST001D_GLOBAL_AUDIT=str((w/'results/global_independent_audit.json').resolve()),
                   PYTHONPATH=os.pathsep.join([str(source.resolve()),str(scan_dir.resolve())]))
        # Unit source-free tests run on both scanner original and new adapter.
        _,stderr=subprocess_run(['-m','unittest','-q','test_certified_sign_scan.py'],cwd=scan_dir,env=env,timeout=65)
        _,stderr2=subprocess_run(['-m','unittest','-q','test_source_bound_adapter_v1.py'],cwd=source,env=env,timeout=65)
        result['source_free_unittest_groups']='67_scanner_and_17_integration_source_only'
        # Full global independence: two separate rational engines, 1400 leaves.
        new_global=w/'global_recomputed.json'
        subprocess_run([str(source/'global_independent_verify_v1.py'),
                       '--engine-dir',str(globaldir),'--parent-dir',str(parents),
                       '--archive',str(globalzip),'--out',str(new_global)],cwd=source,env=env,timeout=240)
        saved_global=(w/'results/global_independent_audit.json').read_bytes()
        if new_global.read_bytes()!=saved_global:raise ValueError('independent 1400-panel result not byte-identical')
        result['independent_global_1400_panels_replayed']=True
        result['global_independent_audit_sha256']=sha(saved_global)
        # Parent bracketer full replay and adversarial equality.
        root_audit=w/'root_replay.json'
        subprocess_run([str(root/'verify_release.py'),'--archive',str(bracket),
                       '--work-dir',str(root),'--parent-dir',str(parents),'--full',
                       '--out',str(root_audit)],cwd=root,env=env,timeout=110)
        if root_audit.read_bytes()!=(w/'results/parent_root_replay.json').read_bytes():
            raise ValueError('sealed bracketer not byte-identical')
        result['root_source_replayed']=True
        # Adapter imports only pinned proof engine code and does independent
        # source-authenticated point evaluation (not compiled float signs).
        new_scan=w/'new_source_coverage.json'
        base=[str(scan_dir/'scan_cli.py'),'--adapter','source_bound_adapter_v1:make_adapter',
              '--uniqueness-parent-sha256',GLOBAL_SHA,'--mode','theorem']
        subprocess_run(base+['--out',str(new_scan)],cwd=scan_dir,env=env,timeout=160)
        if new_scan.read_bytes()!=(w/'results/source_bound_coverage.json').read_bytes():
            raise ValueError('coverage source replay differs from protected receipt')
        subprocess_run(base+['--replay-receipt',str(new_scan)],cwd=scan_dir,env=env,timeout=160)
        result['all_12_new_endpoint_guards_replayed']=True
        result['coverage_sha256']=sha(new_scan.read_bytes())
        # Mutated self-rehashed numerical results MUST be caught by replay.
        new_adv=w/'new_adversarial.json'
        subprocess_run([str(source/'protected_adversarial_v1.py'),
                       '--expected',str(new_scan),'--engine',str(root),'--parents',str(parents),
                       '--root',str(bracket),'--global-audit',str(new_global),
                       '--scanner-dir',str(scan_dir),'--out',str(new_adv)],cwd=source,env=env,timeout=180)
        if new_adv.read_bytes()!=(w/'results/protected_adversarial_audit.json').read_bytes():
            raise ValueError('adversarial replay differed from protected audit')
        result['adversarial_receipt_regenerated']=True
        result['adversarial_checks']=json.loads(new_adv.read_bytes())['adversarial_check_count']
        result['status']='PASS_SCOPED_SOURCE_DEPENDENT_REPLAY_NO_PHYSICAL_PROMOTION'
    return result


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--archive',type=Path,required=True)
    ap.add_argument('--full',action='store_true')
    ap.add_argument('--out',type=Path)
    a=ap.parse_args(argv)
    try:
        result=test_release(a.archive,a.full)
        code=0
    except Exception as exc:
        result={'schema':'HIST001D_SOURCE_BOUND_SIGN_COVERAGE_CLEAN_REPLAY_AUDIT_V1',
                'status':'UNRESOLVED', 'reason':type(exc).__name__+':'+str(exc)[:400],
                'physical_provider_admitted':False,
                'scientific_authority_promoted':False}
        code=2
    result['receipt_sha256']=sha(canonical(result))
    payload=canonical(result)
    if a.out:a.out.write_bytes(payload)
    else:sys.stdout.buffer.write(payload)
    return code

if __name__=='__main__':sys.exit(main())
