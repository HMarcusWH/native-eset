# HIST-001D/D2e — Original March K180 **saturated-aperture** endpoint identity and all-aperture blocker

**Source-bound conditional mathematical candidate · 2 November 2026 · NONPROMOTING.** Neither the original March physical continuous field, Weyl lens, nor the current Native ESET v1.7.2 equations are validated by this archive. It does not use or substitute the D2d 11,520-node regenerated shadow density.

## Frozen sources and precise mathematical objects

Original 46 source files plus three archived negative controls are authenticated against composite source SHA-256 `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`. The nested original-180 source parent ZIP is `original_parent.zip` (SHA-256 `3cc0f201c40c7b260d8700b1be54709b7643d82eafceb0dc6022d95a4b1ccf18`). It contains original March `reg_v2` six-lens 180-radius stored `r,w,rho_S,S0` arrays and verified original scalar sets. `all180_parent.zip` and `c3_derivative_parent.zip` are separately verified previous candidate evidence parents, SHA-256 `2e3c13ba68bbed98ef2c529a2e331b15c666d8927da22daf1be78d33a79f6391` and `725d7ba004d1bd54fb6be2838ca995fc5ba7ce45b54213f1926f0d78bd7e7f11` respectively.

For **only** the separately defined selected smooth historical *acceleration-equivalent* mass

\[
M_\ast(r)=\left[\frac{M_b r^2}{(r+a)^2}+M_d y^3\{I_0(y)K_0(y)-I_1(y)K_1(y)\}\right]\frac{\delta f(r)}{1-\delta f(r)},\quad y=\frac r{2R_d},\quad f=\frac{r^n}{r^n+r_0^n},
\]

define a mathematical radial density `rho_*(r)=M_*'(r)/(C4pi*r²)` where `C4pi` is the ORIGINAL stored binary64 `4*np.pi` interpreted as an exact rational. This **is not** a physically selected stress-energy source or a proof of arbitrary-input original SciPy/NumPy accuracy.

For any real `A>=0`, let `phi(A,r)=1` for `r<=A`, and otherwise `1-sqrt(1-A²/r²)`. The exact continuous radial-cylinder mathematical projection on the **finite original support** is

\[
P_\ast(A)=\int_{r_{\min}}^{r_{\max}}M_\ast'(r)\,\phi(A,r)\,dr,
\]

while the original frozen-node mathematical K180 operator using original, stored **clipped** `rho_S` is

\[
Q_{\rm March,180}(A)=\sum_{j=0}^{179}w_j\,C_{4\pi}\,r_j^2\rho_{S,j}\,\phi(A,r_j).
\]

## 1. New exact *saturated-aperture* result

At `A=rmax=120 kpc`, `phi(A,r)=1` throughout the source support. Hence the **fundamental theorem of calculus** gives the exact identity

\[
P_\ast(120)=M_\ast(120)-M_\ast(r_{\min}).
\]

Using (a) the original frozen 180-point radii, positive trapezoid weights and nonnegative source-clipped density, and (b) two fully separate **512-bit and 608-bit outward exact-rational** Bessel endpoint evaluation paths, both independently confirm the following source-conditional strict upper bounds:

| Original six fitted development lens | `|Q_March,180(120)-P_*(120)|` (solar masses) | `|stored original S0(120)-P_*(120)|` (solar masses) |
|---|---:|---:|
| J0822+1828 | < 0.023 | < 0.023 |
| J0915+4211 | < 0.056 | < 0.056 |
| J0930+2855 | < 0.001 | < 0.001 |
| J1021+2028 | < 0.001 | < 0.001 |
| J1111+2234 | < 0.003 | < 0.003 |
| J1135+3720 | < 0.022 | < 0.022 |

The exact integer-micro-solar-mass directed enclosures are in `results/endpoint_saturation_producer.json` and `results/endpoint_saturation_independent.json`. Both independently rehash all original 46+3 source/negative files, and the latter uses manual IEEE754 decoding, an independently implemented special-function series and separate cancellation-aware arithmetic. Neither uses sampled SciPy Bessel values as proof. The source's last stored `S0(120)` result also differs from a mathematically summed exact-rational source `K180` by only ~10–160 micro-M☉ for the six lenses.

**Why small error is possible:** For an exactly uniform real mesh, first-order endpoint / three-point central finite differences and trapezoidal weights obey the exact **telescoping identity** `sum(w_i*grad_i(M)) == M_last-M_first` for any mass samples whatsoever. `conservation_identity.py` proves the more general exact nonuniform-mesh correction formula. The actual stored March grid is nearly, but not exactly, uniform as binary64 rationals (its radial steps differ by ≤1.43e-14 kpc). This is an **algebraic conservation property at saturation**, **not proof that arbitrary apertures or physical roots are accurate**.

## 2. Full-aperture error not resolved: a finite but useless uniform BV bound

The positive-cylinder weight `phi(A,r)` satisfies `0<=phi<=1` and is **nonincreasing in source radius r**, with `Var_[a,b](phi)=phi(A,a)-phi(A,b)` for every fixed `A`. Write `g=M_*'`, and use the previously verified **conditional** source mathematical cell bounds `|M_*''|<=M2_i`. By elementary bounded-variation trapezoidal error,

\[
|\mathrm{Trap}_h(g\phi)-P_\ast(A)|\le\tfrac12\sum_i h_i\operatorname{Var}_{[r_i,r_{i+1}]}(g\phi).
\]

On each cell, with `G_i=max(|g(r_i)|,|g(r_{i+1})|)+h_i*M2_i/2`,

\[
\operatorname{Var}(g\phi)\le G_i\bigl[\phi(A,r_i)-\phi(A,r_{i+1})\bigr]+h_i M2_i,
\]

so **uniformly for every real aperture** `A>=0`,

\[
|Q_{\ast,180}(A)-P_\ast(A)|\le\underbrace{\tfrac12\max_i(h_iG_i)+\tfrac12\sum_i h_i^2M2_i}_{\text{BV cellwise bound}}
+\underbrace{\sum_j|w_{j,\rm source}-w_{j,\rm exact\ mesh}|\,|g(r_j)|}_{\text{original source-weight rounding allowance}}.
\]

`Q_*(A)` is the K180 stencil using **smooth mathematical derivatives at the original nodes**, NOT the clipped recorded source density. It is a third distinct object. `all_aperture_bv.py` independently source-locks the C3 earlier M2 candidate and the complete 180-node Bessel/difference certificate. A second code path reuses only separately audited *global* M2 caps and independent signed node intervals, giving a larger but independently valid upper. The **tighter cellwise** all-real upper results are:

| Lens | All-real BV error upper in M☉ |
|---|---:|
| J0822 | 40,510,778,699,951,522 |
| J0915 | 105,447,993,721,149,219 |
| J0930 | 528,631,954,032,029 |
| J1021 | 27,315,778,084,889,536 |
| J1111 | 4,703,789,855,812,785 |
| J1135 | 8,222,297,894,149,834 |

These finite mathematical bounds are **too loose by many orders of magnitude** to yield an accurate K180 root-neighborhood theorem. The strong saturated result must not be extrapolated to the root apertures.

## 3. Positive smooth node-only non-identifiability counterexample

Let original adjacent radii be exactly `a=r_0`, `b=r_1`, `h=b-a`. The compact perturbation

```
rho_lambda(r) = rho_base(r) + lambda*((r-a)*(b-r))^4  if a < r < b
              = rho_base(r)                       otherwise
```

is nonnegative and C³ when `rho_base` is nonnegative C³, and leaves **every one of the original 180 radial density samples unchanged**. At `A>=b`, the extra continuous projected mass is

\[
\Delta P(A)=C_{4\pi}\lambda\,h^9\left(\frac{a^2}{630}+\frac{ah}{630}+\frac{h^2}{2310}\right)>0.
\]

The certificate sets a positive **exact rational** `lambda` giving exactly `10^9 M☉` extra projected mass at `A=120`, while leaving the original 180-point K180 quadrature unchanged. Scaling `lambda` makes the disagreement unbounded. **THIS DOES NOT preserve the selected analytic Msh mass law**; it demonstrates that nodal observations and positivity *alone* cannot select a continuous physical source or yield a continuum quadrature error theorem.

## 4. Reproducibility and strict scientific limits

Run in an isolated clean extraction:

```
python endpoint_producer.py
python endpoint_independent.py
python all_aperture_bv.py
python all_aperture_bv_independent.py
python node_identifiability_obstruction.py
python endpoint_adversarial_qa.py
python -m pytest -q test_conservation_source_free.py test_bv_source_free.py
python verify_archive.py
```

All external original input archives remain nested and SHA-protected; no original data are required in public GitHub. `results/` and manifest entries are deterministic. **No promotion** to the original March 180×120 floating algorithm's arbitrary-radius behavior, same-source physical Weyl lensing, current Native ESET v1.7.2 equations, D3/D4 observational validation, cosmology/no-CDM provider or canonical Theory-State graph. Original development-lens fitted 6/6 and separate D2d 11,520-node numerical 3/6 remain different identities. `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`, Theory-State v0.16.39 unchanged.

**Next scientific target:** cancellation-sensitive, source-derived **interval integration** of `g(r)phi(A,r)` on the six **root-relevant A-bands**, allowing the integrable `r=A` kernel cusp without a global M2 majorant; a separate validated SciPy/NumPy and clipping operation budget; only then total H and derivative/variation root transport. If source physical/microphysical selection cannot be justified, the result remains mathematical/phenomenological.

## 5. v1r1 source-review correction (2 November 2026; no claim promotion)

The originally archived v1 producer used the field name
`source_float_S0_at_Rmax_minus_exact_K180_integer_micro_Msun` for an interval
that actually enclosed **K180 minus recorded source S0**. The v1r1 producer
preserves that legacy field, adds the correctly signed and explicitly labeled
`source_float_S0_at_Rmax_minus_exact_K180_CORRECTED_integer_micro_Msun`,
and asserts the exact interval-negation relation. Historical v1 files remain
immutable. The producer does not modify the original March inputs or the six
certified absolute endpoint discrepancy ceilings.

The v1r1 QA now separately requires *all four* six-lens result lists to be
complete, unique and aligned (rather than using chained `!=` for lengths).
It rejects **26/26** adversarial claims, including missing, empty, duplicated,
extra and incorrectly signed records. The source-free suite runs **51 tests**
including the new signed-interval migration contract. This source-review
repair is nonpromoting and does not establish a root-aperture error bound.
