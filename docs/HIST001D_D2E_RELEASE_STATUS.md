# HIST-001D/D2e — merged numerical diagnostics and non-certification release ledger

**29 October 2026.** This is a bounded historical fitted-proxy numerical release ledger, not an independent observation, global numerical-error theorem, physically sourced Weyl-lensing provider, proof of Native ESET v1.7.2 equivalence, or a canonical Theory-State promotion.

## Release chain (all six platform jobs passed on each exact merge)

| Package | PR | Merge SHA | Exact post-merge CI |
| --- | --- | --- | --- |
| D2d full radius-dependent independent structured-root integration | [#18](https://github.com/HMarcusWH/native-eset/pull/18) | `f1f70c5703547a24d37267ce2a823bf6653abbba` | [#40950068510](https://github.com/HMarcusWH/native-eset/actions/runs/40950068510) |
| D2e-A sampled root topology, gradient-clipping and finite-cutoff stress | [#20](https://github.com/HMarcusWH/native-eset/pull/20) | `4930e73f7d5eee84d001b02d7fb85269cca92693` | [#40962056889](https://github.com/HMarcusWH/native-eset/actions/runs/40962056889) |
| D2e-B conditional interval root exclusion outside an unresolved guard | [#21](https://github.com/HMarcusWH/native-eset/pull/21) | `a9d174bfcfbc9cebe565dbdba7433572356ca33c` | [#40964163900](https://github.com/HMarcusWH/native-eset/actions/runs/40964163900) |
| D2e-C gradient and radial-continuation alternative error menu | [#22](https://github.com/HMarcusWH/native-eset/pull/22) | `73fd0cc9e69878c5edd194d0a6a334dd9c2512e2` | [#40965990422](https://github.com/HMarcusWH/native-eset/actions/runs/40965990422) |

Original March source lock: `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a` (46 historical source/config/input files plus three archived negative records). All six lenses are historical **fitted development cases**, not blinded holdouts. The original 180-point/120-angle fitted 6/6 and the independent finite-domain D2d 3/6 across 180–11,520 radial points remain **distinct reproducible numerical execution identities**, with no refit.

## Specific outcomes and limitations

- D2e-A: the historical model's normalized critical-mass function shows one **sampled** sign change on 45-, 181- and 721-node radius scans for all six lenses, but sampled positive-slope intervals occur. No root-count theorem follows. Shadow-mass/density negative clipping is inactive on the 42 checked sampled arrays. The 180-grid pointwise interpolated density is about 25,000–53,000 times the 11,520-grid value at 0.1 kpc for the six fitted lenses; fine-root convergence does not prove uniform density convergence. Removing known outer shadow shells to 80 kpc and 100 kpc shifts the checked roots by at most 0.02027 and 0.00636 observational sigma respectively; it does **not** bound unknown mass beyond 120 kpc.
- D2e-B: derives positive-component mass and four-corner `q_eff` bounds for adaptive intervals away from a 2% root guard. A relative mass numerical error allowance of `1e-6` is **assumed and unproved**. A conditional exclusion outside that guard is not a rigorous floating-point interval certificate, a root-uniqueness proof within the guard, or a bound on unmodeled inner/outer mass.
- D2e-C: source-locked `np.gradient` versus edge-order-2/PCHIP derivative alternatives; new analytic inner-Hernquist and hypothetical `r^-4/r^-5` outer shadow continuation scenarios, each a separately identified numerical counterfactual. The tool computes individual root/mass displacements in the historical upper-error sigma normalization. Maxima across this **finite set of scenarios are not global or probability-calibrated error bounds**. No physically sourced continuation outside [0.02,120] kpc has been admitted.

## Reproducibility and release receipts

The continuous-integration matrix is Ubuntu/Windows × Python 3.10/3.12/3.13. Each job runs pytest, Ruff, Git-index SHA manifest validation, original source-lock and existing historical regressions. D2e-A/B/C CLI execution and a **second source-reexecuting verifier** run in separate Python processes. CI source reexecution proves reproducibility of the **same finite numerical prescriptions**; it does not provide a mathematical error theorem or an independent empirical sample.

Run the latest three reproducible diagnostics from exact GitHub source:

```bash
python tools/hist001d_d2e.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_a
python tools/hist001d_d2e.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_a/receipt.json
python tools/hist001d_d2e_interval.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_b
python tools/hist001d_d2e_interval.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_b/receipt.json
python tools/hist001d_d2e_error_budget.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_c
python tools/hist001d_d2e_error_budget.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_c/receipt.json
```

The CI workflow additionally uploads the **three generated report/receipt sets** only on successful pushes to `main`. Those artifacts have their own provider file IDs and retention period; they are execution evidence, not cryptographic signatures or raw private-source snapshots.

## Gate disposition (MUST remain fail closed)

`HIST001D_D2E_NUMERICAL_SENSITIVITY_COMPLETE_SCOPED_NOT_ERROR_CERTIFIED` is the correct status of the implemented A/B/C work. The following must remain **FALSE / NOT_ESTABLISHED**:

- `root_uniqueness_mathematically_certified`
- `global_error_bound_established`
- `uniform_quadrature_error_budget_proved`
- `mass_outside_finite_domain_bounded`
- `physical_weyl_lensing_derived`
- `physical_provider_admitted`
- `native_v172_equivalence_proved`
- `new_holdout_scored`
- `empirical_validation=NOT_ESTABLISHED`

[D2e scientific issue #19](https://github.com/HMarcusWH/native-eset/issues/19) remains **OPEN** for validated quadrature/derivative error enclosures, full-domain root isolation including tangencies/guard, and a source-authorized radial continuation or explicit proof that no such closure is available. [D3/D4/D5 parent issue #11](https://github.com/HMarcusWH/native-eset/issues/11) remains **OPEN** for published correlated/asymmetric measurement covariance, a truly disjoint preregistered holdout, and a same-sourced metric/Weyl physical lensing derivation. [HIST-001B PR #7](https://github.com/HMarcusWH/native-eset/pull/7) is separate and unmerged; [HIST-001E issue #12](https://github.com/HMarcusWH/native-eset/issues/12) still requires explicit contemporary action/field transport or distinct historical-theory classification.

**Authority separation:** GitHub code/CI are executable evidence; Drive release archives and handovers are provenance; only the separate canonical Theory-State decision process can change scientific provider/validation status. Do not infer scientific promotion from green software CI.
