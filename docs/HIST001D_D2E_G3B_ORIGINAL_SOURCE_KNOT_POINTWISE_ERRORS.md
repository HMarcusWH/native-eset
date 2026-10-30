# HIST-001D/D2e-G3b — original March 180/120 pointwise numerical discrepancies (DRAFT)

**Scientific scope:** only 12 preregistered original-source-grid knots across six previously fitted SWELLS development lenses. This code is not a full-radius numerical-error or Einstein-root theorem, physical Weyl metric, independent holdout, or empirical validation.

## Provenance

The original source uses a 180-knot grid from `np.linspace(0.02,120.0,180)`. At each knot it constructs the bulge by `K.dot(hernquist_density(...))`, with the original 180-node weighted matrix, and the disk using the frozen `projected_disk_mass_exponential(..., ntheta=120)`. That implementation integrates a 120-angle `endpoint=False` grid with `np.trapezoid` and does not close the final angular arc.

The original high-level fitting function does not return its intermediate bulge, disk, or q_eff arrays. G3b reexecutes the unchanged source functions in a verified disposable source copy, reconstructing those arrays at all original knots. It computes the source's internal q_eff expression from the recreated mass arrays, and independently checks the source's structured-shadow circularization implementation with a synthetic monotone array. The q_eff array is a **derived source-prescribed intermediate**, not an original emitted return.

This is **not** the D2c SciPy and full-period 1024-angle reference algorithm audited in G3a.

## Precommitted knot selection

The registration was frozen before original mass outputs were inspected: `registry/hist001d_d2e_g3b_knots_v1.json` with SHA-256 `b561182ef3569152408c75d97218b6daa80ab3bdab3e3037ce0b2d0eef3b0180`. For each development lens the observed-radius anchor selects the lower source-grid knot, the pinned D2d-root anchor the upper knot. A same-index collision shifts the D2d index upward by one. The fixed pairs are (2,3), (2,3), (7,8), (1,3), (5,7), (2,4) in registered lens order.

These **12 grid knots**, not the off-knot observed or D2d-root anchors, are the numerical evaluation points. No source-output-dependent selection, re-fitting, or interpolation is permitted.

## Pointwise mathematical certificate

For exact returned binary64 value V and rigorous frozen-parameter analytic-continuum target T in the existing G1 or G2b interval [L,U], compute the exact-rational upper bound E = max(abs(V-L),abs(V-U)). Only final display is rounded upward. The original March K-matrix bulge and nonperiodically-closed 120-angle disk discrepancies are assessed at each selected knot. A G1/G2b positive mass-box four-corner calculation gives an analogous bound for the derived q_eff. An unmet precision target is reported, not silently rounded into success.

## Proof receipt and CI

Run:

`python tools/hist001d_d2e_g3b_original_knot_errors.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_g3b`

`python tools/hist001d_d2e_g3b_original_knot_errors.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_g3b/receipt.json`

The report and receipt are canonical, SHA-bound to the frozen original source, G3a proof predecessor, preregistration, selection helper, source runner and pointwise error kernel. Independent source reexecution and adversarial receipt tests must reject forged errors and unauthorized scientific claims. CI must run Ubuntu/Windows x Python 3.10/3.12/3.13 with every preceding A–G3a source replay and full packaging tests. A 180-minute per-job compute allowance is not an assumed error tolerance.

**Release is blocked** until this draft passes exact-head 6/6, merge, postmerge 6/6, complete artifact SHA/ZIP and Drive readback. G3a must independently pass its own release gate before G3b is promoted.

## Not established

All-radius original-model numerical error, source interpolation away from the 12 knots, q_eff root-map errors, continuous source-gradient/shadow uncertainty, density or matter beyond [0.02,120] kpc, complete root existence/count/uniqueness including tangencies, observational covariance, disjoint masked holdout, same-source metric/Weyl lensing, current Native v1.7.2 transport, cosmological no-particle-CDM or empirical validation. Issues #19, #27 and #31 remain open.
