# HIST-001 — Historical J2141 / SWELLS Set A: execution and integration plan

## Implemented here: isolated, source-exact historical regression

- Original source: March 14, 2026 frozen SWELLS merged triad `swells_pack_v2/solv/*.py` **copied byte-for-byte**, with the original fitted J2141 config, cleaned lens tables, published SWELLS support tables, and strict regression baseline.
- Original nested archive: `dma_swells_benchmark_pack_v2_merged_acceptance_triad_v7p2_clean_build_stagec_checklist_2026-03-14 (1).zip`, 1,214,157 bytes, SHA-256 `283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e` (unmodified source remains in external June master archive; we do **not** re-archive it in Git).
- Parent June master archive SHA-256 `8609eb7896114f26f9355553208930bbdba5402d20a8c3454bc80c114f81f9f0`; source location: <https://drive.google.com/file/d/1SFGcJvNGeanT3Ro4OyBxWd5x_oEmhiOk/view>.
- The 46 selected source + data files remain **unmodified**. Hashes are pinned in `research/legacy/hist001/SOURCE_LOCK.json` and checked before running. Stage C external acquisition and the bulk of original archival outputs are deliberately not included.
- Historical model: `dma_v0p1_test1_axisym_structproj_baryonq`, using fitted baryon and gate parameters plus radius-proxy and structured baryonic-shadow projection. Official provisional portable candidate: `ra0_gated_geometry_sigmoid_reg_v2`.
- The original solver works in a disposable copy to prevent writes into immutable Git inputs. A separate wrapper implements **one predeclared spherical-projection ablation** without editing the archived solver or retuning anything.

```bash
python -m pip install -r requirements/hist001-constraints.txt
python tools/replay_hist001.py --preflight-only
python tools/replay_hist001.py --out runs/hist001 --ablation
python -m pytest -q tests/test_hist001_replay.py
```

### Acceptance and negative evidence

| Case | Frozen value | Role |
|---|---:|---|
| J2141 velocity reduced chi² | 1.1087208637638946 | Historical fitted regression |
| J2141 Einstein-radius pull | 1.2456888888888888σ | Historical fitted regression |
| J2141 lensing-mass pull | 0.20461194029850702σ | Historical fitted regression |
| J2141 η−1 magnitude | 0 | Conditional no-slip by construction |
| Set A mean absolute Einstein-radius pull | 0.975973270592819σ | Historical central regression |
| Set A mean absolute mass pull | 0.5980326367412955σ | Historical central regression |
| Set A structured-projection dual passes | 6/6 | Historical central regression |
| **Set A spherical-projection dual passes** | **2/6** | Newly rerun no-refit ablation |
| **Set A spherical mean absolute radius pull** | **8.168644014357623σ** | Newly rerun negative |
| 1% geometry/morphology width, 1,000 archived trials | 323/1,000 six-pass | **Archived**, not rerun here |
| 2% width | 140/1,000 six-pass | **Archived**, not rerun here |
| 5% width | 23/1,000 six-pass | **Archived**, not rerun here |
| 10% width | 3/1,000 six-pass | **Archived**, not rerun here |

**No inference of independent holdout validation, covariant physical lensing, current Native v1.7.2 equivalence, CDM replacement, perturbation/CMB prediction, or Theory-State promotion.**

## Exact next integration increments (each separate PR)

### HIST-001A — installed backend adapter, without source modification

Define a `LegacyHistJ2141Backend` read-only adapter exposing exactly two capabilities: `historical_rotation_lensing_regression` and `historical_setA_portability`. It must execute the frozen `solv` code in a subprocess/isolated directory and consume its output as a restricted `RunReceipt`. Do **not** expose the outputs as native v1.7.2 `lensing` physical predictions. The core `RunSpec` requires source SHA, finite model ID, numerical library versions, input table SHA, projection identity, and data-use role `REGRESSION`; it must reject `HELD_OUT_VALIDATION` for these same source tables. Pass criterion: `eset historical j2141 --strict` emits the same 4 scalars and round-trip verifiable receipt while refusing unsupported observables.

### HIST-001B — original robustness evaluator and uncertainty scope

Recover the original accelerated geometry/morphology Range-Finder evaluator from the master archive, including exact seed and six perturbed input fields; verify central equality, the 600 pre-run transition-radius checks, and independently replay all 4 × 1,000 trials at 1/2/5/10% with original counts, without retuning. Preserve failed lenses and sensitivity width explicitly. Reproduce the milder-half-circularization ablation with exactly the archived intervention. Any change in outputs creates a new executable identity; do not alter the frozen baseline.

### HIST-001C — declared model/equation crosswalk

Link this historical backend to the canonical ESET graph through a **noncanonical evidence overlay**, using original source filenames, SHA-256 and the older ESET3/4 DM-A branch identity. Register the equations/assumptions: `∇·(ε∇Φ)=4πGρ_b`, `ε` radius-proxy gate, halo shadow-density/projection approximation, fitted baryon/axis ratios, conditional `Φ=Ψ` and projected lens score. Explicitly mark distinctions from the current fixed-`M_P` one-material-map v1.7.2 theory: no current covariant `X=I_struct F_charge G_local` derivation, no sourced charge law, no current linear Einstein/Boltzmann prediction, and no proof that the fitted projected shadow is a physical Weyl-lensing observable. No old model status inherited by v1.7.2.

### HIST-001D — independent reproduction and observations

Lock published SWELLS II/III source table/measurement assumptions, stellar mass/IMF and redshift/cosmology conventions, and perturbations with physically justified uncertainties and covariance. Audit solver convergence with multiple radial mesh/projection quadratures, astrophysical priors, negative controls, same-solution dynamics vs lensing consistency and no post-outcome projection selection. Freeze a **genuinely new** independent lens sample before accessing outcomes. Do not count the six development lenses as unseen holdouts. Real physical admission remains controlled by Theory-State, not GitHub.

### HIST-001E — current Native v1.7.2 bridge: prove compatibility or keep separate

Only after a source-level field/action/constitutive crosswalk may an implementation claim carryover to Native ESET. The current one-map `φ^A`, fixed reduced Planck mass, full causal MEM and separately staged DM-A response are not interchangeable with legacy radius-lookup and projected-density recipes. Implement formal counterchecks for GR/off limit, tensor slip, conservation, source/law completeness, current `F_charge` and material backgrounds. If no precise equivalence exists, classify `DISTINCT_HISTORICAL_THEORY`, not failed Native cosmology and not a merged module. Native perturbation and physically admitted lensing must be a new finite-model identity.

## GitHub CI, packaging, and source security

- The root B2 package/CLI is untouched by this PR. Original historical modules live in `research/legacy/hist001` outside installable `native_eset` to preserve independent model identity.
- `requirements/hist001-constraints.txt` supplies pinned numpy/pandas/scipy for this research lane only. CI runs on Ubuntu and Windows (Python 3.10/3.12/3.13). Any floating-point tolerance differences are investigated, not tuned away.
- Raw SWELLS small input tables are included because the historical tests explicitly consume them; this is a **publication/reuse-rights review point** before further source/data widening in the public repository.
- Full master archive and 1,000-trial datasets remain off-Git; only narrow frozen summaries are imported, hashes recorded. No raw private Theory-State graph, broader survey FITS, session tokens, or personal data.
- Both central passes and the spherical negative must be replayed in CI. A green run has meaning `HISTORICAL_REGRESSION_REPRODUCED_NOT_SCIENTIFICALLY_VALIDATED`.
