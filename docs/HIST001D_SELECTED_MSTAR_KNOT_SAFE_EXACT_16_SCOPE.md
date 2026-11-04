# HIST-001D — Knot-safe exact zero count for six selected mathematical quadrature remainders

**Candidate source-conditional mathematical certificate · 4 November 2026 · NONPROMOTING.**

## Explicit objects and provenance

For each of the six original historical March lens input sets, retain the authenticated frozen 180 radial nodes, their binary64 trapezoid weights, the mathematical acceleration-equivalent smooth mass law selected in the earlier HIST-001D certificates, and the exact historical six aperture bands. Define

\[
D_i(A) = Q_{\partial M,i}(A)-P_{*,i}(A),\quad
Q_{\partial M,i}(A)=\sum_{j=0}^{179}w_{ij}^{\mathrm{stored}} M_{*,i}'(r_{ij})\phi_A(r_{ij}),\quad
P_{*,i}(A)=\int_{r_{i,\min}}^{r_{i,\max}}M_{*,i}'(r)\phi_A(r)\,dr.
\]

Here \(\phi_A(r)=1\) for \(r\le A\), and \(1-\sqrt{1-A^2/r^2}\) otherwise. The original clipped-density K180 sum \(Q_{\rm src}\) is **not** \(Q_{\partial M}\). These are mathematical *radial projection remainder* zeros, **not** Einstein roots, physical lensing predictions or claims about the original arbitrary-radius floating implementation.

## Why knot-aware analysis is essential

The frozen-node kernel contribution has a one-sided square-root derivative singularity as \(A\uparrow r_j\) from below. Thus \(D\) is continuous, but global C1 derivative-based zero counting across the source radii is invalid. The six bands were partitioned **at every original radial knot**. The proof divides the resulting intervals into precisely:

- **16 disjoint local root brackets**, each with a source-locked strict sign change and a strictly one-sided derivative throughout its knot-free interior; hence one and only one zero per bracket.
- **All complementary gap intervals**, covered by strict-sign bounds from monotone positive cylinder projections, direct derivative monotonicity, or two-endpoint derivative envelopes. Every band endpoint and radial knot belongs to covered intervals, and each root bracket/exclusion is source-conditional.

For \(P_*'(A)\), the derivative-kernel primitive is enclosed with an arctangent square-root identity and radial-panel mass-slope/Peano bounds. Independent 128-bit integer interval arithmetic uses its own sqrt, atan and cylinder-cell implementations and does not import the producer's fixed-point arithmetic or endpoint routines. The prior 512-bit real-integral Bessel and 1,344 real-radius \(M_*'\) enclosures remain explicit upstream dependencies, not claims of an independently admitted physical source.

| Historical lens | Exactly \(D_i\)-zeros in the stated A band | Root derivative panels | Strict-sign exclusion panels | Interior original knots |
|---|---:|---:|---:|---:|
| J0822+1828 | 3 | 11 | 24 | 2 |
| J0915+4211 | 2 | 10 | 24 | 1 |
| J0930+2855 | 3 | 3 | 15 | 1 |
| J1021+2028 | 3 | 50 | 41 | 2 |
| J1111+2234 | 2 | 7 | 22 | 1 |
| J1135+3720 | 3 | 5 | 23 | 2 |
| **TOTAL** | **16** | **86** | **149** | **9** |

These counts refer to the **six original specified aperture bands**, not all positive apertures or the universe of possible mass continuations. All 86 derivative panels and 149 complementary exclusions were verified from source-locked serialized interval inputs by an independent 128-bit implementation. No UNKNOWN intervals remain in the six stated bands; outside-band zeros remain uncounted.

## Audit boundary

The receipt asserts **exactly 16 across six separate mathematical functions on six specified bands**, conditional on the inherited selected source, interval Bessel/derivative enclosures, frozen node identities and the independently verified interval algebra. It does not assert exactly 16 Einstein roots; uniqueness of the smooth full-H residual; any original physical continuous shadow density; Weyl metric or same-action source; native ESET v1.7.2 provider; D3/D4 observational validation; or no-particle-CDM cosmology. `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`, `scientific_authority_promoted=false`. No controlling Theory-State graph or main release changes.

## Source identity and reproducibility

Original March 46+3 frozen source composite: `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`. The upstream protected 16-existence parent: `23251d6c5a153e8cb149143f7fcf25f02c21097e6f625b3c46fdb9645fef96e1`. Previous protected cancellation-aware parent: `639ee5973a59a63c14e63d59522c03d659de10dd6d7c195586de13e8186159c9`.

The archive includes the **protected** prior parents and serialized source-node / mass enclosures; those data must not enter GitHub. Run `python reference/hist001d_k180_exact_count_candidate/verify_release.py --quick` in an isolated clean extraction to audit the SHA manifest, every geometric/claim constraint and all 40 negative controls. Run `--independent` to re-execute the six distinct 128-bit interval checkers. Run `--full` to re-execute the source-dependent input/unique-root/gap-exclusion producers as well; this is the expensive operation. Verify the archive SHA externally, and insist on exact-head CI, source/license security review and external mathematical review before considering any authority promotion.
