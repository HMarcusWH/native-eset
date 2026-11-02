# HIST-001D — original March K180 versus selected smooth continuum at six fixed diagnostic apertures

**2 November 2026 · NEW mathematical candidate · DRAFT / NONPROMOTING · not an original March root theorem.** This follows the saturated-aperture candidate under PR #51, with original data held outside GitHub. The current parent software baseline is G4b.1b; canonical Theory-State v0.16.39 and physical/empirical admission remain unchanged.

## Scope of the six claims

The source is the *original March* six-by-180 `reg_v2` frozen source: exact interpretations of each recorded binary64 radius, trapezoid weight, clipped shadow density, `4*np.pi` and parameter. The original 46+3 composite SHA-256 is `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a` and source parent ZIP SHA-256 is `3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18`.

For each lens, `A` is **exactly the binary64 real** read from that lens's *separate numerical* diagnostic JSON `HIST001D_K180_Root_Aperture_Six_Lens_Diagnostic_NONPROOF_v1_2026_11_02.json`, SHA-256 `298a467e6ceab5c48ced00e08ac2fdb1082627eebedb6340139021f090430812`. These are six chosen *points*, **not entire original crossing-cell bands** and **not a certified mapping of all real Einstein radii through q(R)**.

The selected smooth mathematical continuation is

\[
M_*(r)=\left[M_b\frac{r^2}{(r+a)^2}+M_d y^3F(y)\right]\frac{\delta f(r)}{1-\delta f(r)},\qquad
F(y)=I_0(y)K_0(y)-I_1(y)K_1(y),\quad y=\frac{r}{2R_d},\quad f(r)=\frac{r^n}{r^n+r_0^n}.
\]

It is not a physical Native ESET v1.7.2 mass or Weyl-potential source. Define

\[
P_*(A)=\int_{r_{\min}}^{120}M_*'(r)\phi_A(r)\,dr,\qquad
Q_{\rm March}(A)=\sum_{i=0}^{179}w_i C_{4\pi}r_i^2\rho_{S,i}^{\rm recorded}\phi_A(r_i),
\]

with \(\phi_A(r)=1\) for \(r\le A\) and \(1-\sqrt{1-(A/r)^2}\) otherwise.

## Exact continuum transformation: cusp removed

For \(r_{\min}<A<120\), set \(u=\sqrt{1-(A/r)^2}\) on \(r>A\). Integration by parts gives

\[
P_*(A)=M_*(120)(1-u_{120})-M_*(r_{\min})+
\int_0^{u_{120}}M_*\!\left(\frac{A}{\sqrt{1-u^2}}\right)du.
\]

In this representation the integrand is smooth on the compact transformed domain for every fixed positive A. It has no source-radius square-root cusp at \(r=A\).

## Endpoint special-function derivative theorem

The modified-Bessel addition theorem (see NIST DLMF §10.44) implies the positive integral

\[
F(y)=\frac{2}{\pi}\int_0^\pi K_0(2y\sin t)\sin^2t\,dt,\qquad y>0.
\]

The standard positive Laplace representation \(K_0(z)=\int_0^\infty e^{-z\cosh s}\,ds\) yields complete monotonicity of F. In particular

\[
F>0,\qquad F'<0,\qquad F''>0,\qquad F'''<0.
\]

Therefore, on an *entire* real cell \(y\in[y_0,y_1]\), the function and its first two derivatives are enclosed by directed-rational endpoint evaluations:

\[
F(y_1)\le F(y)\le F(y_0),\quad F'(y_0)\le F'(y)\le F'(y_1),\quad F''(y_1)\le F''(y)\le F''(y_0).
\]

These do not assume that sampled data imply full-real monotonicity of **M**. Its derivatives are enclosed separately using the exact analytic gate and product rule. The derivative identity used is

\[
F''(y)=4F(y)-\frac{2F'(y)}y-\frac{2I_1(y)K_1(y)}{y^2}.
\]

All Bessel point bounds are the source-reused 512-bit outward exact-rational series/enclosure implementation, not SciPy floats. The method has one Bessel arithmetic family: this is **not** independent-engine reproduction or external peer review.

## Provable integration error per transformed cell

For each source-radius interval \([r_i,r_{i+1}]\) above A, map the endpoints to outward intervals \([u_i,u_{i+1}]\), subdividing cells adaptively at exact rational radius midpoints. Define \(g(u)=M_*(r(u))\). Then

\[
g''(u)=M_*''(r)(r')^2+M_*'(r)r'',\qquad
r'=\frac{r^3u}{A^2},\quad r''=\frac{r^3(1+2u^2)}{A^2(1-u^2)}.
\]

Using full-real directed interval bounds for \(M_*'\), \(M_*''\), \(r'\), \(r''\) on the cell, apply the classical trapezoidal error bound

\[
\left|\int_{u_i}^{u_{i+1}}g(u)\,du-\tfrac12(u_{i+1}-u_i)(g(u_i)+g(u_{i+1}))\right|\le
\frac{(u_{i+1}-u_i)^3}{12}\sup_{[u_i,u_{i+1}]}|g''|.
\]

All square roots, coefficients, local errors and interval sums round outwards at the inherited 512-bit integer fixed-point scale. Independently, Q is enclosed directly from the frozen original source arrays by the same directed sqrt, with every original binary64 input interpreted as an exact rational. Finally compute the outward interval for \(Q-P\). The JSON result contains outward-rounded integer-solar-mass endpoints.

## Status and research limits

- This is an **a posteriori conditional mathematical source comparison** for exactly six specified binary64 apertures. It does not bound the original March `np.gradient`/SciPy operation path for arbitrary newly generated inputs.
- The earlier six-lens **saturated A=120** error ceilings remain a different result. The present proof does not extend those tiny endpoint ceilings to smaller radii; rather it certifies a positive mismatch at the chosen fixed apertures.
- The numerical six-aperture diagnostic was an input locator, not proof. Its floats were never used as interval bounds for the continuum integral.
- No continuum root existence/uniqueness, original full H error, all-real crossing-cell aperture band, q(R) transformation, D120 omitted-arc or target interpolation transfer, physical density positivity/source law, Weyl/Native v1.7.2 equation closure, D3/D4 validation, no-CDM or production provider has been established.
- No scientific status authority may be promoted by a successful sign certificate. `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`, `all_aperture_bands_proved=false`, `original_off_grid_H_root_count_proved=false`.

## Replay

The full **external protected** v1r1 review-repair ZIP and six-aperture diagnostic JSON must be available locally. The public repository provides only the certifier and source-free tests:

```bash
python reference/hist001d_k180_root_aperture_candidate/root_aperture_certifier.py \
  --external-zip /path/to/HIST001D_K180_SATURATED_REVIEW_REPAIR_V1R1_NONPROMOTING_2026_11_02.zip \
  --diagnostic-json /path/to/HIST001D_K180_Root_Aperture_Six_Lens_Diagnostic_NONPROOF_v1_2026_11_02.json \
  --bisections 120 --out root_fixed_A_certificate.json
pytest -q tests/historical/test_hist001d_k180_root_aperture_source_free.py
```

## Next genuinely open gate

To replace the **pointwise** result with an **all-aperture-band** result, obtain source-defined rigorous \(A(R)\) enclosures over each original crossing interval and certify the continuous/discrete difference for *every real A* in those bands (e.g. with subdivided A-bands and interval kernel propagation). Only then transport the shadow result into the original full H source and test existence/root count/uniqueness using suitable cusp-aware variation or one-sided derivative methods. Preserve an explicit failure result if any band does not pass.

## Exact directed six-lens fixed-A result (outward integer solar masses)

The following are **pointwise** intervals of `Q_March(A)-P_*(A)` in solar masses, not errors in the full historical Einstein root function. The six A coordinates are the exact binary64 numbers in the diagnostic input; the values below are integer enclosures rather than floating point estimates. All are strictly positive.

| Lens | Fixed diagnostic A (kpc; decimal for navigation) | Certified `Q_March-P_*` (solar masses) | transformed integration cells |
|---|---:|---:|---:|
| J0822+1828 | 2.49605533047 | [254,308,399, 267,921,497] | 296 |
| J0915+4211 | 1.69791056503 | [165,572,669, 175,267,038] | 297 |
| J0930+2855 | 6.23564642787 | [1,276,547,188, 1,363,259,240] | 290 |
| J1021+2028 | 1.80222257575 | [40,172,228, 42,273,731] | 297 |
| J1111+2234 | 5.12272780490 | [63,958,572, 77,745,893] | 292 |
| J1135+3720 | 3.40707526639 | [318,042,242, 327,803,542] | 294 |

Proof/certificate receipt SHA-256: `d8f7a8d327b7af89b7eee0c6e49a643c218e4b8de7b689df51667c0338771e00`. Source-repair parent SHA-256: `99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce`. Protected source parent: <https://drive.google.com/file/d/1NtGLmtv5wq6wOK4Nv4jvNLC58B7xAace/view>. The full original data and result JSON stay in the separate protected science ZIP.

The positive lower endpoints reflect the particular chosen `M_*` continuation and original frozen clipped data, **not an assertion that the historical model is empirically wrong or physically invalid**. A second arithmetic engine and external review of the complete-monotonicity/interval argument remain advisable before publication as a formal theorem.
