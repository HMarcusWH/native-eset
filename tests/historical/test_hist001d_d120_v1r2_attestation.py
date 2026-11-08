"""Source-free negative controls for the v1r2 externally pinned D120 attestor.

No historical 180x120 source arrays or protected parent ZIPs are required.
Any numerical/physical source certificate requires separate protected replay.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'reference/hist001d_d120_seam_candidate'))
from attested_replay_v1r2 import (good_path, good_sha, replay, sha, verify_tree, verify_zip, HARDENED_HELPER_SHA)  # noqa: E402


def _small_zip(tmp_path, files: dict[str,bytes], manifest_override=None):
    p=tmp_path/'small.zip'
    manifest={'schema':'SOURCE_FREE_FIXTURE_NOT_HISTORICAL',
              'files':{k:sha(v) for k,v in files.items()}}
    if manifest_override:
        manifest.update(manifest_override)
    with zipfile.ZipFile(p,'w') as z:
        z.writestr('MANIFEST_SHA256.json',json.dumps(manifest,sort_keys=True).encode())
        for name,data in files.items():z.writestr(name,data)
    return p,manifest


@pytest.mark.parametrize('unsafe',["../a", "x/../a", "x//b", "/absolute", "C:\\windows", "x\\y", "./a", "", "a/./b"])
def test_rejects_noncanonical_zip_path(unsafe):
    assert not good_path(unsafe)


def test_accepted_path_and_hash_grammar():
    assert good_path('reference/hist001d_d120_seam_candidate/verify_seam.py')
    assert good_sha('a'*64)
    assert not good_sha('A'*64)
    assert not good_sha('a'*63)
    assert sha(b'abc')==hashlib.sha256(b'abc').hexdigest()
    assert HARDENED_HELPER_SHA['reference/hist001d_original_float_bridge_candidate/float_bridge.py'] == '00a0c4c4fa78c9b3e2507062ac716a3a723e0d606d6926856aed301443add4a9'


def test_unpinned_whole_zip_fails_closed(tmp_path):
    archive,_=_small_zip(tmp_path,{'source.py':b'print(1)\n'})
    with pytest.raises(ValueError,match='external SHA'):
        verify_zip(archive,'')
    with pytest.raises(ValueError,match='whole-file SHA'):
        verify_zip(archive,'0'*64)


def test_self_rehashed_fake_archive_cannot_substitute_original_release(tmp_path):
    archive,_=_small_zip(tmp_path,{'source.py':b'print("FAKE_PASS")\n'})
    # Even an internally self-consistent ZIP is NOT an authentic HIST001D proof.
    with pytest.raises(ValueError,match='mathematical operator'):
        verify_zip(archive,sha(archive.read_bytes()))


def test_attested_source_tree_rejects_mutated_executable_even_if_local_manifest_rehashed(tmp_path):
    archive,manifest=_small_zip(tmp_path,{'code/independent_checker.py':b'raise ValueError("bad")\n'})
    root=tmp_path/'local';(root/'code').mkdir(parents=True)
    (root/'code/independent_checker.py').write_bytes(b'print("UNVERIFIED_PASS")\n')
    forged={'files':{'code/independent_checker.py':sha((root/'code/independent_checker.py').read_bytes())}}
    (root/'MANIFEST_SHA256.json').write_text(json.dumps(forged))
    with pytest.raises(ValueError,match='differs from authenticated ZIP'):
        verify_tree(archive,root,manifest)


def test_attested_tree_accepts_only_exact_authored_bytes(tmp_path):
    archive,manifest=_small_zip(tmp_path,{'code/independent_checker.py':b'raise ValueError("bad")\n'})
    root=tmp_path/'exact';(root/'code').mkdir(parents=True)
    (root/'code/independent_checker.py').write_bytes(b'raise ValueError("bad")\n')
    assert verify_tree(archive,root,manifest)==1


def test_missing_file_fails_closed(tmp_path):
    archive,manifest=_small_zip(tmp_path,{'proof.py':b'hello'})
    root=tmp_path/'missing';root.mkdir()
    with pytest.raises(ValueError,match='missing / redirected'):
        verify_tree(archive,root,manifest)


@pytest.mark.parametrize('opt', ['','-O','-OO'])
def test_full_legacy_cli_requires_external_whole_zip_authority(opt,tmp_path):
    script=ROOT/'reference/hist001d_d120_seam_candidate/verify_release.py'
    command=[sys.executable]
    if opt:command.append(opt)
    command.extend([str(script),'--full','--root',str(tmp_path)])
    x=subprocess.run(command,capture_output=True,text=True,timeout=20)
    assert x.returncode==2
    obj=json.loads(x.stdout)
    assert obj['status']=='UNRESOLVED' and 'expected-sha256' in obj['reason']


def test_no_budget_returns_unresolved_not_a_fake_scientific_receipt(tmp_path):
    with pytest.raises(ValueError,match='no execution budget'):
        replay(tmp_path/'missing.zip','a'*64,budget_seconds=0)


def test_duplicate_path_or_symlink_is_rejected_before_execution(tmp_path):
    path=tmp_path/'duplicate.zip'
    manifest={'schema':'SOURCE_FREE_FIXTURE_NOT_HISTORICAL','files':{'a':sha(b'1')}}
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',UserWarning)
        with zipfile.ZipFile(path,'w') as z:
            z.writestr('MANIFEST_SHA256.json',json.dumps(manifest))
            z.writestr('a','1')
            z.writestr('a','1')
    with pytest.raises(ValueError,match='duplicate / invalid'):
        verify_zip(path,sha(path.read_bytes()))


def test_unsafe_member_rejected_before_math(tmp_path):
    path=tmp_path/'traversal.zip'
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('MANIFEST_SHA256.json','{}')
        z.writestr('x/../evil.py','danger')
    with pytest.raises(ValueError,match='duplicate / invalid'):
        verify_zip(path,sha(path.read_bytes()))


def test_symlink_member_rejected_before_math(tmp_path):
    path=tmp_path/'symlink.zip'
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('MANIFEST_SHA256.json','{}')
        member=zipfile.ZipInfo('proof.py');member.create_system=3
        member.external_attr=(0o120777<<16)
        z.writestr(member,'../outside.py')
    with pytest.raises(ValueError,match='symlink'):
        verify_zip(path,sha(path.read_bytes()))
