import pytest
from native_eset.gates import Admission, AdmissionError, ClaimStatus


def test_internal_pass_not_physical_admission():
    a=Admission(provider_id="P1R", status=ClaimStatus.INTERNAL_PASS)
    with pytest.raises(AdmissionError):
        a.authorize("CMB_TT")


def test_admitted_provider_requires_declared_output_and_receipt():
    a=Admission("SCOPED",ClaimStatus.PHYSICAL_PROVIDER_ADMITTED,("H_of_z",))
    with pytest.raises(AdmissionError):
        a.authorize("H_of_z")
    a=Admission("SCOPED",ClaimStatus.PHYSICAL_PROVIDER_ADMITTED,("H_of_z",),"sha256")
    with pytest.raises(AdmissionError):
        a.authorize("H_of_z")
    with pytest.raises(AdmissionError):
        a.authorize("CMB_TT")
