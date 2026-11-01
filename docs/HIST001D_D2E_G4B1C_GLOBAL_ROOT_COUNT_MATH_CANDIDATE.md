# HIST-001D / G4b.1c — Full finite-proxy root-count mathematical code for review

**CANDIDATE_ONLY / NOT_PEER_REVIEWED / MARCH_180x120_NOT_PROVED / physical provider NOT_ESTABLISHED.**

This change imports the **exact original source-only arithmetic/producer/independent-verifier scripts** from the separately verified G4b.1c 41-member candidate kit, not its underlying historical files, six lens arrays, prior evidence JSON, source ZIP, or scientific output JSON. It deliberately has no access to an original March source root during normal GitHub CI. Passing repository CI only attests to a bounded set of source-free regression checks; it cannot prove the six-lens theorem.

## Exact model and quantified theorem candidate

The only mathematical function under study is

`H(R)=B_continuum_finite_Hernquist(R)+D_continuum_elliptical_exponential(R)+S_piecewise_linear_finite(A(R))-pi*Sigma_crit_math*R^2`,

`A(R)=min(120,R/sqrt(q(R)))`, `q=(q_b B+q_d D)/(B+D)`, `R∈[float64(0.02),120] kpc`.

The original 46+3 March source and the six 11,520-node source-derived profiles are SHA-bound **externally**. The result is **conditional on the archived G4a critical-density theorem and the independent G4b.1c v3/v4/narrow-point antecedent certificates**. The new reviewed source presents exactly 25 strict-positive `H` cells and 157 strict-negative `H'` cells, plus the earlier inner, outer, and narrow crossings. The full 182-cell partition has strictly contiguous exact-rational endpoints, covering the remaining subdomains. The older 0.10-kpc intervals have rigorous opposite endpoint signs and strict decreasing `H`, giving one simple finite-proxy zero per interval. The new exclusion covers any additional real zero or tangency **only for this source-defined mathematical finite proxy**.

## Source-arithmetic audit checklist

- **Cylindrical shell integral.** For any nonnegative spherical 3D source, the projected cylinder mass divided by `4*pi` is the exact interior radial moment plus an exterior radial moment weighted by `1-sqrt(1-(R/r)^2)`. This positive kernel decreases in `r` for fixed `R`; `sqrt_lo/sqrt_hi` therefore give honest shell enclosures. Source density is piecewise linear between exactly represented original binary64 nodal pairs; its `r^2*rho` primitive is polynomial and integrated exactly.
- **Disk.** For `q_d∈(0,1]`, the source-equivalent continuum elliptic disk reduces to an integral over `t∈[0,1]`. The square-root geometry `g(t)` and `1/(1+t²)` yield a monotone integrand. Since `1-(1+x)e^-x = ∫_0^x y e^-y dy`, `F(Cg)/g²=C²∫_0^1 u exp(-Cgu)du` is decreasing in `g`; endpoint rectangles are sound. The two source codes independently bound real `pi` through Machin's identity and exponentials through alternating Taylor/range reduction.
- **Geometry and derivative.** From `q=(qb B+qd D)/(B+D)`, exact differentiation gives `q'=(qb-qd)*(B'D-BD')/(B+D)^2`. Positive B,D cell envelopes yield four-corner q bounds, exact outward sqrt aperture guards, and a conservative upper on `A'`. In unsaturated cells, `H' = B'+D'+2*pi*A*Sigma_S(A)*A'-2*pi*Sigma_crit_math*R`.
- **Finite shadow upper.** `Sigma_S(A)=2∫_0^sqrt(120²-A²) rho(sqrt(A²+t²))dt`. Since each source's 3D nodal density is independently checked as strictly unimodal, the upper on any entire radial interval is the maximum of both endpoint densities and its unique peak (if included). Subdivision of the entire t-domain provides an *all-aperture-band upper*; the old narrow-band `Sigma'_S>0` is NOT extrapolated to the global interval.
- **Global logical topology.** Strict `H>0` on `[rmin,Lw]` and new cells `[Lw,P]`; strict `H'<0` on `[P,Ln]`; exactly one simple root in `[Ln,Un]`; strict `H'<0` on `[Un,Uw]`; strict `H<0` on `[Uw,120]`. Exact endpoint joins and six independent source identities must be verified before any candidate count.

## Reproduction and CI limits

Full source-bound candidate proof kit: [canonical nonpromoting Drive ZIP](https://drive.google.com/file/d/1KRV9R3DtRVZBDwwQAZYhUttx3D0w_g40/view), SHA-256 `06629a149a4774acc33bfd58f6eab26c63fdca15ca3e5c72775ea90c6d525776`. Extract the **external** kit to a disposable private directory, then run its own `reproduce_g4b1c_global_finite_proxy_v1.py --stage inner_v3`, `outer_v4`, `narrow`, `producer`, `independent`, `tamper`, and `audit` in separate bounded commands. The independently verified archive replay receipt and hashes are tracked in [issue #35](https://github.com/HMarcusWH/native-eset/issues/35). **Do not copy the kit's original 46+3 sources, nodal data, or generated results into this public Git repository.** These public math-only files must remain byte-identical to their original candidate artifacts to make the mathematical review attributable.

Repository-only CI independently checks exact imported-source SHA, directed arithmetic invariants, analytic circular-disk and constant-density-cylinder special cases, the mass-weighted q identity, and absence of source arrays or physical-claim flags. Decimal sanity tests are deliberately *not proof* and do not substitute for the exact-rational source-bound replay.

## Explicit scientific firewall

Historical March fitted **6/6** development regression differs from D2d independent finite 11,520-node **3/6**. The current source-only candidate **does not** prove original March 180/120 numerical all-real root counts, a uniform numerical-to-mathematical error bound, physical Einstein/Weyl lensing, Native ESET v1.7.2 action/field equivalence, independent D3/D4 holdout, dark-matter replacement, empirical validation, or canonical Theory-State provider admission. `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`, `external_mathematical_peer_review_completed=false`. Canonical graph v0.16.39 unchanged. Last independently archived software release remains G4b.1b. Draft PR #40 remains a separate evidence-handling increment; its CI and merges cannot promote the global mathematical theorem.

## Unresolved independent review obligations

1. External mathematical review of all inequalities and inherited G4a/G4b.1c source premises, including derivative regularity at finite-density interpolation knots, mathematical source-domain endpoints and interval exhaustive cover.
2. Source-matched original March **180×120** all-real numerical-error bridge, including omitted-arc disk quadrature, finite Hernquist integration and interpolated radius root.
3. Separate physical same-source metric/Weyl and Native v1.7.2 source-equivalence audit, primary-source observational covariance and genuinely blinded held-out testing.
