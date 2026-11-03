# Original March180 Bessel/gate/floating mass / source gradient split

**Source-audited mathematical candidate. Historical six-lens data only. Not a physical provider or validation.**

- `upstream_float_split.py`: SHA-checks original parent/source, dynamically loads the **frozen original** baryonic/dmalane/shadow-density modules in an isolated temporary directory and reexecutes the original binary64 180-node `gbar`, radius gate `epsilon`, mass difference, `np.gradient` and clipped density. Requires exact 180/180 bitwise density match per lens. Saves six protected binary64 float-mass arrays. Uses inherited 512-bit Bessel and distinct 608-bit interval helpers at 24 crossing-neighborhood nodes, and inherited **all-node** stencil certificates to split fixed-input arithmetic errors.
- `independent_stencil_check.py`: Does *not* import the producer, original Python source, NumPy or SciPy. Reads only the binary64 mass arrays and source-node inputs under protected SHA, manually decodes their IEEE754 representations, computes the exact-rational nonuniform stencil by a separate algebraic formula, and recomputes the six all-aperture `E_round` bounds and inherited prior bounds.
- `adversarial_qa.py`: Fail-closed source, identity, dimension, bound and science-claim mutations.
- `verify_release.py`: Sealed ZIP/member SHA and CRC, independent checker and QA. Optional `--full` original-function/source math replay, which requires NumPy/SciPy compatible with the saved runtime and recomputes protected binary64 masses.
- `tests/historical/test_hist001d_upstream_bessel_mass_sourcefree.py`: synthetic pure arithmetic tests; never opens protected data.

See `docs/HIST001D_ORIGINAL_BESSEL_MASS_GRADIENT_K180_FLOAT_SPLIT_SCOPE.md` for the mathematics and the strict nonclaims.

Clean extracted release:

```bash
python reference/hist001d_upstream_bessel_candidate/verify_release.py --root .
python -m pytest -q tests/historical/test_hist001d_upstream_bessel_mass_sourcefree.py
python reference/hist001d_upstream_bessel_candidate/verify_release.py --root . --full
```

The original 46+3 source and binary64 arrays remain **only in the protected ZIP**; the public PR adds no protected inputs or mathematical result JSON.
