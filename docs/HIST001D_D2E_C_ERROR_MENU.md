# HIST-001D/D2e-C — discrete-gradient, finite-boundary and root/mass error-menu audit

**Release class:** source-locked diagnostic, distinct from the original March 180/120 fitted 6/6 and the independent D2d 3/6. **Not validated**: no mathematically certified error bound, all-R uniqueness, source-authorized radial continuation, physical metric/Weyl-lensing provider, disjoint holdout, or current Native ESET v1.7.2 equivalence.

## Motivation and ancestry

The D2d method reconstructs a nonnegative shadow-density array using the original fitted constitutive law, maps its finite-domain spherical mass through a radius-dependent baryonic `q_eff(R)`, and brackets the critical Einstein-mass equation. D2e-A found no clipping on 42 tested sampled arrays but extremely large near-boundary pointwise coarse-grid density discrepancies. D2e-B added conditional interval exclusion outside a 2% guard; its global `10^-6` mass-error premise was **assumed**, not certified. Neither result resolves the original source's derivative discretization or unknown exterior mass.

This increment measures *specific new counterfactual numerical identities*, without changing the original source, parameters, observations, angular law, or boundary convention. A finite set of sensitivity results does **not** become a worst-case error certificate.

## Derivative discretization choices

The original source uses

```
Mshadow = max(Meff - Mbar, 0)
rho = max(np.gradient(Mshadow, r)/(4*pi*r*r), 0)
```

on the interval 0.02–120 kpc. D2e-C preserves that exact `SOURCE_GRADIENT` result and separately reconstructs `EDGE_ORDER_2` and monotonicity-preserving `PCHIP_DERIVATIVE` derivatives of the *same frozen nodal* `Mshadow`. Each alternative uses the same nonnegative-density convention and full D2c piecewise-linear cylinder integration; changing a differentiation rule changes the numerical execution identity.

We record the weighted L1 difference

```
integral[0.02,120] 4*pi*r*r*abs(rho_alt-rho_original) dr
```

and the corresponding finite spherical-shadow-mass fraction, plus pointwise density difference and source-versus-alternative Einstein radius and projected mass shifts. No result is promoted to a model refit or physical density measurement.

## Radial-domain scenarios: known versus unknown

**Inner baryon diagnostic.** The original finite Hernquist bulge projection excludes `r<0.02` kpc. If that exact Hernquist profile were explicitly extended to the center, the enclosed interior mass would be

```
M_inner = M_bulge * (rmin/(rmin + Re/1.8153))**2
```

for `rmin=0.02` kpc. All of this would contribute to a projected cylinder of radius exceeding the cutoff. D2e-C measures this separately, and when constructing the **new** `ANALYTIC_INNER_HERNQUIST` counterfactual, consistently updates the baryonic `q_eff` map as well. It is **not** the frozen D2d source definition and supplies **no bound on missing inner shadow mass**.

**Outer shadow tail diagnostic.** No physical continuation beyond 120 kpc was supplied. For the sole purpose of sensitivity, new conditional continuations match the outermost sampled density as `rho(r)=rho(120)*(120/r)**p` with `p=4,5` for `r>120`. These are *invented counterfactual model assumptions* and are not counted as source-backed mass bounds. The projected mass is independently calculated with a stable `u=120/r` transform:

```
M_tail(A,p) = 4*pi*rho(120)*120*A*A*
              integral[0,1] u**(p-2)/(1+sqrt(1-(A*u/120)**2)) du
```

at the effective cylindrical aperture `A<120` kpc. Explicitly unrecognized is any other radial continuation, notably a slower-decaying or divergent one.

## What the numerical comparisons mean

Each scenario retains the same 11,520-grid source input, galaxy parameters, lens observations and `H0=70`, `Omega_m=0.3` critical-distance convention. The tool searches for the alternative root in the fixed ±15% window around the verified D2d root. A missing bracket is reported as `UNBRACKETED_IN_FIXED_WINDOW`, not converted into `no root`. At the observed radius, each alternative projected-mass change is normalized by the source's quoted *upper* mass-error sigma; alternative root shifts are normalized by the source's quoted *upper* radius error. These are *historical diagnostic normalization conventions*, not a source-justified correlated uncertainty model.

The result reports max absolute observed root/mass excursions across this small, deliberately enumerated menu. It **does not add those differences in quadrature**, infer statistical independence, justify global extrema, or bound the unknown tail and inner shadow. Root uniqueness and a global/interval certificate remain open.

## Executable and release controls

```bash
python tools/hist001d_d2e_error_budget.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_c
python tools/hist001d_d2e_error_budget.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_c/receipt.json
```

- Source SHA-256 frozen March 46+3: `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`.
- Pinned merged D2e-A source SHA: `ea0aaebc74738524f7bf071e7594cf2c275d5f9b9aff1f75d04051b7c1f876f2`.
- Pinned merged D2e-B source SHA: `d2784a4609460cd562b479c3b442a9a34aaa12ad9d3d709bc48959978c209155`.
- Original March source and archived negatives verified before/after disposable-copy execution; separate original historical 6/6 check.
- Canonical JSON report, SHA-256 receipt/sidecar and verifier that independently reexecutes source calculations rather than trusting self-rehashed numerical claims.
- New synthetic tests cover gradient alternatives, exact Hernquist interior, power-law tail formula and source integrity. CI must pass on Ubuntu/Windows Python 3.10/3.12/3.13 with a separate real CLI source-reexecution step.

## Remaining blockers and exit classification

**Scientific D2e remains open.** The correct exit label is `SCOPED_EMPIRICAL_SENSITIVITY_REPORTED_NOT_CERTIFIED`, regardless of how small the sampled root changes look. A rigorous proof requires interval-certified quadrature and derivative bounds, root count including the guarded region, and a physically sourced truncation/continuation contract. D3 joint observational covariance and IMF uncertainties, D4 disjoint blinded holdout, D5 one-sourced metric/Weyl lensing, HIST-001B original accelerated generator, and HIST-001E modern-theory action/constitutive mapping remain independent.

No user-land claim or source flag may promote `physical_provider_admitted`, `physical_weyl_lensing_derived`, `root_uniqueness_mathematically_certified`, `global_error_bound_established`, `native_v172_equivalence_proved`, or `empirical_validation`.
