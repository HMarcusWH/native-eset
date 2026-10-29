# HIST-001B — Supplemental source/RNG provenance

## Immutable scientific boundary

HIST-001A source lock (46 code/config/data files, 3 negative-summary files):
`fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`.
The original HIST-001A source tree is **not modified** by B. No Native v1.7.2,
physical lensing, cosmology, heldout validation or Theory-State promotion.

Verified June master archive:
`8609eb7896114f26f9355553208930bbdba5402d20a8c3454bc80c114f81f9f0`
(34,052,504 bytes). Nested March triad archive:
`283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e`
(1,214,157 bytes).

`hist001b_source.py` independently pins the archived ledger, four CSVs, four
summary JSONs, curve summary, and two later support scripts by byte SHA.
These 12 files are an **archival oracle for comparison**, not proof of the
original producer's executable identity. Their byte identifiers were
recovered from the SHA-verified June archive. Third-party raw data and the
full 34 MB master are deliberately kept off public GitHub.

## Open original-producer dependency

The archive contains:

- `fixed_law_geometry_nuisance_survival.py` (serial continuous RNG stream),
  SHA `329074375fff7f54596f0f690778fa5eae9fc52871a1aaf48a2bc28beef3c8da`.
- `fixed_law_geometry_nuisance_survival_parallel.py` (per-trial
  `SeedSequence([2141,trial])`), SHA
  `1b7d112db6b60290e983745fb8470f9bddc1ff935ed5088e21635f3d8693980f`.

**Neither independently reproduces the first archived trial.** The June
execution ledger references an accelerated evaluator and a 600-case
transition-radius grid-cell precheck, but the precise original accelerated
implementation, original input-case manifest, draw order and seed scheme
have not been authenticated. The runner must not substitute a new 600-case
test and claim this historical check passed. Calls to the B precheck
authorization function always fail closed until those identities are
obtained and independently pinned.

A new source can be admitted only if it is recovered with defensible
provenance and exact source hashes. An implementation that happens to
produce archived aggregate counts is **not** source-exact authority.

## Independent replay findings (29 October 2026)

| Width | Archived 6/6 | B diagnostic 6/6 | Archived 5+ | B diagnostic 5+ |
|---|---:|---:|---:|---:|
| 1% | 323 | 328 | 844 | 838 |
| 2% | 140 | 135 | 631 | 633 |
| 5% | 23 | 14 | 239 | 253 |
| 10% | 3 | 4 | 69 | 70 |

Same-index failure vectors match only 314/235/129/109 of 1,000 rows;
aggregate resemblance therefore conceals substantial per-trial differences.
The no-refit half-circularization negative does reproduce 2/6 both passes
(mean radius pull 5.582136435311303; mass pull 1.8743997197121056).

Original requested science claim remains **BLOCKED**. Software CI green means
the fail-closed implementation is behaving as intended; it does not prove
the missing original producer.

## Exact extraction of the B oracle

The B oracle is a **flat, separately supplied** 12-file directory matching
the approved names and SHA digests in `hist001b_source.py`. It contains
the archived ledger, both recovered later support scripts, the four
`w01/w02/w05/w10` CSVs and summary JSONs, and curve summary.
Do not place these inside `research/legacy/hist001`: that source's
inventory is deliberately exact and rejects extra members. If the oracle
is absent, record `HIST001B_SOURCE_NOT_RECOVERED_NO_ORACLE`.

Use `tools/hist001b_run.py` for isolated execution and
`tools/hist001b_verify.py` for independent receipt checking.
A hash establishes integrity against an independently known digest; it
does not certify who authored or executed the original code.
