# HIST-001D/D2e-G1/G2 — rigorous analytic baryonic enclosures

**Status:** bounded numerical-science increment. Theorems concern **exact frozen binary64 scalars inserted into analytic mathematical models**, not floating SciPy quadrature, the historical 1024-angle projector, source density continuum, full Einstein-root solver or physical Weyl lensing.

## Ancestry / frozen source

The historical original March 46+3 SHA `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`, historical fitted 180 radial / 120 angular original 6/6 and separately integrated D2d 11,520 radial finite-discrete 3/6 remain unchanged. All six SWELLS Set A cases are **previously fitted development lenses**, never a new holdout.

D2e-F [PR #26](https://github.com/HMarcusWH/native-eset/pull/26) certifies finite discrete shadow-cylinder mass for **all real apertures** within six source-verified aperture bands; its `R→q_eff(R)→A(R)` bridge was **conditional** on mathematically justified bulge/disc mass bounds. This increment provides those mathematical bounds for separately identified analytic continuum bulge/disk identities, **without certifying historical floating integrations**.

## G1: finite Hernquist bulge exact-rational positive-cylinder bound

For the mathematical bulge profile truncated to radial support `[r_min,r_max]=[0.02,120] kpc`, freeze `M_b` and `a=R_e/1.8153` as the **exact binary64 outputs** of the historical parameter computation:

```
rho_b(r) = M_b a / [2π r (r+a)^3].
B(R) = 4π integral[rmin,min(R,rmax)] rho_b(r) r² dr
     + 4π integral[max(R,rmin),rmax] rho_b(r) r (r-sqrt(r²-R²)) dr.
```

With `R>rmin`, the inner integrand `2 M_b a r/(r+a)^3` has the exact rational primitive `M_b a[-2/(r+a)+a/(r+a)^2]`. No numerical quadrature is needed for the inside region.

For each outer radial shell `[l,u]`, let `w(r)=2 M_b a/(r+a)^3>0` and `g(r,R)=r-sqrt(r²-R²)=R²/(r+sqrt(r²-R²))`. For `r>R`, `g'<0` and `g''=R²/(r²-R²)^(3/2)>0`. Exact moment integrals

```
W0=integral[l,u] w(r)dr
   = M_b a[(l+a)^(-2)-(u+a)^(-2)],
W1=integral[l,u] r*w(r)dr
   = M_b a[2/(l+a)-a/(l+a)^2-2/(u+a)+a/(u+a)^2]
```

make **both the secant upper bound and midpoint-tangent lower bound integrable exactly** as weighted affine functions. Independently valid monotone kernel bounds `g(u)W0 <= integral w*g <= g(l)W0` are intersected with the convex bounds so the new enclosure cannot be weaker than either. Every required square root is enclosed using exact rational integer-isqrt arithmetic, default 100 bits. All endpoint values and derivatives use outward rational bounds; final mass aggregation uses directed 70-digit Decimal arithmetic. The adaptive shell priority affects only work order; it is NOT the proof. The fixed `relative_width <= 1e-6` target and 8,192 split budget are engineering goals; a legitimate `target_met=false` still returns the actual valid enclosure.

B(R) is nondecreasing for nonnegative source density, so B(Rlo) lower and B(Rhi) upper mathematically enclose the **analytic continuum** B(R) at every real radius R within [Rlo,Rhi].

**Limit:** the historical `reference_bulge_finite()` computes a floating `scipy.integrate.quad` approximation. Its `epsrel` setting is **not** proof of its numerical error or equivalence to the exact mathematical interval. Differences are reported as observational diagnostics, not merged identities.

## G2: rigorous but deliberately COARSE periodic exponential disk envelope

The historical analytic exponential disk is

```
D(R) = Σ0 integral[0,2π] dθ integral[0,R] r exp(-g(θ)r/s) dr
Σ0 = M_d/(2π q_d s²),
g(θ) = sqrt(cos²θ + sin²θ/q_d²),
s=R_e,disc/1.67835, 0<q_d<=1.
```

With `1 <= g(θ) <= 1/q_d` and positivity, define `H(x)=1-(1+x)exp(-x)`. Without any angular quadrature approximation:

```
M_d q_d H(R/(q_d s)) <= D(R)
                      <= min(M_d, (M_d/q_d) H(R/s)).
```

For a continuous R interval [Rlo,Rhi], evaluate the lower expression at Rlo and upper at Rhi. `exp(-x)` is rigorously enclosed using exact rational alternating Taylor sums for range-reduced `x<=32`, with positive monotone powers; for x>32 an exact nonnegative lower and `1/sum_{k=0}^{48} x^k/k!` upper follow from `e^x` positive series. The derived disk bounds are converted with directed rounding. This is a **legitimate but potentially very wide geometric envelope** around the continuum analytic disk, not an approximation to or error theorem for the 512/1024-angle historical trapezoid. Accurate source-equivalent periodic quadrature certification remains **OPEN**.

## G3 (restricted): bounded analytic-continuum q_eff guard

Take the G1 lower/upper analytical bulge and G2 lower/upper analytical disk masses over the fixed D2d-root ±2% radius guard. Convert the rational-Decimal results to outward binary64 endpoints, then reuse D2e-F exact four-corner `q_eff` and outward `A=R/sqrt(q_eff)` interval functions. The combined resulting q/A band is now mathematically justified **for the exact frozen-scalar CONTINUUM B(R),D(R) functions**.

It is NOT proved for the original numerical `reference_bulge_finite` SciPy and `reference_periodic_disk(...,ntheta=1024)` outputs; these have independent approximation error. Therefore D2e-F's **frozen implemented root** is not yet interval-certified, and no global/multiple/tangent-root claims are authorized.

The G1/G2 result is never used to overwrite the existing D2d numerical root or to assert the original 6/6 and D2d 3/6 have changed. The G2 interval may be too broad for efficient root isolation; narrowing it requires a separate rigorous angular proof, not post hoc tolerance adjustments.

## Source-locked execution and release

```bash
python tools/hist001d_d2e_g_baryon_boxes.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_g
python tools/hist001d_d2e_g_baryon_boxes.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_g/receipt.json
```

The runnable computes six fitted development-lens analytic baryonic envelopes, source quadrature comparisons, analytic-continuum q/A guard bands, original historical fitted regression readback and new no-promotion receipt. The receipt includes original March source lock, pinned D2e-F implementation SHA, both proof kernel hashes and a canonical JSON report; independent verification recomputes original source inputs and the new mathematical bounds. Synthetic tests include independently evaluated finite Hernquist cylinders, exponential enclosures at high Decimal precision, independent periodic-angle disk samples, invalid parameter attacks, source SHA and self-rehashed numerical/provider forgery rejection.

CI requires Ubuntu/Windows × Python 3.10/3.12/3.13, clean SHA manifest, Ruff, earlier D2e-A/B/C/D/E/F source replays and a separate G1/G2 original-source run and verifier. Main success exports all A–G report/receipt/sha files for independent Drive readback.

**Still nonclaims:** historical source numerical and continuum-parameter uncertainty, validated mass outside [0.02,120] kpc, original source gradient/clipping continuum, entire R root topology, same-solution metric/Weyl lensing, new disjoint holdout, D3 covariance and IMF uncertainties, contemporary Native v1.7.2 physical-equation equivalence, no-particle-CDM cosmology, empirical validation and physical provider authorization.
