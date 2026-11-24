# HIST-001D — Original March K180 versus selected smooth continuum on six complete crossing-cell apertures

**2 November 2026 · CONDITIONAL MATHEMATICAL CANDIDATE · NONPROMOTING · SOURCE-PRESERVING.**

This work extends the six *fixed diagnostic aperture* inequalities in stacked draft PR #53 to six **whole** source-defined original-March crossing aperture bands. It does **not** establish the original March off-grid full Einstein-root function, any continuum-root location or uniqueness theorem, physical source admissibility, original floating SciPy/NumPy error for arbitrary inputs, or current Native ESET v1.7.2 Weyl/lensing predictions. The historical Set A six lenses were fitted development lenses, not a blind test. No physical provider, empirical validation, production scoring, no-particle-CDM or new canonical Theory-State release is authorized.

## Exact frozen mathematical objects and provenance

Original March 46 files plus three negative controls: SHA-256 `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`. Original-180 source parent: SHA-256 `3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18`. Source 180 binary64 radius nodes, trapezoid weights, clipped shadow densities and `C4pi` are **exact fractions**. All raw data stay in the external, protected, hash-locked archive. No D2d regenerated 11,520-node shadow profile is substituted.

The selected *mathematical*, acceleration-equivalent historical smooth mass is the separately authored

\[
M_*(r)=\left[\frac{M_b r^2}{(r+a)^2}+M_d y^3\{I_0(y)K_0(y)-I_1(y)K_1(y)\}\right]\frac{\delta f(r)}{1-\delta f(r)},\qquad y=\frac{r}{2R_d},\quad f(r)=\frac{r^n}{r^n+r_0^n}.
\]

For \(a_r=\mathrm{binary64}(0.02)\), \(b_r=120\), and \(\phi(A,r)=1\) for \(r\le A\) or \(1-\sqrt{1-A^2/r^2}\) for \(r>A\), compare

\[
Q(A)=\sum_{i=0}^{179}w_i C_{4\pi}r_i^2\rho_{S,i}^{\mathrm{stored}}\phi(A,r_i),\qquad
P_*(A)=\int_{a_r}^{b_r}M_*'(r)\phi(A,r)\,dr.
\]

The original recorded source `S0_i`, this frozen K180 operator and the selected smooth mathematical continuum are distinct objects. The calculation is entirely conditional on *this* \(M_*\) law, not on nodal values and positivity alone. Nodal non-identifiability remains a separate valid obstruction outside the chosen law.

## Source-defined aperture bands, not an assumed true-root interval

The six historical *sampled* root radii locate six original source radial cells \([R_i,R_{i+1}]\); the sampled crossing is not itself a proof of a unique or physical continuous root. With the original binary64 \(B_i,D_i,q_b,q_d\), define the explicitly labelled **mathematical off-grid extension**:

\[
q(R)=\frac{q_b B_{\rm PL}(R)+q_d D_{\rm PL}(R)}{B_{\rm PL}(R)+D_{\rm PL}(R)},\quad
A(R)=\min(120,R/\sqrt{q(R)}).
\]

On each original source interval, \(N=q_bB_{\rm PL}+q_dD_{\rm PL}\) and \(P=B_{\rm PL}+D_{\rm PL}\) are affine. Their ratio has derivative \(q'(R)=C/(hP^2)\) with \(C=N_1P_0-N_0P_1\). The producer **independently rechecks on all 179 source intervals** the conservative exact-dyadic inequality

\[
2\min(q_i,q_{i+1})-R_{i+1}\max(0,C/[h\min(P_i,P_{i+1})^2])>0.
\]

Thus unsaturated \(A(R)\) is strictly increasing across every source interval in the specified *piecewise-linear extension*. Exact outward 512-bit square-root enclosures of the two crossing-cell endpoint \(q\) values yield rational \(A_{\rm lo}\le A(R_i)\) and \(A_{\rm hi}\ge A(R_{i+1})\). All six bands lie strictly inside the original finite radial support. These rational bands contain the full image of the named source cells, not arbitrary target radii or a true-root uniqueness guarantee.

## Cusp-free continuum and whole-band curvature inequality

For \(a_r<A<b_r\), put \(u_b=\sqrt{1-(A/b_r)^2}\), \(\theta_b=\arccos(A/b_r)\). Integration by parts removes the explicit \(r=A\) cusp:

\[
P_*(A)=M_*(b_r)(1-u_b)-M_*(a_r)+\int_0^{u_b}M_*\!\left(\frac A{\sqrt{1-u^2}}\right)du.
\]

Differentiating the original finite-radius projection, using the smooth selected law, gives the **correct exact** identities

\[
P_*'(A)=\int_0^{\theta_b}M_*'(A\sec\theta)\,d\theta,
\qquad
P_*''(A)=\int_0^{\theta_b}M_*''(A\sec\theta)\sec\theta\,d\theta
-\frac{M_*'(b_r)}{b_r\sqrt{1-(A/b_r)^2}}.
\]

The implementation bounds the magnitude of the integral conservatively via \(\sec\theta\le\sec^2\theta\), so its cellwise positive geometric factors become differences of \(\tan\theta=\sqrt{r^2-A^2}/A\). It does **not** assert that the \(\sec^2\theta\) expression equals \(P_*''\). For cells completely beyond the band, \(d(A)=\sqrt{r_{hi}^2-A^2}-\sqrt{r_{lo}^2-A^2}\) increases with \(A\); hence the safe upper is \(d(A_{hi})/A_{lo}\). For crossing cells, the safe upper is \(\sqrt{r_{hi}^2-A_{lo}^2}/A_{lo}\). The endpoint term is bounded by \(|M_*'(b_r)|/[b_r\sqrt{1-(A_{hi}/b_r)^2}]\). These operations use outward integer rational square-root enclosures and **all-real cell** enclosures of \(|M_*''|\).

The inherited source Bessel implementation uses the positive integral representation

\[
I_0(y)K_0(y)-I_1(y)K_1(y)=\frac2\pi\int_0^\pi K_0(2y\sin\theta)\sin^2\theta\,d\theta.
\]

Together with the positive Laplace representation of \(K_0\), this establishes the complete-monotonicity sign pattern for the Bessel combination on positive \(y\). The previously recorded 512-bit rational Bessel arithmetic, source gamma enclosure and gate law are reused, not independently reimplemented in this PR. The all-real \(M_*''\) enclosure is a source-conditional mathematical calculation. Summing conservative rounded integer contributions yields a uniform per-lens constant \(K\) such that \(|P_*''(A)|\le K\) throughout the full aperture band.

## Convex frozen K180 and exact whole-subband witness

Between adjacent *aperture* node locations \(A=r_i\), every unsaturated positive-shell summand of \(Q(A)\) is convex because

\[
\frac{\partial^2\phi(A,r_i)}{\partial A^2}=
\frac{1}{r_i^2[1-(A/r_i)^2]^{3/2}}>0\quad(A<r_i),
\]

while saturated terms are constant. The producer first **splits at every crossed original radial node**, then recursively subdivides. Within a certified subband \([L,U]\) with midpoint \(T\), convexity guarantees the supporting line

\[
Q(A)\ge Q(T)+Q'(T)(A-T).
\]

The right-hand side is evaluated with outward rational bounds and signed-slope direction (upper slope for \(A<T\), lower slope for \(A>T\)). The continuum interpolation remainder gives, for every real \(A\in[L,U]\),

\[
P_*(A)\le P_L^{\rm upper}+\frac{A-L}{U-L}(P_U^{\rm upper}-P_L^{\rm upper})
+\frac K2(A-L)(U-A).
\]

The difference of these two expressions is an **exact rational quadratic**, minimized analytically on each side of \(T\), with a floor to integer solar masses. Acceptance requires its lower bound \(>0\); otherwise bisect or explicitly mark unresolved at the depth cap. The release records every rational boundary, signed tangent and continuum endpoint upper, integer curvature ceiling, lower-witness floor and leaf coverage. An independent *arithmetic/topology* checker re-evaluates all leaf quadratics and rejects gaps, overlaps, duplicate/missing lenses and source-node crossings. It is **not** a second independent Bessel evaluator, which remains a review obligation.

## Current source-conditional six-lens result

| Historical fitted lens | Strict positive lower bound across **entire** aperture band (M☉) | Positive subbands | Unresolved |
|---|---:|---:|---:|
| J0822+1828 | 21,805,299 | 19 | 0 |
| J0915+4211 | 4,150,093 | 18 | 0 |
| J0930+2855 | 103,251,442 | 9 | 0 |
| J1021+2028 | 1,489,373 | 26 | 0 |
| J1111+2234 | 9,141,000 | 15 | 0 |
| J1135+3720 | 30,566,152 | 14 | 0 |

**101/101** accepted rational subbands, **0 unresolved**. Per-lens lower bounds are conservative intervals and differ from earlier exploratory candidate values. They do not measure physical lensing error, nor show where the original full historical \(H(R)\) crosses zero.

The six-lens manifest/receipt, protected numerical files, full original source/data parent, complete leaf ledgers, QA records and exact SHA-256 values are retained outside public GitHub. The controlling G4b.1b software main and canonical Theory-State v0.16.39 are not changed.

## Auxiliary selected-source derivative-positivity audit

A separate source-conditional 512-bit outward Bessel/derivative run divides the original radial support \([\mathrm{binary64}(0.02),120]\) into adaptive dyadic cells and verifies \(M_*'(r)>0\) on **every real point** within those cells, not only at the 180 recorded nodes. The six lenses required 181, 181, 179, 181, 180 and 915 accepted positive cells respectively (J1135 needed the finest near-origin subdivisions), with **zero unresolved** at the depth-18 cap. This is a *selected mathematical mass function* property, not proof of physical density source admission. It is auxiliary: the main convex-K180/curvature band certificate does not assume global \(M_*'\) positivity.

## Reproduction and review gates

Run the source-only scripts using the *original, protected* v1r1 parent and the source-locked diagnostic JSON, with the same configurations recorded per lens:

```bash
for i in 0 1 2 3 4 5; do
  # run with the explicitly recorded per-lens bisection/depth values
  python reference/hist001d_k180_crossing_band_candidate/crossing_band_certifier.py \
    --index "$i" --external-zip /protected/saturation_v1r1.zip \
    --diagnostic-json /protected/root_diagnostic.json \
    --bisects 55 --max-depth 9 --out "lens${i}.json"
done
python reference/hist001d_k180_crossing_band_candidate/assemble_receipt.py \
  --external-zip /protected/saturation_v1r1.zip \
  --diagnostic-json /protected/root_diagnostic.json --result-dir . \
  --out whole_band_certificate.json --adversarial-out adversarial_qa.json
pytest -q tests/historical/test_hist001d_k180_crossing_band_source_free.py
```

For **byte-identical replay** of the deposited per-lens JSON, use the exact bisection/depth numbers included in each record (J1021 used 50 bisections, the other five used 55; J1135 used max-depth 9, the other five max-depth 8). The generalized example above may create numerically different but still safe intervals and is not itself a guarantee of matching the deposited SHA. Public CI runs source-free tests only, never the private source archive.

Before any merge: independently review the Bessel rational arithmetic and complete-monotonicity argument, whole-band curvature and tangent inequalities, original q/circularization source-law scope, exact data-dependent replay, privacy/license provenance and exact-head six-platform CI. After an independently authorized merge, separately check postmerge CI and protected Drive readback. **No original full historical H off-grid theorem, root count, physical source selection, GR/Weyl same-source lens, D3/D4 blind validation, no-CDM or provider is admitted.**
