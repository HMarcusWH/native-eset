"""Adversarial regression tests for defects reproduced in B1r1.

These are infrastructure tests. None claims ESET physical validation.
"""
from dataclasses import FrozenInstanceError
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import pytest

from native_eset.runner import RunSpec, run_control, InvalidRunSpec, runtime_environment, run_identity
from native_eset.serialization import strict_loads, require_sha256
from native_eset.evidence.receipts import canonical_json, digest_bytes, verify_run_receipt, ReceiptIntegrityError
from native_eset.evidence.selection import DatasetUse, audit_holdout_conflicts
from native_eset.evidence.data_roles import check_data_role, DataContaminationError
from native_eset.graph.snapshot import GraphSnapshot, GraphIntegrityError, canonical_graph_digest
from native_eset.graph.records import Node
from native_eset.graph.resolver_adapter import (
    VerifiedResolver, authorize_physical_output, UnauthorizedPhysicalOutput, _lf_bytes, approved_lock,
)
from native_eset.graph.trust_roots import APPROVED_ESET_SNAPSHOT_SHA256
from native_eset.graph.query import GraphQuery
from native_eset.capabilities import CAPABILITIES
from native_eset.numerics.integrators import simpson

REPO = Path(__file__).resolve().parents[1]


def source_spec():
    return json.loads((REPO / 'tests/fixtures/E_of_z.json').read_text(encoding='utf-8'))


def tiny_graph(tmp_path, *, parallel=False):
    root = tmp_path / 'graph'
    root.mkdir(parents=True)
    rows = [
        {'id': 'a', 'type': 'TheoryFamily', 'name': 'A', 'notes': ['unchanged']},
        {'id': 'b', 'type': 'TheoryModule', 'name': 'B'},
        {'id': 'c', 'type': 'TheoryModule', 'name': 'C'},
        {'id': 'r1', 'type': 'Relation', 'name': 'AB', 'subject': 'a', 'predicate': 'REQUIRES', 'object': 'b', 'scope': {'domain': 'D1'}},
        {'id': 'r2', 'type': 'Relation', 'name': 'BC', 'subject': 'b', 'predicate': 'REQUIRES', 'object': 'c'},
    ]
    if parallel:
        rows.append({**rows[-2], 'id': 'r3', 'scope': {'domain': 'D2'}})
    p = root / 'test.jsonl'
    p.write_bytes(b''.join(canonical_json(r) for r in rows))
    lock = {'schema': 'NATIVE_ESET_THEORY_STATE_GRAPH_LOCK_V1', 'release_version': 'SYNTHETIC',
            'file_count': 1, 'record_count': len(rows), 'relation_count': len(rows)-3, 'verdict_count': 0,
            'graph_sha256': canonical_graph_digest(rows),
            'files': [{'name': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}]}
    lp = tmp_path / 'lock.json'
    lp.write_bytes(canonical_json(lock))
    return root, lp


def cli(*args, cwd=REPO):
    env = dict(os.environ)
    env['PYTHONPATH'] = str(REPO / 'src')
    return subprocess.run([sys.executable, '-m', 'native_eset', *args], cwd=cwd,
                          capture_output=True, text=True, encoding='utf-8', env=env)


def rewrite_receipt(folder, modify):
    receipt = json.loads((folder / 'receipt.json').read_text())
    modify(receipt)
    data = canonical_json(receipt)
    (folder / 'receipt.json').write_bytes(data)
    (folder / 'receipt.sha256').write_text(digest_bytes(data)+'\n')


def test_run_spec_no_mutable_alias_or_stale_digest(tmp_path):
    raw = source_spec()
    spec = RunSpec(raw)
    raw['parameters']['omega_m']['value'] = '0.2'
    exposed = spec.raw
    exposed['claim_intent'] = 'PHYSICAL_PROVIDER'
    exposed['parameters']['omega_m']['value'] = '0.4'
    assert spec.raw['parameters']['omega_m']['value'] == '0.3'
    result = run_control(spec, tmp_path)
    path = Path(result['output_dir'])
    receipt = json.loads((path/'receipt.json').read_text())
    assert receipt['spec_sha256'] == digest_bytes((path/'run_spec.json').read_bytes())
    assert receipt['data_use'] == 'INTERNAL_TEST'
    with pytest.raises(InvalidRunSpec):
        RunSpec(source_spec(), '0'*64)
    with pytest.raises(FrozenInstanceError):
        spec.spec_sha256 = '0'*64


@pytest.mark.parametrize('patch', [
    {'equation_id': 'invented:proven-equation'},
    {'frame': 'NATIVE_V172_EINSTEIN_FIXED_MP'},
    {'model_id': 'validated:eset'},
    {'absolute_tolerance': '1e900'},
    {'absolute_tolerance': '1e-900'},
    {'redshifts': ['1_000']},
    {'redshifts': ['NaN']},
    {'redshifts': ['101']},
    {'claim_intent': 'PHYSICAL_PROVIDER'},
    {'theory_id': 7},
])
def test_invalid_run_identity_and_numeric_contracts(patch):
    with pytest.raises((ValueError, RuntimeError)):
        RunSpec({**source_spec(), **patch})


@pytest.mark.parametrize('blob', ['{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}'])
def test_ambiguous_or_nonfinite_json_is_rejected(blob):
    with pytest.raises(ValueError):
        strict_loads(blob)


def test_run_identity_includes_environment_and_complete_spec():
    env = runtime_environment()
    a = run_identity('a'*64, 'b'*64, 'c'*64, env)
    assert a != run_identity('a'*64, 'b'*64, 'c'*64, {**env, 'python': '0.0.0'})
    assert a != run_identity('d'*64, 'b'*64, 'c'*64, env)


def test_fabricated_resolver_with_trusted_digest_cannot_authorize():
    provider = {'id':'prov', 'type':'Provider', 'name':'Forged', 'provider_admitted':True,
                'production_scoring_authorized':False, 'physical_outputs_authorized':['CMB_TT'], 'source_refs':['fake']}
    verdict = {'id':'v', 'type':'Verdict', 'name':'Forged', 'subject':'prov', 'axis':'provider_state',
               'value':'PROVIDER_ADMITTED', 'scope':'ALL', 'authority_refs':['fake']}
    partition = {'subject':'prov', 'axis':'provider_state', 'scope':'ALL', 'resolved_state':'PROVIDER_ADMITTED',
                 'resolution_status':'RESOLVED', 'scope_quality':'EXPLICIT_OR_GLOBAL', 'active_verdicts':['v'],
                 'authority_basis':{'v':[{'authority':'fake'}]}, 'blocked_by':[]}
    product = {**partition, 'axis':'physical_claim_state', 'resolved_state':'PHYSICAL_OUTPUTS_ADMITTED_NARROW'}
    snap = GraphSnapshot(Path('/nonexistent'), approved_lock(),
                         {r['id']:Node(r['id'],r['type'],r['name'],r,APPROVED_ESET_SNAPSHOT_SHA256)
                          for r in (provider, verdict)}, (), APPROVED_ESET_SNAPSHOT_SHA256)
    forged = VerifiedResolver(snap, (partition, product), (), {'resolver_execution_status':'PASS_SCOPED'})
    with pytest.raises(UnauthorizedPhysicalOutput):
        authorize_physical_output(forged, 'prov', 'CMB_TT', 'ALL')


def test_graph_raw_and_lock_defensive_copies(tmp_path):
    root, lock = tiny_graph(tmp_path)
    snap = GraphSnapshot.load(root, lock)
    snap.nodes['a'].raw['notes'].append('forged')
    snap.lock['files'][0]['sha256'] = '0'*64
    assert snap.nodes['a'].raw['notes'] == ['unchanged']
    assert snap.lock['files'][0]['sha256'] != '0'*64
    with pytest.raises(TypeError):
        snap.nodes['invented'] = snap.nodes['a']
    scope = snap.relations[0].scope
    scope['domain'] = 'ALL'
    assert snap.relations[0].scope == {'domain':'D1'}


def test_extra_partition_resolver_suffix_is_rejected(tmp_path):
    root, lock = tiny_graph(tmp_path)
    (root/'injected.jsonl.txt').write_text('{}\n')
    with pytest.raises(GraphIntegrityError, match='inventory'):
        GraphSnapshot.load(root, lock)


def test_scoped_parallel_relations_are_preserved(tmp_path):
    root, lock = tiny_graph(tmp_path, parallel=True)
    snap = GraphSnapshot.load(root, lock)
    matches = GraphQuery(snap).neighbors('a', ['REQUIRES'], direction='out')
    assert len(matches) == 2
    assert {r['scope']['domain'] for r in matches} == {'D1', 'D2'}


def test_predicate_generator_does_not_get_consumed_between_hops(tmp_path):
    root, lock = tiny_graph(tmp_path)
    q = GraphQuery(GraphSnapshot.load(root, lock))
    assert q.shortest_path('a','c',(x for x in ['REQUIRES']))['edge_count'] == 2
    assert q.reachable('a',(x for x in ['REQUIRES']),direction='out')['depths']['c'] == 2
    for kwargs in ({'direction':'bad'}, {'direction':'out','max_nodes':0}):
        with pytest.raises(ValueError):
            q.shortest_path('a','a',['REQUIRES'],**kwargs)
    with pytest.raises(ValueError):
        q.neighbors('a',['INVENTED_IMPLICATION'],direction='out')


def test_graph_cli_status_and_singular_predicate(tmp_path):
    root, lock = tiny_graph(tmp_path)
    r = cli('graph','status','--graph-dir',str(root),'--lock',str(lock))
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)['record_count'] == 5
    r = cli('graph','neighbors','a','--predicate','REQUIRES','--graph-dir',str(root),'--lock',str(lock))
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)['neighbors'][0]['neighbor'] == 'b'
    r = cli('graph','impact','c','--predicates','SUPPORTS','--graph-dir',str(root),'--lock',str(lock))
    assert r.returncode == 0
    assert json.loads(r.stdout)['depths'] == {}


def test_generated_resolver_newline_normalization_is_explicit():
    assert _lf_bytes('χ\r\n'.encode()) == 'χ\n'.encode()
    with pytest.raises(GraphIntegrityError):
        _lf_bytes(b'a\rb')


@pytest.mark.parametrize('mutation', ['missing_spec', 'promote', 'change_code', 'change_environment', 'extra_artifact'])
def test_resealed_malformed_receipts_rejected(tmp_path, mutation):
    result = run_control(RunSpec(source_spec()), tmp_path)
    folder = Path(result['output_dir'])
    if mutation == 'missing_spec':
        rewrite_receipt(folder, lambda r: r['output_files'].pop('run_spec.json'))
    elif mutation == 'promote':
        rewrite_receipt(folder, lambda r: r.update(claim_boundary='VALIDATED'))
    elif mutation == 'change_code':
        rewrite_receipt(folder, lambda r: r.update(code_sha256='f'*64))
    elif mutation == 'change_environment':
        rewrite_receipt(folder, lambda r: r['environment'].update(python='0.0.0'))
    else:
        (folder/'untracked.json').write_text('{}')
    with pytest.raises(ReceiptIntegrityError):
        verify_run_receipt(folder/'receipt.json')


def test_external_receipt_anchor_and_claim_boundary(tmp_path):
    result = run_control(RunSpec(source_spec()), tmp_path)
    path = Path(result['output_dir'])/'receipt.json'
    assert verify_run_receipt(path,result['receipt_sha256'])['integrity_anchor'] == 'EXTERNAL_EXPECTED_DIGEST_MATCHED'
    with pytest.raises(ReceiptIntegrityError):
        verify_run_receipt(path,'0'*64)


def test_holdout_lineage_and_cross_model_reuse_fail_closed():
    records = [DatasetUse('a'*64,'CALIBRATION','MODEL_A','known-fit'),
               DatasetUse('b'*64,'HELD_OUT_VALIDATION','MODEL_B','derived',('a'*64,))]
    assert audit_holdout_conflicts(records)['status'] == 'FAIL_CLOSED_HOLDOUT_CONTAMINATION'
    with pytest.raises(DataContaminationError):
        DatasetUse('z'*64,'REGRESSION','M','invalid digest')
    with pytest.raises(DataContaminationError):
        check_data_role('HELD_OUT_VALIDATION','CONTROL_ONLY')
    check_data_role('CALIBRATION','REGRESSION_ONLY')  # retained role, NOT independent evidence


def test_mutable_backend_registry_rejected():
    with pytest.raises(TypeError):
        CAPABILITIES['native-v1.7.2-one-map'] = CAPABILITIES['external-gr-lcdm-control']


@pytest.mark.parametrize('steps',[True,2.0,3,0,131074])
def test_simpson_rejects_invalid_step_contract(steps):
    with pytest.raises(ValueError):
        simpson(lambda x:x,0,1,steps)


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, REPO/'tools'/f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_filename_and_secret_patterns_have_positive_and_negative_controls():
    audit = load_tool('security_audit')
    assert audit.scan(['.env.production','runs/secret.json','.env.example']) == ['.env.production','runs/secret.json']
    assert audit.scan_content('config.txt', ('ghp_'+'a'*36).encode())
    assert audit.scan_content('key.txt', ('-----BEGIN '+'PRIVATE KEY-----').encode())
    assert audit.scan_content('normal.py',b'print("hello")') == []


def test_no_git_is_not_reported_as_security_pass(tmp_path):
    r = subprocess.run([sys.executable,str(REPO/'tools/security_audit.py')],cwd=tmp_path,capture_output=True,text=True)
    assert r.returncode == 2
    assert json.loads(r.stdout)['status'] == 'NOT_VERIFIED'


def test_manifest_covers_previously_ignored_setup_cfg(tmp_path):
    checker = load_tool('check_manifest')
    (tmp_path/'setup.cfg').write_text('[metadata]\nname=unexpected\n')
    assert 'setup.cfg' in checker.candidates(tmp_path)


def test_explicit_lf_checkout_contract():
    assert '* text=auto eol=lf' in (REPO/'.gitattributes').read_text()


@pytest.mark.parametrize('value',['z'*64, 'A'*64, 'f'*63, True, None])
def test_digest_grammar(value):
    with pytest.raises(ValueError):
        require_sha256(value)


def test_scientific_identity_refuses_nontext_and_implicit_module_characters():
    from native_eset.identity import ScientificIdentity
    base = dict(theory_id='T', equation_source_sha256='a'*64, constitutive_id='C',
                species_id='S', initial_condition_id='I')
    with pytest.raises(ValueError):
        ScientificIdentity(**{**base,'theory_id':9})
    with pytest.raises(ValueError):
        ScientificIdentity(**base,enabled_modules='MEM')
    with pytest.raises(ValueError):
        ScientificIdentity(**base,enabled_modules=('MEM','MEM'))


def test_doctor_fails_closed_on_changed_resolver(monkeypatch,tmp_path,capsys):
    from native_eset import cli as commands
    from native_eset.graph import resolver_adapter
    bogus=tmp_path/'resolver.py'
    bogus.write_text('print("forged")\n')
    monkeypatch.setattr(resolver_adapter,'RESOLVER_SCRIPT',bogus)
    monkeypatch.setattr(sys,'argv',['eset','doctor'])
    assert commands.main()==2
    result=json.loads(capsys.readouterr().out)
    assert result['status']=='FAIL_CLOSED' and result['failure_category']=='INTEGRITY_FAILURE'


def test_executable_schemas_required_fields_agree_with_runtime(tmp_path):
    spec_schema=json.loads((REPO/'registry/run_spec.schema.json').read_text())
    receipt_schema=json.loads((REPO/'registry/run_receipt.schema.json').read_text())
    assert set(spec_schema['required'])==set(source_spec())
    run=run_control(RunSpec(source_spec()),tmp_path)
    receipt=json.loads((Path(run['output_dir'])/'receipt.json').read_text())
    assert set(receipt_schema['required'])==set(receipt)
    assert receipt['schema']==receipt_schema['properties']['schema']['const']


def test_equation_crosswalk_cannot_escape_or_import_arbitrary_namespace(tmp_path):
    from native_eset.evidence.equation_bindings import inspect_bindings,EquationBindingError
    base=json.loads((REPO/'registry/equation_bindings.json').read_text())
    base['bindings'][0]['source_path']='../outside.py'
    path=tmp_path/'bindings.json';path.write_text(json.dumps(base))
    with pytest.raises(EquationBindingError):
        inspect_bindings(path,REPO)
    base=json.loads((REPO/'registry/equation_bindings.json').read_text())
    base['bindings'][0]['implementation']='os.system'
    path.write_text(json.dumps(base))
    with pytest.raises(EquationBindingError):
        inspect_bindings(path,REPO)


@pytest.mark.parametrize("text", ["1e999", "-1e999", '{"x":1e999}'])
def test_exponent_overflow_json_rejected(text):
    from native_eset.serialization import strict_loads
    with pytest.raises(ValueError):
        strict_loads(text)


def test_statement_fields_defensive_and_not_string():
    from native_eset.graph.statement_contract import StatementContract
    values = dict(id="s", theory_id="t", source_sha256="a"*64, frame="f", gauge="g",
                  validity_domain="d", quantifier_scope="q", normalization="n", units="1")
    fields = ["x", "y"]
    contract = StatementContract(field_set=fields, **values)
    fields.append("z")
    assert contract.field_set == ("x", "y")
    with pytest.raises(ValueError):
        StatementContract(field_set="xy", **values)
    with pytest.raises(ValueError):
        StatementContract(field_set=["x", "x"], **values)


@pytest.mark.parametrize("preserve", [False, True])
def test_git_index_manifest_catches_line_ending_drift(tmp_path, preserve):
    import subprocess
    import sys
    from pathlib import Path
    tool = Path(__file__).resolve().parents[1] / "tools/check_manifest.py"
    (tmp_path / "schema.json").write_bytes(b'{"x":1}\r\n')
    attrs = "* text=auto eol=lf\n" + ("schema.json -text\n" if preserve else "")
    (tmp_path / ".gitattributes").write_text(attrs)
    subprocess.run([sys.executable, str(tool), "--root", str(tmp_path), "--write"], check=True, capture_output=True)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    result = subprocess.run([sys.executable, str(tool), "--root", str(tmp_path), "--git-index"], capture_output=True)
    assert (result.returncode == 0) is preserve
