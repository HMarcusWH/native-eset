# HIST-001D/D2e — original March 180-node rational Bessel / K180 audit

**Status:** NONPROMOTING mathematical candidate for source and code review. 2 November 2026. No physical provider or empirical claim is changed.

## Frozen model identity

The external, separately SHA-pinned original March `reg_v2` source provides six lenses' **180** binary64 source radii, quadrature weights, clipped shadow-density samples, source baryon/disk/critical-target arrays, and original 46-source-file + three-negative-control integrity records. The mathematical comparison evaluates the selected smooth historical acceleration-equivalent shadow-mass formula at those **same** radii. The later D2d 11,520-node shadow-density interpolant is **not** used or substituted. GitHub contains source-only review code, no frozen source ZIPs, numerical arrays or proof JSON.

## Mathematical comparison (fixed inputs only)

For each original source radius `r_j`, the stored reconstructed mass gradient is

`D_stored,j = C4pi_stored * r_j**2 * rho_shadow_stored,j`.

The two source-independent computational implementations bound the ideal nonuniform three-point derivative of the selected smooth mass `Msh*` at the original nodes, and bound `Msh*'(r_j)` independently. Both treat all archived binary64 inputs as exact rational numbers. The largest producer a-posteriori **stored-versus-ideal-stencil** error ceiling is below **1 M_sun/kpc** across all **1,080** nodes; this is not a blanket software-float error theorem.

For the original 180-node finite-cylinder projection kernel, `phi(A,r)=k(A,r)/r**2` obeys `0<=phi<=1`. Positive original source quadrature weights allow propagation of each exact source-versus-smooth sampled derivative interval into a rigorously conservative **all-real-aperture difference between two frozen 180-node mathematical K180 projections**. The tighter crossing-cell variant uses original baryon-axis ratios and original final-H sampled sign-change cell endpoints to bound the circularized aperture before applying `phi`; an independent 184-bit sqrt guard checks the producer's 120-bit bound.

| Historical fitted development lens | Max node stencil upper, M_sun/kpc | Global all-real K180 difference upper, M_sun | Original crossing-cell K180 upper, M_sun |
|---|---:|---:|---:|
| J0822+1828 | 0.061977 | 3,142,927,254 | 1,074,673,662 |
| J0915+4211 | 0.164782 | 4,045,230,322 | 1,168,557,575 |
| J0930+2855 | 0.027883 | 6,222,203,764 | 1,943,508,289 |
| J1021+2028 | 0.018732 | 840,347,482 | 185,204,566 |
| J1111+2234 | 0.049255 | 1,151,993,991 | 189,475,713 |
| J1135+3720 | 0.041915 | 1,516,195,026 | 582,941,267 |

Displayed decimals are integer-micro-M_sun/kpc upper ceilings; controlling proofs and exact per-node intervals are in the protected full-data archive. These remain very conservative relative to a physically useful full residual-root tolerance.

## Replay and independent checks

Source-only GitHub regression: `python -m pytest -q tests/historical/test_hist001d_all180_bessel_source_free.py` (28 synthetic checks in the archived candidate, not data-dependent replay). The proof scripts in `reference/hist001d_all180_bessel_candidate/` must retain their archived bytes for review, and intentionally cannot run their full source-dependent replay without the **external** archive's original protected inputs.

Full independently inspectable candidate ZIP: SHA256 `2e3c13ba68bbed98ef2c529a2e331b15c666d8927da22daf1be78d33a79f6391`, 1,266,963 bytes, 28 ZIP members / 27 SHA-manifested files. It includes the original source-bound parent ZIP with expected SHA256 `3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18`; nested 46+3 original source composite SHA256 `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`. Verify `python verify_archive.py` and then replay all six producer and six separately implemented independent-verifier stages, aggregate, crossing bands, and adversarial controls. Every actual stage must reproduce the exact archive's SHA-locked result bytes. **Repository CI cannot claim it has rerun source-private data.**

## Requirements before release

1. Independently review rational Bessel/log/Euler/real-power enclosures at small and large arguments and the nonuniform finite-difference algebra.
2. Verify the six frozen source identities, all signed per-node bounds, positive K180 weights, and complete crossing-cell aperture guards using the external archived input ZIP.
3. Verify exact PR-head CI (Ubuntu/Windows x Python 3.10, 3.12, 3.13), Git path inventory, SHA manifest and absence of source data in the public PR. Keep this PR draft until separately authorized.
4. If code is eventually merged, require its own postmerge exact-main CI, six artifact audit and authenticated Drive byte readback before changing the controlling software release.

**Stop conditions:** This does **not** establish an original March 180x120 true off-grid error or continuous-source root-count theorem, the original SciPy/NumPy arbitrary-input roundoff, original K180 radial quadrature against a smooth physical density, D120 omitted-angle continuum error, full q/A/target/derivative/variation error, physical same-solution Weyl/Native v1.7.2 equivalence, D3 covariance, D4 disjoint blinded validation or a no-CDM cosmology. Historical fitted development 6/6 and independently integrated D2d numerical 3/6 are distinct model identities. `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`; canonical Theory-State v0.16.39 and G4b.1b controlling software release unchanged.

**Next scientific gate:** Define the continuous-source projection and control K180-versus-that-target quadrature, special-function roundoff/clipping and the combined H-derivative/variation error. If current bounds cannot isolate an original-source root, preserve the failure and source identity.
