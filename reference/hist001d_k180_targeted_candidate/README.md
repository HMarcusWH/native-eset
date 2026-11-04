# HIST-001D — Targeted inter-node Peano interpolation and six-lens sign-reversal audit

**Candidate source-conditional mathematics. NONPROMOTING.** This repository source is not a physical density or Weyl-lensing provider.

## Protected evidence and source inputs

The source-frozen full parent ZIP is `inputs/cancel_parent_v1.zip` with SHA-256 `639ee5973a59a63c14e63d59522c03d659de10dd6d7c195586de13e8186159c9`. It contains the previous signed affine-mass six-aperture-band candidate and its nested original 46+3 March data/independent real-Bessel certificates. The original 46+3 composite SHA-256 is `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`.

For the separately defined selected mathematical mass `Mstar`, compute `Q_derivative(A)-Pstar(A)`. The `targeted_refine.py` producer subdivides 128 highest-weight radial Peano panels per lens, recalculates new real-integral Bessel intervals at each dyadic midpoint and keeps signed affine-cylinder contributions. `verify_targeted.py` redoes curvature and kernel arithmetic independently in exact Fractions and a separate fixed-point sqrt/atan interval engine; `witness_contract.py`, `adversarial_targeted.py` and source-free tests check claims and tampering.

**Result (source conditional): at least 1,2,3,1,2,1 distinct zeros of this mathematical quadrature-remainder function in the six respective original crossing-aperture bands.** This is **not** an exactly-one/unique zero assertion, and none is an Einstein-radius root or a physical prediction. See `docs/HIST001D_TARGETED_PEANO_SIGN_REVERSALS_SCOPE.md` for exact operators, safe interpretations, and the 10 verified bracket locations.

## Reproducible commands (clean extracted ZIP)

```
python reference/hist001d_k180_targeted_candidate/verify_release.py --quick
python -m pytest -q tests/historical/test_hist001d_targeted_zero_source_free.py
python reference/hist001d_k180_targeted_candidate/adversarial_targeted.py
python reference/hist001d_k180_targeted_candidate/assemble_targeted.py
```

For **data-dependent full proof verification**, run each independently (can run in parallel if each writes separate `--out` file; see code):

```
python reference/hist001d_k180_targeted_candidate/verify_targeted.py --lens 0
# repeat --lens 1,2,3,4,5
```

For **full source-dependent producer replay**, regenerate each existing receipt and compare SHA-256 to the sealed manifest:

```
python reference/hist001d_k180_targeted_candidate/targeted_refine.py --lens 0 --out results/targeted_lens_0.json
# repeat for --lens 1,2,3,4,5
python reference/hist001d_k180_targeted_candidate/verify_release.py --quick
```

The source files and tests alone can execute under the stacked GitHub PR without the private numerical parent. The protected archive carries the parent and receipt bytes for authenticated reexecution; public CI does **not** reexecute private inputs.

## Strict gates

The independent verifier originally had a coverage bookkeeping bug: untouched radial panels' integer keys were accidentally replaced with the previous split's `k`. It is fixed by `canonical_active_leaf_set` and specifically covered by the source-free regression suite. There was no change to the original six producer receipt files.

The entire proof chain is source-conditional on the original stored March radial mesh, frozen source scalars, selected mathematical mass continuation, earlier Bessel-integral interval enclosures, and accurate Peano/kernal variation identities. External mathematical review is still required. No promotion: `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`, no original arbitrary-radius H theorem, no global selected-smooth root uniqueness, and no cosmological provider claim.
