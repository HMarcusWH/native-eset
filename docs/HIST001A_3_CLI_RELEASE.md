# HIST-001A/3 — Installed historical regression CLI and wheel gate

**Scope**: source-exact HIST-001 J2141 and SWELLS six-lens Set A **historical fitted regression only**. This increment activates only the dedicated historical package capability; it does not change the 46 frozen originals, source locks, GR-control RunSpec/receipt validator, private Theory-State, or any current Native v1.7.2 physical provider.

## Installed command and explicit external source

With the package installed and the separately distributed source pack available:

```bash
eset historical j2141 --source-root /verified/research/legacy/hist001 --out runs --strict --ablation spherical
eset verify --receipt runs/<hist001-run-id>/receipt.json --source-root /verified/research/legacy/hist001 --expected-sha256 <independently-recorded-digest>
```

`--strict` is mandatory. `--ablation spherical` is optional, produces the exact 2/6 no-refit spherical-projection negative, and does not authorize fitting or any extra observable. Omitting the ablation executes the strict central regression only. The source pack remains external to the installed wheel; `--source-root` requires all 46 historical files, all three original negative source records, an immutable trusted source lock, and exact six-lens selection.

`eset doctor --historical-source-root ...` verifies source bytes but **does not execute physics**; the `eset status` capability registry marks only `historical_rotation_lensing_regression` and `historical_setA_portability` as executable. Physical ESET, unrestricted lensing/CMB and current fixed-MP v1.7.2 remain unsupported.

## Receipt schema isolation and integrity

`eset verify` performs a bounded strict schema read and dispatches exact `NATIVE_ESET_HIST001_RUN_RECEIPT_V1` to `verify_hist001_receipt`; the historical path **requires** `--source-root`. Existing `NATIVE_ESET_RUN_RECEIPT_V2` GR controls remain routed unchanged to `verify_run_receipt` and disallow `--source-root`. Unsupported receipt types fail closed. A user-supplied digest checks external integrity; even with a repaired self-hash, historical verifier rejects forged physical/admission flags, per-lens numerical changes, incorrect source identity and false claims of reexecuted archived robustness. Hashes are not digital signatures or independent proofs that code actually executed.

## Installed-wheel cold verification

`tools/hist001_wheel_smoke.py` runs `python -I -m native_eset` from a temporary directory unrelated to the checkout **after** a clean wheel install, proves `native_eset` imports from site-packages, runs the full central+spherical historical computation from an explicit source path, verifies the receipt and rejects missing source roots, missing strict mode and incorrect expected digests. The existing GR wheel smoke also runs. The pinned source pack is not vendored into the wheel.

**Required release gates:** Ruff; Git-index source SHA manifest; bounded security scan; all historical and GR tests; native wheel/sdist build; installed-wheel cold replay; all six Ubuntu/Windows Python 3.10/3.12/3.13 jobs green on PR and merged main. Never overwrite previous releases on failure.

## Frozen numerical and scientific boundary

- Historical J2141 reduced velocity chi² `1.1087208637638946`; Einstein pull `1.2456888888888888σ`; mass pull `0.20461194029850702σ`; imposed no-slip.
- Six development lenses: central dual radius/mass pass `6/6`; spherical-projection negative `2/6`.
- Geometry/morphology 1/2/5/10% archived 1,000-trial survival counts `323/140/23/3`: **archived only**, not rerun here.
- The six lenses are fitted historical development regressions, not blind holdouts.
- `physical_provider_admitted=false`, `native_v172_equivalence_proved=false`, `empirical_validation=NOT_ESTABLISHED`.

**Release decision when CI passes:** `HIST001_INSTALLED_HISTORICAL_REGRESSION_REPRODUCED_NOT_VALIDATED`. Next **HIST-001B** recovers/replays full 4×1,000 geometry RangeFinder trials, preserving original seed, perturbation fields, failures and negative evidence.
