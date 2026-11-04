# HIST-001D knot-aware exact 16 — source-only review candidate

This directory contains reusable mathematical interval arithmetic, source-bound
producer code and independent verification for exactly **3,2,3,3,2,3** zeros
of six **separate** selected-M* quadrature remainder functions `D(A)` on their
specified original crossing-aperture bands. It does not contain the frozen
March 180-node data, previous Bessel/Peano evidence, or the six candidate
result receipts. Those are in the external protected release.

The proof separates every aperture band at the original radial knots: 16
knot-free root brackets with strict endpoint signs and strict monotonicity,
plus 149 strict-sign exclusion panels for the complete complement. An
independent 128-bit fixed-point arithmetic engine reconstructs all 86 derivative
panels and the full coverage without importing the producer's fixed-point
arithmetic. A structural guard rejects 40 invalid/falsely promoted outcomes.

The function is specifically
`Q_original_weights_of_sampled_selected_Mstar_prime(A) - P_selected_Mstar(A)`.
It is **not** the original clipped shadow-density K180 sum, any Einstein
residual, an independently admitted physical source, or a Weyl-lensing solution.
No outside-band zero count or empirical validation is established.

For protected replay, see the canonical Drive archive and run `verify_release.py`
within the extracted root; `--quick` checks saved evidence, `--independent`
reconstructs every source-locked inequality, and `--full` additionally
reruns the expensive input/producer stages. Public CI only uses the separately
source-free `tests/historical/test_hist001d_knot_exact_count_source_free.py`.
