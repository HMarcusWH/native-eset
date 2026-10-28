# HIST-001A/1 — source-bound historical specification (review contract)

This increment **does not run historical physics through the installed `native_eset` package**. HIST-001 already has a separate cold replay (`tools/replay_hist001.py`). Here we register a trusted source and a non-promoting run request before attaching the executor in HIST-001A/2 and the public CLI in HIST-001A/3.

## Frozen identity

- Theory: `LEGACY_ESET3_DM_A_FITTED_STRUCTURED_PROJECTION` — **not** Native fixed-Planck-mass v1.7.2.
- Finite model: `HIST-001-SWELLS-J2141-SETA-FROZEN`.
- Backend ID: `legacy-hist001-j2141-seta`, with **disabled** execution and two eventual capabilities (`historical_rotation_lensing_regression`, `historical_setA_portability`). No general physical lensing, CMB, growth, or background capability.
- Independently pinned `research/legacy/hist001/SOURCE_LOCK.json` SHA-256: `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`.
- Original frozen March archive SHA-256: `283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e`. That external archive is **not** included in the installed Python wheel.
- Trust metadata: `native_eset.historical/hist001_approved_lock.json`, itself independently checked by `hist001_approved.py`. The metadata is versioned package data and an **integrity** reference, not a signature or independent scientific authority.
- Frozen source bundle: 46 exact original source/config/measurement files plus three SHA-pinned original negative-evidence summaries. No fitting or dataset-selection options.

## Public Python API (source and spec; no solver dispatch)

```python
from native_eset.historical import HistoricalRunSpec, verify_hist001_source
from native_eset.historical.hist001_spec import CENTRAL, CENTRAL_SPHERE

source = verify_hist001_source("research/legacy/hist001")
assert source["physical_provider_admitted"] is False
assert source["capability_executable"] is False

spec = HistoricalRunSpec.from_mode(CENTRAL_SPHERE)
assert spec.raw["claim_intent"] == "REGRESSION_ONLY"
# History is a source-bound regression ONLY. There is no executable HIST-001 package backend yet.
```

`HistoricalRunSpec` enforces schema `NATIVE_ESET_HIST001_RUN_SPEC_V1`, fixed original branch/candidate/observable and lens IDs, original fitted calibration history, `REGRESSION` use, original SHA pin(s), source-native kpc/km/s/Msun/arcsec convention, and exact output classes. Both modes are strict: `STRICT_CENTRAL`, `STRICT_CENTRAL_PLUS_SPHERICAL_NEGATIVE`. There are **no** numeric overrides, user-selected lenses, physical claims, unrestricted scope, or holdout role. The source root is an explicit filesystem argument to the source verifier, not a machine path serialized in the portable RunSpec.

Returned `.raw` is an independent decoded object, never a mutable alias of the internal immutable canonical JSON bytes. Changing request fields requires a new request digest; changing the original fitted implementation requires a separately reviewed historical source identity and cannot be accomplished through this spec.

## Verification and failure gates

`verify_hist001_source(root)` checks the approved metadata, independently pinned original `SOURCE_LOCK.json` bytes, file inventory/hash for all 46 sources plus 3 archived negative summaries, exact branch/candidate/config/baseline/table identifiers, full Set A lens IDs/order, no extra source files, no symlinks, and modest file/total-byte budgets. It reads source files **without importing or executing legacy code**; it never contacts Drive or publishes a scientific verdict.

New tests exercise altered solver/config/table/baseline/negative summaries, edited lock+solver pair, changed or missing files, symlinks, forged packaged metadata, changed model, data role, lens selection, fake validation/physical provider, wrong units/gauge, arbitrary fitted parameters, duplicate-key/nonfinite/oversize JSON, and mutation after spec construction. The original GR-only RunSpec/receipt verifier is unchanged.

**Important limitation:** SHA-256 comparisons are integrity checks, not cryptographic signatures or claims that code from an untrusted origin is safe to run. This increment does not execute those sources; the isolated subprocess and runtime environment controls belong to HIST-001A/2.

## PR sequencing and acceptance

1. **A/1 (this PR):** metadata, source byte verification, immutable HistoricalRunSpec, disabled capability, tests, installed-wheel trust-data import check. Must pass all six GitHub Ubuntu/Windows Python 3.10/3.12/3.13 jobs. The March 46-file original pack must remain bit-for-bit identical.
2. **A/2 (next):** wrap unchanged `tools/replay_hist001.py` with package-bound isolated subprocess execution, expected numerical/negative gates, output inventory and historical verified receipt. Do not weaken the GR-specific receipt verifier.
3. **A/3 (later):** installed `eset historical j2141` CLI, external `--source-root`, strict verifier dispatch and complete installed-wheel cold end-to-end across CI. Only then change the new historical capability from disabled to executable.

Known historical outcomes: J2141 reduced velocity χ² ≈1.1087208637638946, Set A central 6/6, spherical-projection 2/6. Original archived 1/2/5/10% 1000-trial results 323/140/23/3 must **remain labeled archived, not replayed** until HIST-001B.

**Final A/1 status when green: `HIST001_A1_SOURCE_BOUNDARY_READY_EXECUTOR_DISABLED`.** Nothing in this PR proves physical/empirical ESET validity or permits a new canonical Theory-State promotion.
