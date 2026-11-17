"""No-kit, cross-platform fail-closed tests of the G4b.1c external evidence gate."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import zipfile
import pytest

GATE = Path(__file__).resolve().parents[2] / "tools" / "g4b1c_evidence_replay_gate.py"
spec = importlib.util.spec_from_file_location("g4b1c_evidence", GATE)
gate = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(gate)


def test_scope_is_candidate_only():
    assert gate.SOURCE_LOCK_SHA256 == "fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a"
    assert set(gate.KITS) == {"adapter", "existence", "prepeak", "surface_slope"}
    assert all(len(cfg["sha256"]) == 64 for cfg in gate.KITS.values())
    assert "NOT_ORIGINAL_MARCH" in gate.MODEL


def test_bad_source_kit_sha_rejected(tmp_path):
    p = tmp_path / "wrong.zip"
    p.write_bytes(b"not-a-valid-source-archive")
    with pytest.raises(gate.EvidenceGateError, match="SHA mismatch"):
        gate.replay_one("adapter", p)


def test_missing_or_symlink_kit_refused(tmp_path):
    with pytest.raises(gate.EvidenceGateError):
        gate.assert_zip_safe(tmp_path / "missing.zip")
    source = tmp_path / "original.zip"
    with zipfile.ZipFile(source, "w") as z:
        z.writestr("valid.txt", "data")
    link = tmp_path / "link.zip"
    link.symlink_to(source)
    with pytest.raises(gate.EvidenceGateError):
        gate.assert_zip_safe(link)


def test_path_traversal_member_refused(tmp_path):
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(bad, "w") as z:
        z.writestr("../cross-boundary.txt", "no")
    with pytest.raises(gate.EvidenceGateError, match="unsafe"):
        gate.assert_zip_safe(bad)


def test_duplicate_member_refused(tmp_path):
    bad = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(bad, "w") as z:
        z.writestr("valid.txt", "a")
        z.writestr("valid.txt", "b")
    with pytest.raises(gate.EvidenceGateError, match="duplicated"):
        gate.assert_zip_safe(bad)


def test_all_four_kits_required():
    with pytest.raises(gate.EvidenceGateError, match="all four"):
        gate.run_all({})


def _partial(kind, **changes):
    result = {
        "kind": kind,
        "entrypoint": gate.KITS[kind]["entry"],
        "kit_sha256": gate.KITS[kind]["sha256"],
        "source_kit_original_46plus3_sha256": gate.SOURCE_LOCK_SHA256,
        "replay_exit": 0,
        "transcript_sha256": "b" * 64,
        "scope": "LOCAL_CONDITIONAL_FINITE_MATHEMATICAL_PROXY_ONLY",
    }
    result.update(changes)
    return {"schema": "HIST001D_G4B1C_REPLAY_ONE_KIT_V1",
            "status": "PASS_SCOPED_ONE_KIT_ONLY", "result": result}


def test_aggregate_duplicates_fail_closed(tmp_path, capsys):
    files = []
    for i in range(4):
        p = tmp_path / f"receipt{i}.json"
        p.write_text(json.dumps(_partial("adapter")),encoding="utf8")
        files.append(str(p))
    assert gate.main(["--aggregate", *files]) == 2
    assert "FAIL_CLOSED" in capsys.readouterr().out


def test_aggregate_forged_physical_claim_fails(tmp_path, capsys):
    files=[]
    for kind in gate.KITS:
        record = _partial(kind)
        if kind == "existence":
            record["result"]["physical_provider_admitted"] = True
        p=tmp_path/(kind+".json");p.write_text(json.dumps(record),encoding="utf8")
        files.append(str(p))
    assert gate.main(["--aggregate",*files]) == 2
    assert "FAIL_CLOSED" in capsys.readouterr().out


def test_aggregate_only_provenance_scope(tmp_path,capsys):
    files=[]
    for kind in gate.KITS:
        p=tmp_path/(kind+".json");p.write_text(json.dumps(_partial(kind)),encoding="utf8")
        files.append(str(p))
    assert gate.main(["--aggregate",*files]) == 0
    o=json.loads(capsys.readouterr().out)
    assert o["four_kits_authenticated_and_replayed"] is True
    assert o["original_march_180x120_numeric_all_R_root_theorem"] is False
    assert o["full_root_count_or_uniqueness_certified"] is False
    assert o["physical_provider_admitted"] is False
    assert o["empirical_validation"] == "NOT_ESTABLISHED"
