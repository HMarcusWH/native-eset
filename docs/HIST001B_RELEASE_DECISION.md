# HIST-001B — Release decision (29 October 2026)

**Decision: NOT ADMITTED — original accelerator, original RNG and original 600 checks still missing.**

Scope remains fitted historical J2141/SWELLS Set A regression only.
The frozen original HIST-001A implementation remains installed and separately
verifiable. This document controls B's scientific status only.

## Implemented within draft PR #7

1. Preserved original 46/3 source lock, no GR or HIST-001A receipt schema changes.
2. Replaced aggregate-count-only exact-replay promotion with a nonpromotion cap.
3. Added independent SHA-pinned archive/oracle register and path/symlink checks.
4. Added row-by-row, failure-vector and per-lens archived summary comparator.
5. Added immutable diagnostic B RunSpec and separate receipt verifier.
6. Added disposable isolated source copy, bounded subprocess, immutable run
   directory, content SHA inventories and separate fail-closed exit codes.
7. Added adversarial forged-count/forged-receipt/invalid-source tests.
8. Kept 4x1000 and 600-original-precheck **unverified** until authentic source
   is recovered. Partial/diagnostic output is never named an admitted provider.

## Reproducible commands

With the exact external A source pack available:

```bash
python tools/hist001b_run.py \
  --source-root research/legacy/hist001 \
  --out runs/hist001b-smoke --smoke --trials 3

python tools/hist001b_verify.py \
  --source-root research/legacy/hist001 \
  --receipt runs/hist001b-smoke/<run-id>/receipt.json \
  --expected-sha256 <digest-printed-by-run>
```

For the full diagnostic replay, supply the **separately SHA-verified**
12-file B oracle:

```bash
python tools/hist001b_run.py \
  --source-root research/legacy/hist001 \
  --oracle-root /verified/flat/hist001b-oracle \
  --out runs/hist001b-full
```

Full mode computes all 4,000 rows, independently checks the archive,
produces a verifiable **failure** receipt and exits 4 as long as the
original accelerated producer and 600 prechecks remain unauthorized.
Do not interpret this nonzero exit as a claim that the Native ESET theory
was falsified; it is a historical reproducibility/source-authority blocker.

## Required before scientific HIST-001B completion

- [ ] Original accelerated implementation identified, SHA verified,
      admitted under a *supplemental* source identity.
- [ ] Original draw order and RNG behavior verified against original code.
- [ ] Original input-case identities and all 600 grid-cell checks rerun.
- [ ] 4,000/4,000 ordered source-equivalent trials and all four archival
      summaries matched within original tolerances.
- [ ] All negative projection cases retained with untouched fitted law.
- [ ] Independently verified full B receipt and no physical claim promotion.
- [ ] Six-platform PR CI and post-merge main CI successful.
- [ ] Merge with exact head SHA and preserve original A + GR contracts.

No date, SHA or CI link is proof of a missing scientific execution.
