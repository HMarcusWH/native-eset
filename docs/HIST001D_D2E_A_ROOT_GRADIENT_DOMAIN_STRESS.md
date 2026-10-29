# HIST-001D/D2e-A — numerical root topology, source derivative and finite-domain sensitivity

**29 October 2026 · noncanonical, source-locked historical-model numerical diagnostics.**

## Scope and exact execution identity

- Frozen March original `research/legacy/hist001/SOURCE_LOCK.json` SHA-256: `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`; 46 original files plus 3 archived negative controls remain unchanged.
- Historical fitted candidate: `ra0_gated_geometry_sigmoid_reg_v2`; original six SWELLS Set A **development lenses only**. The original 180/120 numerical source is separately preserved at **6/6**.
- D2e uses the *new* finite-domain independent structured-shadow calculation from D2d (already **3/6**, no refit) and D2c independent piecewise-linear spherical shadow-mass quadrature. Dependencies are SHA-pinned, not replaced or retuned.
- Domain **[0.02,120] kpc** and source shadow-density grids **180,360,720,1440,2880,5760,11520**; flat reference cosmology H0=70 km/s/Mpc, Ωm=0.3; complete periodic 1,024-angle analytic disc.
- New full-domain scans at 45, 181, 721 logarithmically spaced radii use dimensionless `G(R) = M_total(R)/(π Σcrit R²) − 1`, with independent finite-domain bulge and disc masses and `M_shadow(R/sqrt(q_eff(R)))` at every sampled radius.
- All numerical tolerances and scan sizes are *locked in the source of this test increment*, **not externally preregistered or mathematically certified error bounds**.

## D2e-A finding 1 — sampled root topology, NOT global uniqueness

Each lens had **one sampled sign-changing bracket** at all 45/181/721 scan densities. Nevertheless, `G(R)` was **not monotonically decreasing at every sampled interval**: the positive-slope counts below are enough to prevent any inference of global monotonicity or proof that no tangent roots occur between samples.

| Development lens | Positive-slope intervals, 45/181/721 | D2d 11,520-point Einstein R (kpc) | 24-vs-48 Gauss root difference (σ) |
|---|---:|---:|---:|
| J0822+1828 | 2 / 7 / 27 | 1.933552128 | +1.75e-12 |
| J0915+4211 | 2 / 7 / 27 | 1.463126000 | +5.94e-13 |
| J0930+2855 | 2 / 7 / 28 | 4.676255360 | +8.47e-12 |
| J1021+2028 | 2 / 6 / 26 | 1.362052753 | +6.16e-13 |
| J1111+2234 | 2 / 7 / 28 | 4.051186316 | -9.23e-12 |
| J1135+3720 | 2 / 7 / 27 | 2.300346592 | -3.64e-13 |

Each root from the 721-node sampled bracket agrees with the SHA-pinned D2d 11,520-point root at **<10⁻⁷ observational σ**. Root derivatives calculated with finite differences using `h≈10⁻⁴ R` and `h/2` are negative at those six selected roots; their relative differences are approximately `7×10⁻⁹–1.3×10⁻⁸`. This is a **local condition-number screen**, not an interval enclosure or a globally unique-root theorem.

### Why the topology certificate remains OPEN

A finite sign scan may miss pairs of roots, tangent roots, or nonmonotonic behavior between grid points. A rigorous root-count proof would need validated interval ranges or derivative/monotonicity enclosures over the entire interval, including inner/outer boundaries and `q_eff(R)`/density interpolation breakpoints. D2e-A does **not** provide those enclosures. The 45-point D2d scan was not independently sufficient either.

## D2e-A finding 2 — frozen mass/derivative clipping is inactive on tested grids

Original source `solv/shadow_density.py` constructs `Mshadow=max(Meff−Mbar,0)` and `rho=max(∇Mshadow/(4πr²),0)`. For each of **6 lenses × 7 frozen radial grids**, D2e-A recomputed the exact source array: **zero negative preclip shadow-mass values, zero negative preclip radial derivatives and zero zero-valued postclip density samples**. The source clipping branches therefore do not activate on *these sampled original arrays*. This is not proof they are inactive between samples, under changed parameters, or in other physical models.

### Pointwise inner-grid sensitivity (coarse 180 divided by 11,520 reference)

| Lens | 0.1 kpc density factor | 0.5 kpc density factor | 2 kpc density factor | 10 kpc density factor |
|---|---:|---:|---:|---:|
| J0822+1828 | 35,626× | 143.7× | 1.198× | 0.9959× |
| J0915+4211 | 39,287× | 145.6× | 1.203× | 0.9929× |
| J0930+2855 | 53,100× | 151.7× | 1.234× | 0.9985× |
| J1021+2028 | 25,432× | 138.4× | 1.174× | 0.9936× |
| J1111+2234 | 51,260× | 151.0× | 1.238× | 1.0041× |
| J1135+3720 | 39,810× | 146.2× | 1.237× | 0.9923× |

**Interpretation:** the first 180-point interval is very wide (~0.67 kpc) relative to 0.1/0.5 kpc; interpolating its stored derivative-density values at these small radii produces enormous pointwise differences from an independently sampled much finer radial grid. This is a **finite-grid density interpolation comparison**, not a measured physical density error or an equal-sized error in integrated projected mass/root. It explicitly rules out interpreting small late-grid root shifts as uniform convergence of the underlying density field. The inner `[0,0.02)` domain is absent, and no physical inner continuation is specified.

## D2e-A finding 3 — outer shadow-shell cutoff sensitivity **within** archived source

D2e-A removes only original **shadow density** in the intervals `(80,120]` or `(100,120]` kpc, respectively; baryonic projected masses, fixed gate, `q_eff(R)` and critical surface density remain unchanged. The root equation is then **solved anew**. These *counterfactual numerical domain variants* are not the frozen historical result, not physical outer boundary conditions, and cannot bound any unprovided mass beyond 120 kpc.

| Lens | Δ Einstein radius for 80 kpc shadow cut (σ) | Δ Einstein radius for 100 kpc shadow cut (σ) |
|---|---:|---:|
| J0822+1828 | -0.000855 | -0.000262 |
| J0915+4211 | -0.001242 | -0.000379 |
| J0930+2855 | -0.020263 | -0.006358 |
| J1021+2028 | -0.000041 | -0.000012 |
| J1111+2234 | -0.013092 | -0.003577 |
| J1135+3720 | -0.000118 | -0.000037 |

Maximum shifts are **0.02027σ** (80 kpc cut) and **0.00636σ** (100 kpc cut), both below an explicitly retrospective 0.05σ engineering screen for this frozen six-lens sample. The code does not extrapolate or constrain `(120,∞)` mass. It also does not bound the missing `(0,0.02)` mass.

## Engineering cross-checks versus open mathematical error obligations

| Work | Result | Claim ceiling |
|---|---|---|
| Exact March source bytes and six fitted rows | SHA-locked 46+3, original fitted 180/120 6/6 separately reproduced | Historical source identity only |
| D2d independent full structured root at high grid | 3/6 source-fitted lenses; each D2e 721-node root matches pinned D2d value | Different numerical identity, no refit |
| Gauss–Legendre 24/48 shadow integration at the root | Root changes <10⁻¹⁰ observational σ | Agreement of two Gaussian orders, not global error bound |
| Finite root sign scan | 1 sign-change bracket at 45/181/721 samples; positive-slope intervals exist | **No interval/root uniqueness certificate** |
| Source clipping branch | Not activated on any of 42 sampled lens/grid arrays | No off-grid/alternate-model theorem |
| Inner pointwise source density | Coarse 180-grid interpolation differs massively at 0.1/0.5 kpc | **No uniform density convergence** |
| Removal of outer *known* shell | ≤0.02027σ root shift on six studied inputs | **No mass bound outside [0.02,120] kpc** |

## Executable and adversarial receipt

`tools/hist001d_d2e.py` independently loads the pinned merged D2c/D2d modules, verifies original SOURCE_LOCK, copies original source to a disposable directory, runs source-code-equivalent source mass/gate/density calculations, and independently evaluates `G(R)` on every sampled scan and the cutoff variants. It writes canonical JSON with all sampled radii/residuals, 42 density-grid records and the six complete numerical summaries. The receipt binds SHA-256 of the exact file bytes, exact source identity and both numerical dependencies; verifying with CLI **reexecutes all original source experiments** from a newly loaded Python process.

```bash
python tools/hist001d_d2e.py --source-root research/legacy/hist001 --out runs/hist001d_d2e
python tools/hist001d_d2e.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e/receipt.json
```

`tests/historical/test_hist001d_d2e.py` includes 10 source/protocol, numerical, integrity and attack tests. The unit tests use a previously source-verified fixture for isolated comparator tests; **the real CLI source reexecution is a separate mandatory CI step and was run independently locally**. Merely repairing a report and its sidecar hashes does not make it source-reproducible. The old frozen code is never changed or refitted.

## Next required research

1. **D2e-B root theorem or honest open result:** bound the root count via verified interval arithmetic/derivative enclosures including interpolation breakpoints and near-tangent cases. A denser sample alone does not prove uniqueness.
2. **D2e-C true finite-domain model closure:** obtain sourced inner and outer physical densities/boundary conditions and propagate their uncertainty through the complete structured root. The current source defines no such bound.
3. **D2e-D cross-uncertainty:** isolate density-derivative/grid interpolation errors and upstream fitted-gate parameter uncertainties in an explicit composite error budget; do not treat a post-outcome 0.05σ screen as a theorem.
4. **D3/D4/D5 remain separate:** source-backed asymmetric/correlated SWELLS measurement uncertainties; a truly disjoint preregistered holdout; physically sourced shared-metric Weyl-lensing derivation. Historical B RangeFinder source/RNG/600 remains blocked and Native v1.7.2 action/field transport remains unproved.

**Canonical authority: unchanged.** `new_holdout_scored=false`, `physical_provider_admitted=false`, `physical_weyl_lensing_derived=false`, `native_v172_equivalence_proved=false`, `global_error_bound_established=false`, `root_uniqueness_mathematically_certified=false`, `mass_outside_finite_domain_bounded=false`, `empirical_validation=NOT_ESTABLISHED`.
