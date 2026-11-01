# HIST-001D/D2e-G4b.1 — exact-rational boundary bridge (STACKED DRAFT)

**Status: purely mathematical helper.** This increment depends on G4b.0 draft PR #36. It is not historical source reexecution, actual finite-lens root exclusion, root existence/count/uniqueness, observational validation, or physical Weyl lensing.

## Two source-identified numerical gaps

**Inward float rounding:** prior G1/G2b/D2e-F _fraction coerces every argument through float(), including exact rational radius cells and rigorously outward-printed Decimal mass box endpoints. Round-to-nearest can raise a lower or lower an upper bound. The new exact_number parses Decimal strings as Fraction(Decimal(text)), retains exact integers, and treats binary64 floats as their exact dyadic rationals. Outward source-radial endpoint conversions use nextafter and verify real-rational inclusion after rounding. No old kernel is modified by this draft.

**Positive Hernquist first-boundary projected mass:** the complete source radius domain includes R0=Fraction.from_float(0.02). Existing certified_hernquist_point rejects R=R0. Finite Hernquist cylindrical mass is strictly positive there because shells with r>R0 project into the aperture R0. For frozen M>0,a>0,

B(R0)=2*M*a * integral_[R0,120] (r-sqrt(r*r-R0*R0))/(r+a)^3 dr.

On [R0,2R0] the projection factor is at least R0/4 and the denominator at most (2R0+a)^3. Therefore

B(R0) >= M*a*R0^2/[2*(2*R0+a)^3] > 0.

This exact strictly positive LOWER certificate is intentionally conservative and cannot alone establish a residual sign. A separately certified upper mass bound at the cell's upper endpoint is still needed.

## Pure mathematical helper contracts

- Exact rational decimal intervals, exact integers and outward binary64 real-source cell cover.
- Positive finite Hernquist projected mass at source R0.
- Independent positive baryonic mass-box four-corner q_eff extrema, with exactly frozen source binary64 q-floor 0.001 and q clipping.
- Rational integer-isqrt bounds and outward 120-kpc capped aperture band.
- Malformed/inverted/negative/oversized proof inputs are rejected.
- Physical-provider, root and empirical claims remain explicitly false.

Nine local pure tests passed. GitHub CI remains a separate gate. This draft intentionally adds no actual source-matching report/receipt stage; future source-locked mass/shadow/Sigma integration must add independent evidentiary receipts and adversarial controls before claiming any lens residual bound.

## Predecessors and next gates

G4b.0 exact source-partition PR #36 must separately complete repaired exact-head six-platform CI and merge/postmerge archive verification before this dependent stacked PR is rebased or merged. G4a remains the controlling verified release until G4b.0 clears its archive and Drive readback.

G4b.1 source integration must use independently sound full real-radius Hernquist/disk mathematical mass boxes matching frozen D2d finite-proxy scalars; the matching G4a mathematical critical density; SHA-pinned nonnegative 11520-node nodal shadow input; certified exact q/aperture bounds; D2e-F shadow enclosures; and the G4b.0 conditional H residual inclusion. Every unexcluded root-containing interval stays UNRESOLVED, including tangencies, endpoints and any resource-limited cell.

Original March 46+3 source SHA fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a. Original fitted 180/120 six-of-six and independent finite D2d three-of-six are distinct; no source all-R implementation accuracy, outer physical shadow matter, independent blinded holdout, physical Weyl, contemporary Native ESET v1.7.2 field transport or empirical validation follows.
