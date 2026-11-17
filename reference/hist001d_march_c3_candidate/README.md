# HIST-001D / D2e — rigorous *conservative* M″ and M‴ derivative bounds on the original March radial mesh

**2 November 2026 | mathematical certificate CANDIDATE | STRICTLY NONPROMOTING.**

## 1. Exact scope

This research kit takes the **same exact stored binary64 parameters and original 180 radial nodes** as the verified historical March `ra0_gated_geometry_sigmoid_reg_v2` *source*; it does **not** replace the source with the separately generated 11,520-node D2d density model. Its target is the independently defined smooth acceleration-equivalent shadow mass

\[
\begin{aligned}
y&=R/(2R_d),\qquad F(y)=I_0(y)K_0(y)-I_1(y)K_1(y),\\
A(R)&=M_b\frac{R^2}{(R+a)^2}+M_d y^3F(y),\\
f(R)&=\frac{R^n}{R^n+r_0^n}, \qquad g(R)=\frac{\delta f(R)}{1-\delta f(R)},\\
M_{\rm sh}(R)&=A(R)g(R), \quad R\in[\mathrm{float64}(0.02),120]\;\mathrm{kpc}.
\end{aligned}
\]

All six archived original finite parameter sets have positive masses and scale radii, `4 < n < 5` and `0 < delta < 1`, which are explicitly enforced. Every binary64 input is interpreted as its *exact rational value*. The original 46 source files plus three negative controls and all six 180-node source input arrays are independently SHA-256 verified against the archived identities.

**This smooth function is a mathematical extension, not an authorized physical Weyl density and NOT the original source's certified arbitrary-radius numerical behavior.** Source mass/density clips and original binary64 operation errors are not proved inactive or bounded at all real radii.

## 2. Rigorous special-function bounds, avoiding numerical Bessel calls

For real `y > 0`, DLMF 10.32.3 gives `I_m(y)=1/pi * ∫[0,pi] exp(y*cos(theta))*cos(m*theta) dtheta` for integer `m>=0`. Differentiating under the integral implies `|I_m^(j)(y)| <= exp(y)` for all nonnegative integers `j`.

DLMF 10.32.9 gives `K_m(y)=∫[0,infinity] exp(-y*cosh(t))*cosh(m*t) dt`; differentiation, positivity, and `cosh(t)^j*cosh(m*t)<=cosh((m+j)t)` yield `|K_m^(j)(y)|<=K_(m+j)(y)`. The positive-integral representation also proves `K_v(y)` increases with nonnegative order `v`, so `K_(m+j)(y)<=K_(m+j+1/2)(y)`.

Using the exact half-integer formula (DLMF 10.39.2 and its `K` three-term recurrence),

\[
K_{\ell+1/2}(y)=\sqrt{\pi/(2y)}e^{-y}P_\ell(1/y),\quad
P_\ell(x)=\sum_{s=0}^\ell\frac{(\ell+s)!}{s!(\ell-s)!}\left(\frac{x}{2}\right)^s,
\]

for integer `ell<=4`. The `exp(y)` and `exp(-y)` cancel *symbolically* in each product bound. Thus for `k=0,1,2,3` and all `y >= y_min>0`,

\[
|F^{(k)}(y)| \le \sqrt{\frac{22}{14\,y_{\min}}}
\sum_{j=0}^k {k\choose j}
\bigl[P_{k-j}(1/y_{\min})+P_{k-j+1}(1/y_{\min})\bigr].
\]

Here `pi < 22/7` and the square-root factor is rounded **outward** to a 64-bit dyadic rational (producer) or to a separately coded 96-bit dyadic rational (independent verifier); neither numerical evaluation of `I` nor `K` is used in the proof. The inverse-radius polynomials are positive, hence their upper envelopes are attained at the lower interval endpoint. Separate producer and verifier implement `P_l` respectively via exact factorial sums and a recurrence.

Use Leibniz's rule on `y^3 F(y)` through order three and the explicit exact rational bulge derivatives to obtain four nonnegative enclosures `A_0,...,A_3` on each rational radius band.

## 3. Radius-proxy and third derivatives

Write `p=f(1-f)`. The *exact* identities

\[
\begin{aligned}
f' &=np/R,\\
f''&=np[n(1-2f)-1]/R^2,\\
f'''&=np\{[n(1-2f)-2][n(1-2f)-1]-2n^2p\}/R^3
\end{aligned}
\]

show that `0<p<=1/4` and `|1-2f|<=1` are sufficient for global positive derivative majorants. Because **the six actual source exponents all satisfy `4<n<5`**, tighter exact rational `p` upper bounds are available: below `R<=r0`, `p<=min(1/4,(R/r0)^4)`; above `R>=r0`, `p<=min(1/4,(r0/R)^4)`. Each interval uses only its correct endpoint, and intervals crossing `r0` retain `p<=1/4`. Likewise `f_max<=min(1,(R_hi/r0)^4)` below `r0`, else `f_max<=1`. Consequently `1-delta*f >= 1-delta*f_max >0` and the first three derivatives of `g(f)=delta*f/(1-delta*f)` are bounded using ordinary chain rules. No floating-point real-power or special-function evaluation is needed.

Finally the exact *upper bounds* for the chosen smooth mass are

\[
\begin{aligned}
\|M_{\rm sh}''\|_{\infty,[u,v]} &\le A_2G_0+2A_1G_1+A_0G_2,\\
\|M_{\rm sh}'''\|_{\infty,[u,v]}&\le A_3G_0+3A_2G_1+3A_1G_2+A_0G_3.
\end{aligned}
\]

Each of the **179 frozen original radial intervals** is subdivided into four exact-rational subintervals. Their individual maxima cover the entire original mesh. Each interior nonuniform three-point gradient bound takes the maximum on its two adjacent original cells; each one-sided endpoint takes its original neighbor cell. Thus all **4,296 subcells / 1,074 source cells / 1,080 formal ideal exact-gradient error caps** are covered with no numerical sampling gaps.

## 4. Result: finite certified mathematical upper candidates, but insufficient accuracy

Exact integer ceilings from the independently source-verified producer and verifier:

| Source-lens | global `|M''|` upper (M☉/kpc²) | global `|M'''|` upper (M☉/kpc³) | maximum *ideal exact-sample finite-difference* upper (M☉/kpc) |
|---|---:|---:|---:|
| J0822+1828 | 3,289,131,675,291,070 | 2,574,152,987,582,747 | 1,102,318,487,154,823 |
| J0915+4211 | 8,580,187,341,698,067 | 7,363,575,857,229,276 | 2,875,561,109,656,270 |
| J0930+2855 | 48,858,789,753,890 | 354,322,806,332,896 | 26,531,359,838,189 |
| J1021+2028 | 2,258,773,715,294,722 | 2,592,634,532,773,229 | 757,004,665,813,027 |
| J1111+2234 | 355,383,409,192,591 | 136,980,539,280,519 | 119,103,076,633,876 |
| J1135+3720 | 646,665,104,047,851 | 305,838,075,932,237 | 216,723,126,211,346 |

A separate mpmath/Bessel symbolic-derivative **24-sample numerical sanity test** passes. This is *not* part of the rigorous proof. 20 source-free mathematical unit tests and 21 source/claim/bound adversarial mutations are also checked separately. Passing them does not imply formal proof-assistant verification or external referee acceptance.

**The exact gradient discrepancy cap remains much too large to isolate a historical physical/root model**. An ideal exact sample is `M_sh(r_i)` for this chosen smooth function; the original March program uses *rounded and possibly clipped* samples, and an exact mathematical error bound on those original operations is still missing.

## 5. Explicitly OPEN and forbidden inferences

- **Original floating-point operations:** No interval-certified error for SciPy Bessel, source `gbar`/epsilon/real-power, products, clipping or NumPy gradient. To use these bounds, certify node-level `|M_software(r_i)−M_smooth(r_i)|<=E_i` and propagate the errors through the original gradient weights.
- **Original source clipping:** Nonnegative source-node arrays are verified; whether off-grid mass or derivative clips are inactive is **not** established.
- **Physical source:** The `Mbar_acc` is the historical acceleration-equivalent mass definition, not a derived physical Weyl solution, smooth 3D matter profile or current Native ESET v1.7.2 action.
- **Full original numeric H or uniqueness:** The propagated density/K180/D120/q/Sigma full uniform error and derivative/variation root-count bound remain **UNRESOLVED**. The historical fitted 6/6 and independent D2d 11,520 numerical 3/6 are distinct development identities; no empirical holdout has been tested.
- **Admission:** No physical provider, CDM removal, production-scoring permission, new canonical Theory-State verdict, or empirical validation. Theory-State remains v0.16.39; verified G4b.1b remains controlling software release.

**Next rational direction:** obtain source operation-level Bessel and real-power *value* enclosures and sharpen derivative bands through cancellation-aware product representations. The present rigorous but coarse global majorants are useful as a source-compatible baseline, not a final numerical approximation theorem.

## 6. Reproduction

This archive contains the unchanged previously SHA-verified source diagnostic as `inputs/frozen_smooth_shadow_gradient_parent.zip`, SHA256 `3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18`. The independent verifier verifies all original 46+3 source files and six nodal inventories without importing the producer or math helper. The pinned source anchors were rechecked from original files, not accepted from names or titles.

From the extracted archive, using Python 3.10+:

```bash
python src/produce.py
python src/independent_verify.py
python src/adversarial_qa.py
python -m pytest -q tests/test_source_free.py
# Optional numeric sanity (not proof): requires sympy and mpmath
python src/highprecision_sanity.py
```

The producer and independently implemented exact verifier use only the Python **standard library**. `pytest`, `sympy` and `mpmath` are optional testing/sanity dependencies. Each source-dependent result should be compared to `RESULT_HASHES.json` after replay. The archive SHA manifest and ZIP CRCs are additionally checked by `src/verify_archive.py`. All code/inputs/results have exact SHA-256 identities.

**Public mathematical references:** [DLMF 10.32.3](https://dlmf.nist.gov/10.32.E3), [DLMF 10.32.9](https://dlmf.nist.gov/10.32.E9), [DLMF 10.39.2](https://dlmf.nist.gov/10.39.E2).
