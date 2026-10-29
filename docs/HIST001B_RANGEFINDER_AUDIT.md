# HIST-001B — source-recovered RangeFinder independent replay audit

**29 October 2026 — diagnostic implementation, not scientific promotion.**

## Scope and source authority

- Original 34,052,504-byte June master SHA-256: 8609eb7896114f26f9355553208930bbdba5402d20a8c3454bc80c114f81f9f0.
- Original 1,214,157-byte March triad SHA-256: 283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e.
- Installed SOURCE_LOCK.json SHA-256: fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a; 46 original solver/input files plus three negative-summary records.
- Recovered separately: fixed_law_geometry_nuisance_survival.py and fixed_law_geometry_nuisance_survival_parallel.py (not part of the 46).
- Six fitted development lenses are **NOT** independent holdouts. No refits or parameter, scoring, or projection changes.

## Actual independent 4 x 1000 diagnostic execution

The new evaluator independently reconstructs the frozen Set A contractions with vectorized 120-angle disk integration and compares its calculations with the original, untouched source evaluator for the **same** perturbed rows. The recovered multiprocessing script uses the source-defined per-trial RNG SeedSequence([2141, trial]). Six perturbed input fields: bulge/disc axis ratio; bulge/disc effective radius; and multiplicatively varied bulge/disc mass via logarithmic columns. Scale is not perturbed.

| Input half-width | Archived 6/6 | Independent 6/6 | Archived 5+ | Independent 5+ |
|---|---:|---:|---:|---:|
| 1% | 323 | 328 | 844 | 838 |
| 2% | 140 | 135 | 631 | 633 |
| 5% | 23 | 14 | 239 | 253 |
| 10% | 3 | 4 | 69 | 70 |

**Disposition: HIST001B_ARCHIVED_REPLAY_MISMATCH_FAIL_CLOSED.**

Archived trial zero at 1% has mean absolute radius pull 1.2373450582603616; the recovered per-trial-seeded script gives 1.4004816306466654. These are distinct random realizations despite similar aggregate behavior. Numerical closeness does not certify source-exact reproduction. Do not widen tolerances or adjust RNG until counts happen to match.

## Independently reexecuted half-circularization negative

The predeclared no-refit intervention is f(R) = 1 - 0.5 * (1 - sqrt(q_eff(R))) instead of sqrt(q_eff(R)).
Original-source six-lens rerun: **2/6 dual passes**, 2 radius passes, 5 mass passes;
mean absolute radius pull **5.582136435311303**;
mean absolute mass pull **1.8743997197121056**.
Failed: J0822+1828, J0915+4211, J0930+2855, J1111+2234.
This is a projection-sensitivity negative control, not independent physical lensing.

## Executable and release discipline

With the installed package and separately verified frozen source:

    python tools/hist001b_rangefinder.py --source-root research/legacy/hist001 --out runs/hist001b

Full mode fixes four widths x 1,000 trials, source-verifies **before** import,
writes all per-trial CSVs and their digests, and compares early rows with the
original evaluator. The audit is retained even on mismatch; a mismatch returns
exit 4, **not** a successful completion receipt.

The narrow CI smoke command is:

    python tools/hist001b_rangefinder.py --source-root research/legacy/hist001 --out runs/hist001b-smoke --smoke --trials 3

Smoke output is always labeled SMOKE_ONLY, never a 4,000-trial rerun.
No native provider admission, no current v1.7.2 equivalence, no independent
held-out validation, no CMB/growth/production scoring, and no Theory-State mutation.

## Explicit blockers before HIST-001B release/merge

1. Recover the original **accelerated** evaluator and full width/trial RNG realization.
   The recovered serial/parallel stress scripts alone have not established it.
2. Reexecute the original **600 pre-run transition-radius equivalence checks**.
3. Independently verify all 4,000 rows and original 323/140/23/3 with untouched
   fitted law, predeclared seed and controls. Preserve every failed lens.
4. Pass Ruff, complete historical + GR regressions, source SHA manifest,
   Ubuntu/Windows Python 3.10/3.12/3.13 matrix and post-merge main CI.

HIST-001A is installed and operational; **HIST-001B remains not admitted**.
