# HIST-001D PR58 — v1r2 attested historical source-mass/K180 arithmetic review

**SOURCE-CONDITIONAL · MATHEMATICAL ONLY · DRAFT · NONPROMOTING — 8 November 2026.**

The March 14 frozen 46+3 original source (SHA-256 `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`) and six 180-node shadow-density arrays remain outside public GitHub. The source-original `Mshadow`/epsilon/clipped-gradient outputs and stored binary64 sample nodes are preserved *byte-identically* to v1. Previous protected v1 source-result hash `4d56fce6b8f28675000585a31efea137c0a9b0c1a5fabd4e730346bbf49008e6`, independent exact-stencil SHA `831db0aa6654fa46af88c31158fcf015fb209628f41b5ea01c7f4dac7204420a`, and 26-case QA SHA `50f74d15b71af099056013b52abf6cbfe6c31f98f2534ec3e9c3960f7d7510e6` remain unchanged.

## Security defect reproduced

The v1 `verify_release.py` imported `independent_stencil_check.check` and `adversarial_qa.audit` from a *locally editable extraction directory* before reading the manifest. Its SHA verification was against the *same local directory's rehashable* manifest. A controlled substitution replaced the independent stencil checker with a function that merely compared the supplied receipt to the archived result and returned the saved independent JSON, then updated the local manifest hash. Executing the original **full** source replay under `python -OO` returned `BESSEL_SOURCE_RELEASE_PASS ... source replay True` (exit 0), despite **not** independently recalculating the exact-dyadic 1,080-node stencil. The protected ZIP was unchanged.

## v1r2 fail-closed replacement

- `attested_replay_v1r2.py` requires an externally authenticated **whole-ZIP SHA-256**. An internal self-rehashed manifest cannot supply or substitute that trust anchor. It rejects duplicate/traversal/symlink ZIP entries, untracked files, missing scientific/nonpromoting flags, wrong source lineage, frozen mass-array changes, tampered saved numerical/QA SHA, and forged local executable source bytes. The attestation binding is conditional on the external SHA trustworthiness.
- The attestor uses Python isolated mode with only the verified source directory inserted, and a fresh temporary extraction. It re-executes the unchanged March source and 180 stored binary64 samples with recorded NumPy/SciPy assumptions. The independent checker consumes **regenerated** results and newly recomputed six binary64 mass arrays, not the saved JSON as authority; the 26-case adversarial QA also reexecutes. All three outputs must have the original sealed byte hashes.
- The v1 `verify_release.py` entrypoint now rejects unpinned calls with `UNRESOLVED` exit 2 and delegates only to the externally pinned attestor. **Successful ZIP/member or CI checks alone are not mathematical proof or physical validation.**
- Source-only regression tests include missing/wrong external pin, a self-rehashed ZIP, swapped local executable, symlinks and traversal, duplicate entries, optimized Python (`-O`/`-OO`), zero budgets, malformed and extra source files. The `-OO` source-dependent run is a separate protected gate.

## Narrow unchanged mathematical result

At each original frozen radial knot, all six `180/180` shadow-density samples and recreated exact float masses reproduce; the independent rational nonuniform-gradient check confirms the frozen K180 fixed-input arithmetic separation. The upper bound for the original finite weighted K180 sum (not the continuum) is `E_round = Σ_i w_i |C r_i² rho_source,i − D_i[m_source]|` since the frozen nonnegative cylinder kernel lies between 0 and 1. This **does not certify an arbitrary-input SciPy Bessel ulp bound**, physical continuous shadow density, arbitrary-aperture continuum quadrature, true source-original off-grid H root or Weyl lensing. These are fitted development lenses, not a blind validation set. No Native v1.7.2 physical provider, D3/D4, sound horizon, no-CDM or cosmology claim is admitted.

## Release and GitHub review

Source-only GitHub changes are limited to an independently pinned attestor, a fail-closed entrypoint, source-free tests/CI/docs and root manifest regeneration on the corrected PR57 branch. Protected original source, SHA-locked parents, full numerical result JSON and binary64 mass arrays remain in the separately versioned **private protected evidence ZIP**. The original parent and v1 release are immutable. External source/licensing/security and mathematical peer review plus exact-head six-platform CI remain premerge requirements. Canonical Theory-State and `main` are unchanged; `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`, `scientific_authority_promoted=false`.
