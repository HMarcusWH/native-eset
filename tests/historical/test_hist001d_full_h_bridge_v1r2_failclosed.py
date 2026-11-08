"""Source-free adversarial regressions for historical mathematical proof guards.

All tests are synthetic. They do not replay original March fitted arrays or
certify physical lensing/empirical validation.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import hashlib
import pytest

ROOT=Path(__file__).resolve().parents[2]
SCRIPTS=ROOT/'reference/hist001d_full_h_bridge_candidate'


def script(source):
    return (f'import sys\n'
            f'sys.path.insert(0,{str(SCRIPTS)!r})\n'
            + source)


def run(opt, source):
    return subprocess.run([sys.executable,*opt,'-c',script(source)],capture_output=True,text=True,check=False)


@pytest.mark.parametrize('opt',[[],['-O'],['-OO']])
def test_unproved_global_aperture_monotonicity_always_rejected(opt):
    code='''from verify_full_h_witness import CheckLens
from fractions import Fraction as F
obj=CheckLens.__new__(CheckLens)
obj.r=list(map(F,range(1,181)))
obj.B=[F(1)]+[F(100)]*179
obj.D=[F(100)]*180
obj.qb=F(1);obj.qd=F(0)
try:
    obj.global_aperture_monotone()
except ValueError as exc:
    if 'monotonicity unproved' not in str(exc):raise
else:
    raise SystemExit('INVALID_PROOF_ACCEPTED')
'''
    p=run(opt,code)
    assert p.returncode==0,(p.stdout,p.stderr)
    assert 'INVALID_PROOF_ACCEPTED' not in p.stdout


@pytest.mark.parametrize('opt',[[],['-O'],['-OO']])
def test_corrupted_isqrt_must_not_validate_enclosure(opt):
    code='''from fractions import Fraction as F
import full_h_finite_source as s
s.isqrt=lambda v: 0
try:
    s.sqrt_rational_bounds(F(4,9),bits=16)
except ValueError as exc:
    if 'square-root enclosure' not in str(exc):raise
else:
    raise SystemExit('INVALID_SQRT_ACCEPTED')
'''
    p=run(opt,code)
    assert p.returncode==0,(p.stdout,p.stderr)
    assert 'INVALID_SQRT_ACCEPTED' not in p.stdout


def import_attestation():
    f=SCRIPTS/'attested_replay_v1r2.py'
    spec=importlib.util.spec_from_file_location('hist001d_attested_replay_v1r2_test',f)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_unpinned_external_archive_is_unresolved(tmp_path):
    mod=import_attestation()
    p=tmp_path/'empty.zip';p.write_bytes(b'dummy')
    with pytest.raises(ValueError,match='external archive'):
        mod.verify_zip_identity(p,'0'*64)
    with pytest.raises(ValueError,match='missing/malformed external'):
        mod.verify_zip_identity(p,'')


def test_archive_source_versus_executed_source_mutation(tmp_path):
    mod=import_attestation()
    raw=b'print("legitimate")\n'
    name='reference/hist001d_full_h_bridge_candidate/verify_full_h_witness.py'
    root=tmp_path/'root';file=root/name;file.parent.mkdir(parents=True)
    file.write_bytes(raw)
    archive=tmp_path/'synthetic.zip'
    with zipfile.ZipFile(archive,'w') as z:z.writestr(name,raw)
    sha=hashlib.sha256(raw).hexdigest()
    manifest={'files':{name:sha}}
    assert mod.verify_local_tree(archive,root,manifest)==1
    file.write_bytes(b'print("forged")\n')
    with pytest.raises(ValueError,match='local source/receipt'):
        mod.verify_local_tree(archive,root,manifest)
    file.unlink()
    with pytest.raises(ValueError,match='missing'):
        mod.verify_local_tree(archive,root,manifest)


def test_executable_source_uses_unambiguous_zip_paths():
    mod=import_attestation()
    for path in ('../out','/absolute/path','a//b','a/../b','a\\b',''):
        assert not mod.valid_path(path)
    assert mod.valid_path('reference/hist001d_full_h_bridge_candidate/test.py')


def test_no_implicit_pass_without_evaluation_budget(tmp_path):
    mod=import_attestation()
    assert mod.digest(b'')==hashlib.sha256(b'').hexdigest()
    # A valid unmodified archive would be needed to reach the budget guard;
    # source-free contract requires strict invalid budgets independent of -OO.
    code='''import attested_replay_v1r2 as m
try:
    m.replay.__name__
except Exception:raise
if m.ORIGINAL_SOURCE_SHA != "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a":
    raise SystemExit("SOURCE_LOCK_BROKEN")
'''
    for opt in ([],['-OO']):
        assert run(opt,code).returncode==0

@pytest.mark.parametrize('opt',[[],['-OO']])
def test_both_proof_input_lists_truncated_identically_rejected(opt, tmp_path):
    finite=tmp_path/'finite.json';band=tmp_path/'band.json'
    finite.write_text(json.dumps({'schema':'HIST001D_MARCH180_SOURCE_CONSISTENT_FINITE_FULL_H_CROSSING_CELL_V1',
      'physical_provider_admitted':False,'empirical_validation':'NOT_ESTABLISHED',
      'lenses':[{'lens':str(i)} for i in range(5)]}))
    band.write_text(json.dumps({'all_six_crossing_aperture_bands_positive':True,
      'lenses':[{'lens':str(i)} for i in range(5)]}))
    code=("import verify_full_h_witness as m\n"
          "m.load_source=lambda *args: ([],[],[],[],[])\n"
          "try:\n"
          f"    m.verify({str(finite)!r},None,None,{str(band)!r})\n"
          "except ValueError as exc:\n"
          "    if 'missing or extra lens' not in str(exc):raise\n"
          "else:\n"
          "    raise SystemExit('FIVE_LENSES_ACCEPTED')\n")
    p=run(opt,code)
    assert p.returncode==0,(p.stdout,p.stderr)
    assert 'FIVE_LENSES_ACCEPTED' not in p.stdout
