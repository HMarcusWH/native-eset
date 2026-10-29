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


### Independent NEW 600-case grid diagnostic (not the historical 600)

A separately implemented deterministic grid-cell check now evaluates **600 newly
constructed six-lens-derived perturbation cases** (100 per lens), using
`SeedSequence([2141,0xB001,case])` and cycling the 1/2/5/10% widths.
Each compares the original frozen transition-radius grid finder against an
independent direct Bessel/acceleration computation without calling
`J2141BaryonicModel.total_vbar` on the independent side.

Local execution against the original source: **600/600 exact grid-cell matches**;
first indices `[3584,3607,3884,3638,3869,3709]`.
Index-list SHA-256 `ff63c7a7b1acd29d27ce44c6f804b778c3a755ac9d8cac49c513c00fc19f2e57`.
The new result is verified **only for this new input corpus**. It is not the
archive's original 600-case input set and not an independently recovered
original accelerated implementation.

Executable: `python tools/hist001b_new600.py --source-root research/legacy/hist001`.
A dedicated regression test enforces the 600/600 result and original-precheck
nonpromotion flags. The original `require_original_600_prechecks()` guard
continues to fail closed.

## Original-versus-replay width-pair RNG forensics (new evidence)

The four SHA-pinned original 1,000-row CSVs were aligned by trial number.
Across six width pairs, the archived mean-absolute radius-pull correlations
range from **-0.03875 to +0.01700**, while the reproduced
`SeedSequence([2141,trial])` diagnostic ranges from **+0.58211 to +0.89443**.
Archived mass-pull correlations lie between -0.03332 and +0.02452,
versus +0.78787 to +0.96167 for the diagnostic.

The same trial number therefore does **not** couple the original width
records in the same way as the recovered parallel script. This narrows the
RNG question to distinct width-specific streams, reseeding, or trial-order
mapping. It does not prove which original seed formula was used or recover
the accelerated source. The full per-pair JSON analysis is retained
externally with independent file digests.

Execute using a separate SHA-verified 12-file oracle directory:

```bash
python tools/hist001b_rng_forensics.py \
  --oracle-root /path/to/approved-flat-archive \
  --diagnostic-root /path/to/independent-4-width-CSV
```

The diagnostic never grants source-exact replay, scientific validation or
physical provider admission. Keep the original 600-case precheck blocked.
