# HIST-001D/D2e-D — exact-rational finite shadow-cylinder mass enclosure

**Scope:** one rigorous *discretized-input, fixed-aperture* numerical component, not a theorem for the complete Einstein root, current Native ESET physics, observational data, or mass beyond the historical radial domain.

## 1. Historical identity and preserved negative evidence

The original March SHA-locked 46+3 archive is untouched (`fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`). The original 180-point/120-angle fitted historical 6/6 is a distinct execution from the independent finite-domain D2d 3/6 across 180–11,520 shadow-density samples. All six Set A lenses were *used for development/fitting* and cannot be called blind holdouts.

D2e-A sampled root signs, gradient clipping and in-domain cutoffs. D2e-B conditionally excluded intervals outside a 2% root guard **assuming without proof** a universal `1e-6` mass-error allowance. D2e-C measured a finite, separately identified menu of derivative and radial-continuation counterfactuals. This D2e-D increment replaces **only one local piece** of the missing error budget with a source-derived, outward enclosure for the finite discretized spherical shadow projection.

## 2. Precisely defined mathematical object

Freeze every nodal radial coordinate `r_i`, every sampled nonnegative shadow density `rho_i`, and the effective shadow aperture `A` as their **exact binary64 rational values**. Interpolate density linearly between neighboring nodes; no claim is made about errors in the source equations, density construction, gradient clipping, input measurements or other radii.

For the source's finite interval `[a,b]=[0.02,120] kpc`, the spherical cylindrical mass is

```
M_sh(A) / (4*pi) =
  integral[a,min(A,b)] rho(r)*r^2 dr
  + integral[max(A,a),b] rho(r)*r*(r-sqrt(r^2-A^2)) dr.
```

The inner contribution of each linear-density cell is an **exact rational polynomial integral**. For outer shells, the positive geometry kernel

```
g(r,A) = A^2*r/(r + sqrt(r^2-A^2))
```

is decreasing in `r` for `r >= A`. For an outer interval `[u,v]`, therefore,

```
g(v,A)*integral[u,v]rho(r)dr
 <= integral[u,v]rho(r)*g(r,A)dr
 <= g(u,A)*integral[u,v]rho(r)dr.
```

A shell crossing `r=A` is divided into an exact inner polynomial and a bounded outer portion. The radius/density inputs, polynomial coefficients, nonnegative cell integrals and geometry bounds use Python `Fraction`, retaining **exact binary64 input semantics**.

The only square roots are bounded using `math.isqrt` on scaled rational integers: if `q>=0` and `k=isqrt(floor(q*2^(2p)))`, then `k/2^p <= sqrt(q) < (k+1)/2^p`. Default `p=88`. There is no floating square-root or numerical quadrature call in the mathematical bound.

Finally, `pi = 16*atan(1/5)-4*atan(1/239)` is enclosed by rational alternating-series sums and the next-term remainder. Positive lower and upper shell bounds are accumulated using decimal arithmetic with **directed floor/ceiling rounding** (70-digit context), before multiplication by the corresponding directed `4*pi` enclosure. The resulting decimal strings are rational representations enclosing the exact integral over the specified piecewise-linear source. No new numeric-error tolerance is assumed in this component.

**Important:** these inequalities bound the integral for the *frozen discretized density and exact selected binary64 aperture*. They do not prove the physical source law or the floating-point evaluation of the baryonic `q_eff(R)` map, or guarantee a root/error bound over a continuum of radius values.

## 3. Source reexecution and independent quadrature comparison

The new `src/native_eset/numerics/exact_shadow_bounds.py` provides a reusable pure-Python rational enclosure, including a one-sided upper error bound on a proposed binary64 quadrature output relative to this exact discrete mathematical object.

The source-locked runner `tools/hist001d_d2e_d_exact_projection.py` reconstructs original 11,520-node shadow-density arrays from a disposable, SHA-checked copy of the frozen source. For each of six fitted Set A development lenses, it evaluates **five fixed trial radii**: the observed Einstein radius, the SHA-pinned D2d 11,520-grid root, the two 2% guard boundaries, and 0.1 kpc. Each trial radius is passed through D2c's baryonic `q_eff` map to obtain an exact-as-binary64 spherical shadow aperture, independently projected by D2c Gauss orders 24 and 48.

The report records the exact-rational mass lower/upper enclosure, its width, both numerical Gauss estimates and their guaranteed **pointwise error upper bounds relative to the discretized shadow integral**. The report's maximum across 30 selected points is *not* an all-radius supremum. Increasing numerical precision does not reduce the physical/source-model uncertainty; refining radial density grids changes numerical identity and needs a separate report.

```bash
python tools/hist001d_d2e_d_exact_projection.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_d
python tools/hist001d_d2e_d_exact_projection.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_d/receipt.json
```

The receipt pins original March SHA, D2e-A source SHA, this runner, the pure proof kernel and the exact canonical report. Verification **reexecutes** the full six-lens source and mathematical interval computation, rather than trusting internally repaired hashes. CI runs across Ubuntu and Windows × Python 3.10, 3.12 and 3.13 with the original D2d/D2e regressions, manifest, security checks, lint, synthetic negative tests and standalone source-reexecution receipt.

## 4. Theorems and gates that remain OPEN

This **does not establish** the 1e-6 mass assumption across every D2e-B radius interval: the new enclosure is checked only at the 30 fixed effective apertures, is generally wider than that assumed allowance, and does not include baryonic/`q_eff` approximation errors. No claim of unique/missing roots, tangent-root exclusion, finite-domain continuation, covariance marginalization or physical Weyl-lensing follows.

Still required: global interval-root isolation including the unresolved 2% guard, independently controlled baryonic/gradient/continuous-radius error, source-authorized density outside 0.02–120 kpc, D3 published observational uncertainties and covariance, D4 truly disjoint blind holdout and D5 same-sourced metric/Weyl potential. HIST-001B original accelerated producer/RNG/600 checks and HIST-001E current-theory transport remain separate.

**Allowed:** `shadow_piecewise_linear_pointwise_enclosed=true` only for the exact binary64 nodal/selected aperture scope. **Blocked:** `global_error_bound_established`, `root_uniqueness_mathematically_certified`, `old_d2e_b_mass_assumption_proved`, `mass_outside_finite_domain_bounded`, `physical_provider_admitted`, `physical_weyl_lensing_derived`, `native_v172_equivalence_proved`, `new_holdout_scored`, `empirical_validation`.
