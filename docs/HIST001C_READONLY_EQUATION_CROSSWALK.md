# HIST-001C — Read-only historical equation and identity crosswalk

## Status: NONCANONICAL EVIDENCE DESCRIPTOR — NOT scientific admission

Built independently of draft HIST-001B PR #7 from the merged HIST-001A/3 main commit.
The original 46 frozen J2141/SWELLS Set A source/input files, 3 negative
summaries, existing GR controls, existing HIST-001A receipt verifier and
canonical 31-file Theory-State graph are not edited or expanded.

## Provenance

- Finite ID: HIST-001-SWELLS-J2141-SETA-FROZEN
- Historical backend: legacy-hist001-j2141-seta
- Historical theory: LEGACY_ESET3_DM_A_FITTED_STRUCTURED_PROJECTION
- Original fitted branch: dma_v0p1_test1_axisym_structproj_baryonq
- Fitted candidate: ra0_gated_geometry_sigmoid_reg_v2
- Source lock SHA-256: fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a
- Original March archive SHA-256: 283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e
- Sealed Theory-State reference: release 0.16.39, SHA-256 163de068decc50d5339daa0a3fa4d38441f2441bf414a3131267ea02b312bc31
- Crosswalk descriptor SHA-256: 546a56e363524c07c0e19cae46edca04408e041ff9cb28ba6661e103f3beface

## Nine independently source-hashed numerical statements

| Historical implementation | Frozen original source | Modern transport limitation |
|---|---|---|
| Clipped radius-proxy epsilon | solv/dmalane.py | Not a covariant sourced constitutive law |
| Structure/charge-named fitted gate factors | solv/dmalane.py | Does not derive current F_charge |
| g_total=g_bar/epsilon and velocity recipe | solv/run_j2141_axisym_lens.py | Not numerical covariant PDE |
| Effective shadow density from mass difference | solv/shadow_density.py | Not independently sourced stress-energy |
| Axis-ratio weighted shadow circularization | solv/run_j2141_axisym_lens.py | Not physical Weyl lensing derivation |
| Equal Phi/Psi columns | solv/run_j2141_axisym_lens.py | Equality imposed, not slip proved |
| Frozen fitted Set A candidate | solv/run_setA_port_cand.py | No holdout validation |
| Projected Einstein-radius / mass pulls | solv/run_setA_port_cand.py | Not current Native lensing provider |
| Dual 2-sigma regression score | solv/scoring.py | Six fitted lenses are development evidence |

The research plan's expression div(epsilon grad Phi)=4 pi G rho_b is recorded
as a *declared phenomenological interpretation*, NOT an executable full
covariant or even full PDE solve by the historical numerical script.

## Noncanonical Theory-State link

The descriptor refers only to the approved sealed 0.16.39 snapshot digest.
No guessed graph node identifiers, Relation/MAPS_TO edges, Verdicts,
Authority objects, source graph partitions or production providers are made.
Eight explicit v1.7.2 obligations remain UNRESOLVED, including fixed-MP
action derivation, material one-map charge/source law, conservation/GR limit,
slip derivation, physical Weyl-lensing, perturbations/CMB/growth, independent
holdout testing and the original HIST-001B RangeFinder reproduction.

## Execution

With separately verified HIST-001A original source available:

    python tools/hist001c_crosswalk.py --source-root research/legacy/hist001

With the actual approved private 31-file graph available locally:

    python tools/hist001c_crosswalk.py --source-root research/legacy/hist001 --graph-dir /path/to/sealed/31-file-graph

The second form replays the ORIGINAL pinned ESET resolver read-only and
reports only the verified graph identity; it does not publish private source
records, alter graph state or re-adjudicate any scientific authority.
CI works without graph credentials, reporting the graph as NOT_SUPPLIED.

## Historical evidence boundaries

Central J2141 and six fitted-lens Set A regression outputs are source-locked.
The spherical projection negative is 2/6 and retained. Four archival
RangeFinder 1000-trial widths remain NOT SOURCE-EXACT REEXECUTED because
original accelerated RNG/source and 600 prechecks are missing (draft PR #7).
Neither historical fitted regression nor this overlay establishes Native
v1.7.2 equivalence, empirical validation, current lensing/CMB providers,
production scoring, or any new Theory-State canonical authority.

Future progress: HIST-001D independent observational tests, HIST-001E action
and constitutive equivalence proof or DISTINCT_HISTORICAL_THEORY disposition.
