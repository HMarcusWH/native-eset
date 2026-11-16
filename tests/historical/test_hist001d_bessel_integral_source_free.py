"""Source-free mathematical and fail-closed tests for independent real-integral K0,K1."""
from fractions import Fraction as Q
from pathlib import Path
import sys
import pytest

SOURCE=Path(__file__).resolve().parents[2]/"reference"/"hist001d_k180_bessel_integral_candidate"
sys.path.insert(0,str(SOURCE))
from real_integral_bessel import X, exppos, logpos, I0I1, K0K1_integral, F_and_prime  # noqa: E402
from stencil_verify import parse64, scale_interval, minus, plus, maxabs  # noqa: E402

@pytest.mark.parametrize('q', [Q(0),Q(1,16),Q(1,3),Q(1),Q(4)])
def test_exp_positive_encloses_ordinary_rational_taylor(q):
    box=exppos(q)
    s=Q(1);term=Q(1)
    for k in range(1,180):
        term=term*q/k;s+=term
    # For x<=4, omitted terms from 180 onward are nonnegative and geometrically bounded.
    next_term=term*q/180
    tail=next_term/(1-q/181)
    assert box.lower()<=s and box.upper()>=s+tail

@pytest.mark.parametrize('q', [Q(1),Q(3,2),Q(2),Q(1,17),Q(12)])
def test_log_exp_consistency_at_rationals(q):
    lo,hi=logpos(q).lower(),logpos(q).upper()
    assert lo<=hi
    if q==1:assert lo<=0<=hi
    if q==2:assert lo>0

@pytest.mark.parametrize('y', [Q(1,1000),Q(1,5),Q(1),Q(5)])
def test_integral_bessel_wr_positivity_and_recurrence(y):
    a,b=I0I1(y)
    c,d,_=K0K1_integral(y)
    assert a.lower()>0 and b.lower()>0
    assert c.lower()>0 and d.lower()>0
    wr=a*d+b*c
    assert wr.lower()<=1/y<=wr.upper()
    f,df,_=F_and_prime(y)
    assert f.lower()>0 and df.upper()<0

@pytest.mark.parametrize('y', [Q(1,3),Q(3),Q(13)])
def test_bessel_integral_two_resolutions_intersect(y):
    import real_integral_bessel as method
    saved=method.H
    try:
        method.H=Q(1,32)
        f,df,_=method.F_and_prime(y)
        method.H=Q(1,64)
        ff,dd,_=method.F_and_prime(y)
        assert ff.lower()<=f.upper() and f.lower()<=ff.upper()
        assert dd.lower()<=df.upper() and df.lower()<=dd.upper()
    finally: method.H=saved

@pytest.mark.parametrize('r', [Q(7,13),Q(-3,17),Q(2**15)])
def test_exact_rational_fixedpoint_interval_contains(r):
    v=X(r)
    assert v.lower()<=r<=v.upper()
    assert (v*X(1)).lower()<=r<=(v*X(1)).upper()

def test_manual_ieee754_decoder():
    import struct
    assert parse64(struct.pack('>d',0.5))==Q(1,2)
    assert parse64(struct.pack('>d',-0.125))==Q(-1,8)
    assert parse64(struct.pack('>d',0.02))==Q.from_float(0.02)
    with pytest.raises(ValueError):parse64(struct.pack('>d',float('inf')))
    with pytest.raises(ValueError):parse64(struct.pack('>d',float('nan')))

def test_signed_interval_arithmetic():
    a=(Q(2),Q(5));b=(Q(7),Q(11))
    assert minus(b,a)==(Q(2),Q(9))
    assert scale_interval(-2,a)==(Q(-10),Q(-4))
    assert plus(a,b)==(Q(9),Q(16))
    assert maxabs((Q(-13),Q(3)))==13

def test_trapezoid_error_upper_is_explicit_and_positive():
    _,_,meta=K0K1_integral(Q(1,2))
    assert meta['trapezoid_upper']==Q(8)/(Q(1,2)*((1<<192)-1))
    assert meta['tail_upper']>=0
    assert meta['grid_points']>=1

def test_non_promoting_source_metadata():
    from source_audit import SAT_SHA, SOURCE_SHA
    assert len(SAT_SHA)==64 and len(SOURCE_SHA)==64

# Source-identity guards remain active when Python discards language asserts.
def test_source_audit_rejects_mismatched_lens_identity():
    from source_audit import audit_lens
    with pytest.raises(ValueError, match="lens identity mismatch"):
        audit_lens(None, {"lens_id": "J0822+1828"}, {"lens_id": "J0915+4211"}, None)

def test_source_audit_rejects_bad_original_node_bytes():
    from source_audit import audit_lens
    class FakeSource:
        def read(self, name):
            return b"short"
    c={"lens_id": "J0822+1828", "node_file": "fake.be64", "node_sha256": "0"*64}
    with pytest.raises(ValueError, match="180-node source bytes"):
        audit_lens(FakeSource(), c, {"lens_id": c["lens_id"]}, None)

def test_source_audit_rejects_wrong_inherited_node_sha():
    import hashlib
    import json
    from source_audit import audit_lens
    raw=bytes(180*64)
    digest=hashlib.sha256(raw).hexdigest()
    c={"lens_id": "J0822+1828", "node_file": "nodes", "node_sha256": digest}
    a={"lens_id": c["lens_id"], "source_scalar_binary64_hex": {
        k: "0x1.0000000000000p+0" for k in
        ("Mb", "Md", "a", "Rd", "delta", "r0", "n", "C4pi")}}
    class FakeSource:
        def read(self, name):
            return raw
    class FakePrevious:
        def read(self, name):
            return json.dumps({"source_180_node_sha256": "f"*64}).encode()
    with pytest.raises(ValueError, match="inherited 180-node SHA"):
        audit_lens(FakeSource(), c, a, FakePrevious())

def test_quick_verifier_rejects_failed_claim_guard_under_optimized_python(monkeypatch, tmp_path):
    import json
    import importlib.util
    spec=importlib.util.spec_from_file_location(
        'hist001d_pr60_verify_release_for_tests',SOURCE/'verify_release.py')
    vr=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vr)
    result={"synthetic": True}
    evidence=tmp_path/"results"
    evidence.mkdir()
    (tmp_path/"inputs").mkdir()
    (evidence/"stencil_summary.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    for i in range(6):
        (evidence/f"lens_{i}.json").write_text("{}")
    (evidence/"cross_resolution.json").write_text("{}")
    monkeypatch.setattr(vr, "ROOT", tmp_path)
    monkeypatch.setattr(vr, "verify", lambda *args: result)
    monkeypatch.setattr(vr, "validate", lambda *args: False)
    with pytest.raises(ValueError, match="claim guard rejected"):
        vr.run_quick()

def test_quick_verifier_uses_sibling_claim_guard_despite_cached_foreign_name(monkeypatch):
    import importlib.util
    import types
    foreign = types.ModuleType("claim_guard")
    foreign.validate = lambda *_args: True
    monkeypatch.setitem(sys.modules, "claim_guard", foreign)
    spec = importlib.util.spec_from_file_location(
        "hist001d_k180_claim_guard_identity_test", SOURCE / "verify_release.py")
    assert spec and spec.loader
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    assert verifier.validate is not foreign.validate
    assert Path(verifier.validate.__code__.co_filename).resolve() == (
        SOURCE / "claim_guard.py").resolve()
