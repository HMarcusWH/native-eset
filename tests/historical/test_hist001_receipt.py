"""A self-hashed summary is insufficient: verify original table rows and claim scope."""
from __future__ import annotations

import hashlib
import csv
import json
from pathlib import Path
import shutil

import pytest

from native_eset.evidence.receipts import canonical_json
from native_eset.historical.hist001_backend import LegacyHistJ2141Backend
from native_eset.historical.hist001_spec import HistoricalRunSpec
from native_eset.historical.hist001_receipt import HistoricalReceiptIntegrityError, verify_hist001_receipt

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/legacy/hist001"


@pytest.fixture(scope="module")
def original_run(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("hist001_a2_verify")
    result = LegacyHistJ2141Backend().run(HistoricalRunSpec.from_mode(),
                                          source_root=SOURCE, output_root=out)
    return Path(result["output_dir"])


def copy_run(original_run: Path, tmp_path: Path) -> Path:
    p = tmp_path / original_run.name
    shutil.copytree(original_run, p)
    return p


def alter_parsed_csv_number(path: Path, column: str, delta: float) -> None:
    """Damage real numeric content, never rely on version-specific float spelling."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)
    assert fieldnames and rows and column in fieldnames
    before = float(rows[0][column])
    rows[0][column] = repr(before + delta)
    assert float(rows[0][column]) != before
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def reseal(folder: Path, *modified_files: str) -> None:
    """Attacker repairs *both* the artifact manifest and the self-hash."""
    data = json.loads((folder / "receipt.json").read_text())
    for name in modified_files:
        data["output_files"][name] = hashlib.sha256((folder / name).read_bytes()).hexdigest()
    raw = canonical_json(data)
    (folder / "receipt.json").write_bytes(raw)
    (folder / "receipt.sha256").write_bytes((hashlib.sha256(raw).hexdigest() + "\n").encode())


def deny(folder: Path, *, expected_hash: str | None = None) -> None:
    with pytest.raises(HistoricalReceiptIntegrityError):
        verify_hist001_receipt(folder / "receipt.json", source_root=SOURCE, expected_sha256=expected_hash)


def test_unaltered_full_tables_verify(original_run: Path) -> None:
    assert verify_hist001_receipt(original_run / "receipt.json", source_root=SOURCE)["source_verified"]


@pytest.mark.parametrize("file", [
    "setA_center.csv", "setA_spherical.csv", "j2141/j2141_solver_output_filled.csv",
    "j2141/j2141_lensing_output_filled.csv", "j2141/j2141_acceptance_scoreboard_filled.csv",
    "setA_center.json", "j2141/j2141_run_summary.json",
])
def test_tampered_table_or_summary_denied_even_if_self_resealed(original_run: Path, tmp_path: Path, file: str) -> None:
    folder = copy_run(original_run, tmp_path)
    p = folder / file
    # Change a meaningful result, then repair every self-contained digest.
    if file.endswith(".csv"):
        modifications = {
            "setA_center.csv": ("einstein_radius_pull_sigma", 0.2),
            "setA_spherical.csv": ("einstein_radius_pull_sigma", 0.2),
            "j2141/j2141_solver_output_filled.csv": ("rho_shadow_Msun_per_kpc3", 1000.0),
            "j2141/j2141_lensing_output_filled.csv": ("predicted_einstein_radius_arcsec", 0.1),
            "j2141/j2141_acceptance_scoreboard_filled.csv": ("value", 0.1),
        }
        column, delta = modifications[file]
        alter_parsed_csv_number(p, column, delta)
    else:
        data = json.loads(p.read_text())
        if file == "setA_center.json":
            data["results"]["n_both_pass"] = 5
        else:
            data["metrics"]["velocity_reduced_chi2"] = 1.2087208637638946
        p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    reseal(folder, file)
    deny(folder)


def test_coordinated_forged_lens_row_pass_with_updated_self_hash(original_run: Path, tmp_path: Path) -> None:
    folder = copy_run(original_run, tmp_path)
    csv_path = folder / "setA_center.csv"
    alter_parsed_csv_number(csv_path, "einstein_radius_pull_sigma", 0.1)
    reseal(folder, "setA_center.csv")
    deny(folder)


def test_forged_physical_provider_status_with_recomputed_receipt_hash(original_run: Path, tmp_path: Path) -> None:
    folder = copy_run(original_run, tmp_path)
    rec = json.loads((folder / "receipt.json").read_text())
    rec["physical_provider_admitted"] = True
    raw = canonical_json(rec)
    (folder / "receipt.json").write_bytes(raw)
    (folder / "receipt.sha256").write_text(hashlib.sha256(raw).hexdigest() + "\n")
    deny(folder)


def test_forged_replay_of_archive_with_self_hash(original_run: Path, tmp_path: Path) -> None:
    folder = copy_run(original_run, tmp_path)
    rec = json.loads((folder / "receipt.json").read_text())
    rec["archived_robustness"]["status"] = "REEXECUTED_ALL_4000_TRIALS"
    raw = canonical_json(rec)
    (folder / "receipt.json").write_bytes(raw)
    (folder / "receipt.sha256").write_text(hashlib.sha256(raw).hexdigest() + "\n")
    deny(folder)


def test_forged_child_command_denied_with_self_hash(original_run: Path, tmp_path: Path) -> None:
    folder = copy_run(original_run, tmp_path)
    steps = json.loads((folder / "execution_steps.json").read_text())
    steps[0]["command"] += ["--adjust-gate-from-lens-data"]
    data = canonical_json(steps)
    (folder / "execution_steps.json").write_bytes(data)
    rec = json.loads((folder / "receipt.json").read_text())
    rec["output_files"]["execution_steps.json"] = hashlib.sha256(data).hexdigest()
    rec["steps_sha256"] = hashlib.sha256(data).hexdigest()
    rec_bytes = canonical_json(rec)
    (folder / "receipt.json").write_bytes(rec_bytes)
    (folder / "receipt.sha256").write_text(hashlib.sha256(rec_bytes).hexdigest() + "\n")
    deny(folder)


def test_extra_file_in_run_inventory_denied(original_run: Path, tmp_path: Path) -> None:
    folder = copy_run(original_run, tmp_path)
    (folder / "unapproved_extra.csv").write_text("independently validated data\n")
    deny(folder)


def test_symlinked_output_denied(original_run: Path, tmp_path: Path) -> None:
    folder = copy_run(original_run, tmp_path)
    target = folder / "setA_center.csv"
    backup = tmp_path / "backup.csv"
    shutil.copyfile(target, backup)
    target.unlink()
    try:
        target.symlink_to(backup)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are disabled in this test environment")
    deny(folder)


def test_untrusted_expected_digest_denied(original_run: Path) -> None:
    with pytest.raises(HistoricalReceiptIntegrityError, match="expected receipt"):
        verify_hist001_receipt(original_run / "receipt.json", source_root=SOURCE,
                               expected_sha256="0"*64)


def test_source_pack_substitution_denied(original_run: Path, tmp_path: Path) -> None:
    source = tmp_path / "hist001_untrusted"
    shutil.copytree(SOURCE, source)
    (source / "swells_pack_v2/solv/dmalane.py").write_text("# altered source\n")
    with pytest.raises(HistoricalReceiptIntegrityError):
        verify_hist001_receipt(original_run / "receipt.json", source_root=source)


def test_whitespace_change_rejected_by_independent_expected_digest(original_run: Path, tmp_path: Path) -> None:
    folder = copy_run(original_run, tmp_path)
    original_digest = hashlib.sha256((folder / "receipt.json").read_bytes()).hexdigest()
    p = folder / "setA_center.csv"
    p.write_bytes(p.read_bytes() + b"\n")
    reseal(folder, "setA_center.csv")
    deny(folder, expected_hash=original_digest)
