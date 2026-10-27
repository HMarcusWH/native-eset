import hashlib
import json
from pathlib import Path
import pytest
from native_eset.runner import RunSpec,InvalidRunSpec,run_control
from native_eset.capabilities import UnsupportedCapability
from native_eset.conventions import compatible_units,normalize_si,decimal_string
from native_eset.evidence.receipts import verify_run_receipt,ReceiptIntegrityError
from native_eset.evidence.selection import DatasetUse,audit_holdout_conflicts
from native_eset.evidence.equation_bindings import inspect_bindings
from native_eset.numerics.integrators import refined_simpson,NumericalNonconvergence

REPO=Path(__file__).resolve().parents[2]


def spec(name='E_of_z'):
    return RunSpec.read(REPO/f'tests/fixtures/{name}.json')


def test_runner_reference_controls_and_immutable_receipt(tmp_path):
    v=spec()
    r=run_control(v,tmp_path,REPO)
    out=Path(r['output_dir'])
    values=json.loads((out/'outputs.json').read_text())['values']
    assert [x['z'] for x in values]==['0','1','3']
    assert float(values[0]['value'])==1.0
    assert float(values[2]['value'])>1
    assert verify_run_receipt(out/'receipt.json')['run_id']==r['run_id']
    with pytest.raises(FileExistsError):run_control(v,tmp_path,REPO)
    (out/'outputs.json').write_text('{}')
    with pytest.raises(ReceiptIntegrityError):verify_run_receipt(out/'receipt.json')


def test_numeric_convergence_controls(tmp_path):
    r=run_control(spec('chi_dimensionless_of_z'),tmp_path,REPO)
    values=json.loads((Path(r['output_dir'])/'outputs.json').read_text())['values']
    assert float(values[0]['value'])==0
    assert float(values[2]['value'])>float(values[1]['value'])
    f=refined_simpson(lambda x:1,0,1)
    assert f.value==pytest.approx(1)
    with pytest.raises(NumericalNonconvergence):
        refined_simpson(lambda x:x**4,0,1,n=2,absolute_tolerance=1e-16)


def test_source_and_model_identity_fail_closed(tmp_path):
    d=json.loads((REPO/'tests/fixtures/E_of_z.json').read_text())
    d['backend_id']='native-v1.7.2-one-map'
    p=tmp_path/'bad.json';p.write_text(json.dumps(d))
    with pytest.raises(UnsupportedCapability):RunSpec.read(p)
    d['backend_id']='external-gr-lcdm-control';d['equation_source_sha256']='0'*64
    p.write_text(json.dumps(d))
    with pytest.raises(InvalidRunSpec,match='equation source changed'):
        run_control(RunSpec.read(p),tmp_path,REPO)
    d['equation_source_sha256']=hashlib.sha256((REPO/'src/native_eset/controls.py').read_bytes()).hexdigest()
    d['parameters']['omega_m']['unit']='kg';p.write_text(json.dumps(d))
    with pytest.raises(InvalidRunSpec):RunSpec.read(p)
    d['parameters']['omega_m']['unit']='1';d['redshifts']=['NaN'];p.write_text(json.dumps(d))
    with pytest.raises(ValueError):RunSpec.read(p)
    d['redshifts']=['1'];d['claim_intent']='PHYSICAL_PROVIDER';p.write_text(json.dumps(d))
    with pytest.raises(ValueError):RunSpec.read(p)


def test_units_no_silent_frame_conversion():
    assert compatible_units('km','m')
    assert normalize_si('2','km')==decimal_string('2000')
    assert not compatible_units('kg','km')
    with pytest.raises(ValueError):compatible_units('SPACE','m')


def test_holdout_contamination():
    a=DatasetUse('a'*64,'CALIBRATION','M','cal')
    b=DatasetUse('a'*64,'HELD_OUT_VALIDATION','M','held')
    assert audit_holdout_conflicts([a,b])['status']=='FAIL_CLOSED_HOLDOUT_CONTAMINATION'
    assert audit_holdout_conflicts([a])['status']=='PASS_ROLE_DISJOINTNESS_ONLY'


def test_equation_crosswalk_source_matches():
    result=inspect_bindings(REPO/'registry/equation_bindings.json',REPO)
    assert result['bindings'][0]['status']=='SOURCE_ID_AND_ATTRIBUTE_EXIST_NOT_PHYSICS_PROVED'
    assert result['bindings'][1]['status']=='NOT_IMPLEMENTED'
