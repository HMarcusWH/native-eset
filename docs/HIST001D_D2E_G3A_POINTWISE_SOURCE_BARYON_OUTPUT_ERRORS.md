# HIST-001D/D2e-G3a — pointwise D2c reference-output discrepancy bounds

**Scope:** exact a posteriori numerical-output discrepancy for the independent D2c numerical reference bulge, full-period 1,024-angle disk and baryon-weighted q_eff calculations at **12 preregistered radii** (observed Einstein radius and independently pinned D2d 11,520-node root for each of six **already fitted development lenses**).

**Critical provenance:** D2c `reference_bulge_finite` and `reference_periodic_disk(...,ntheta=1024)` are independent source-equivalent reference algorithms; the latter integrates the full period, unlike the original March 120-angle/omitted-arc implementation. This PR **does not certify any binary64 outputs of the original March 120-angle algorithm**. Its pointwise certificate applies to the recorded independent D2c outputs only.

This is a distinct software/proof identity, not a full-radius error certificate, a probability-calibrated observational uncertainty estimate, proof of a physically sourced Weyl lensing metric, or contemporary Native ESET v1.7.2 admission.

## Mathematical statement

Let `V` be a finite binary64 number actually returned by the original source-equivalent numerical bulge/disk projector. It has an **exact rational interpretation** `V = Fraction.from_float(value)`. Independently, let the exact frozen-parameter *mathematical* analytic continuum target `T` be enclosed by rigorously established endpoints `L<=T<=U` from G1 Hernquist or G2b disk. The endpoints are canonical directed Decimal strings representing exact rational numbers. Then

```
|V-T| <= max(|V-L|, |V-U|) = E_max.
```

This inequality is elementary and **does not require certifying the internals of SciPy, NumPy, the periodic trapezoid or transcendental operations**. It gives a sound absolute error upper bound of the **specific returned binary64 value** relative to the exact-parameter analytic model target at the registered radius. It covers floating implementation discrepancy at this point by treating the output as the exact returned dyadic number.

If `L>0`, then `E_max/L` bounds the relative error compared to the unknown positive true analytic value. If `V>0`, `E_max/V` bounds the error relative to the returned number. Both are computed in exact rational arithmetic, rounded only **upward** for a Decimal display. When `L=0`, the true-relative error is withheld, not fabricated.

**Important source identity:** The analytic target is for *exact frozen binary64 scalars* computed from the historical input table: `M_b=10**logMb`, `a=(Re_bulge_arcsec*scale)/1.8153`, `M_d=10**logMd`, `s=(Re_disc_arcsec*scale)/1.67835`, and input `q_b,q_d`. The **independent D2c reference** returned `reference_bulge_finite` and full-period `reference_periodic_disk(ntheta=1024)` numbers. These are NOT the original March 180/120 execution's numerical outputs. This bounds discrepancy **relative to the mathematical model represented by those exact frozen scalars**, not numerical errors in the earlier derivation of the model parameters or any physical boundary continuation.

## Q_eff with a mathematical target interval

For exact analytic continuum bulge/disk mass ranges `B∈[B_l,B_h]`, `D∈[D_l,D_h]` and exact frozen axis factors `q_b,q_d`, the `q_eff=clip[1e-3,1]((q_b B+q_d D)/(B+D))` extrema lie at the four positive mass-box corners. The independent D2c reference implementation returns a distinct rounded binary64 q computed from its own two source numerical mass outputs.

The same exact rational pointwise-discrepancy construction produces a **single-source-call q_eff error upper bound** relative to the analytic mathematical interval. It does not bound the q_eff calculation for any other radius, establish correlation/covariance, or certify propagation to root position.

## Registered source replay

The runner `tools/hist001d_d2e_g3a_pointwise_baryons.py` reconstructs original March 46+3 frozen source bytes under lock SHA `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`. It verifies historical original fitted 180/120 6/6, and preserves the independent D2d finite-source 3/6 without re-fitting. For each development lens and registered radius, it records:

- exact binary64 source returned bulge, disk and q_eff values, source Python/NumPy/SciPy versions and frozen input parameters;
- G1 independently certified positive Hernquist continuum point mass with its unmodified target width and actual result;
- G2b rigorous 1,024-midpoint analytic-continuum disk point mass (success or failure against **predeclared 1% width target**) and intersection with the original independent coarse G2 proof;
- exact rational a posteriori absolute/relative discrepancy upper bounds for the two masses and q_eff, with recorded exact dyadic numerator/denominator;
- strict nonpromotion flags for global source implementation numerical accuracy, continuum density, outside-source-domain mass, critical surface density numerical/physical error, lens root uniqueness, independent holdouts and Weyl/Native ESET physical provider status.

```bash
python tools/hist001d_d2e_g3a_pointwise_baryons.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_g3a
python tools/hist001d_d2e_g3a_pointwise_baryons.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_g3a/receipt.json
```

A canonical report and receipt with SHA-256 of source-locked runner, frozen G2b prerequisite and proof helper is generated. A second **independent source reexecution** validates every numerical field in the report and rejects self-rehashed forgery. Synthetic tests cover exact dyadic distance inequalities, directed ratio upper bounds, zero/unordered inputs, false physics/provider promotion and unexpected receipt files. Six-platform CI (Ubuntu/Windows × Python 3.10/3.12/3.13) retains all preceding HIST-001D numerical tests, source replays and manifest/security/lint checks.

## Scientific gate disposition

**Newly certified:** pointwise absolute/relative **discrepancy upper bounds for exact, recorded source numerical outputs versus the specified analytic-continuum mathematical target**. These can be computed even when the error is not small; no target-driven refit or result censorship is allowed.

**Still unproved:** a uniform error envelope for every R in the Einstein-root guard, mass dependence across neighboring radii, complete model residual and radius propagation, Sigma_crit source numerical/physical accuracy, full root topology including tangencies, shadow density continuum, matter outside [0.02,120] kpc, physical metric/Weyl lensing, D3 covariance, D4 outcome-blinded truly disjoint holdout, Native v1.7.2 theory transport, no-particle-CDM and empirical validation.

**Prohibition:** numerical software green CI or source-reexecuted agreement must never be promoted to evidence of physical/empirical agreement. The original historical 180/120 fitted 6/6 and separately computed D2d finite-source 3/6 remain distinct identities. **Original-March output pointwise errors remain unbounded by G3a.**
