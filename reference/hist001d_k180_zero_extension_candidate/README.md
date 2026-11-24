# Supplemental selected-M* quadrature zero existence witnesses

**Historical source-conditional mathematics only. Draft/nonpromoting.**

This is a source-only checker against the immutable protected PR #63 archive. It contributes exactly three additional strict positive aperture values, turning the prior six-lens minimum `(1,2,3,1,2,1)` into `(3,2,3,3,2,3)`, hence **at least 16 distinct zeros total across six functions**. It proves neither exactly 16 nor any physical or Einstein root.

## Verification

Source-free: `python -m pytest -q tests/historical/test_hist001d_zero_extension_source_free.py`.

To verify a protected release containing `inputs/targeted_parent_v1.zip`, run:

```text
python reference/hist001d_k180_zero_extension_candidate/verify_release.py
python reference/hist001d_k180_zero_extension_candidate/verify_release.py --full
python reference/hist001d_k180_zero_extension_candidate/adversarial_extra.py
```

`--full` uses a temporary clean extraction of the SHA-locked parent and reruns the 512-bit first source and the separate 192-bit Fraction checker. Neither reruns the previous 128 new Bessel midpoint evaluations: those are already protected and independently checked by PR #63.

The original March arrays and all signed result receipts remain in a protected archive and must not be committed to public GitHub. The parent archive is not a physical stress-energy or Weyl-lensing source. `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`.
