"""Block package version drift and accidentally omitted CI audit steps."""
from pathlib import Path
from native_eset import __version__

def test_source_version_matches_project_metadata():
    root = Path(__file__).resolve().parents[1]
    assert __version__ == "0.1.0"
    assert 'version = "0.1.0"' in (root / "pyproject.toml").read_text(encoding="utf-8")

def test_security_scan_is_mandatory_on_ci():
    workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/ci.yaml").read_text(encoding="utf-8")
    assert "run: python tools/security_audit.py" in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "run: python tools/check_manifest.py" in workflow
