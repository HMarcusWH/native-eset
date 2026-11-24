# Full historical H mathematical bridge — source-only draft

This folder contains **public source code only**. The original March 46+3 source, six-by-180 stored binary64 arrays, fitted lens data and full numerical receipts are protected in a separately SHA-locked Drive ZIP. They must not be committed to GitHub.

Source-constrained objects:

1. Original sampled H crossing root from March `np.interp`-like nodal sign-change interpolation.
2. **Defined** frozen off-grid `H_finite=B_PL+D_PL+S0_PL(A(R))−pi_source*Sigma_source*R²`. Its exact global one-root-per-lens certificate is conditional on the stored source and named PL extension, **not** a floating SciPy/NumPy arbitrary-input proof.
3. **Defined** selected mathematical smooth-continuum `H_*=B_PL+D_PL+P_*(A(R))−pi_source*Sigma_source*R²`. Source-conditional interval endpoints show at least one root in each original crossing cell and the band gap shows any such root must precede the finite-model root. **No selected H_* global or local uniqueness claim**.

See `docs/HIST001D_FULL_H_BRIDGE_SCOPE.md` for proofs, root brackets, SHA locks, limitations and reproducibility. Public CI runs only the source-free `test_hist001d_full_h_bridge_source_free.py`; the protected replay is external and independently audited in the release artifact. Neither this candidate nor the stacked #51–#54 branches authorizes a physical provider, empirical validation or a science graph promotion.
