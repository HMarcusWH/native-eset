# Native ESET — B2 final predeployment bootstrap

**Infrastructure version 0.1.0 — 28 October 2026.** This is the frozen bootstrap for a research repository, not a completed or validated ESET cosmology. Historical J2141/G-D, current v1.7.2 physics and external scientific solver adapters still require their separate source-preserving imports.

B2 audits and repairs B1r1 rather than merely renaming it. It contains the read-only ESET Theory-State reader and original authority resolver, strict scientific identities, numerical reference runner, data-use checks, source locks, receipts, regression tests, packaging tools and CI configuration. The original B0 ZIP remains byte-identical in `provenance/`.

## Install and verify

Use Python 3.10 or later. Only Python 3.13 on this Linux build host was executed locally; the configured GitHub Windows/Linux matrix has **not** run. The runtime uses only the Python standard library.

From this source directory, with package-index access:

```bash
python -m venv .venv
# Activate .venv using your platform's usual command.
python -m pip install -r requirements/ci-constraints.txt
python -m pip install --no-build-isolation --no-deps -e .
python tools/check_manifest.py
python tools/security_audit.py --manifest MANIFEST_SHA256.json
python -m pytest -q
python -m native_eset doctor
```

For offline runtime installation, install the wheel supplied under the release bundle's `release/dist/` directory:

```bash
python -m pip install --no-index --no-deps /path/to/native_eset-0.1.0-py3-none-any.whl
python -m native_eset doctor
```

This does not install pytest, Ruff or build tooling. They must be available separately to execute those checks. `doctor` verifies embedded source locks; it does **not** certify CI, scientific validity or repository permissions.

## First reproducible computation

The source bundle provides two reference fixtures:

```bash
python -m native_eset run --spec tests/fixtures/E_of_z.json --out runs
python -m native_eset run --spec tests/fixtures/chi_dimensionless_of_z.json --out runs
python -m native_eset verify --receipt runs/<run-id>/receipt.json --expected-sha256 <printed-receipt-digest>
```

These are external GR/ΛCDM controls, not ESET predictions. Run identifiers bind the validated specification, implementation files, finite-model identity and actual execution environment. A rerun never overwrites an existing run. Numerical refinement checks are **not rigorous error certificates**. Receipt verification establishes recorded-byte consistency, not independent execution or author authentication; preserve the expected digest separately.

## Read the existing ESET graph

The release includes the source lock and unchanged original resolver, **not the private 31-file graph corpus**. Acquire the exact bytes through authorized access, then:

```bash
python -m native_eset graph validate --graph-dir /secure/eset-graph
python -m native_eset graph node eset:module:mem --graph-dir /secure/eset-graph
python -m native_eset graph neighbors eset:module:mem --predicate REQUIRES --graph-dir /secure/eset-graph
python -m native_eset graph explain eset:provider:bg8-current-bbn-composition-v0.1 --graph-dir /secure/eset-graph
```

The pinned snapshot is v0.16.39: 31 files, 7,030 records including 3,003 relations, 246 primary verdicts, 219 resolver partitions and 202 summaries. Later research annexes are not silently merged into this snapshot. ESET's own resolver controls scientific scopes; RHKG-inspired traversal is navigation, not proof. Existing scoped background/composition admissions remain distinct from empirical validation, P3 and production scoring.

## What to read before changing source

- `AGENTS.md`: contributor rules and historical-model separation.
- `docs/BUILD_STATE.md`: implemented scope and real outstanding work.
- `docs/FINAL_AUDIT.md`: reproduced B1r1 defects and repairs.
- `docs/THREAT_MODEL.md`: integrity guarantees and their boundaries.
- `docs/RELEASE_PROTOCOL.md`: immutable releases and multi-turn handover.
- `registry/equation_bindings.json`: implementation-to-equation crosswalk.

Use the supplied `verify_final_bundle.py` on the complete release ZIP before import. Commit the `native-eset/` source subtree, not generated wheel, sdist or run outputs. Preserve B0 as historical evidence; do not rebuild the already working infrastructure instead of importing the actual historical solvers.

## Publication and remaining gates

No open-source license has been selected for new ESET code. Keep the initial repository private pending the owner's licensing/publication review. Do not publish raw scientific graph partitions, private catalogs, credentials or unreviewed third-party code. This build does not change Drive sharing or canonical scientific records.

**Ruff and real GitHub Actions: NOT_RUN.** The local audit uses actual tests, compile checks, graph replay, distribution builds and cold wheel execution; it does not relabel those as a Ruff or Windows CI pass. Full results and exact hashes are supplied in `release/FINAL_BUILD_RECEIPT.json` of the release bundle.
