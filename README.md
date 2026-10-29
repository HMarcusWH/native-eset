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

## HIST-001 — original March 2026 J2141 / six-lens SWELLS regression

The source-exact historical DM-A solver has been recovered into `research/legacy/hist001/swells_pack_v2` with SHA locks, frozen J2141/Set A fixtures, negative projection controls and a read-only execution wrapper. This is a historically *fitted regression*, **not** a Native ESET v1.7.2 model or an independent lensing validation.

```bash
python -m pip install -r requirements/hist001-constraints.txt
python tools/replay_hist001.py --out runs/hist001 --ablation
```

See `docs/HIST001_INTEGRATION_PLAN.md` for the detailed next integration steps and negative controls. The original 1,214,157-byte triad archive is retained externally with SHA-256 `283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e`.

## HIST-001A/3 — Installed historical CLI (source-locked, fitted regression ONLY)

The restored historical J2141 + six-lens SWELLS Set A solver now has a separately scoped installed package command. Install the optional pinned numerical environment, supply a separately verified frozen March source-root, and do not treat its fitted outputs as current v1.7.2 physics:

```bash
python -m pip install -r requirements/hist001-constraints.txt
eset historical j2141 --source-root research/legacy/hist001 --out runs --strict --ablation spherical
eset verify --receipt runs/<hist001-run-id>/receipt.json --source-root research/legacy/hist001 --expected-sha256 <separately-saved-digest>
eset doctor --historical-source-root research/legacy/hist001
```

The historical source pack is **not** installed with the wheel. The command verifies all 46 original source/config/data files and three archived negative records before executing a disposable copy. It then verifies full numerical tables, central Set A 6/6 and spherical 2/6 negative, retains content-addressed receipts, and refuses refits, modified sources, unrestricted physical outputs or false held-out status. The geometry robustness 4×1,000 campaigns remain **archived** pending HIST-001B. See `docs/HIST001A_3_CLI_RELEASE.md`.

The repository's actual GitHub CI gates are recorded on PRs; old B2 predeployment notes above describe the original archived B2 ZIP, not the current merged GitHub code.

## HIST-001C read-only historical model crosswalk

HIST-001C adds a separately pinned, noncanonical J2141/SWELLS Set A equation and
identity descriptor. It source-verifies nine original numerical statements and
records eight **unresolved** modern Native ESET v1.7.2 compatibility obligations,
without editing the sealed 31-file Theory-State graph, inferring a modern
provider, or claiming independent historical validation. Execute:

    python tools/hist001c_crosswalk.py --source-root research/legacy/hist001

An optional `--graph-dir` replays the approved sealed graph's original resolver
read-only if those private files are independently available. See
`docs/HIST001C_READONLY_EQUATION_CROSSWALK.md`. HIST-001B RangeFinder source-
exact reproduction remains blocked in draft PR #7.


## HIST-001D — frozen-model numerical sensitivity (nonpromoting)

The historical six fitted Set A lenses have an executable no-refit radial/angle
grid-sensitivity test: the original 180-point/120-angle calculation passes 6/6,
but radial grids of 90 and 360 points pass 2/6 and 3/6 respectively. This
exposes **numerical sensitivity of the historical projection**, not new
observational data, Native v1.7.2 falsification, or a physical Weyl solution.
Run `python tools/hist001d_convergence.py --source-root
research/legacy/hist001 --out runs/hist001d_d2`; inspect
`docs/HIST001D_CONVERGENCE_AND_SOURCE_REGISTER.md`. The independent holdout
remains unselected and unscored.

## HIST-001D/D2b — source-locked projection/root error attribution

A new strictly historical **nonpromoting** 2×2 density-grid versus radial
projector/root-grid test identifies why the originally fitted 180-point Set A
calculation passes 6/6 while its 360-point evaluation passes 3/6: the
projection/root-grid factor determines those failures in the tested factorial
comparison, not shadow-density grid resolution alone. Independent finite-domain
Hernquist integration exposes 180-point bulge-mass underintegration, the
original first-root interpolation differs from a consistent quadratic-target
bracket root, and the disc trapezoid omits its final periodic angular interval.
No old source, model fit, blind holdout, canonical graph or physical-provider
claim is altered. Run `python tools/hist001d_d2b.py --source-root
research/legacy/hist001 --out runs/hist001d_d2b`. See
`docs/HIST001D_D2B_PROJECTION_ROOT_AUDIT.md`. Issue #14 tracks remaining
quantitative quadrature closure; HIST-001B's source-exact blocker remains open.

## HIST-001D/D2c — independent shadow-mass projection and high-grid diagnostic

On the six **fitted development lenses only**, a new SHA-locked diagnostic
independently integrates the full finite-domain spherical shadow-density
cylinder mass with a fixed baryon-derived effective aperture. Source 180-point
K-matrix results differ by +0.71% to +3.79% from independent piecewise-linear
density quadrature at the same fixed aperture. Source shadow densities refined
from 180 to 11,520 points pass a 0.05% empirical late-grid Cauchy screen, but
**not** a global/root error bound or physical Weyl lensing proof. No holdout is
selected or scored. See `docs/HIST001D_D2C_INDEPENDENT_SHADOW_PROJECTION.md`
and `tools/hist001d_d2c.py`; source-exact HIST001B and modern ESET provider
admission remain blocked.

## HIST-001D/D2d — independently integrated structured-root numerical diagnostic

The historical fitted six-lens Set A **6/6 at the original 180/120 method**
remains intact. A new source-locked numerical identity evaluates the
finite-domain Hernquist bulge and full-periodic disc masses at *each* trial
radius, recomputes the original fitted q_eff(R) map and full independent
piecewise-linear shadow cylinder mass at R/sqrt(q_eff(R)), then solves the
quadratic critical-mass root with a bracketed numerical solver. This new,
nonrefitted finite-domain implementation yields **3/6 on each of seven source
density grids (180 through 11,520)**; J0822, J1021 and J1111 fail. The last
two refinements meet a 0.05σ root and 0.05% mass engineering screen, **not** a
global mathematical or physical-lensing error certificate. All fitted/source
inputs and archived negatives are untouched; no blind holdout is scored.
See `docs/HIST001D_D2D_FULL_STRUCTURED_ROOT.md` and
`tools/hist001d_d2d.py`. Independent receipt verification reexecutes the
whole calculation. This is not Native ESET v1.7.2 physical-provider admission.

## HIST-001D/D2e-A — sampled root topology, original gradient, in-domain cutoff

Source-locked D2e-A compares 45/181/721-point finite-domain root scans of the
already-fitted Set A independent structured-shadow numerical identity (D2d);
each has one sampled crossing but positive-slope intervals, so **global root
uniqueness is NOT proved**. No source shadow-density clips activate on the
six lenses at the seven tested original grids. The original 180-point
interpolated density at 0.1 kpc differs from the 11,520-point reference by
25,000–53,000x: **root stability is NOT uniform density convergence**.
Removing known outer shadow shells from 80/100–120 kpc changes the root by at
most 0.02027/0.00636 observational sigma, but **mass beyond 120 kpc is
unconstrained**. This is a new numerical diagnostic, not a physical Weyl
prediction, global error theorem or new blind holdout.
See `docs/HIST001D_D2E_A_ROOT_GRADIENT_DOMAIN_STRESS.md` and
`tools/hist001d_d2e.py`. All original fitted 6/6 and new D2d 3/6 identities
remain distinct; scientific D2e certification remains open.

## HIST-001D/D2e-B — conditional interval root-exclusion diagnostic

D2e-B bounds the positive baryonic and piecewise-linear finite-domain shadow masses over whole radius **intervals**, including conservative corner bounds on the radius-dependent `q_eff`. It adaptively excludes intervals *outside* a deliberately unresolved 2%-wide D2d-root guard, assuming an explicit **unproven** 1e-6 relative numerical mass error. Any zero-containing, budget-exhausted, or unverified interval remains unresolved. This is strictly stronger structurally than counting signs at dense sample nodes, but **does not prove global root uniqueness or certified numerical error**. Six fitted development lenses only; no theory/physical/held-out admission. See `docs/HIST001D_D2E_B_CONDITIONAL_INTERVAL.md` and `tools/hist001d_d2e_interval.py`.
