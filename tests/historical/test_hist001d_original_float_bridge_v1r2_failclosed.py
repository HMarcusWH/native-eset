"""Synthetic PR56 fail-closed guards; zero protected sources needed in CI."""
from __future__ import annotations
import hashlib
import importlib.util
from fractions import Fraction as Q
from pathlib import Path
import subprocess
import sys
import zipfile
import pytest

ROOT=Path(__file__).resolve().parents[2]
CODE=ROOT/'reference/hist001d_original_float_bridge_candidate'
LENSES=('J0822+1828','J0915+4211','J0930+2855','J1021+2028','J1111+2234','J1135+3720')


def run_script(src,flags=()):
    body='import sys\nsys.path.insert(0,'+repr(str(CODE))+')\n'+src
    return subprocess.run([sys.executable,*flags,'-c',body],capture_output=True,text=True,check=False)


@pytest.mark.parametrize('flags',[(),('-O',),('-OO',)])
def test_five_record_truncated_inputs_rejected_under_optimization(flags):
    code='''from float_bridge import require_six_lens_groups,LENSES
cap=[{'lens_id':l} for l in LENSES]
q=list(cap)
meta=list(cap)
finite=[{'lens':l} for l in LENSES[:-1]]
try:
    require_six_lens_groups(cap,q,meta,finite)
except ValueError as e:
    if 'missing/extra' not in str(e):raise
else:
    raise SystemExit('INCOMPLETE_FINITE_LENS_SET_ACCEPTED')
'''
    p=run_script(code,flags)
    assert p.returncode==0,(p.stdout,p.stderr)


@pytest.mark.parametrize('flags',[(),('-O',),('-OO',)])
def test_four_source_groups_each_enforce_lens_identity(flags):
    code='''from float_bridge import require_six_lens_groups,LENSES
for bad in range(4):
    groups=[[{'lens_id':l} for l in LENSES] for _ in range(3)] + [[{'lens':l} for l in LENSES]]
    groups[bad][1]=dict(groups[bad][0])
    try:require_six_lens_groups(*groups)
    except ValueError as e:
        if 'lens identity/order mismatch' not in str(e):raise
    else:raise SystemExit('INVALID_SOURCE_GROUP_ACCEPTED:'+str(bad))
'''
    p=run_script(code,flags)
    assert p.returncode==0,(p.stdout,p.stderr)


@pytest.mark.parametrize('flags',[(),('-O',),('-OO',)])
def test_corrupted_integer_isqrt_cannot_pass_interval_proof(flags):
    code='''import independent_float_check as m
from fractions import Fraction as F
m.isqrt=lambda x:0
try:m.floor_sqrt_different(F(4,9))
except ValueError as e:
    if 'sqrt enclosure' not in str(e):raise
else:raise SystemExit('INVALID_SQRT_ACCEPTED')
'''
    p=run_script(code,flags)
    assert p.returncode==0,(p.stdout,p.stderr)


def import_attestation():
    f=CODE/'attested_replay_v1r2.py'
    spec=importlib.util.spec_from_file_location('hist001d_pr56_attested_test',f)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_valid_lens_groups_and_sqrt_brackets():
    sys.path.insert(0,str(CODE))
    from float_bridge import require_six_lens_groups
    from independent_float_check import floor_sqrt_different
    rows=[[{'lens_id':l} for l in LENSES] for _ in range(3)] + [[{'lens':l} for l in LENSES]]
    require_six_lens_groups(*rows)
    for x in (Q(0),Q(1),Q(4,9),Q(2),Q(15,19)):
        lo,hi=floor_sqrt_different(x)
        assert lo**2<=x<hi**2


def test_local_source_must_match_verified_archive(tmp_path):
    mod=import_attestation()
    f='reference/hist001d_original_float_bridge_candidate/independent_float_check.py'
    raw=b'print("verified")\n'
    z=tmp_path/'test.zip'
    with zipfile.ZipFile(z,'w') as arc:arc.writestr(f,raw)
    root=tmp_path/'root';(root/f).parent.mkdir(parents=True)
    (root/f).write_bytes(raw)
    manifest={'files':{f:hashlib.sha256(raw).hexdigest()}}
    assert mod.verify_tree(z,root,manifest)==1
    (root/f).write_bytes(b'print("forged")\n')
    with pytest.raises(ValueError,match='local proof/evidence'):
        mod.verify_tree(z,root,manifest)
    (root/f).unlink()
    with pytest.raises(ValueError,match='missing local'):
        mod.verify_tree(z,root,manifest)


@pytest.mark.parametrize('path',['../bad','/absolute','a//b','a/../b','a\\b','','a/./b'])
def test_zip_path_safety(path):
    assert not import_attestation().valid_path(path)


def test_attestation_requires_external_sha(tmp_path):
    archive=tmp_path/'archive.zip';archive.write_bytes(b'not a zip')
    mod=import_attestation()
    with pytest.raises(ValueError,match='independently supplied'):
        mod.verify_zip(archive,'')
    with pytest.raises(ValueError,match='mismatches independently'):
        mod.verify_zip(archive,'0'*64)


def test_no_budget_rejected_independent_of_python_assertions():
    # Empty valid archive cannot pass provenance stage; no implicit success.
    mod=import_attestation()
    assert mod.digest(b'')==hashlib.sha256(b'').hexdigest()
    assert mod.SOURCE_SHA=='fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a'
    assert not mod.valid_path('a//b')


def test_stale_parent_source_guard_present():
    mod=import_attestation()
    assert mod.H_SHA=='02c93bed1c2d5338972c192013270921264d00320b41d8d17ad44769b47dd7d6'
    assert len(mod.RESULT_SHA)==3
    assert 'reference/hist001d_full_h_bridge_candidate/full_h_finite_source.py' in mod.EXECUTED
