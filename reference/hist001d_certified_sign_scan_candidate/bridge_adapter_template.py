"""Adapter CONTRACT ONLY. Must be implemented inside the sealed source-bound package.

Never use this template to create a source-replayed or scientific sign claim.
"""
from certified_sign_scan import SourceContract, Unresolved

class ProtectedHIST001DAdapter:
    def replay_parents(self, contract: SourceContract) -> dict:
        """Verify the pinned original 46+3 source, mathematical model, root
        bracketing ZIP, the separately sealed global uniqueness theorem, and
        all parent proof traces. Return a validated attestation matching the
        keys in parent_attestation(). Absolutely no check-by-hash-only shortcut.
        """
        raise Unresolved("NOT_IMPLEMENTED_SEALED_PARENT_SOURCE_REPLAY_REQUIRED")

    def point_guard(self, lens: str, x_hex: str) -> dict:
        """Call the *existing* strict exact-real two-engine sign API. Return:

        {"schema":"HIST001D_TWO_ENGINE_SIGN_GUARD_V1",
         "kind":"POINT", "model_id":MODEL_ID, "source_sha256":SOURCE_SHA256,
         "lens":lens,"lo_hex":x_hex,"hi_hex":x_hex,"status":"CERTIFIED",
         "engines":[{"engine_id":"<unique engine A>",
                     "lo":"<exact signed rational>","hi":"<exact signed rational>",
                     "proof_trace_sha256":"<SHA from replayed engine trace>"},
                    {"engine_id":"<unique engine B>",
                     "lo":"<rational>","hi":"<rational>",
                     "proof_trace_sha256":"<SHA>"}]}

        If the sign is inconclusive, return status UNRESOLVED.
        Do not use float residuals, synthetic signs, or a new Bessel shortcut.
        """
        raise Unresolved("NOT_IMPLEMENTED_SEALED_TWO_ENGINE_SIGN_GUARD_REQUIRED")

    def range_guard(self, lens: str, lo_hex: str, hi_hex: str) -> dict:
        """Optional. Rigorously enclose exact-real H_new over the *entire*
        requested real interval, using BOTH replayed interval engines. Use
        kind='RANGE_ALL_REAL'. A sample-only endpoint sign is NOT sufficient.
        """
        raise Unresolved("NOT_IMPLEMENTED_ALL_REAL_RANGE_ENCLOSURE_REQUIRED")


def make_adapter():
    return ProtectedHIST001DAdapter()
