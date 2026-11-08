# HIST-001D — D120 seam verification hardening (v1r2, 2026-11-08)

**NONPROMOTING · original frozen March 180×120 historical fitted source only.**

## Failure demonstrated in the v1r1 protected verifier

The original `verify_release.py --full` checks file hashes against a local
`MANIFEST_SHA256.json`, then executes the local checkout's `verify_seam.py`.
An attacker who replaces the checker and *also* updates the unchecked local
manifest can make the original full-replay wrapper issue a misleading PASS.
In the recorded synthetic attack, the standalone independent proof invocation
was replaced with a no-op while the original source replay and 30-case QA
were untouched; the original wrapper exited 0 and printed `D120_SEAM_CLEAN_REPLAY_OK`.
The original protected ZIP bytes and saved mathematical receipts were NOT
altered by this attack. It demonstrates an executable-provenance vulnerability,
not a counterexample to the saved six-lens seam theorem.

## v1r2 repair and explicit gate

`attested_replay_v1r2.py` requires a **whole ZIP SHA-256 from outside the release**
and verifies the ZIP itself (exact member set, path safety, duplicate paths,
CRC, file hashes and no symlinks), immutable historical parent ZIP digests,
original source composite and separate numerical receipts. It also verifies
that the entire optional local extraction tree matches the authenticated ZIP,
including the actual independent checker, before any runtime claim.

It then creates a fresh private extraction, rechecks every member and executes
that authenticated source with isolated Python entrypoints, replays D120, S,
H at the original 6×180 binary64 nodes, the six archived first sampled roots,
the independent positive/reciprocal exponential bounds and the 30-case
adversarial receipt. The archived JSON outputs must be byte-identical.
The inherited `full_h_finite_source.py` and `float_bridge.py` helpers use the
**repaired PR55/PR56** guard implementations, but the original protected
saturation/full-H parent ZIPs and original six-lens mathematical/numerical
result receipts are preserved byte-identically.

The old `verify_release.py --full` **without** an external archive/hash pin now
fails closed with `UNRESOLVED`/exit 2. Full replay command:

```bash
python -OO reference/hist001d_d120_seam_candidate/attested_replay_v1r2.py \
  --archive /protected/HIST001D_D120_v1r2.zip \
  --expected-sha256 <independently-attested-64-character-hash> \
  --extracted-root /path/to/candidate/extraction
```

The checker attests a mathematical **alternative fixed-node seam stencil**
under the stored source and tested NumPy environment, *not* the continuous
physical full-azimuth integral, a rigorous interval bound on the counterfactual
floating root-shift, the original floating off-grid H, or a Native ESET
v1.7.2 physical Weyl provider. `physical_provider_admitted=false`,
`empirical_validation=NOT_ESTABLISHED`, and no Theory-State authority promotion.
Source rights/licensing and independent mathematical review remain OPEN.
