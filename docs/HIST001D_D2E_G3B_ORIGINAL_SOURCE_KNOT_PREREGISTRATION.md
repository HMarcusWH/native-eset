# D2e-G3b: predeclared original March 180/120 knot selection — draft-only

This incremental change freezes **which original March source-grid outputs will be audited later**; it does not calculate, report or certify any mass, disk, q_eff or root discrepancy. It is a preparation branch based on merged G3a (commit `2eee363060c30a6b7873d7edd85a80b97cc3c228`). No merged/main release or Drive pointer advancement is authorized here.

## Why separate knots from anchor radii?

The frozen March solver evaluates its `K.dot(hernquist_density(...))` bulge and 120-angle omitted-arc `np.trapezoid` disk arrays on **180 source knots**. G3a's two predeclared continuous radii (observed Einstein radius, independently pinned D2d 11,520-node root) are normally off-grid. Looking up a numerical array at those radii by interpolation would introduce another operator, which G3b does *not* certify.

Importantly, on the 180-knot grid each of the six development lenses' two anchor radii has the same **nearest** knot index. Reusing that knot would test the same point twice and misstate independence. Therefore the selection is fixed entirely from source inputs before inspecting outputs:

- Observed role: lower bracketing grid knot, `searchsorted(r, observed, side='right') - 1`.
- D2d role: upper bracketing grid knot, `searchsorted(r, root, side='left')`.
- Collision: shift D2d role by exactly one higher grid index, fail closed if out of domain. This occurs for J0930+2855.
- Every reported comparison must evaluate the **exact-parameter analytical target at the selected source grid knot**, never at the off-knot anchor.

| Frozen fitted-development lens | Observed-role index | D2d-role index |
| --- | ---: | ---: |
| J0822+1828 | 2 | 3 |
| J0915+4211 | 2 | 3 |
| J0930+2855 | 7 | 8 (collision shift) |
| J1021+2028 | 1 | 3 |
| J1111+2234 | 5 | 7 |
| J1135+3720 | 2 | 4 |

Source lock: `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`. See exact numeric inputs and source file SHA locks in `registry/hist001d_d2e_g3b_knots_v1.json`.

## Required subsequent proof

The future source runner must capture actual **original March** bulge and disk arrays without modifying original source bytes, including the 180-node K-matrix finite-sampled Hernquist and 120-angle omitted-arc disk. It must reconstruct the frozen source q_eff formula on these source-returned arrays, clearly labeling q_eff as **derived** (the current frozen source function does not separately return a q_eff array). Then at each selected knot compute rigorous G1 finite Hernquist and G2b continuum disk intervals for the matching exact historical scalar inputs and exact dyadic pointwise maximum-endpoint discrepancy bounds. No new fit or changed historical algorithm.

Independent locked source reexecution, canonical receipts with source and runner hashes, forged-receipt rejection, and full Ubuntu/Windows x Python 3.10/3.12/3.13 CI are mandatory for any subsequent G3b release. No universal all-radius numerical error, root existence/uniqueness, critical density accuracy, density-gradient continuum, exterior shadow mass, current Native v1.7.2 transport, physical metric/Weyl lensing, independent holdout or empirical validation is established by this registration. Parent issues #27 and #19 remain open; specific G3b plan is #31.

This is an **unpromoted PR preparation artifact** while G3a's exact-merge-main evidence archive is being verified.
