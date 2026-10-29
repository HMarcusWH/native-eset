# HIST-001D — frozen J2141/Set A source, numerical resolution, and holdout firewall

**29 October 2026 · noncanonical research evidence · original historical model ONLY**

## Identity, source and scope

- Candidate: `ra0_gated_geometry_sigmoid_reg_v2` from the March 14 frozen SWELLS triad.
- Original SOURCE_LOCK.json SHA-256: `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`.
- Exact source inventory: 46 SHA-locked solver/config/data files and three archived negative controls. No original file changed.
- This study evaluates six **previously fitted/development** lenses (J0822+1828; J0915+4211; J0930+2855; J1021+2028; J1111+2234; J1135+3720). No fresh holdout was selected or scored.
- The original Set A lens input is `cleaned/lens_set_A_run_fo_74bb5e.csv`; axis ratios are merged from `raw_support/swells3_table3_structure.csv`; angular diameter scales come from `cleaned/setA_scale_kpc_per_arcsec.csv`. The exact input digests are pinned by the HIST-001A source lock.
- The original calculation fixes flat LCDM reference distances with H0=70 km/s/Mpc, Omega_m=0.3. The fitting law, baryon masses, radius gate, shadow-density method and geometry projection are held fixed in this diagnostic.

## D1 — publication and uncertainty lineage audit (partial, NOT completed)

Primary sources informing the audit:

- [SWELLS I: sample definition](https://arxiv.org/abs/1104.5663) — a lens-selection sample, not a disjoint blind holdout established here.
- [SWELLS II: J2141 bulge/disc/halo](https://arxiv.org/abs/1101.1622) — simultaneous lensing and kinematics with substantial model/IMF dependence.
- [SWELLS III: 20-lens stellar fractions](https://academic.oup.com/mnras/article/422/4/3574/1055422) — mass inside lens critical curves, SPS stellar masses and IMF comparisons.
- [SWELLS IV: independent J2141 precision model](https://arxiv.org/abs/1201.1692) — a different axisymmetric halo/stellar dynamics implementation.
- [SWELLS V: bulge/disc IMF distinction](https://arxiv.org/abs/1206.4310) — bulge and disc mass inference need not share the same IMF response.

The original regression uses the **upper quoted radius and projected-mass error** as the denominator for both signs of each residual. It does not model a full observational covariance, asymmetric likelihood, shared stellar population/IMF uncertainty, redshift/distance uncertainty, or the original published paper model correlations. The historical trial-width uniform perturbations are **not** a substitute for a paper-justified joint uncertainty model. Underlying row-level primary-paper reconstruction, covariance and data-redistribution rights remain **OPEN**.

## D2 — deterministic no-refit numerical discretization study

Original source `solv/run_setA_port_cand.py` uses radial `linspace(0.02,120,180)`, a trapezoid projection matrix, and `projected_disk_mass_exponential(...,ntheta=120)`. The parallel evaluator `tools/hist001d_convergence.py` calls these same source functions but explicitly changes only the radial grid size and/or angular quadrature. A 180/120 source-original slow-path readback matches all six predicted radius/mass pulls to 1e-9. A separate source-original slow-path substitution on 360/120 independently confirmed **zero numerical differences** from the diagnostic evaluator in local tests.

The following six regimes were fixed in the local diagnostic code before the first local execution; this was **not** a third-party-blind preregistration. A further 720/1440/2880-point follow-up below was selected after seeing the initial instability and is explicitly exploratory.

| Radial points | Angular points | Joint 2-sigma passes | Mean absolute radius pull (sigma) | Changed lenses vs 180/120 |
|---:|---:|---:|---:|---|
| 90 | 120 | **2/6** | 2.684115 | J0822, J0930, J1021, J1111 |
| **180** | **120** | **6/6** | 0.975973 | None (historical baseline) |
| 360 | 120 | **3/6** | 1.574949 | J0822, J1021, J1111 |
| 180 | 60 | 6/6 | 0.874297 | None |
| 180 | 240 | 6/6 | 1.028745 | None |
| 360 | 240 | **3/6** | 1.619853 | J0822, J1021, J1111 |

**Interpretation:** the historically calibrated 6/6 is **not numerically stable** under the tested radial grid changes, even though the identical fitted law and data are retained. No refinement was used to adjust fit parameters or choose a preferred post-outcome score. This undermines the inference that a 6/6 fitted regression alone establishes a numerically resolved physical solution.

An additional **exploratory** original-slow-function radial extension at 720, 1440 and 2880 points (at both 120 and 240 angles) returned **3/6 in all six extensions**, with the same failed lenses J0822, J1021 and J1111. Mean radius pulls approach about 1.802 sigma (2880/120) and 1.889 sigma (2880/240). These extra cases are not the six locked primary regimes and still do not prove mesh convergence for arbitrary physical lensing quantities or a covariant PDE.

## Execution and independent report verifier

The tool checks original bytes, runs from a disposable source copy, changes no historical file, compares the 180/120 diagnostic against the original slow Set A implementation, writes an immutable report/receipt and then **reexecutes all 36 lens/regime combinations** when independently verifying the receipt.

```bash
python tools/hist001d_convergence.py --source-root research/legacy/hist001 --out runs/hist001d_d2
python tools/hist001d_convergence.py --source-root research/legacy/hist001 --verify runs/hist001d_d2/receipt.json
```

Both execution and verification keep `physical_provider_admitted=false`, `native_v172_equivalence_proved=false`, `new_holdout_evaluated=false` and `empirical_validation=NOT_ESTABLISHED`. A matching diagnostic receipt is not a physical/empirical proof. On a modified original source or forged/self-rehashed report, the verifier must fail closed.

## D3–D7 next scientific gates

1. **D3:** publish a source-backed correlation/asymmetric-error and IMF/stellar M/L uncertainty map; no independent uniform-proxy trial as a substitute. Compare reference cosmology and sigma_crit conventions.
2. **D2 follow-up:** isolate radial-gradient shadow density, projected mass integration matrix, inner boundary and critical-radius root finder for finer-grid consistency. Report two-grid changes with no post-outcome retuning. The current projected-density proxy is not a covariant Weyl field solve.
3. **D4:** freeze a genuinely new, eligible disjoint lens dataset and masking/measurement/likelihood rule *before* viewing outcomes. The machine-readable noncanonical `registry/hist001d_holdout_preregistration_v1.json` intentionally records **NOT_SELECTED_NOT_FROZEN_NOT_SCORED**.
4. **D5:** prove or leave unresolved same-solution dynamics and physical Weyl lensing from an action and stress-energy source. The historical scalar potential equality `Phi=Psi` is imposed.
5. **D6–D7:** preserve spherical 2/6, half-circularization 2/6, historical robustness mismatch and original-source freeze. Independent reproduction receipts and legal reuse checks are required before promoting any observational or physical claim.

B remains [PR #7](https://github.com/HMarcusWH/native-eset/pull/7), historically blocked on original accelerated RangeFinder/RNG/600 prechecks. The merged HIST-001C is a noncanonical crosswalk and does not change this study's scientific status.
