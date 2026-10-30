# HIST-001D/D2e-G2b — certified full-angular analytic exponential disk

**Scope:** a rigorously bounded *mathematical analytic-continuum disk mass* for exact frozen binary64 parameters, independent of the historical 1024-angle numerical trapezoid. All six SWELLS Set A lenses were fitted development cases. This does not establish physical lensing, old numerical implementation error, root topology, independent observations, or Native ESET v1.7.2 field-equation equivalence.

## Fixed history and authority

Previous G1/G2 [PR #28](https://github.com/HMarcusWH/native-eset/pull/28) introduced a finite exact-rational Hernquist cylinder mass enclosure and a **very coarse** geometry-only disk bound. D2e-F [PR #26](https://github.com/HMarcusWH/native-eset/pull/26) bounds finite-discrete shadow mass over every real aperture in a reported interval. The original frozen March 46+3 SHA is `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`; historically fitted original 180/120 **6/6** and independently integrated D2d finite-structured **3/6** remain separate, source-locked numerical execution identities.

## 1. Exact trigonometric-free integral transformation

The analytic elliptical exponential disk from the historical mathematical model has exact frozen scalar mass `M`, scale `s`, axis ratio `0<q<=1`, and positive radial cutoff `R`. Let

```
H(v) = 1 - (1+v)*exp(-v),
g(theta)^2 = cos(theta)^2 + sin(theta)^2/q^2.

D(R)/M = [1/(2*pi*q)] integral[0,2*pi] H((R/s)*g(theta))/g(theta)^2 dtheta.
```

All four quadrants are symmetric. On a quadrant substitute `tan(theta)=q*tan(phi)`. The Jacobian and the `1/g^2` factor cancel exactly, yielding

```
D(R)/M = (2/pi) integral[0,pi/2]
         H((R/s)/sqrt(cos(phi)^2+q^2*sin(phi)^2)) dphi.
```

No historic source trapezoid, omitted angular arc, fitted correction, or numerical angular calibration is used in this identity. It is the source-equivalent analytic periodic disk **as a mathematical continuum object**.

## 2. Rigorous composite midpoint error, independent of a guessed tolerance

Set `x=R/s`, `alpha=1-q^2`, `d(phi)=1-alpha*sin(phi)^2`, and `v(phi)=x*d(phi)^(-1/2)`. Then `d∈[q^2,1]`, `|d'|<=alpha`, `|d''|<=2*alpha` and

```
|v'| <= x*alpha/(2*q^3),
|v''| <= x*(3*alpha^2/(4*q^5) + alpha/q^3).
```

Since `H'(v)=v*exp(-v)`, `|H'(v)|<=v<=x/q`, and `H''(v)=(1-v)*exp(-v)` obeys `|H''(v)|<=1` for all nonnegative `v`, the normalized integrand `h(phi)=H(v(phi))` has the exact finite bound

```
|h''(phi)| <= K = x^2*(alpha^2/q^6 + alpha/q^4).
```

The standard composite midpoint identity, derived by Taylor remainder integration on each subinterval, gives the global bound

```
|D(R)/M - (1/N)*sum_{j=0}^{N-1} h((2j+1)*pi/(4N))|
     <= K*pi^2/(96*N^2).
```

**The implemented bound is stronger and remains rigorous:** on each angular cell (j), `d(phi)` is decreasing, so evaluate a rational *upper* bound on `sin(phi)` at the cell's right endpoint (the last physical endpoint uses the exact identity `sin(pi/2)=1`). Thus the certified `dmin_j = 1-alpha*sin_upper_j^2 >= q^2` is a valid all-cell lower bound. Replace the global `K` by

```
K_j = x^2*(alpha^2/dmin_j^3 + alpha/dmin_j^2).
|normalized midpoint error|
    <= pi^2/(96*N^3) * sum_{j=0}^{N-1} K_j
    <= K*pi^2/(96*N^2).
```

The program rounds each cell's rational error *upward* and accumulates it with a directed Decimal context; no huge cross-cell rational denominator is needed. The original global `K` is preserved in the receipt as an auditable fallback theoretical bound, not used to dilute the tighter interval. Both are mathematical truncation guarantees, not statistical error bars or observed mesh convergence estimates. For near-circular q, both bounds vanish smoothly.

## 3. Certified midpoint values

Each midpoint angle `phi=(2j+1)*pi/(4N)` is trapped between exact rational lower/upper Machin-pi multiples. On `[0,pi/2]`, sine is monotone increasing. An alternating rational Taylor series of 12 terms (and its next-term remainder) encloses sine at each endpoint. These enclose `d(phi)`; the square root uses integer-isqrt rational bounds at 100 binary bits. `H(v)` is monotone increasing in `v`, and the previously frozen G2 exact rational exponential-series routine bounds its value at the resulting `v` endpoints. Every midpoint contributes an exact rational lower and upper value; directed 65-digit Decimal summation and division give a certified interval for the sample mean.

The explicit analytic midpoint remainder is subtracted from the lower bound and added to the upper bound under directed rounding; the normalized answer is intersected with `[0,1]` from positive total-disk mass. Finally, multiplication by exact source binary64 `M` uses directed Decimal rounding. **No floating trigonometric, logarithmic or exponential approximation occurs in the proof computation**.

## 4. Registered numerical execution identity

- Registered midpoint count: **1,024** (not the same angular grid as original source).
- Predeclared relative interval-width *target*: **0.01 = 1%**; failure to reach it retains a sound interval and reports `target_met=false`.
- Mathematical model: exact binary64 `M, s, q, R`; full analytic azimuth `0..2*pi`; no new fit or source modification.
- A radius-band enclosure follows by positivity and monotonicity: at every real `R∈[Rlo,Rhi]`, `D(Rlo) lower <= D(R) <= D(Rhi) upper`.
- The refined disk interval intersects the independent G2 coarse **analytic-continuum** enclosure. Their intersection remains a valid mathematical enclosure, even if one independent numerical interval is not nested inside the other.
- Existing G1 finite-analytic Hernquist bounds and exact-rational D2e-F four-corner q_eff mapping then give an improved mathematical *analytic-continuum* aperture interval over the fixed ±2% D2d guard.
- No bound here has yet established the original 1,024-angle **floating implementation's** numerical error. Existing source output is only compared as an empirical diagnostic, never substituted for certified mathematics.

## 5. Implementation, evidence and negative controls

```bash
python tools/hist001d_d2e_g2b_angular_boxes.py --source-root research/legacy/hist001 --out runs/hist001d_d2e_g2b
python tools/hist001d_d2e_g2b_angular_boxes.py --source-root research/legacy/hist001 --verify runs/hist001d_d2e_g2b/receipt.json
```

A new pure module `src/native_eset/numerics/certified_disk_angular.py` evaluates rigorous midpoint enclosures. Tests cover high-precision independent circular disk, numerical independent full-period quadrature (as a **test** rather than the proof), angular parameter extremes, malformed inputs, proof-envelope compatibility, nonpromoting claims, source SHA and rehashed fake provider/numerical receipts. The source runner reconstructs the original six fitted lenses from verified 46+3 March files, reproduces the original historical 6/6 without refit, uses the SHA-pinned G1/G2 analytic source, reports both independent coarse/refined bounds, and produces canonical source-reexecution receipts.

CI requires Ubuntu/Windows × Python 3.10/3.12/3.13, complete previous D2e A–F and G1/G2 numerical source replays, Git index SHA manifest, Ruff, source reexecution verifier and A–G2b artifact export after merge. A living Drive pointer advances only after **exact merged SHA** success, immutable artifact download and byte/hashes readback.

## 6. Explicit remaining blockers

Even successful G2b does **not** certify the old SciPy finite bulge integrator or 1024-angle periodic disk numerical approximation, the original source-law density-gradient continuum, arbitrary all-R total numerical error, any root count/uniqueness including tangent roots, missing physical matter outside [0.02,120] kpc, D3 published SWELLS covariance/IMF, D4 genuinely blind holdout, D5 same-solution metric/Weyl, HIST-001E current native action/field transport, or physical/empirical model promotion.

The new proof's quantitative width belongs only to the **frozen-parameter mathematical continuum disk**. The historical fitted 6/6 and independent finite-source D2d 3/6 are still different software/model execution identities. D2e scientific issue #19 and G parent #27 remain OPEN.
