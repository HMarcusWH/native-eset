# HIST-001D/D2e-B — conditional interval exclusion outside the fitted Einstein root

**Status:** source-locked numerical research only. **NOT** a mathematical root-uniqueness certificate, observed holdout, physical Weyl-lensing calculation, modern Native ESET v1.7.2 result, or error theorem.

## Scientific question and distinct identity

The merged D2d procedure evaluates a complete *finite-domain*, radius-dependent structured-shadow proxy for six already fitted SWELLS Set A development lenses. Its 11,520-point density-grid result is 3/6 under the historical joint 2-sigma *upper-error* scoring rule; the frozen original 180-point/120-angle regression remains a distinct 6/6 numerical identity. D2e-A (merged PR #20) checked 45/181/721 sampled sign changes, local derivative and sampled clipping, and bounded sensitivity to removing known outer shells. None proves that there are no additional roots between sampled points.

This D2e-B addition replaces sign-only confidence with **conservative component-mass enclosures** on adaptive intervals outside a predeclared 2% window around the D2d 11,520-grid root. It does **not** establish uniqueness *inside* that window, nor does it bound unknown matter outside the source interval [0.02, 120] kpc. It remains explicitly a **conditional** calculation: the 10^-6 relative numerical mass-error allowance is assumed, not proven.

## Equation, positivity and enclosure derivation

For each radius \\(R\\), the preexisting D2d mass function is

\\[
F(R)=M_b(R)+M_d(R)+M_{\\mathrm{sh,sph}}\\!\\left(\\min\\left[120,\\frac{R}{\\sqrt{q_{\\mathrm{eff}}(R)}}\\right]\\right)-\\pi\\Sigma_{\\mathrm{crit}}R^2,
\\]

with \\(q_{\\mathrm{eff}}(R)=\\mathrm{clip}_{[10^{-3},1]}[(q_bM_b+q_dM_d)/(M_b+M_d)]\\).

Given an interval \\([\\ell,h]\\), positivity of the source bulge, disc and piecewise-linear shadow-density profiles makes each corresponding cylinder mass nondecreasing with aperture. Hence \\(M_b(\\ell)\\le M_b(R)\\le M_b(h)\\), and likewise for the disc. Let the two corresponding positive projected masses be \\(B\\) and \\(D\\). The un-clipped effective axis ratio \\((q_bB+q_dD)/(B+D)\\) is fractional linear in each independent mass variable, so its extrema over the positive rectangle occur at its four corners. Denote the clipped minimum and maximum by \\(q_-\\) and \\(q_+\\).

The effective shadow aperture is therefore bounded by

\\[
A_- = \\min(120,\\ell/\\sqrt{q_+}),\\qquad
A_+ = \\min(120,h/\\sqrt{q_-}).
\\]

As the finite-domain shadow cylinder mass is nondecreasing, the lower and upper total-mass bounds are

\\[
M_- = M_b(\\ell)+M_d(\\ell)+M_{\\mathrm{sh}}(A_-),\\qquad
M_+ = M_b(h)+M_d(h)+M_{\\mathrm{sh}}(A_+).
\\]

With a **hypothetical, not proven** relative mass error bound \\(\\epsilon_M=10^{-6}\\), the diagnostic evaluates

\\[
G_-=\\frac{(1-\\epsilon_M) M_-}{\\pi\\Sigma_{\\mathrm{crit}}h^2}-1,\\qquad
G_+=\\frac{(1+\\epsilon_M) M_+}{\\pi\\Sigma_{\\mathrm{crit}}\\ell^2}-1.
\\]

Under the explicit numerical-error assumption, an interval with \\(G_->0\\) or \\(G_+<0\\) can contain no root. Otherwise the interval is bisected until the configured depth/visit limits; all unresolved intervals are recorded, not dropped. These inequalities are a mathematically defensible *structure* for enclosure, but the floating-point quadrature and global 10^-6 error premise have **not** been interval-validated. Therefore an excluded interval is reported only as **CONDITIONAL**, never a rigorous theorem.

## Input, executable and controls

- Original March 46+3 source SHA: `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`.
- Input numerical dependency: D2e-A source SHA `ea0aaebc74738524f7bf071e7594cf2c275d5f9b9aff1f75d04051b7c1f876f2`. D2e-A already pins merged D2c and D2d source bytes.
- Source grids: 11,520 points; exact same fitted `ra0_gated_geometry_sigmoid_reg_v2`, same six rows and same 70/0.3 reference cosmology.
- Frozen guard: `root × [0.98, 1.02]`. Only its complement is evaluated for conditional root exclusion; the guard is **not** certified to contain a unique root.
- Adaptive budget: depth 18, at most 2,048 intervals per lens; unresolved branches and visit exhaustion are preserved.
- Independent source reexecution from a disposable verified source copy; canonical JSON report and receipt, with SHA-256 of tool, dependency and observed numerical inputs.

Execute:

```bash
python tools/hist001d_d2e_interval.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_b
python tools/hist001d_d2e_interval.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_b/receipt.json
```

The test suite includes synthetic two-root and tangential-root cases where endpoint signs match or never change. Such cases remain unresolved by interval enclosures; they cannot be misreported as root-free merely because no sampled sign change exists.

## Release gate and scientific stop line

A reproducible scoped result requires source-verification and nonpromotion flags, clean lint, full existing regression tests, standalone production run and a **fresh independent source reexecution**, complete manifest and six-platform GitHub CI. A CI pass does not prove physical Weyl lensing or global numerical accuracy.

Remaining D2e research: prove or fail numerical mass-error enclosures with certified quadrature; obtain true interval derivative/root-count bounds *including the guard*; characterize density-derivative discretization and both radial truncation boundaries; and propagate validated errors into the fitted radius and mass diagnostics. D3 original published SWELLS covariance, D4 disjoint preregistered holdout, D5 same-sourced metric/Weyl solution, historical B RangeFinder and current Native v1.7.2 compatibility remain independent open tasks.

**Claims stay false:** `uniform_quadrature_error_budget_proved`, `root_uniqueness_mathematically_certified`, `global_error_bound_established`, `mass_outside_finite_domain_bounded`, `physical_provider_admitted`, `physical_weyl_lensing_derived`, `new_holdout_scored`, `native_v172_equivalence_proved`.
