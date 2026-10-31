# HIST-001D/D2e-G4b.0 — original finite-proxy exact source-grid partition (DRAFT)

This increment freezes **only the full source-radius domain and adaptive partition policy** for the next G4b all-real-R mathematical root investigation. It does not evaluate an actual historical residual, discover a root, prove root existence or uniqueness, certify original floating source all-radius errors, validate Weyl lensing, or promote any physical provider.

## Frozen target and provenance

- Original March source SHA-256 `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a` (46 files + 3 archived negative records), read-only.
- Six **historically fitted** SWELLS Set A development lenses in frozen source order, no new holdout.
- **Distinct numerical model:** D2d/D2e 11,520-node finite structured-shadow proxy; neither original fitted March **180-radial/120-angle** numerical algorithm nor physically sourced Native v1.7.2 model. Original fitted March 6/6 vs independent finite D2d 3/6 unchanged.
- Predecessor G4a mathematical FlatLCDM Sigma_crit source-output bridge is merged as PR #34 SHA `4af22d7b1923289983d2898a9cd199161dd3b144`, but G4a postmerge release and Drive audit remain prerequisite **before G4b promotion**.

The frozen `registry/hist001d_g4b0_root_partition_v1.json` pins original source bytes, D2e root-label source, G4a runner bytes, the six immutable lens IDs and the complete partition policy. The D2d numeric roots appear only as **provenance labels** and have no effect on initial partition selection.

## Original exact binary64 source domain and deterministic cover

The mathematical domain endpoints are the exact dyadic representations of the original March floats:

`R_min = Fraction.from_float(0.02)` and `R_max = Fraction.from_float(120.0)`.

Because the actual binary64 value of 0.02 is not the exact real fraction 1/50, **do not silently replace its rational value**. The initial domain is partitioned into **64 uniform exact-rational adjacent cells**. The initial cell provenance is `00:, 01:, ..., 63:`. An optional dyadic refinement appends a `0` (lower half) or `1` (upper half), always at exact rational midpoints. The maximum is **8 bits of refinement per initial cell**, for a maximum budget of **16,384 leaves across the full domain**. Any unmatched leaf path, gap, overlap, duplicate, wrong order, out-of-domain radius, depth overflow or unsupported budget fails closed.

The pure `assert_complete_cover` checks exact adjacency and full coverage. It does **not** imply that a sign has been established anywhere.

## Conditional signed residual mathematics (synthetic primitive, not yet sourced)

`conditional_H_box` implements a purely algebraic enclosure over a rational radius cell for

`H(R) = B(R) + D(R) + S(A(R)) - π Σcrit R².`

For **separately sound** positive mathematical mass intervals `B in [b_l,b_h], D in [d_l,d_h]`, nonnegative finite-shadow interval `S in [s_l,s_h]`, and positive mathematical critical-density interval `Σ in [σ_l,σ_h]`, using the audited rational real-π bounds `[π_l,π_h]`:

`H_lower = b_l + d_l + s_l - π_h σ_h R_high²`,

`H_upper = b_h + d_h + s_h - π_l σ_l R_low²`.

If `H_lower > 0` or `H_upper < 0` the cell has a rigorous sign **conditional on the externally supplied boxes really enclosing the matching mathematical functions for all R in the cell**. If zero remains in the interval the result is **UNRESOLVED**. The helper **does not certify its input mass/shadow/sigma intervals, source numerical error, continuity, existence, tangencies or uniqueness**. This target treats π as mathematical real π; original floating source `np.pi` is a different numerical identity.

G4b.0 does **not** plug source baryonic numerics or residuals into this primitive; it creates the deterministic audit and tests the conditional algebra on synthetic data only.

## Source reexecution and receipt integrity

`tools/hist001d_d2e_g4b0_root_partition.py` checks the frozen 46+3 original source, SHA-pinned G4a/D2e prerequisites, six historical fitted lens IDs and root-label reference constants; builds the 64-cell exact cover per lens; writes an immutable canonical JSON report and receipt with report SHA-256 and sidecar. A fresh independent CLI process can regenerate all registered cells. Adversarial tests deny changed input registry, mutated source, dropped intervals, incorrectly promoted scientific claims, unexpected receipt members and self-rehashed output forgeries.

**Proposed CI:** Ubuntu/Windows x Python 3.10,3.12,3.13, all earlier source replay stages, new G4b.0 source-input partition reexecution, manifest/packaging checks. No claims of actual historical root isolation can follow from a green CI.

## Next engineering increments

G4b.1 must source-lock actual mathematical G1/G2b positive all-real-R mass bands, D2e-F finite nodal shadow aperture envelopes and G4a mathematical Sigma bounds, prove their sound **matching input identities and clipping conventions** across each real radius cell, then invoke the conditional H-box with explicit source-verified input certificates.

G4b.2 must implement bounded complete-domain branch-and-bound with original frozen nodal density source, unresolved leaf reporting, full boundary coverage and explicit tangent-root detection. Neither positive/negative sampled signs nor source's first-crossing estimator is a uniqueness theorem. Only a separately proved sign enclosure or analytic derivative/root-count bound can upgrade an unresolved cell; resource exhaustion must stay visible.

All physical mass outside [0.02,120] kpc, original March all-R source implementation error, D3 covariance, D4 blind holdout, D5 same-source Weyl metric, current Native ESET action/field transport and empirical validation remain open. Parent issues #19/#27 and [G4b issue #35](https://github.com/HMarcusWH/native-eset/issues/35) govern those boundaries.
