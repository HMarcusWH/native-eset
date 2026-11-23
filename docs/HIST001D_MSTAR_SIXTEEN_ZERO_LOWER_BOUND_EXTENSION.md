# HIST-001D / D2e — Extra exact-rational Peano witnesses: sixteen-zero existence **lower bound**

**4 November 2026 · mathematics only · source-conditional · NONPROMOTING · not a physical lensing model.**

## Frozen objects and controlling prior work

Keep **exactly** the selected historical acceleration-equivalent mathematical mass continuation \(M_*(r)\) and original frozen 180-node source geometry. The previously sealed PR #63 candidate proved at least 10 distinct zeros across six different functions, with certified \(M_*'(r)>0\), 128 targeted midpoint refinements per lens, a bounded Peano interpolation remainder, and separately validated strict aperture-endpoint signs. That parent archive is **unchanged** and SHA-locked to
`0eec91a8e531516529a58cf811685581233aba6d5bc8150c9897b50de88ae651`.

The quantity here is **not** the original clipped March shadow projection or the Einstein residual:

\[
D_i(A)=\sum_{j=0}^{179}w_{ij}^{\rm stored}M_{*,i}'(r_{ij})\phi_A(r_{ij})
      -\int_{r_{i,0}}^{r_{i,179}}M_{*,i}'(r)\phi_A(r)\,dr,
\quad \phi_A(r)=\begin{cases}1,&r\le A\\1-\sqrt{1-A^2/r^2},&r>A.\end{cases}
\]

The new investigation was motivated by a **nonproof** dense numerical scan showing that the prior sparse witness sets had not sampled the near-knot positive lobes in J0822, J1021 and J1135. A numerical scan **alone never contributes a certified zero**; it supplied test locations.

## A strict source-dependent extension, reusing the prior Peano budget

No new Bessel values are needed. Exactly three additional rational apertures are selected on the parent source-defined 128-step aperture grids, with the **same** inherited independently audited targeted radial leaves and symmetric \(E_{\rm Peano}\) budgets. The mathematical comparison is bounded as

\[
 Q_\partial(A)-L_{\rm affine}(A)-E_{\rm Peano}
 \le D(A)\le
 Q_\partial(A)-L_{\rm affine}(A)+E_{\rm Peano},
\]

where both \(Q_\partial\) and \(L_{\rm affine}\) are directed interval evaluations at that exact rational aperture. All displayed mass intervals are rounded **outward** to whole solar masses:

| Lens | Source-band grid index | Approx. A (kpc) | New strict D(A) interval (M☉) | Prior minimum → new minimum |
|---|---:|---:|---:|---:|
| J0822+1828 | 25/128 | 2.027058398 | [+63,914,506, +75,972,430] | 1 → 3 |
| J1021+2028 | 33/128 | 1.358125743 | [+4,644,041, +6,662,422] | 1 → 3 |
| J1135+3720 | 29/128 | 3.378623910 | [+129,637,630, +140,315,404] | 1 → 3 |

The **independent** 192-bit exact-Fraction geometric-kernel method encloses each result conservatively, with one solar mass of additional outward slack where required. The second engine does **not** import the 512-bit producer's interval arithmetic, and reassembles the original 180 source-node sum and all refined affine-slope segments from the SHA-locked parent.

For each affected lens the new strictly **positive** node is bracketed by two previously proved strictly **negative** aperture nodes. Consequently there are **two disjoint open sign-change intervals**, one on each side of the new positive node. By continuity of \(D(A)\), each contains **at least one distinct zero**. The prior single additional sign reversal elsewhere in the band remains. Three affected lenses therefore have *at least three* zeros each, compared with *at least one* in the earlier receipt.

The other three lens bounds remain unchanged: J0915 ≥2, J0930 ≥3, J1111 ≥2. Hence the new six-lens minimum is

\[
(3,2,3,3,2,3),\qquad \sum_i N_i\ge16.
\]

This is a **lower bound** on the sum of counts across **six different functions**, not one function with sixteen roots, not a count of Einstein radii, and not a claim of exactly sixteen.

## Why upper-count exclusion is separate

The derivative of the original frozen analytic-derivative sum is, for an aperture different from all stored source-node radii,

\[
Q_\partial'(A)= \sum_{r_j>A} w_j M_*'(r_j)
              \frac{A}{r_j\sqrt{r_j^2-A^2}}.
\]

The continuous derivative is the integrable transformed expression

\[
P_*'(A)=A\int_{\max(r_{\min},A)}^{r_{\max}}
           \frac{M_*'(r)}{r\sqrt{r^2-A^2}}\,dr
\quad (0<A<r_{\max}).
\]

At any frozen positive-weight source radius \(r_j\), the associated term of \(Q_\partial'(A)\) diverges as \(A\uparrow r_j\) and vanishes for \(A>r_j\), while \(Q_\partial\) and \(D\) themselves are continuous. Thus **a global \(C^1\) derivative or unsplit interval-Newton assumption is invalid**. A future exact upper count needs interval exclusion and piecewise derivative-sign verification **split at every original radial knot**, with one-sided handling near those knots and a certified bound on \(P_*'(A)\).

A 1,001-point SciPy diagnostic scan suggests exactly 3,2,3,3,2,3 ordinary crossings in the six bands, but it is **NONPROOF** and makes no upper-count claim; the present receipt proves only the above minima.

## Independent evidence, limitations and next gate

The protected release includes the unchanged prior candidate, exact rational new selected apertures, producer 512-bit signed values, independent 192-bit source-bound comparison, a claim guard rejecting mutations, and source-free unit tests. **No original March source parameter or stored array has been modified.** Its public GitHub component contains only scripts/tests/docs/manifest, not protected arrays or numerical receipts.

**Not established:** exactly 16 zeros, sign or monotonicity of \(D'\) throughout any complete aperture band, smooth-H Einstein-root uniqueness, physical stress-energy density, Native ESET action/Weyl solution, blinded D3/D4 empirical validation, a CDM-free cosmological provider, or original arbitrary-radius March floating accuracy. `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`; keep draft/unmerged and do not promote Theory-State.
