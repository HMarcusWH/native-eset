# HIST-001D/D2b — frozen projected-mass and root-discretization audit

**29 October 2026. Original historical fitted J2141/Set A branch only. Diagnostic, not a physical-provider validation.**

## 1. Identity and source boundaries

The original source is the March 14 SWELLS v2 frozen triad, checked against `SOURCE_LOCK.json` and its independent installed-source trust anchor (`fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`). It contains 46 original source/input files and three archived negative-control records. Nothing in the source is edited. The fixed candidate is `ra0_gated_geometry_sigmoid_reg_v2`; cosmology remains flat ΛCDM reference H0=70 and Ωm=0.3. The six lenses are pre-existing fitted/development data. No observational holdout is selected, viewed, or scored.

Relevant SHA-pinned source code:

- `solv/run_setA_port_cand.py` — `247e0a354588aed488cd1f6aa2548633d3edb876ea913322e08a33669e0fc4c9` (radial projection matrix, fixed gate, Set A lens assembly).
- `solv/run_j2141_axisym_lens.py` — `a7b6dd6a4efc43495baa80eb99bf72bcb45d6833ffe1a74fa92b67133aa618c3` (Hernquist density, disc angular integral, structured-shadow projection and first-crossing root interpolation).
- `solv/shadow_density.py` — `1886f6db6e2aab951b542112b5b4b2ee0f41d28bdbed600c1aafd895b293aba5` (finite-difference shadow-density gradient).

## 2. Four-way density-grid and projector/root-grid isolation

Two source-density grids and two evaluation/projection grids were crossed, keeping the fitted parameters and all observations unchanged. Each matrix cell uses exactly the original baryon and gate formulas; when grid sizes differ, the density is linearly interpolated onto the evaluation grid. That *cross-grid interpolation is a diagnostic counterfactual*, not a new physical solution.

| Density field originally computed on | Projection/root evaluated at 180 points | Projection/root evaluated at 360 points |
|---|---:|---:|
| 180-point grid | **6/6** joint 2σ passes (historical) | **3/6** |
| 360-point grid | **6/6** | **3/6** |

On the 360-point projection/root grid, the three failures are J0822+1828, J1021+2028 and J1111+2234. Changing the density-gradient grid *alone*, while retaining the 180-point evaluation grid, does not turn any of the six into a failure. This pins the main sensitivity in these experiments to the **combined radial projection, baryonic integration, mass interpolation and root discretization**, not to shadow-density gradient resolution alone. A later calculation may isolate each part more sharply; these four cells cannot uniquely allocate all error between the coupled numerical operations.

At fixed 180-point density, the radius-pull shifts caused by changing the projection/root grid to 360 points were approximately **+1.353σ, +1.458σ, +1.822σ** for the three affected lenses respectively. Changing density resolution at a fixed 180-point projection grid shifted those same radius pulls by approximately **−0.276σ, −0.018σ, −0.063σ**. These differences are not additive because the nonlinear root and structured shadow projection couple the components.

## 3. Original finite-domain bulge projection versus adaptive integral

The source `_projection_matrix` uses trapezoidal radial weights and an inner radius of 0.02 kpc. For each development lens, the exact same analytic Hernquist density was projected using a separate adaptive SciPy integral on the *same finite radial domain*, 0.02–120 kpc, and evaluated at that lens's observed Einstein radius.

| Lens | 180-point mass bias vs adaptive | 360-point mass bias |
|---|---:|---:|
| J0822+1828 | −12.2% | −3.4% |
| J0915+4211 | −9.7% | −2.7% |
| J0930+2855 | −3.5% | −0.9% |
| J1021+2028 | −20.7% | −6.9% |
| J1111+2234 | −4.2% | −1.1% |
| J1135+3720 | −9.5% | −2.7% |

The adaptive integral is a **numerical quadrature reference** for the source's finite-radius Hernquist profile—not a new physical density fit or a statement about the correctness of the baryonic mass prior. It exposes significant discretization error in a key component of the source's projected mass.

## 4. First-sign-crossing root interpolation and quadratic target

The frozen `solve_einstein_radius_projected` finds the first sign-change bracket and *linearly interpolates* sampled values of `M_projected(R) − π Σ_crit R²`. This linear approximation also interpolates the curved critical-mass term. Holding **all source projected-mass nodes fixed**, a separate bracketing solver instead finds the exact zero of the linearly interpolated `M_projected(R)` against the original **quadratic** `π Σ_crit R²` term within the same bracket.

At the original 180-point grid, this changes the radius pull by **+1.053σ for J0822+1828** (and +0.948σ for J0915+4211). The J0822 change by itself crosses the 2σ dual-pass boundary, while preserving all original source mass samples. This is a *counterfactual root-interpolation calculation*, not a replacement for the original historical frozen 6/6 score. At finer grids the same error decreases, as expected for bracketing refinement.

All six sources had one first sign-crossing in the tested meshes; no multiple-root choice was encountered. The findings are specific to this frozen source and its sampled projected-mass profiles.

## 5. Original disc angular integration omits one periodic interval

The original disc routine constructs `theta = linspace(0, 2π, ntheta, endpoint=False)` and then applies `np.trapezoid` to these `ntheta` samples. Since the last-to-first periodic interval is omitted, it is *not* the complete trapezoidal integral of the periodic integrand over 0–2π. Using the exact same source analytic integrand and a closed-periodic uniform trapezoidal sum, the 120-angle original disc enclosed mass is **0.90%–2.77% lower** across these six lenses, at the observed Einstein radii. The bias halves approximately at 240 angles. This is a code-level integration convention, not an empirical covariance measurement. Any change to the source quadrature would create a *new executable identity*, not retroactively repair the frozen original run.

## 6. Verification, restrictions and next work

Reproduce with:

```bash
python tools/hist001d_d2b.py --source-root research/legacy/hist001 --out runs/hist001d_d2b
python tools/hist001d_d2b.py --source-root research/legacy/hist001 --verify runs/hist001d_d2b/receipt.json
```

The runner verifies the original file lock before and after execution, imports the original solver through a disposable copy without altering its files, independently reproduces the original 180/120 slow solver, records source/diagnostic hashes, and requires an independent reexecution of the 6×4 factorial plus additional quadrature/root checks to validate the receipt. Self-rehashed numerical tampering, altered claim flags, unexpected report files and modified original source must fail closed. Existing HIST-001D tests and HIST-001B historical source gates remain intact.

**No scientific promotion:** The source is a fitted historical six-lens regression, not an unbiased holdout or physical Weyl-lensing provider. The original 6/6 result is preserved alongside these numerical warnings; no correction, fit adjustment or new cosmological model is admitted. `physical_provider_admitted=false`, `native_v172_equivalence_proved=false`, `new_holdout_scored=false`, `empirical_validation=NOT_ESTABLISHED`.

Remaining work: independently bound errors of the *full* shadow-density projected mass rather than only analytic bulge, test the critical-radius root with genuinely independent radial projection quadrature, continue fixed-source high-grid convergence with explicit tolerance, and carry out D3 (published covariance/IMF) and D4 (new disjoint preregistered holdout) separately. HIST-001B's missing original accelerated producer/RNG/600 prechecks remain a separate open source-recovery issue.
