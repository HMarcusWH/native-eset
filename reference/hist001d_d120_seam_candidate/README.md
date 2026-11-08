# HIST-001D original D120 119-segment angular seam audit

**DRAFT / mathematical source audit / NONPROMOTING.** The original March
120 sampled angular nodes and 119 trapezoid segments are preserved, including
the original source-frozen circularization and stored source radii. The proposed
periodic seam is a *different fixed-sample comparison stencil*, not the source's
original result, a certified full-azimuth continuum integral or a physical
provider/observational validation.

- `seam_math.py`: exact-rational interval constructions from two different
  exponential enclosures; no new physics parameters.
- `source_seam_replay.py`: frozen historical D120, circularized S and H sampled
  array replay; no refitting or original March source mutation.
- `verify_seam.py`: independent positive-series/reciprocal bounds and source
  input/receipt checks. Its exact executed bytes must be authenticated.
- `adversarial_seam.py`: 30 historical mutation/overclaim rejections.
- `attested_replay_v1r2.py`: required externally pinned whole-ZIP,
  executable-source-attested clean replay (recommended only source-bound entry).
- `verify_release.py`: deprecated legacy entrypoint now delegates to the
  fail-closed v1r2 attestor; no unpinned full PASS allowed.
- `tests/historical/test_hist001d_d120_v1r2_attestation.py`: source-free
  optimized-Python/provenance/negative-control regression tests.

Execute protected replay only after obtaining the protected release from
**authorized original source**, with its SHA from a separate trusted record:

```bash
python -OO reference/hist001d_d120_seam_candidate/attested_replay_v1r2.py \
  --archive /protected/HIST001D_D120_v1r2.zip \
  --expected-sha256 <independently-known-release-sha256>
```

Both v1r1 results (six-lens seam source JSON and 30-case adversarial JSON) are
immutable and source-dependent. A full replay is not justified by manifest
self-consistency, source-free tests, a new hand-authored hash or a matching
printed label alone. Scientific and publication rights/review gates remain
open; physical provider admission and empirical validation remain blocked.
