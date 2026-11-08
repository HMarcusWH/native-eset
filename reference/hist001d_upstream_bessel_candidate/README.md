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

## 8 November 2026 — v1r2 authenticated replay

The legacy `verify_release.py --root . --full` call is intentionally **disabled**
without an independent release ZIP SHA. Its direct local module imports were
vulnerable to a replaced independent checker plus local SHA-manifest update.
Use the source-only `attested_replay_v1r2.py` instead:

```bash
python -OO reference/hist001d_upstream_bessel_candidate/attested_replay_v1r2.py \
  --archive /secure/HIST001D_MARCH180_BESSEL_FLOAT_MASS_GRADIENT_K180_v1r2.zip \
  --expected-sha256 <independently-authenticated-whole-ZIP-SHA>
```

The replay preserves all six exact frozen binary64 source-density and
Bessel mass/stencil results under the stated runtime and never promotes the
selected mathematical shadow mass to physical lensing. Protected data and
saved results remain outside public GitHub.
