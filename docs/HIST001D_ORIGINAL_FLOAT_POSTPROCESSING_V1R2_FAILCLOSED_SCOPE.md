# HIST-001D — March 180-node original final IEEE-754 postprocessing, v1r2 integrity repair

**8 November 2026 — conditional mathematical/source reproducibility candidate — NONPROMOTING.**

## Identical original mathematical object and historical data

This release **does not change** the six fitted development lenses, the original March `reg_v2` binary64 sampled final H operation, its first sampled positive-to-negative crossing / linear interpolant, the finite off-grid PL mathematical comparator from upstream PR #55, or any original 46+3 source file. The original protected saturation parent ZIP (SHA256 `99bb1678859fbec1d0854ef30e4bdfd6f3e3acc68860270d16a3571a8fb4f2ce`) and full-H mathematical parent (SHA256 `02c93bed1c2d5338972c192013270921264d00320b41d8d17ad44769b47dd7d6`) are retained **byte-for-byte**. All three v1r1 numerical result records are likewise retained byte-for-byte:

- original sampled float postprocessing receipt `00ee91c9d018610d0b4cbbf08a1143ad562b3209961639ebb62a6910d60fd3ee`
- independent NumPy/int-sqrt check `bd404058f0429ab363e4c7a529a13f3f742bca0e5cbc8a82b1700cb4887b6a35`
- 22-case historical adversarial receipt `e4127f04bf9a1f40a1d880ec3ebb7a4972e50e8816d5a2f310fdf0aed067a04a`

## Two fail-open software defects and source provenance

1. `float_bridge.read_locked` validated the order of four six-lens input groups using four Python `assert` statements. Under `-O/-OO`, those checks are omitted, allowing mismatched or shortened in-memory metadata to flow into `zip(...)`. Four unconditional, explicit label/order/length guards now reject incomplete, extra, reordered and duplicated source rows regardless of optimization mode.
2. `independent_float_check.floor_sqrt_different` verified its claimed outward exact integer square-root enclosure with an `assert`. An intentionally corrupted integer square-root result is silently accepted under `-OO` in the historical implementation. It now raises `ValueError` for an invalid enclosure under every optimization mode.
3. The inherited finite-H helper source bundled by the historical PR #56 archive also contained a proof-related `assert`. The v1r2 protected package uses the independently repaired PR #55 helper, replacing only that proof guard with an unconditional exception; the **pinned parent archive remains the original** and the math results remain unchanged.
4. `attested_replay_v1r2.py` distinguishes externally pinned whole-archive identity, ZIP CRC/member SHA integrity, executed local code identity and source-dependent replay. It requires an SHA-256 supplied **out of band** (not learned from the archive), rejects modified extracted executable sources, and re-executes the original-source 1080-sample producer plus the independent NumPy/int-sqrt verifier and 22 mutation checks in a freshly extracted attested process. Any missing evidence, changed source, invalid result or insufficient execution budget gives `UNRESOLVED` exit code 2. Its success confirms those narrowly identified historical operations and does not certify upstream NumPy/scipy Bessel / density-gradient errors.

## Machine replay

```bash
python -m pytest -q tests/historical/test_hist001d_original_float_bridge_source_free.py tests/historical/test_hist001d_original_float_bridge_v1r2_failclosed.py
python -OO reference/hist001d_original_float_bridge_candidate/attested_replay_v1r2.py \
  --archive /protected/HIST001D_MARCH180_ORIGINAL_FLOAT_POSTPROCESSING_v1r2.zip \
  --expected-sha256 YOUR_INDEPENDENTLY_RECORDED_WHOLE_ZIP_SHA256 \
  --extracted-root /clean/verified/extraction \
  --budget-seconds 240
```

The archive verifier requires the retained original full-H and saturation archives and their untouched source-parent hierarchy, but **not** any public GitHub copy of protected original arrays.

## Scientific claim firewall

The original reported radius is a sampled-residual **linear-interpolation** output, not an arbitrary-real-radius source-evaluated root. The finite PL comparator and selected smooth `Mstar` continue to be different mathematical objects. The precise 1080/1080 reproduced original binary64 H nodes, six sampled root values, original historical strict CSV portability and finite-math discrepancies are **historical fitted-source replay**, not a new blind observational test, physical density/action/Weyl metric, original off-grid floating accuracy proof, or no-CDM result. `physical_provider_admitted=false`; `empirical_validation=NOT_ESTABLISHED`; `scientific_authority_promoted=false`. GitHub `main` and Native ESET v1.7.2/Theory-State v0.16.39 scientific claims are unchanged.

**External mathematical proof/source review and publication/license audit remain open. Do not merge from the success of a source-only test alone.**
