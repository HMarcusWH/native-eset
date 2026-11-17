# HIST-001D / G4b.1c — bounded external mathematical evidence-kit replay gate

**Status: source-pinned review infrastructure only; candidate/nonpromoting.** This is a new, narrowly scoped source-integrity and reproducibility gate following the independently verified G4b.1b software release. It does **not** merge, ratify or improve the existing mathematical proofs, modify 46+3 historical sources, or add a new physical/lensing/cosmology provider.

## What is frozen

The standalone `tools/g4b1c_evidence_replay_gate.py` requires four named **external** source/data kits, each with exact expected SHA-256. These four kits already existed in the separately audited 1 November 2026 Drive backup and have been clean-extracted/replayed independently. No original March source files, private catalogs or 69,120 D2d-style nodal values are distributed by this PR.

| Kit | Exact ZIP SHA-256 | Required local witness |
|---|---|---|
| Original-source input adapter | `11830c0729f3fe805b038e449c4c579d90ec3cb44f40cb76877c4e68cef1995b` | 6 authenticated lens input inventories, 69,120 finite binary64 nodal pairs, 10/10 tamper rejections |
| Exact 0.10 kpc existence brackets | `a73f2d46934747f58e81fbb4bbe53ec627737246cf9843e89ed54c7ecb350580` | 12 independent source-bound strict signs, 16/16 tamper rejections |
| Inner/outer and pre-peak support | `cdcca9b8628c16e66dba2fd6eaaeec233ad01366240be1fdcd3cabed65129a9a` | 42 strict positive Bernstein coefficients, 125 negative outer real-R cells, six pre-peak gaps, 16/16 tamper rejections |
| Projected 2D shadow surface slope | `b38a903e579f9ebadf7a806db586ab9af3b0c84a4ad00a2e6bb504d85d19e779` | Positive `Sigma'_S/(2A)` lower bound in the six source-bound root-aperture bands, independent verifier and adversarial QA |

The source authority is the frozen original historical 46+3 source digest `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`, and the source-nodal input identity is the **distinct D2d-style finite piecewise-linear 11,520-node per lens model** with continuum Hernquist/disk and G4a mathematical Sigma. The original fitted March 180/120 numerical model is a **different model**.

## Run the four bounded checks

After obtaining the four original, externally authenticated ZIPs (do not copy them into the Git repository), run each step independently to avoid execution-budget interference:

```shell
python tools/g4b1c_evidence_replay_gate.py --only adapter --adapter /absolute/path/to/adapter.zip --out adapter.json
python tools/g4b1c_evidence_replay_gate.py --only existence --existence /absolute/path/to/existence.zip --out existence.json
python tools/g4b1c_evidence_replay_gate.py --only prepeak --prepeak /absolute/path/to/prepeak.zip --out prepeak.json
python tools/g4b1c_evidence_replay_gate.py --only surface_slope --surface-slope /absolute/path/to/surface.zip --out surface.json
python tools/g4b1c_evidence_replay_gate.py --aggregate adapter.json existence.json prepeak.json surface.json --out combined.json
```

The last command **only verifies and aggregates the four previously executed scoped receipts**; it does not perform an additional independent proof. A one-process all-four execution is also implemented, but can exceed constrained interactive execution budgets. Each per-kit script independently verifies its historical source-kit manifest and runs its own original source-specific producer/checker/QA. The wrapper itself checks source-kit SHA, ZIP integrity, member paths, symlinks, limits, fixed expected scope and fail-closed aggregate identities.

The 9 cross-platform no-kit pytest regressions test negative file/ZIP/identity/claim controls and the scope-limited aggregate. They do **not** imply the original binary source kit was executed inside GitHub CI. Source-replay of the original off-repository kits remains separately evidenced by the exact local/Drive kit hashes and external clean extraction, not by repository-only tests.

## Scientific limitations — locked

The G4b.1c narrow intervals prove **at least one** continuous finite-mathematical-proxy zero per lens. They do not prove exactly one, exclude tangencies, or exclude other middle-radius roots. Strict positivity of finite projected shadow 2D surface slope on the narrow aperture bands **does not determine the derivative sign of total** `H(R)` or its average enclosed mass. All-real central-domain mathematical root count and physical system bridge remain open.

The four-kit aggregation is **not** an original March fitted 180/120 numerical all-R error/root theorem. It does not derive a physical same-solution Weyl potential or contemporary Native ESET v1.7.2 action correspondence. It does not repair SWELLS D1/D3 uncertainties, preregister D4, reproduce original HIST-001B accelerated RNG/600 source, admit a new ESET physical provider, authorize scoring or change Theory-State v0.16.39.

**Next PR required:** actually import reviewed source-bound mathematical proof *logic* as a new source-resident, independently tested mathematical certification module (not bundled original data), and implement comprehensive middle-domain branch-and-bound/derivative or root-count proof with unresolved outcomes. This PR intentionally stops at a reproducible archive gate.
