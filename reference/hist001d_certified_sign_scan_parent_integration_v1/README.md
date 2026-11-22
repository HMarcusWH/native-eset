# HIST-001D — Source-bound sign coverage adapter v1 (PUBLIC SOURCE ONLY)

**8 November 2026 · DRAFT · NONPROMOTING.** This public implementation connects the frozen-source exact-real K180/D120 mathematical comparator to the v0.1 proof-linked binary64 sign scanner in draft [PR #66](https://github.com/HMarcusWH/native-eset/pull/66). It imports the *original SHA-verified* two-engine rational interval sign API. It neither embeds original March arrays nor changes the original March 180x120 sampled-root numerical implementation.

## Mathematical object

`H_new(R) = B_180(R) + D_120(R) + S_180(min(120,R/sqrt(q(R)))) - K*R^2` with original exact stored binary64 source scalars, frozen 180-node K180 and missing D120 closing arc retained. This is **not** an independent action-derived physical Weyl model. The six source-exact mathematical roots are each bracketed by adjacent positive binary64 inputs. The all-domain sign classification depends on the separately source-conditional global uniqueness theorem (November 6), not a universal monotonicity assumption.

## Source-bound parents

These full parent release archives are intentionally **not in public GitHub**:

- Source/bracketing (SHA-256 `252d502a1a6607751c5604de221767a10ff6f28e253b0c92d4988773e65ebb29`)
- Global mathematical knot-safe uniqueness (SHA-256 `ee677eea7f2f7bcf5c90347f5c54658988090340d888870c7e60071263693fff`)
- Exact-real two-engine sign API (SHA-256 `963b852b61ce0fbec9fa3f508050dd59b6cf3d0a7098800c28f51d7228cdd33e`)
- Original 180-node source, full-H geometry, massPL, and exhaustive pockets, each with exact hashes in the bracket parent's `PARENT_SHA256.json`.
- Precomputed *fresh independent* global check of all **1400** proof-exclusion leaves / six root-derivative checks, hash pinned to `878823bb4a4e9355802d33f97d47a9472181dc7a6d5f99395dc3f3103b413935`. This is reproducible via the supplied `global_independent_verify_v1.py` and the sealed parents. The entire original global **producer** was not regenerated; the independent checker was.

## Operation

The source-only v0.1 scanner must be importable as `certified_sign_scan`; use `PYTHONPATH` to add both source directories. Set these required absolute local paths in the *protected isolated execution environment*:

- `HIST001D_ENGINE_DIR` — clean extraction of verified root-bracketer full ZIP
- `HIST001D_PARENT_DIR` — six original full ZIPs, named exactly as pinned
- `HIST001D_ROOT_ZIP` — original 53 KB root-bracketing full ZIP
- `HIST001D_GLOBAL_AUDIT` — matching fresh independent global 1400-panel receipt

Run source-only tests (no protected data needed):

```bash
python -m unittest -q test_source_bound_adapter_v1.py  # 18 tests
```

Run protected scanner when all parents are available:

```bash
python /path/to/scanner/scan_cli.py \
  --adapter source_bound_adapter_v1:make_adapter \
  --uniqueness-parent-sha256 ee677eea7f2f7bcf5c90347f5c54658988090340d888870c7e60071263693fff \
  --mode theorem --out /protected/source_bound_coverage.json

python /path/to/scanner/scan_cli.py \
  --adapter source_bound_adapter_v1:make_adapter \
  --uniqueness-parent-sha256 ee677eea7f2f7bcf5c90347f5c54658988090340d888870c7e60071263693fff \
  --mode theorem --replay-receipt /protected/source_bound_coverage.json
```

Full protected ZIP verifier:

```bash
python verify_integrated_release_v1.py \
  --archive /protected/HIST001D_BINARY64_SIGN_COVERAGE_FULL_SOURCE_BOUND_v1_2026_11_08_NONPROMOTING.zip \
  --full --out /protected/CLEAN_REPLAY_AUDIT.json
```

`--full` re-executes all 1400 independent theorem panels, 112 original bracketer source-guard checks, 12 new scanner endpoint guards, and adversarial suite. It compares new source-bound receipts byte-for-byte. Full runtime depends on the local numerical environment; there is **no** unconditional cross-platform NumPy/libm guarantee. Any failure returns `UNRESOLVED`, exit 2.

## Verified local scope

- 6/6 source-bound theorem-mode sign-coverage records, 12 original-API point guards
- Complete positive-finite original binary64 support: `340337023840388388` input bit patterns across six distinct mathematical functions (compact contiguous segment representation, not an exhaustive per-float evaluation)
- 1400/1400 original whole-real source-domain exclusion panels independently replayed
- New adapter 18/18 source-free tests + inherited scanner 67/67
- Protected adversarial QA: 28/28 scoped checks (including baseline and fail-closed operational checks); two self-rehashed numerical forgeries rejected by source replay
- Exact source-dependent replay byte-for-byte; SHA digests in private sealed release.

## Hard release firewall

`physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`, `scientific_authority_promoted=false`, `original_compiled_float_signs_certified=false`. Original March sampled root interpolation remains a separate historical numerical identity; there is no third independently derived Bessel proof or observational holdout. The global uniqueness *producer* and independent external mathematical review are open. Do not merge solely because source-only CI is green.
