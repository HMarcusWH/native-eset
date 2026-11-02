"""Source-free exact sign migration and QA-length guard regressions."""
import pytest
import sys
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[2]/"reference"/"hist001d_k180_saturation_candidate"
if SOURCE.is_dir():sys.path.insert(0,str(SOURCE))
from signed_gap_contract import source_return_minus_k180_from_legacy

@pytest.mark.parametrize('legacy,corrected',[([4,9],[-9,-4]),([-9,-4],[4,9]),([-3,7],[-7,3]),([0,0],[0,0])])
def test_signed_gap(legacy, corrected):
    assert source_return_minus_k180_from_legacy(legacy)==corrected

@pytest.mark.parametrize('bad',[[],[1],[1,2,3],[2,1],[1.0,2],['1',2],True,None])
def test_invalid_gap(bad):
    with pytest.raises(ValueError):source_return_minus_k180_from_legacy(bad)
