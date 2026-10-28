# HIST-001A/2 — Source-exact historical execution and independently checked receipts

**Scope:** Internal package-level execution only. The installed historical CLI and public
backend capability remain disabled until HIST-001A/3. Historical calibrated regression is
not a current Native ESET v1.7.2 physical or observational prediction.

## Source anchors and non-change boundary

- Previous verified main: `53a5ee910afdd6027d9af092a4d9e1ca4b26c7b7` (HIST-001A/1).
- Approved frozen pack: `research/legacy/hist001` (46 original byte-locked files and three archived negative-control summaries). Independently approved `SOURCE_LOCK.json` SHA-256 is
  `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`.
- The historical theory is `LEGACY_ESET3_DM_A_FITTED_STRUCTURED_PROJECTION`, finite identity
  `HIST-001-SWELLS-J2141-SETA-FROZEN`, candidate `ra0_gated_geometry_sigmoid_reg_v2`.
- Original `swells_pack_v2/{solv,configs,cleaned,raw_support,templates,validation}` files
  **must not change**. No new data selection, calibrated parameter change, model inference,
  fit, stage-C import, physical-provider admission or Theory-State mutation is permitted.

## Runnable package API (not yet CLI)

```python
from pathlib import Path
from native_eset.historical.hist001_spec import HistoricalRunSpec, CENTRAL_SPHERE
from native_eset.historical.hist001_backend import LegacyHistJ2141Backend
from native_eset.historical.hist001_receipt import verify_hist001_receipt

source = Path('research/legacy/hist001').resolve()
spec = HistoricalRunSpec.from_mode(CENTRAL_SPHERE)
result = LegacyHistJ2141Backend().run(spec, source_root=source, output_root=Path('runs'))
verified = verify_hist001_receipt(
    Path(result['output_dir']) / 'receipt.json',
    source_root=source,
    expected_sha256=result['receipt_sha256'],
)
assert verified['physical_provider_admitted'] is False
```

`CENTRAL` also works and deliberately omits the spherical negative artifacts. This does **not**
enable `eset historical` yet, nor set `CAPABILITIES['legacy-hist001-j2141-seta'].executable` true.
The installed wheel holds only the adapter/approval metadata/expected numerical rows; it does
**not** vendor the original frozen source pack. Supply a separately verified `source_root`.

## Execution and receipt protocol

1. Reconstitute the immutable HistoricalRunSpec from canonical bytes and SHA-256, check
   approved packaged trust anchor, and SHA-check every original source and archived negative.
2. Compute content-addressed run ID from spec digest, full executable package source digest,
   and Python/OS/NumPy/Pandas/SciPy environment. Reject an existing run directory.
3. Create a staging directory outside the original source and SHA-check a full disposable
   source copy. Run the original J2141 and Set A commands with a fixed candidate/config,
   subprocess timeout, no shell, and a constrained process environment. In spherical mode
   apply only the known original spherical-cylindrical projection via a process-local wrapper.
4. Preserve five newly generated J2141 outputs, two Set A outputs and optionally two
   spherical outputs. Also store the canonical RunSpec and exact command step receipts.
5. Verify original bytes remain unchanged. Compare every row of J2141/Set A/spherical CSVs
   against SHA-pinned regression records with fixed tolerances; recompute six lens IDs,
   radius/mass dual gates, means, and J2141 scalar tolerances from output tables.
6. Write canonical `NATIVE_ESET_HIST001_RUN_RECEIPT_V1` with exact output hashes, all step
   hashes, source lock, original archive, model/mode, environment and explicit claim caps.
   Write `receipt.json` last, independently verify the entire staged result and atomically
   rename to its final content-addressed directory. Failure leaves no completed receipt.

`verify_hist001_receipt` rejects noncanonical spec/receipt files, wrong source root or pack,
changed original input, wrong IDs, tampered tables even when their self-hash is repaired,
changed solver command, missing/extra paths, symlinked artifacts, false provider/holdout
status or claims that the old 4x1000 robustness campaign was reexecuted.
An **external independently supplied receipt SHA-256** is required to detect deliberate
nonsemantic byte edits that are self-resealed; SHA digests are not digital signatures or
independent proofs that the recorded subprocesses actually ran.

## Exact numerical regression gates

- J2141: reduced velocity chi² `1.1087208637638946`, radius pull
  `1.2456888888888888`, mass pull `0.20461194029850702`, imposed `|eta-1|=0`.
- Six development lenses: central Set A `6/6`, radius mean `0.975973270592819σ`,
  mass mean `0.5980326367412955σ`; spherical projection negative `2/6`, radius mean
  `8.168644014357623σ`, mass mean `3.234216692852517σ`.
- Original archived-only geometry/morphology survival from 1000 trials/width: 323/140/23/3
  at 1/2/5/10%. **These 4000 trials are not newly executed in this increment.**
- These are in-sample/fitted historical baselines, not a held-out test of Native ESET.

## Non-change zones, next increment and release gate

New modules: `src/native_eset/historical/hist001_backend.py`, `hist001_ablation.py`,
`hist001_receipt.py`, `hist001_golden_rows.json`. Tests: `tests/historical/test_hist001_execution.py`,
`test_hist001_receipt.py`. Modify only package data, CI import checks, source SHA manifest and
this documentation. Keep GR control `src/native_eset/runner.py`, `evidence/receipts.py`, the
LegacyJuneBackend background stub, capability executable flag, and historical source files
unchanged.

**HIST-001A/2 accepted only if** original replay and spherical negative execute, full
local suite and each of six Linux/Windows Python 3.10/3.12/3.13 GitHub jobs pass, original
source hashes remain byte-exact, wheel imports the new backend+verifier without bundling the
original data, and all negative/forgery tests reject as designed. Its status is
`HIST001_A2_EXECUTOR_RECEIPTS_READY_CAPABILITY_DISABLED`.

**Next HIST-001A/3:** installed `eset historical j2141 --source-root ... --strict`,
authenticated historical `eset verify` dispatch, full wheel execution from an independent
working directory, and only then enable historical capability. HIST-001B separately reruns
4×1,000 archived robustness trials after A completes.
