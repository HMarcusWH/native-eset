"""Source-free arithmetic and scientific claim-firewall tests; not a proof of original source or physics."""
from __future__ import annotations
import json
import math
import os
import runpy
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path
import pytest
ROOT=(Path(__file__).resolve().parents[2]/'reference'/'hist001d_full180_comparator_candidate')
# Load standalone archived arithmetic by exact path, never a shared basename.
_MATH = runpy.run_path(str(ROOT / 'full180_math.py'), run_name='_hist001d_full180_math')
_INDEPENDENT = runpy.run_path(str(ROOT / 'independent_verify.py'), run_name='_hist001d_full180_independent')
sqrt_box, frac, ceil_frac = (_MATH[name] for name in ('sqrt_box', 'frac', 'ceil_frac'))
dyadic_from_float64, enclosing_root, exactpair, ppoint = (
    _INDEPENDENT[name] for name in ('dyadic_from_float64', 'enclosing_root', 'exactpair', 'ppoint')
)

@pytest.mark.parametrize('v',[0.02,120.0,1e10,-34.5,0.0,2.0**-1022,2.0**-1074])
def test_manual_binary64_fraction(v):
    assert dyadic_from_float64(v)==F.from_float(v)

@pytest.mark.parametrize('x',[F(2),F(1,9),F(7,3),F(1,2**56),F(11,13)])
def test_two_independent_directed_sqrt_boxes(x):
    l,u=sqrt_box(x,bits=56)
    li,ui=enclosing_root(x)
    assert l*l<=x<=u*u and li*li<=x<=ui*ui
    assert l<=ui and li<=u


def test_exact_source_floats_are_not_decimal_reinterpretations():
    assert frac(0.02)!=F(1,50)
    assert frac(120.0)==F(120)


def test_exact_affine_q_ratio_monotonicity():
    qb,qd=F(2,3),F(1,4)
    b0,b1=F(10),F(18);d0,d1=F(15),F(23)
    N0,N1=qb*b0+qd*d0,qb*b1+qd*d1
    P0,P1=b0+d0,b1+d1
    delta=N1*P0-N0*P1
    vals=[]
    for t in (F(0),F(1,4),F(1,2),F(3,4),F(1)):
        q=ppoint(N0,N1,t)/ppoint(P0,P1,t)
        assert min(qb,qd)<=q<=max(qb,qd)
        vals.append(q)
    assert vals==sorted(vals,reverse=(delta<0))


def test_composed_component_interpolant_not_equal_to_final_residual_interpolant():
    # A nonlinear operation applied AFTER affine interpolation need not equal
    # linearly interpolated values of that operation at the endpoints.
    q0,q1=F(1,4),F(1)
    A0=1/math.sqrt(float(q0));A1=2/math.sqrt(float(q1))
    amid=1.5/math.sqrt(float(F(5,8)))
    assert abs(amid-(A0+A1)/2)>0.05


def test_critical_target_interpolation_identity():
    r0,r1=F(1,10),F(11,10);r=F(3,4)
    C=F(13,5);t0=C*r0*r0+F(1,2**50);t1=C*r1*r1-F(1,2**48)
    pl=ppoint(t0,t1,(r-r0)/(r1-r0))
    e=C*(r-r0)*(r1-r)+ppoint(t0-C*r0*r0,t1-C*r1*r1,(r-r0)/(r1-r0))
    assert pl-C*r*r==e


def test_source_knot_h_is_not_claimed_offgrid():
    # Scientific boundary: even exact knot matches do not establish off-grid equality.
    assert F(0)==F(0)
    assert F(1,4)!=F(1,2)


def test_noncanonical_pairs_rejected():
    with pytest.raises(AssertionError):exactpair({'num':'01','den':'1'})
    with pytest.raises(AssertionError):exactpair({'num':'1','den':'0'})
    with pytest.raises(AssertionError):exactpair({'num':'1','den':'2','physical_provider_admitted':True})


def test_integer_ceil_outward():
    assert ceil_frac(F(1001,1000))==2
    assert ceil_frac(F(-1,10))==0


def test_science_model_schema_is_explicit_not_source_root_theorem():
    # producer.py uses a bare sibling import. Give that import its own process
    # and bind the exact archived sibling, not any module cached by other tests.
    script = """
import importlib.util
import json
import runpy
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
math_path = root / "full180_math.py"
spec = importlib.util.spec_from_file_location("full180_math", math_path)
if spec is None or spec.loader is None:
    raise RuntimeError("missing comparator sibling")
math_module = importlib.util.module_from_spec(spec)
sys.modules["full180_math"] = math_module
spec.loader.exec_module(math_module)
assert Path(math_module.__file__).resolve() == math_path
producer_path = root / "producer.py"
producer = runpy.run_path(str(producer_path), run_name="_hist001d_full180_producer")
assert Path(producer["__file__"]).resolve() == producer_path
assert producer["load"] is math_module.load
assert producer["ceil_frac"] is math_module.ceil_frac
print(json.dumps(producer["GUARDS"]))
"""
    proc = subprocess.run(
        [sys.executable, '-I', '-c', script, str(ROOT)],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    GUARDS = json.loads(proc.stdout)
    assert set(GUARDS)=={'J0822+1828','J0915+4211','J0930+2855',
                         'J1021+2028','J1111+2234','J1135+3720'}
    for center,span in GUARDS.values():
        assert F(span)==F(3,100)


@pytest.mark.parametrize('module',[
    'producer.py','independent_verify.py','full180_math.py',
    'verify_bundle.py','adversarial_qa.py'])
def test_assert_dependent_candidate_fails_closed_in_optimized_python(module):
    # No protected data: candidate execution must stop before stripped guards.
    proc=subprocess.run([sys.executable,'-OO','-c',
                         'import runpy,sys;runpy.run_path(sys.argv[1])',
                         str(ROOT/module)],capture_output=True,text=True,timeout=15)
    assert proc.returncode != 0
    assert 'HIST001D_COMPONENT_PL_OPTIMIZED_EXECUTION_REJECTED' in proc.stderr


# Exercise actual pytest collection and execution in isolated fresh processes.
# The nested run excludes this regression to avoid recursively spawning itself.
@pytest.mark.parametrize(
    'order,poison_cache',
    [
        ((45,), False),
        ((46,), False),
        ((45, 46), False),
        ((46, 45), False),
        ((45, 46), True),
        ((46, 45), True),
    ],
    ids=[
        'comparator-only', 'gradient-only',
        'comparator-first', 'gradient-first',
        'comparator-first-poisoned', 'gradient-first-poisoned',
    ],
)
def test_candidate_import_isolation(order, poison_cache):
    test_dir = Path(__file__).resolve().parent
    modules = {
        45: test_dir / 'test_hist001d_full180_comparator_source_free.py',
        46: test_dir / 'test_hist001d_source_smooth_shadow_gradient_sourcefree.py',
    }
    script = """
import runpy
import sys
from pathlib import Path
from types import ModuleType

# Load ordinary dependencies before taking the candidate-import snapshot.
import numpy
import pytest
from scipy import special

poison = sys.argv[1] == "1"
paths = [Path(arg).resolve() for arg in sys.argv[2:]]
names = ("producer", "independent_verify", "full180_math", "smooth_math")
if poison:
    for name in names:
        fake = ModuleType(name)
        fake.__file__ = str(paths[0].parent / ("unrelated_" + name + ".py"))
        sys.modules[name] = fake
missing = object()
cached = {name: sys.modules.get(name, missing) for name in names}
before_path = list(sys.path)

for i, path in enumerate(paths):
    ns = runpy.run_path(str(path), run_name=f"_hist001d_collection_probe_{i}")
    assert sys.path == before_path, "candidate collection leaked a search path"
    assert all(sys.modules.get(name, missing) is cached[name] for name in names), (
        "candidate collection changed a shared module cache entry"
    )
    if path.name == "test_hist001d_full180_comparator_source_free.py":
        root = path.parents[2] / "reference" / "hist001d_full180_comparator_candidate"
        expected = {
            "sqrt_box": "full180_math.py", "frac": "full180_math.py",
            "ceil_frac": "full180_math.py", "dyadic_from_float64": "independent_verify.py",
            "enclosing_root": "independent_verify.py", "exactpair": "independent_verify.py",
            "ppoint": "independent_verify.py",
        }
    else:
        assert path.name == "test_hist001d_source_smooth_shadow_gradient_sourcefree.py"
        root = path.parents[2] / "reference" / "hist001d_smooth_msh_gradient_candidate"
        expected = {
            "source_mass_and_analytic_gradient": "smooth_math.py",
            "nonuniform_gradient_exact": "smooth_math.py",
            "conditional_finite_difference_bounds": "smooth_math.py",
        }
    for name, filename in expected.items():
        actual = Path(ns[name].__code__.co_filename).resolve()
        assert actual == root / filename, (name, actual, root / filename)

# Run the real, complete source-free tests in the requested order; include all
# existing optimized-Python checks and the actual producer GUARDS assertion.
result = pytest.main([
    "-q", "--import-mode=importlib", "-p", "no:cacheprovider",
    "-k", "not test_candidate_import_isolation", *map(str, paths),
])
assert result == pytest.ExitCode.OK, result
assert all(sys.modules.get(name, missing) is cached[name] for name in names), (
    "candidate tests replaced a shared module cache entry"
)
# pytest itself may alter its import path; candidate reference directories must
# never be newly inserted into the caller's shared search path.
roots = {
    str(paths[0].parents[2] / "reference" / "hist001d_full180_comparator_candidate"),
    str(paths[0].parents[2] / "reference" / "hist001d_smooth_msh_gradient_candidate"),
}
assert not (roots & (set(sys.path) - set(before_path)))
print("HIST001D_CANDIDATE_IMPORT_ISOLATION_PASS")
"""
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    proc = subprocess.run(
        [sys.executable, '-I', '-c', script, str(int(poison_cache)),
         *(str(modules[number]) for number in order)],
        cwd=Path(__file__).resolve().parents[2], env=env,
        capture_output=True, text=True, timeout=180,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert 'HIST001D_CANDIDATE_IMPORT_ISOLATION_PASS' in proc.stdout
