# HIST-001D — independent real-integral Bessel proof route (all 180×6 frozen nodes)

**Source-conditional candidate, nonpromoting. 3 November 2026.**

## Source identity and exact object

The original March 46+3 source/negative-control composite is SHA-256 `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`, loaded from the immutable saturated v1r1 archive, SHA-256 `99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce`. The audit uses the **original** six binary64 frozen source sets and six × 180 frozen positive radii/weights/clipped densities. No regenerated 11,520-point D2d source is substituted.

The selected mathematical, acceleration-equivalent shadow mass is

\[
M_*(r)=\left(\frac{M_b r^2}{(r+a)^2}+M_d y^3 F(y)\right)G(r),\quad
 y=\frac{r}{2R_d},\quad F(y)=I_0(y)K_0(y)-I_1(y)K_1(y),
\]

\[
f(r)=\frac{r^n}{r^n+r_0^n},\qquad G(r)=\frac{\delta f(r)}{1-\delta f(r)}.
\]

The derivative uses the exact analytic identity

\[
F'(y)=2\bigl(I_1K_0-I_0K_1+I_1K_1/y\bigr).
\]

This is a **separately selected mathematical continuation**, not a covariantly derived physical shadow stress tensor or an admissible Weyl/lensing provider.

## Entirely different source of Bessel-K intervals

The earlier 512/608-bit routes represented K0/K1 through logarithmic power series involving Euler's constant. The new route does **not** call or import those special-function routines, SciPy, NumPy or mpmath to establish the interval result. Instead it uses, for ν=0,1 and real y>0,

\[
K_\nu(y)=\tfrac12\int_{-\infty}^{\infty}f_\nu(t)dt,\qquad
 f_\nu(t)=e^{-y\cosh t}\cosh(\nu t).
\]

The infinite even trapezoidal series at h=1/32 is

\[
T_{\nu,h}(y)=h\left(\tfrac12 f_\nu(0)+\sum_{k\ge1}f_\nu(kh)\right).
\]

**Analytic-strip error proof.** The integrand is entire and integrable on horizontal shifts ±iπ/3. Since cos(π/3)=1/2, |cosh(ν(t+iπ/3))| ≤ cosh(t) for ν=0,1 and cosh(t) ≥ e^t/2 for t≥0,

\[
\int_{-\infty}^\infty |f_\nu(t+i\pi/3)|dt\le 8/y.
\]

By Poisson summation with contour displacement, the **full infinite** trapezoidal error obeys

\[
|K_\nu(y)-T_{\nu,h}(y)|\le
\frac{8/y}{\exp(2\pi^2/(3h))-1}
\le\frac{8}{y(2^{6/h}-1)}.
\]

Here π>3, e>2; the second inequality deliberately uses conservative elementary integer bounds. For h=1/32 the final exponent is 192. This is an explicit source-free theorem obligation independent of any fitted lens numbers.

**Finite-sum tail.** Let t0=(N+1)h be the first omitted positive grid location, z0=y·exp(t0)/2. The kernel is positive and obeys fν(t) ≤ exp(t)exp[-y exp(t)/2]. Stop when the rational interval proves z0 ≥160. At h=1/32 or 1/64 the majorant's successive term ratio is below 1/4 because exp(h)≤16/15 and exp(h)-1≥h. Thus the omitted positive sum is bounded by

\[
0\le h\sum_{k=N+1}^{\infty}f_\nu(kh)
\le\frac43 h e^{t_0}\exp[-(y/2)e^{t_0}].
\]

All exponential values and reciprocal operations use **512-bit directed integer intervals**: Taylor series after range reduction to ≤1/2, positive geometric-series tail bounds and repeated interval squaring. I0 and I1 use separately bounded positive entire power series (not K's logarithmic series). The material gate uses positive exponential plus an interval atanh expansion for log; this last elementary logarithm is shared mathematical functionality, not a second independent gate theorem.

## Conditional finite-mass/mass-gradient and all-aperture result

All 1,080 original frozen radii have source-conditional positive M*'(r) lower bounds from this new K-integral engine. The per-lens protected JSON files store the **unrounded fraction endpoints** for F, F', M* and M*', the frozen radius hex value, each grid's N, the strip/truncation tail budgets, and the inherited old integer comparison receipt.

Define d_source,i = C4π(source) r_i² ρ_source,i; the ideal nonuniform three-point/endpoint derivative D_i[M*] of the **exact mathematical mass sampled at the original radii**. Since the original trapezoid weights w_i>0 and 0≤φ_A(r_i)≤1 for every real A≥0,

\[
\sup_{A\ge0}\left|\sum_i w_i\bigl(d_{\rm source,i}-D_i[M_*]\bigr)\phi_A(r_i)\right|
\le\sum_i w_i\max\bigl|d_{\rm source,i}-D_i[M_*]\bigr|.
\]

The *independently implemented* Fraction/IEEE754-bit-decoder checker uses a Lagrange three-point stencil rather than the producer's interval special-function arithmetic, and obtains the following outward ceilings:

| Lens | New source-to-ideal stencil bound | Previously inherited upper |
| --- | ---: | ---: |
| J0822+1828 | 1.072016 M☉ | 1.072079 M☉ |
| J0915+4211 | 2.390597 M☉ | 2.390655 M☉ |
| J0930+2855 | 0.540796 M☉ | 0.540857 M☉ |
| J1021+2028 | 0.270967 M☉ | 0.271028 M☉ |
| J1111+2234 | 0.729773 M☉ | 0.729836 M☉ |
| J1135+3720 | 0.721336 M☉ | 0.721396 M☉ |

The new numbers were rounded *up* in integer micro-solar-mass units. These are **uniform bounds on the fixed-node stored source vs ideal mass-difference stencil**, NOT bounds on the difference to the mathematically continuous radial projection or the physical model.

## Independent algebraic checks

At 35 source-defined crossing-neighborhood/support endpoints, intervals from the old logarithmic Bessel representation and the new real-integral route overlap for **both** M* and M*'. At one source-defined crossing node per lens, running a different trapezoid resolution h=1/64 yields overlapping F and F' enclosures with h=1/32, and independently encloses the exact modified-Bessel Wronskian

\[
I_0(y)K_1(y)+I_1(y)K_0(y)=1/y
\]

at both resolutions. This cross-resolution consistency check does not substitute for the all-node h=1/32 proof.

## Status firewall and remainder

No independent external referee or formal theorem-prover has certified the analytic-strip justification or the input-source modeling assumptions. The new route establishes a **candidate** arithmetic enclosure for the selected mathematical source at frozen nodes; it does **not** prove the original arbitrary-input floating Bessel ulps, all-real intermediate-node positivity, source-original continuous-density selection, radial quadrature error to the continuum, full original physical H, physical lensing, blind D3/D4 validation, Native ESET v1.7.2 provider, no-particle-CDM or full cosmology. `physical_provider_admitted=false`; `empirical_validation=NOT_ESTABLISHED`; canonical Theory-State v0.16.39 unchanged.

The next genuinely different scientific gate is **continuous real-radius bounds on selected M*(r) and its derivatives between frozen nodes** and, separately, action-authorized same-source physical density/Weyl closure. This archive is an independent *nodal* Bessel assurance stage, not either of those promotions.
