# HIST-001D/D2e-G4a — source-scalar FlatLCDM Sigma_crit mathematical enclosure (draft)

**Status: unmerged source-locked draft implementation; not an admitted release.** Based on G3b merged commit `63521ec49797de318790ea334c30effb86379ff8` while G3b's own post-merge CI and evidence archive remain pending. The merged G3b predecessor still requires its own exact-merge-main six-platform CI, evidence archive and Drive readback; G4a draft source does not authorize a science or release-pointer upgrade.

## Model and exact frozen-scalar identity

The March 46+3 source SHA is `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`; `solv/cosmology.py` uses `FlatLCDM(H0=70.0,Om0=0.3)`, `Ode0 = 1.0-Om0` and a SciPy-adaptive integral of `f(t) = [Om0*(1+t)**3 + Ode0]**(-1/2)`. Those source integration tolerances are **not** mathematical error bounds. In this kernel every already-defined source float (`C_KMS`, `H0`, `Om0`, computed `Ode0`, `G_KPC_KMS2_MSUN`, `FOUR_PI=4.0*math.pi`, `MPC_IN_KPC`, redshifts) is interpreted as its **exact binary64 rational**, not as an unrounded physical constant. The source `FOUR_PI` dyadic is distinct from exact mathematical `4π`.

Define `I_l = ∫_0^{z_l} f(t)dt`, `I_ls = ∫_{z_l}^{z_s}f(t)dt`. Algebraically eliminating source angular-distance differences gives the mathematical source-scalar target:

`Sigma_crit = [C_KMS*H0*(1+z_l)/(FOUR_PI*G_KPC_KMS2_MSUN*MPC_IN_KPC)] * [1/I_l + 1/I_ls]`.

The representation uses two strictly **positive** integrals, avoiding an unstable interval subtraction of independently bounded distances `chi(z_s)-chi(z_l)`.

## Certificate

For `D(t) = Om*(1+t)^3 + Ode`, `f(t)=D(t)^(-1/2)` is positive and decreasing on each registered nonnegative redshift interval. With `Dmin = D(a)`, `Dprime_max=3*Om*(1+b)**2` and `Dsecond_max=6*Om*(1+b)`, a rigorous rational bound is

`|f''| ≤ K = 3*Dprime_max**2/(4*Dmin**2*sqrt_low(Dmin)) + Dsecond_max/(2*Dmin*sqrt_low(Dmin))`.

At exactly 256 registered trapezoid cells, evaluate endpoints with integer-isqrt rational enclosures at 100 bits. Each endpoint integrand interval is inverted outward. Sum with directed 70-digit Decimal arithmetic. Then add/subtract `K*(b-a)**3/(12*N**2)` with outward rounding. The resulting lower/upper intervals for `I_l` and `I_ls` are **mathematical** enclosures of the model's exact-dyadic-parameter integrals. Since both integrals are positive, their reciprocal bounds combine monotonically into a valid interval for the exact mathematical `Sigma_crit` above. The engineering target is relative interval width `1e-4`; failure reports `target_met=false` and a retained wide interval, never a fabricated precision success.

For a particular separately returned original binary64 `V`, the exact a posteriori discrepancy `max(|V-L|, |V-U|)` bounds the error relative to this frozen mathematical target. It is not a universal certification of SciPy `quad`, observational redshift errors, or source-generated physical lensing.

## Source-informed local tests (not a release)

Six originally fitted Set A redshift pairs were checked with an independent SciPy evaluation as **diagnostics**, not proof. All six mathematical enclosure widths were below the draft predeclared `1e-4` target; the six returned source-formula binary64 values lay inside the enclosures. The mathematical helper's 16 isolated unit tests passed locally. Additional synthetic runner/receipt tests (plus the preserved 16 math tests) exercised forged-source-output rejection and false-physics flags; authentic frozen-source reexecution and full six-platform CI are mandatory future checks, not yet certified by local tests. These tests do not establish the frozen historical source's SHA or prove that a particular value was actually emitted by that source; both are explicit false provenance flags until the final source-reexecuting runner is added.

## Source-locked six-lens executable draft (not released)

`tools/hist001d_d2e_g4a_flatlcdm_sigma.py` now adds the frozen 46+3 March source preflight, exact `solv/cosmology.py` / `solv/constants.py` SHA checks, pinned G3b predecessor, original `FlatLCDM.sigma_crit_msun_per_kpc2(z_l,z_s)` source reexecution for the six formerly fitted Set A lenses, exact-dyadic pointwise error calculation, and immutable canonical `report.json`, `receipt.json`, `receipt.sha256` files. Its independent verifier rejects self-rehashed numerical evidence and scientific claim promotion and recomputes the source result. It deliberately preserves the mathematical helper's `frozen_source_bytes_verified=false` provenance field, while the **source runner**, not the helper, separately verifies original source provenance.

Run the draft source-integrity checks with:

```bash
python tools/hist001d_d2e_g4a_flatlcdm_sigma.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_g4a
python tools/hist001d_d2e_g4a_flatlcdm_sigma.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_g4a/receipt.json
```

The PR's six-platform CI must execute both commands plus all preceding A–G3b replays and synthetic tests. Only actual CI evidence can establish source-run agreement on each platform; these docs are not an execution receipt. Releasing G4a requires verified G3b predecessor archival handoff, exact-head CI 6/6, merge, exact-postmerge CI 6/6, independent eleven-stage ZIP/SHA/member verification, Drive byte readback, and living pointer revision/readback. The original March 46+3 files, original fits, contemporary Theory-State and all previous mathematical kernels remain unchanged.

## Scientific firewall

No Einstein root existence/count/uniqueness (including tangencies), `Sigma_crit` observational or physical error bar, arbitrary-redshift SciPy numerical theorem, source shadow/density continuum error, mass outside `[0.02,120]` kpc, new holdout, Native v1.7.2 compatibility, same-sourced metric/Weyl lensing, empirical validation or physical-provider admission follows. G3b remains an unverified release until its separate postmerge evidence gates pass, and this G4a draft does not satisfy its own independent release gates. Parent issues #19, #27 and #33 remain open.
