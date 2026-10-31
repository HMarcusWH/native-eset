# HIST-001D/D2e-G4b.1a — mathematical analytic-baryon mass intervals on exact real-radius cells

**Stacked draft, not a source-matched root or physics certificate.**

Base: G4b.1 exact-rational boundary PR #37 (head 033b492a5e5a93119cbff97e6dd90bb1b831b31b), which is stacked on unmerged G4b.0 PR #36. Controlling verified historical release remains G4a main 4af22d7b1923289983d2898a9cd199161dd3b144. The original March 46+3 source bytes and all historical fitted values are unchanged.

## Mathematical target and inclusion proof

The input is ONE authenticated G4b.0 dyadic radial cell [l,h] in the exact source interval [Fraction.from_float(0.02), Fraction(120)], plus frozen explicit binary64 bulge/disc masses, scales and axis ratios. The target is the positive mathematical CONTINUUM finite Hernquist bulge cylindrical mass B(R), the positive mathematical CONTINUUM elliptical exponential-disc mass D(R), their mass-weighted clipped q_eff(R), and the implied finite-radius shadow *aperture* A(R). It does not itself evaluate the structured shadow density or model Einstein residual.

For each exact rational source cell, first find binary64 L rounded outward BELOW l and U rounded outward ABOVE h. Check the rational ordering of every endpoint: original source RMIN <= L <= l <= h <= U <= original source RMAX. The earlier rigorous G1/G2 positive-continuum monotonicity theorems imply that mathematical bulge and disk mass at each real R between l and h are bracketed by the G1/G2 certified endpoint intervals evaluated at L and U. Use G1 certified_hernquist_point at L (lower) and U (upper), except at the original RMIN where the predecessor G4b.1 strictly positive finite-shell Hernquist lower lemma replaces the unsupported G1 equality case. Always evaluate the upper G1 certificate at U.

The G2 certified_elliptical_disk_radius_band uses exact stored binary64 scalar parameters and provides a conservative sound all-R analytic disc interval for [L,U]. It is NOT the historical omitted-arc 120-angle numerical implementation, and is less sharp than the independent G2b full-azimuth midpoint proof. G2b intersection is not implemented in this increment.

Read G1/G2 directed Decimal output strings as exact rational Fraction(Decimal(string)) values, preserving strict outward bounds even when two endpoints round to the same binary64 float. Require both lower masses strictly positive. Compute exact frozen mass-weighted q_eff corner bounds using the predecessor G4b.1 q helper, including exact original binary64 q-floor 0.001. Compute the q-dependent [R/sqrt(q)] finite shadow aperture bounds with predecessor outward integer-isqrt and 120-kpc saturation.

Every inclusion is conditional on the already verified G1/G2 mathematical continuum theorems and the explicit frozen parameters. Reporting the engineering target_met flag as FALSE must not invalidate a mathematically SOUND interval; it only denotes proof width. The default valid G1 split budget is 0 for fast conservative certificates; the upper and lower mass bounds may be wide, leaving future model-root cells unresolved.

## Tests, dependencies, and scientific firewall

The mathematical tests exercise four actual certified-kernel real cells (including exact original RMIN, exact RMAX and depth-eight refinement), exact finite positive boundary mass, Decimal sub-binary64-ULP intervals with monkeypatched outputs, malformed input, nonpositive G2 box and proof-budget refusal. Fourteen local interface/contract checks ran with explicitly identified **test-only stubs** for the historical G1/G2 kernels; those are NOT mathematical or source CI evidence. Full exact-head GitHub CI against the real frozen kernels is mandatory.

This draft does NOT import or certify the original 11,520-node piecewise-linear source shadow density, does NOT evaluate the G4a Sigma interval or the H(R) root residual, and does NOT certify any source March 180/120 quadrature error at all radii, root existence/count/uniqueness/tangencies, outside-0.02-to-120-kpc physical mass, same-source Weyl metric, Native ESET field transport, observational covariance/holdout or empirical validation. Physical provider admission and canonical Theory-State promotion are FALSE.

PR #36 and PR #37 must clear their exact release/retarget gates before merging this dependent mathematical slice. A later genuine source-matched stage must SHA-pin the actual six development-lens mass/scalar/nodal-density inputs, pair them with sound B/D/S/Sigma envelopes, produce immutable report/receipt/sidecar evidence and keep every inconclusive radial interval UNRESOLVED rather than claiming a root theorem.
