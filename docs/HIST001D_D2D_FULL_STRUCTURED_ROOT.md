# HIST-001D/D2d — independent full structured-shadow mass and Einstein-root numerical audit

**29 October 2026 · read-only historical fitted-source diagnostic · no physical/observational admission**

## 1. Source identity, decision boundary and distinct numerical policy

This is the **frozen historical** `ra0_gated_geometry_sigmoid_reg_v2` J2141/SWELLS Set A calculation, **not** an executable Native ESET v1.7.2 gravitational provider. The exact original SHA-pinned March source lock is `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a` (46 source/input files, three negative records). All six lenses are **fitted/development cases**, not a new masked/held-out sample. The original historical 180-point/120-angle fitted **6/6** remains an intact separately identified source result.

The D2d algorithm is a **new finite-domain numerical identity**: we retain original model input rows, fitted gate coefficients, ε(r), baryon/shadow density formulas and reference cosmology (H0=70 km/s/Mpc, Ωm=0.3), but change the **numerical integrators**, the disc angular closure and the Einstein-root operation. Therefore D2d's new 3/6 is not the historically executed 180×120 result and is not a refit of its physics. No source, canonical graph, or prior negative control is edited.

Key source files (the exact files are independently verified from the original source lock): `solv/run_setA_port_cand.py` (fitted law and historical 180-point projection), `solv/run_j2141_axisym_lens.py` (structured baryon geometry, finite-projection and historical first-crossing root), `solv/shadow_density.py` (gradient/clipped effective shadow density). This study depends on the merged D2c independent piecewise-linear cylindrical mass quadrature, and binds that integrator's file SHA into its own receipt.

## 2. Independently evaluated mass and root at every trial radius

On the finite historical source interval **a = 0.02 kpc to b = 120 kpc**, reconstruct the original source's nonnegative effective `rho_shadow(r)` for each frozen source-grid size `n ∈ {180,360,720,1440,2880,5760,11520}`. Represent this discrete density by a piecewise-linear interpolant; this is an explicit **numerical assumption** and not an exact continuum density theorem. The shadow cylinder mass is

\[
M_{\rm sh,sph}(R)=4\pi\left[\int_a^{\min(R,b)}\rho_{\rm sh}(r)r^2dr+\int_{\max(a,R)}^b\rho_{\rm sh}(r)r\left(r-\sqrt{r^2-R^2}\right)dr\right].
\]

The independent D2c reference integrates each radial inner cell analytically, and the outer portion under a `t=√(r²−R²)` substitution with Gauss–Legendre quadrature (24 versus 48 nodes). At selected source/root radii, SciPy adaptive quadrature independently agrees. If the effective cylinder aperture exceeds the finite radial domain, the whole finite-domain spherical mass is included; this is also the historical source's right-clipping convention, not an assertion about mass beyond 120 kpc.

For **every** trial radius `R`, not just at a fixed observed radius, independently compute the finite-domain analytic Hernquist bulge cylinder mass `M_b(R)` using SciPy adaptive integration, and the complete periodic exponential-disc mass `M_d(R)` using 1,024 angular samples with the closing angular interval (rather than source's open endpoint 120-sample trapezoid). An independent 128-node Gauss–Legendre finite-domain bulge integral and quadrant-split adaptive angular integral cross-check those baryonic masses at the observed radii and selected roots. The period split matters for high-ellipticity discs; a single unsplit adaptive integral may under-resolve one lens at ~1e-7 relative level.

The radius-dependent fitted historical projection map is then evaluated **directly**, not interpolated from historical K-matrix nodes:

\[
q_{\rm eff}(R)={\rm clip}_{[10^{-3},1]}\!\left(\frac{q_bM_b(R)+q_dM_d(R)}{M_b(R)+M_d(R)}\right),\quad M_{\rm sh,str}(R)=M_{\rm sh,sph}\!\left(\frac{R}{\sqrt{q_{\rm eff}(R)}}\right).
\]

The numerical Einstein root is the **first independently bracketed sign change** of

\[
F(R)=M_b(R)+M_d(R)+M_{\rm sh,str}(R)-\pi\Sigma_{\rm crit}R^2.
\]

A fixed 45-node logarithmic scan over the historical finite source interval checks sample sign-change multiplicity. If no or multiple scanned crossings are found, the code **fails closed**; it does not select a favorable root. A bracketed Brent solver directly resolves the **quadratic** critical-mass target to a relative residual of at most 1e-11. A 45-node sign scan is not a mathematical guarantee of global root uniqueness or exclusion of all narrow oscillatory crossings. Full interval certification and finite radial truncation remain outside this release.

## 3. Original-versus-new results — unchanged fitted development measurements

**Pass** means both observed Einstein-radius and projected mass discrepancies have magnitude at most two times the source's *upper quoted* measurement error. This is the original phenomenological scoring convention; it is not a correlated/asymmetric observation likelihood.

| Lens | Original 180×120 radius pull | New 11,520-grid radius pull | New mass pull | New joint two-sigma pass? |
|---|---:|---:|---:|---|
| J0822+1828 | +1.512σ | +3.177σ | +1.270σ | No |
| J0915+4211 | −1.266σ | +0.578σ | +0.471σ | Yes |
| J0930+2855 | −0.735σ | −0.615σ | −0.048σ | Yes |
| J1021+2028 | +0.704σ | +2.721σ | +1.990σ | No |
| J1111+2234 | +0.498σ | +3.143σ | +1.649σ | No |
| J1135+3720 | +1.141σ | +1.652σ | +0.815σ | Yes |

The original historical 180-point/120-angle source produces **6/6**. The distinct D2d method produces **3/6 for every one of its seven source-density grid sizes** (180 through 11,520) without retuning any fitted law or observational value. J0822, J1021 and J1111 fail at every new grid. Both positive and negative results are preserved.

## 4. Seven-grid numerical refinement and cross-implementation controls

For each of the six lenses, 2,880→5,760 and 5,760→11,520 source-density refinements each change the **new root** by less than 0.05 times that lens's original observational radius uncertainty, and the **new predicted mass at the observed radius** by less than 0.05% relative. The largest observed changes (in absolute value) are:

- **Root:** 0.001163σ and 0.000291σ on the two final refinements.
- **Projected mass at observed radius:** 0.001874% and 0.0004683% on those refinements.
- **Root residual:** below 1e-11 relative to `πΣ_crit R²`, for every tested grid and lens.

Those numerical thresholds were set in the D2d diagnostic code before its first local computation; this was **not** an externally registered, outcome-masked experiment, and the criteria do not provide a rigorous mathematical bound. Convergence is checked only for the six fitted source rows, fixed finite-domain/source prescriptions and chosen quadratures. Further analytic error enclosures, root multiplicity checking, boundary variation, clipping/derivative variation and truly independent physical field sourcing remain open.

For the registered 180, 360 and 11,520 source-grid conditions, independent Gauss 24/48 shadow-mass evaluations are checked at the new root; SciPy adaptive source-density quadrature checks 180/360. All six development lenses' baryonic components are checked using a separately implemented finite-domain Gauss–Legendre Hernquist integral and a quadrant-split adaptive full-periodic disc integral, including at selected new roots. All code and archived original inputs are source-locked; output receipts reexecute the **entire** calculation instead of trusting internally recomputed hashes.

## 5. Audit commands, decision and remaining gates

```bash
python tools/hist001d_d2d.py --source-root research/legacy/hist001 --out runs/hist001d_d2d
python tools/hist001d_d2d.py --source-root research/legacy/hist001 --verify runs/hist001d_d2d/receipt.json
```

The report has the original source's frozen 6/6 results and the separate 42 new numerical grid/lens results, full root/mass component decomposition, `q_eff(R)` sampled at the root and observed Einstein radius, root bracketing, complete per-lens failure decisions, numerical Cauchy deltas, environment, module/integrator SHA, source lock and fail-closed scientific claims. The independent verifier reexecutes and compares every source-derived numerical field and rejects self-rehashed tampering, altered provider or holdout claims, unsafe receipt files and source-root path manipulation.

**Decision:** a stable **3/6** for the explicitly new, independently integrated structured-shadow **finite-domain phenomenological source**. The 6/6 original regression is a documented historical execution but numerically sensitive. This result is not a blind observational test; it does not say whether Native ESET 4/v1.7.2, physical Weyl lensing, CDM, or cosmological species-perturbation equations succeed or fail.

**Still outstanding:** D2e rigorous shadow truncation/source-gradient/covariant error budget; D3 source-backed correlated uncertainties and IMF/mass priors; D4 disjoint preregistered holdout and audited data-contact history; D5 same-metric action/field and Weyl lensing proof; HIST-001E current-theory compatibility; HIST-001B original accelerated RangeFinder/RNG/600-case source recovery. No evidence from D2d authorizes a production provider or Theory-State canonical mutation.
