# HIST-001D — original March 180 shadow-gradient source closure GAP (candidate-only)

**Research source review, 2 November 2026. NONPROMOTING.** Based on verified software `main=f5ce70cc19d4875de1a2adf47ea40f8345a775cf`; canonical Theory-State `v0.16.39` remains unchanged. This source-only draft exposes methods, not the original March code, raw 180-node density vectors, generated evidence, fitted astronomy data, D2d regenerated 11,520-node shadow or any physical provider.

## Exact source identity and diagnostic

The historical `J2141BaryonicModel.bulge_v2`, `disk_v2` and calibrated `epsilon_radius_proxy` define an acceleration-equivalent baryonic mass and a *candidate continuous mathematical shadow-mass extension*:

`Mbar_acc = Mb*r^2/(r+a)^2 + Md*y^3*(I0(y)*K0(y)-I1(y)*K1(y))`, `y=r/(2*Rd)`, `epsilon=1-delta*r^n/(r^n+r0^n)`, `Mshadow_smooth=Mbar_acc*(1/epsilon-1)`.

The original `np.gradient(Mshadow,r)` uses a first/last one-sided secant and a nonuniform three-point stencil at internal nodes, followed by clipping of negative density. Analytic differentiation of the unchanged frozen scalar law yields very different density at the original first radius `R=0.02 kpc`. Distinct SciPy Bessel derivatives at all 1,080 original nodes and 55-digit direct `mpmath.diff` at 5–7 knots per lens check the *numerical evaluation*, but are **not rigorous Bessel interval bounds**. Source/smooth density first-node ratios (original fitted six-lens order): **6.80, 7.72, 11.33, 4.32, 10.84, 7.83 million**.

Replacing only original 180-node shadow-density values by this new mathematical smooth-derivative diagnostic while retaining the original K180, disk120, B/D, q/aperture, Sigma and first-crossing selector changes the six sampled numerical crossings. That is a **different diagnostic**, not a recalibration, source-authenticated continuous density or original off-grid root theorem.

## Conditional C2/C3 mathematical error lemma — critical gate remains OPEN

For a smooth scalar source `M`, write `hm=r_i-r_(i-1)>0`, `hp=r_(i+1)-r_i>0`. The exact-real three-point nonuniform gradient has the Taylor remainder bound

`abs(D_i-M'(r_i)) <= (hm*hp/6) * sup_[r_(i-1),r_(i+1)] abs(M'''(r))`.

For the one-sided first and last derivatives, `abs(D_edge-M'(r_edge)) <= (h/2) * sup_cell abs(M''(r))`. Clipping to the nonnegative reals is 1-Lipschitz. The historical binary64 gbar/epsilon/mass, gradient and clipping require separate certified floating-point allowances.

**No source-validated interval upper bounds on M'', M''' or Bessel/special-function errors have been produced.** Therefore the true source-gradient error and full original 180×120 residual/root-count error remain `UNRESOLVED_DERIVATIVE_SUPREMA_NOT_CERTIFIED`. Synthetic quadratic/cubic tests verify the sharp formula coefficients only.

## External executable evidence; review requirements

The self-contained source-locked [19-member NONPROMOTING archive](https://drive.google.com/file/d/1_INgjkz5_6zo9jGZJa9K1GeYfhvzrcvD/view) has SHA-256 `3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18`. It contains the original protected 46+3 source parent, 180-node source outputs, actual source replay, different numerical Bessel derivative implementations, 55-digit direct derivative checks, 18/18 fail-closed tamper controls, and independent clean-extraction result SHA verification. **No protected source files are included in this GitHub draft.** Local source-free tests: 18/18 PASS. Exact-head GitHub CI and independent mathematical review remain separate gates; public CI cannot claim actual external-source reproduction.

Next: (1) independently interval-certify original Bessel-defined M''/M''' and clipping branches over every original real radial cell; (2) certify source binary64 mass/gradient operational errors and project density through K180 and q circularization; (3) combine all source-selected bulge/disk/Sigma numerical errors and a derivative/variation root-count theorem; (4) separately assess physical Weyl/Native v1.7.2 and genuinely disjoint D3/D4 observational tests. No physical provider, empirical validation, CDM replacement, production scoring or canonical graph promotion is claimed.
