# B2 source audit and corrections

This audit began from the exact B1r1 archive, not an assumed clean working tree. B1r1's source manifest and original tests passed, but additional adversarial tests exposed defects. The audit does not claim exhaustive software verification.

## Reproduced defects

**Mutable RunSpec.** A specification could be changed through a shared dictionary after validation. Execution could then use different role/equation metadata than its recorded specification hash. B2 validates every constructor, copies canonical bytes, returns defensive views and revalidates at execution. A stale caller-supplied digest is rejected.

**Constructed authority object.** A caller could construct a snapshot/result with an approved-looking graph digest and fabricated partitions. B2 binds authority to independently pinned lock, vocabulary, original code and policy; rehashes the actual graph records and original source bytes; replays the unchanged resolver in an isolated exact-input directory; and compares the supplied result with that replay before reporting admission. Neither a hash-shaped string nor a dataclass name confers authority.

## Additional repairs

1. V2 run receipts bind original specification, output files, code, model and actual environment, enforce an exact artifact inventory and reject claim promotion. An externally retained expected receipt digest is supported. V1 receipts require their original archived verifier.
2. JSON input rejects duplicate keys, NaN/Infinity and finite-looking exponents that overflow binary64. Input sizes, decimal domains, coordinate count and reference-model conventions are bounded.
3. Graph source imports reject extra suffix files and aliases. Captured source bytes are replayed rather than rereading a mutable original directory. Parallel relations with distinct scopes remain preserved.
4. The resolver's original output digests are checked. A separately declared LF-normalized digest accommodates Windows output newlines without altering original source bytes or authority semantics. Windows execution itself remains pending.
5. Predicate iterables no longer disappear after one traversal hop; direction, zero-hop queries, cycles and predicate filters receive tests. CLI status/neighbor/filter handling and fail-closed error categories are corrected.
6. Calibration/regression and holdout roles remain distinct. The declared contamination ledger checks dataset lineage across model IDs; changing a model name does not make the same data independent. Undeclared prior use cannot be detected.
7. Filename/security preflight reads Git index bytes and fails rather than returning green outside a repository. A separate manifest mode verifies release files. High-confidence secret patterns supplement filename checks; this is not an exhaustive secret scan.
8. Metadata collections and capabilities use defensive/immutable views. Equation bindings reject paths escaping the source tree and arbitrary import namespaces.
9. Source manifests account for previously ignored configuration files; line endings are fixed for source. Package version is consistent across metadata and runtime. Built wheels are tested from an unrelated directory with isolated Python import mode.
10. Numerical convergence labels explicitly distinguish refinement differences from certified error bounds. Unsupported physics remains unsupported, not a failed theory claim.

**Cold Git import correction.** The original reference record schema has historical CRLF bytes. A broad LF rule silently changed its staged bytes even though the working-tree manifest passed. The exact historical file now has a `-text` attribute and CI checks the full Git-index inventory/digests against the source manifest. This preserves, rather than rewrites, the original schema.

## Positive scientific-status tests

The actual sealed graph was inspected rather than guessing scope names. P1R's primary provider scope is `CURRENT_V1_7_2_T1R_T3R_P1R_NARROW_BACKGROUND_V0_1`; the shorter metadata label is not interchangeable with that authority scope. Both the authentic P1R H(z) table class and BG8 Y_p class are accepted only under their exact declared scopes. CMB and all-cosmology requests are rejected. The underlying graph is unchanged.

## Verification limits

See the machine-readable final receipt for executed commands and environment. Local unit/regression tests, graph replay and wheel installation are not real GitHub CI or Ruff. No Windows runtime, scientific model import or empirical test is claimed. Hashes provide integrity relative to a trusted digest, not signatures, independent execution or proof that physical equations describe nature.
