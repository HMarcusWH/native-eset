# HIST-001D PR #59 — signed K180 stencil/derivative/continuum v1r2 executable-source attestation

**DRAFT · NONPROMOTING · source-connected exact-rational mathematical comparator · 8 November 2026**

The old v1 protected package remains immutable (SHA-256 `b3187bdab19f82a2aadbc4157b78050a27df8857e81f53b536de5eb6a9dc34c2`). Review found **four proof-critical language `assert` checks** in the producer and independent arithmetic. With deliberately corrupted integer square-root behavior, normal Python rejected the false interval but Python `-OO` returned an invalid interval. The source-only fix replaces all four proof assertions with unconditional exceptions and explicitly checks equal-length signed stencil source arrays.

A second, distinct release integrity bug was reproduced: a forged ZIP containing a modified independent checker that **echoed the sealed result instead of recomputing it**, together with an updated ZIP-local manifest, passed original `verify_release.py --full` under `-OO` with exit 0. This forged evidence is not the original v1 archive and is not a mathematical counterexample; it demonstrates that self-consistent hashes do not authenticate the executed proof code.

## v1r2 acceptance contract

`attested_replay_v1r2.py` requires an **independently supplied whole-ZIP SHA-256**, explicit claim nonpromotion, exact ZIP membership and member hashes, pinned critical numerical producer/independent checker/QA SHA, immutable three prior SHA-pinned parents, and unchanged original **three numerical/QA result SHA**. ZIP paths fail closed against traversal, Windows aliases, case-fold collisions, symlinks and unsafe member types. An optionally supplied extracted tree is compared byte-for-byte with the authenticated ZIP, including the actual executable checker. A *fresh* isolated `python -I -OO` extraction regenerates the source-dependent signed K180 producer, independently recomputes the six-lens rational inequalities using alternate integer bisection, and replays the 39 original adversarial cases. Each result must match its original sealed bytes; an unresolved or over-budget calculation returns exit 2 / `UNRESOLVED`.

The old unpinned `verify_release.py --archive ... --full` route now explicitly fails closed. The following is the authoritative protected-source replay:

```bash
python -OO reference/hist001d_k180_signed_stencil_candidate/attested_replay_v1r2.py \
  --archive /secure/HIST001D_SIGNED_STENCIL_V1R2_PROTECTED.zip \
  --expected-sha256 <independently-retrieved-exact-release-SHA> \
  --budget-seconds 180
```

The local 22 source-free original tests and 33 new `unittest` negatives are required in the public branch's six-platform CI; the 33 new tests use `unittest.TestCase` so they actually execute with assertions disabled. **55 total source-free tests** do not by themselves establish source-bound numerical science. The full protected replay and independent mathematical review are distinct stronger gates.

## Scope and nonclaims

The exact rational split `Q_src-P_*=(Q_src-Q_deriv)+(Q_deriv-P_*)` remains the same selected original-frozen-node mathematical result, including the six signed fixed diagnostic aperture remainders and six full source-crossing aperture-band positive witnesses. The inherited Bessel source derivative intervals, source frozen W/r/rho, fixed-point continuum integrations and source-defined q aperture bands are **not independently re-derived** in this v1r2 packet. This is not the original compiled off-grid March solver, not an arbitrary-input SciPy Bessel ulp theorem, not a physical Weyl lensing provider, not blind empirical validation and not Native ESET provider admission. The six lenses remain prior-fitted development data. `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`, `scientific_authority_promoted=false`.

Original protected source arrays, numerical JSONs and parent archives are **not** included in the public GitHub PR. The original v1 archive and its mathematical data are preserved; only the fail-closed code/test/release metadata are versioned. GitHub source-only CI, human code/security/license/rights review and independent mathematical review remain required before any merge. No canonical Theory-State promotion is implied by a repository merge.
