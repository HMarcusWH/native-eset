# Historical March180 inter-node real-integral Bessel mathematical derivative certificate

**Source-only candidate, not a physical or empirical validation.** This branch follows the 1080-point independent Bessel-integral release and extends the selected historical analytic mathematical `M_*` derivative to every real `r` within the 179 original intervals for each of the six lenses.

The producing algorithm reconstructs `F''` from `F,F'` and independent 512-bit integral Bessel endpoints using recurrence/Wronskian relations; it applies complete monotonicity of the Bessel disk kernel to obtain all-real endpoint envelopes. An adaptive exact-rational interval-bound `M_*''` plus nearest-endpoint mean-value inequality certifies positive `M_*'` on dyadic panels. A **separate Fraction arithmetic checker** independently reconstructs `I0,I1` by positive series and recalculates the resulting `F''` and panel inequalities. No protected six-by-180 source arrays belong in GitHub.

Additional `band_bv_producer.py` bounds the original source-geometry trapezoid applied to the **sampled mathematical derivative** against the continuous mathematical radial-cylinder projection, for all `A` in each original crossing-aperture band. Those conservative BV bounds remain too broad for the historical full-H root-gap theorem; do not promote them.

## Protected replay

Inside the protected ZIP, from its clean extraction root:

```bash
python reference/hist001d_k180_inter_node_candidate/inter_node_producer.py --lens 0
# Repeat --lens 1 through --lens 5; the verifier requires all six receipts
python reference/hist001d_k180_inter_node_candidate/verify_inter_node.py
python reference/hist001d_k180_inter_node_candidate/band_bv_producer.py
python reference/hist001d_k180_inter_node_candidate/inter_node_adversarial_qa.py
python -m pytest -q tests/historical/test_hist001d_k180_inter_node_source_free.py
python reference/hist001d_k180_inter_node_candidate/verify_release.py
```

`verify_release.py` has quick hash/receipt mode and optional source-dependent full replay; see its `--help`. The protected archive contains the original source parent and earlier independent integral Bessel parent, SHA-locked; public source imports the preceding public integral implementation but does not import the original March data.

**No original source modification, provider admission, scientific graph promotion or merge.** See `docs/HIST001D_INDEPENDENT_K_BESSEL_REAL_RADIUS_MPRIME_BV_SCOPE.md` for all identities, uncertainties and precise claim ceiling.
