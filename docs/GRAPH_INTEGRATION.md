# Sealed ESET Theory-State graph import and navigation

## One authoritative graph, one derived reader

ESET scientific ontology is stored in 31 original JSONL partitions. This reader consumes those bytes read-only and refuses stale source SHAs. It preserves original `{subject,predicate,object}` edges and source IDs. RHKG is a reference for deterministic traversal/projection patterns; we do NOT import its million-plus Lean-specific edges, and `USES_CONSTANT` is not treated as a physical `DEPENDS_ON` relation.

No private graph files are in the Bootstrap ZIP. Acquire all 31 via authorized Google Drive access using the Drive file IDs and exact SHA digests in `config/graph_snapshot.lock.json`, place them in a single local folder, and run:

```
eset graph prepare --graph-dir /secure/originals --destination /secure/verified --lock config/graph_snapshot.lock.json
eset graph validate --graph-dir /secure/verified --lock config/graph_snapshot.lock.json
eset graph node eset:module:core --graph-dir /secure/verified
eset graph blockers eset:module:mem --graph-dir /secure/verified
eset graph explain eset:provider:bg8-current-bbn-composition-v0.1 --axis provider_state --scope CURRENT_BG8_BBN_COMPOSITION_OUTPUTS_ONLY --graph-dir /secure/verified
```

`prepare` makes an immutable new local copy only after each source partition matches its exact byte SHA; `validate` independently checks the semantic digest and runs the original ESET resolver source. The canonical validation target is 7030 objects / 3003 relations / 219 resolution partitions / 202 summaries and zero inferred promotions. Graph SHA `163de068...`. No file is fetched over the network by the CLI.

Do not add source or authority to the input JSONL. Changes require a newly reviewed Theory-State release and an updated lock in a new PR. The SHA is an integrity check against the reviewed source, not a digital signature.

## Query semantics

- `neighbors`: explicit predicates and `in`/`out`, always showing original subject and object.
- `path`: shortest structural path, not theorem entailment or physical causation.
- `impact`: reverse navigation on `DEPENDS_ON`, `REQUIRES`, `REQUIRES_DOMAIN`.
- `blockers`: declared `BLOCKS` sources; actual active-state resolution is conducted by the pinned resolver.
- `explain`: exact subject/candidate/axis/scope/facet partitions, preserved history and authority basis.
- `diff`: exact changed node/relation bytes between separately verified locked snapshots.
- No auto-inferred provider admission; output-class authorizer requires primary sealed `Provider` and `Verdict` records plus resolved scopes.

The sealed graph has scoped BBN composition and background providers; their limited admissions cannot be generalized to current P3, CMB, cosmological validation or scoring.

## Trust and portability

Input hashes alone are not authorization. The admission helper verifies the embedded approved lock and reruns the pinned resolver against captured exact graph bytes; directly constructing a result object cannot grant approval. The existing primary P1R provider scope is `CURRENT_V1_7_2_T1R_T3R_P1R_NARROW_BACKGROUND_V0_1`. Provider metadata shorthand is not a substitute. On generated resolver outputs only, explicit LF normalization makes the sealed comparison portable; raw generated hashes are retained. This is a compatibility mechanism, not a claim of already executed Windows CI.
