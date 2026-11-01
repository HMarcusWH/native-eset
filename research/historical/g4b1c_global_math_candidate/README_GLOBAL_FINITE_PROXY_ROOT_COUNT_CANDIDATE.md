# HIST-001D / G4b.1c — full finite-proxy real-radius root-count candidate v1

**Status:** local, source-conditional mathematical theorem *candidate*. **Not** a peer-reviewed proof, original March 180×120 numerical algorithm theorem, physical same-source Weyl lens, Native v1.7.2 field equivalence, observational validation or scientific-provider admission. Canonical Theory-State v0.16.39 and G4b.1b controlling software release unchanged.

## Model quantified and source authority

The only model addressed is the separately defined continuous mathematical finite proxy:

\[
H(R)= B(R)+D(R)+S(A(R))-\pi\Sigma_{crit,math}R^2,\quad
A(R)=\min(120,R/\sqrt{q(R)}),\quad q(R)=\frac{q_bB+q_dD}{B+D},
\quad R\in[r_0,120],\ r_0=\mathrm{float64}(0.02).
\]

`B(R)` is finite-support continuum Hernquist projected cylinder mass with input exact stored binary64 parameters; `D(R)` is full-azimuth continuum elliptic exponential disk mass. `S(A)` is the exact mathematical cylindrical mass of the source-generated *finite* 11,520-node-per-lens, nonnegative, piecewise-linear 3D shadow interpolant on `[r0,120]`. `Sigma_crit,math` is the prior G4a exact interval for the mathematical FlatLCDM expression, **not** observational uncertainty. The stored binary64 nodal values, scalars, lenses, redshifts, frozen March 46+3 source-code/negative inputs, and original ledger are checked against immutable external SHA256. None of this certifies the original fitted 180-radial/120-angle SciPy numerical implementation or unknown physical mass outside the finite radial interval.

All six supplied axis ratios satisfy `q_b,q_d > 0.001` and `<=1`, hence the original q clamp is inactive. All newly certified derivative and H cells have `A_hi < 120`, hence the aperture saturation is inactive in the new cells. The previous outer and inner antecedent theorems contain their own bound/clip rules.

## Exact mathematical root-count implication

For each six-lens finite-proxy input, let `Lw` and `Uw` be *already independently source-certified* all-real bands: strict `H>0` on `[r0,Lw]` (prior 42 positive degree-six Bernstein coefficients plus small-R shell lemma), and strict `H<0` on `[Uw,120]` (prior 125 contiguous exact negative outer-radius cells). The prior source-locked 0.10-kpc narrow interval `[Ln,Un]` already has **strict `H(Ln)>0`, `H(Un)<0`** and *independently* bounded `H'<0` at every real point inside; it contains exactly one simple root, conditional on those prior proofs.

For this work, a source-fixed rational `P` is chosen in `[Lw,Ln]`; its selection is an implementation policy, **not** fitted to observations. Two new exact-rational checks:

1. Partition `[Lw,P]` into disjoint, contiguous rational intervals. Prove **strict `H>0` for every real R** in each using certified interval lower enclosures, not sampled signs.
2. Partition `[P,Ln]` and `[Un,Uw]` into disjoint, contiguous rational intervals. Prove **strict `H'<0` for every real R** in each using certified derivative upper bounds, not sampled signs.

Then on `[P,Ln]`, strict decrease and the prior `H(Ln)>0` force `H>0`. On `[Un,Uw]`, strict decrease and the prior `H(Un)<0` force `H<0`. Combining the closed subintervals **leaves no unexamined radius** on the finite `[r0,120]` domain; the single narrow crossing is therefore the **only real zero on the entire finite mathematical proxy domain**, including any potential tangencies. This is an implication of the precisely specified finite continuous proxy and inherited mathematics, not a claim about the historical numerical solver or physical lensing.

## Independent exact-rational bounding methods

**Baryonic cylinder:** write `f(r)=(r/(r+a))²`; finite Hernquist shell mass `dM_B = M_b df`. For projected aperture R, let `K_R(r)=1-sqrt(1-R²/r²)` for r≥R. The cylinder mass is the exact spherical interior mass plus `∫_R^120 K_R dM_B`. `K_R(r)` is positive and strictly decreasing in r. The implementations integrate exactly known spherical shell masses, bounding `K_R` between rigorous rational square-root endpoints. Source-shadow shell masses are derived *exactly* from the piecewise-linear 3D density: the producer uses cubic-polynomial Simpson moments; the independent checker uses independently reconstructed polynomial antiderivatives. Its cylinder mass uses the **same geometric kernel** but a separate radial subdivision.

**Disk:** use the source-locked full-azimuth tangent-half-angle continuum expression with `g(t)²=1+(q_d^-2-1)4t²/(1+t²)²`, t∈[0,1], and `F(x)=1-(1+x)exp(-x)`. Here `F(Cg)/g²=C²∫_0^1 u exp(-Cgu)du` decreases in g for C>0; g increases with t when 0<q_d<=1. Therefore the positive disk angular integrand `F(Cg)/(g²(1+t²))` decreases on [0,1], admitting valid left/right rectangle bounds. All exponentials use alternating Taylor after range reduction to a small positive rational argument and outward rational squaring; π uses rigorous rational Machin arctan alternating-series bounds. `D(R)` is monotone increasing in R.

**Mass/aperture transfer:** positivity/monotonicity of B,D permits bounding them at each cell's radius endpoints. `q=(q_bB+q_dD)/(B+D)` has exact extrema over the resulting positive B/D rectangle at its four corners. Outward rational square roots then give `A_lo<=A(R)<=A_hi`, checked by exact squared inequalities. The nonnegative finite-density shadow cylinder mass increases in aperture, so `S(A_lo)_lo <= S(A(R)) <= S(A_hi)_hi`. Thus every radius in each direct-H cell obeys the rigorous lower

`H_lower = B_lo + D_lo + S_lo - pi_hi*Sigma_crit_hi*R_hi²`.

**Derivative:** for each derivative corridor, source-locked exact B' and D' integrals receive positive monotone quadrature *upper rectangles* with rational sqrt/exp bounds. The original exact formula `q'=(q_b-q_d)(B'D-BD')/(B+D)²` has a rigorously enclosed absolute upper. On the non-saturated aperture interval,

`A' <= 1/sqrt(q_lo)+R_hi*|q'|_hi/(2*q_lo^(3/2))`.

The projected finite shadow surface density `Sigma_S(A)=2∫_0^sqrt(120²-A²) rho(sqrt(A²+t²)) dt` is positive. For any **full** aperture band, independent implementations partition the t-axis, and bound each source-density integrand by an exact maximum over the entire corresponding radial source-knot range (using independently checked strict single-peak nodal density). This is a true **all-band upper** and does **not** extrapolate the earlier narrow-band `Sigma'_S>0` result beyond its certified region. Consequently, for every real R in the derivative cell:

`H'(R) <= Bp_hi + Dp_hi + 2*pi_hi*A_hi*SigmaS_band_hi*Aprime_hi - 2*pi_lo*Sigma_crit_lo*R_lo < 0`.

The independent checker reopens every source SHA-pinned original, recomputes 69,120 binary64 node pairs and 46+3 source/negative SHA records, and uses 44-bit rational sqrt, 19/20-order alternating exponential at half the range-reduced argument, cubic partitions, a different π-series order, a direct source polynomial integral (not Simpson), and different radial/angular/t sample counts. No producer mathematics or shared source adapter is imported into the verifier.

## Reproduced v1 result

| Frozen fitted development-lens label | Exact narrow root bracket (kpc) | New strict `H>0` cells | New strict `H'<0` cells | Independent least-negative derivative upper (10^9 M_sun/kpc) |
|---|---|---:|---:|---:|
| J0822+1828 | (1.883552,1.983552) | 5 | 28 | −3.821662 |
| J0915+4211 | (1.413126,1.513126) | 5 | 32 | −5.300466 |
| J0930+2855 | (4.626255,4.726255) | 13 | 45 | −2.265940 |
| J1021+2028 | (1.312053,1.412053) | 0 (monotone throughout left gap) | 9 | −16.179017 |
| J1111+2234 | (4.001186,4.101186) | 0 (monotone throughout left gap) | 26 | −9.898353 |
| J1135+3720 | (2.250347,2.350347) | 2 | 17 | −6.384509 |

**Totals:** 25 positive-H cells + 157 negative-H' cells = **182/182 independently rechecked strict certificates**, contiguous exact rational cell boundaries, no skipped gap. Under *this exact finite mathematical model and the source-locked earlier strict sign/IVT/narrow-uniqueness lemmas*, each of the six lens models has exactly one real zero on [0.02,120] kpc. No need to assume sampled first crossings or remove possible even-multiplicity extra zeros by fiat.

Additional external high-precision *nonproof* regression tests: π inclusion, 7 e^-x enclosures, 9 full elliptic disk continuum masses, 3 Hernquist-cylinder masses, 3 analytic constant-density finite shadow cylinders. These are sanity tests rather than proof of interval coverage. Fourteen self-rehashed manipulated root/physical/endpoint/count/source/margin assertions were correctly rejected by the independently pinned checker; tamper rejection is an integrity control, not another mathematical lemma.

## Source provenance and immutable artifacts

- March historical source archive: SHA `283490087c81068286303419afc98fa150c3edf9868d3dc4cb72faba0f9d1a1e` (46 original files + three archived negatives, composite `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`). Original source files are treated as *read only*, not rewritten.
- Six-lens 69,120 nodal provenance kit: SHA `804fd8e26b208c9837638ceee90998843e29b484aa3e5ca794dd5d81b3988973`.
- Prior exact sextic-inner + negative outer independent replay: 42/42 positive Bernstein coefficients, 125/125 negative source-moment outer cells (independent verifier logs included).
- Prior 0.10 kpc endpoint signs + separately independent narrow derivative and physical-nonpromotion flags: input witness SHA `5f74321ad4140640e56bf0a9a3147817879c52c40f4e91eab6487d0b61c36899`, prior derivative independent verifier report SHA `6b47c9a013f522be52ffe4afad09a03eb797ddb2b7fffaafbca29996ec82ef84`.
- New global exact-rational *producer* JSON SHA **`97f2146f48c2c7fa3af5d8cb021f68fef0e28e5ce5544d3113e3166c43b53b99`**.
- New genuinely separate global *independent checker* JSON SHA **`8b36bb01b728c8a957d1eb96a1f330fef74516054ff6057a60c8f376db6eae6a`**.
- Self-rehashed forged-result SHA and claim QA report SHA **`c0f364f2d6dbec550d628166077cdd7ecc77c045c57b40721c48b4483cf07895`**.

## Reproduce without internet or changing any protected source

From a clean extracted immutable archive, replay in **six independently bounded invocations** (not one large timed interactive session): `python reproduce_g4b1c_global_finite_proxy_v1.py --stage inner_v3`, then `--stage outer_v4`, `--stage narrow`, `--stage producer`, `--stage independent`, `--stage tamper`, and finally `--stage audit` to recheck all original source-file SHA manifest entries and immutable result bytes. Each stage has its own PASS/FAIL and original SHA checks; a larger unrestricted host may use `--stage all`. This reexecutes the preceding v3 inner and v4 outer original-source independent checkers, the previous narrow derivative checker, then the new producer, separate independent verifier and 14 self-rehashed adversarial controls. The **core proof replay uses only Python 3.11+ standard library**; optional independent `mpmath` numerical controls, when installed, can be run separately with `python g4b1c_global_numeric_crosschecks.py`. A global proof candidate requires PASS at every stage; an omitted or timed-out stage is not a pass.

The replay does **not** re-run an original March 180×120 numerical solver and does **not** claim a current Native v1.7.2 source action, physical metric/Weyl map, full cosmology, new held-out dataset, observational covariance or empirical viability. A source-conditional finite-proxy mathematical root-count certificate can be correct even while the original fitted numerical method fails convergence or the physical ESET theory remains unverified.

**Release rule:** this is **LOCAL MATHEMATICAL CANDIDATE / NO GITHUB REVIEW OR CANONICAL PHYSICS PROMOTION**. Further external mathematics review and separate source-locked GitHub CI/Drive release gates are required before public scientific statements. G4b.1b controlling software archive remains the last independently verified release. Draft PR #40 is an external-replay infrastructure PR and must not be mislabeled as a proof of this new global theorem.
