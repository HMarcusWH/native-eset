# HIST-001D — Original March180 sampled-H floating-point postprocessing reconciliation

**3 November 2026 | source-conditional mathematical/computational candidate | NONPROMOTING**

## 0. What has been audited

The March `reg_v2` solver **does not find a root of a continuously recomputed original K180 projection at arbitrary real radius**. It computes a stored array of 180 projected-mass values, subtracts the Einstein target at the same 180 radii, and uses the first sign change plus a linear interpolation of the **sampled residual array**:

```python
# Original source operator order (relevant excerpts)
target = np.pi * r_grid_kpc**2 * sigma_crit
vals = projected_mass_msun - target
idx = np.where(np.diff(np.sign(vals)))[0]
i = int(idx[0])
return float(x0 - y0*(x1-x0)/(y1-y0))
```

The upstream original source constructs `projected_mass_msun` by summing frozen bulge, disk and circularized shadow projections. This audit **fixes those three stored binary64 columns** and independently authenticates the nested March source against 46 original files plus three negative controls. It only studies the last arithmetic/subtraction/interpolation layer. It is not a theorem for the upstream original SciPy Bessel function, numerical gradients, circularized density, D120 angular quadrature or newly evaluated off-grid source.

## 1. Exact original-grid replay and arithmetic budget

From the source-locked 180 stored binary64 values of each of B, D, circularized S, R, and stored sigma and pi, reexecute **round-to-nearest ties-even binary64 after each elementary operation**. Two implementations reproduce 1080/1080 original binary64 H samples: (a) exact Fraction arithmetic with explicitly rounded output after each operation; (b) independent native NumPy array operations using the source's original expression order.

The source-locked March-180 original sign-chart records and the separate strict-original six-lens portability CSV are consistent: returned root divided by original binary64 kpc-per-arcsecond scale reproduces the original CSV predicted Einstein radius in arcseconds **exactly in binary64 for all six lenses**. The original 180-point sign charts have exactly one positive-to-negative crossing per lens. Source-returned binary64 first-sign-change roots match the original archived March-180 sign-chart root value exactly. In the exact-rational interpolation of those *stored* binary64 H endpoints, the rounding in the reported root is below **0.000000000000000418 kpc**, and the difference to the exact nodal residual assembled from the stored B, D, S and pi sigma R² is below **0.000000000000001158 kpc**.

Separately, compare the source-computed nodal H with the deliberately defined mathematical off-grid finite PL extension **at the exact stored R nodes**, using source-locked B_PL, D_PL, S0_PL and rational q(R) with 112-bit directed rational sqrt enclosures. The resulting exact a posteriori upper bounds are:

| Lens | Source-vs-PL nodal H upper (solar masses) | Original sampled root vs finite PL unique root strict lower (kpc) | Relative order |
|---|---:|---:|---|
| J0822+1828 | 0.043306 | 0.036005161 | sampled root left |
| J0915+4211 | 0.057939 | 0.013942622 | sampled root left |
| J0930+2855 | 0.036427 | 0.000478792 | sampled root right |
| J1021+2028 | 0.041572 | 0.059514056 | sampled root left |
| J1111+2234 | 0.023544 | 0.009740355 | sampled root left |
| J1135+3720 | 0.032232 | 0.023161636 | sampled root left |

All **1080 sampled nodal signs agree** with the explicitly defined H_finite at the same stored nodes. The differences between the two mathematical root definitions are therefore *not* due to the final floating-point residual calculation or the last binary64 interpolation roundoff. The root-object distinction is genuinely the different interpolation construction: the March output roots the residual **after sampling**, while H_finite composes individually interpolated B, D, q and S0 **before** solving its off-grid equation.

The table's bounds are **outward rounded**, with the full exact-rational records in the protected data-dependent result JSON. The final floating error at nodes is tiny because the inputs are already fixed doubles. These bounds **do not constrain errors upstream of those captured columns**.

## 2. What this does not prove

- It does not prove an arbitrary-radius error bound for an original physical or mathematical *continuous* March source. The original code never defined the claimed off-grid operator by evaluating a new K180 integral at a proposed real R in its root solver.
- It does not make the original reported radii zeros of the defined off-grid H_finite. PR #55's independent finite-model one-root theorem and root brackets refer to that explicitly defined mathematical extension.
- It does not establish unique roots of the selected smooth M* model; PR #55 establishes only conditional existence and local ordering.
- It does not prove the accuracy of original upstream SciPy/NumPy gradient construction, shadow density clipping, D120 disk projection, angular circularization or the original physical Weyl field.
- It does not prove a current Native ESET v1.7.2 covariant physical density/provider, blinded D3/D4 success, no-particle-CDM cosmology or empirical validation.

**Status:** `physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`, controlling G4b.1b main and Theory-State v0.16.39 unchanged.

## 3. Reproducibility/independence

`float_bridge.py` authenticates the protected original March arrays and the source-released sign chart, exact-rounds every final operation and derives the rational arithmetic and root-separation bounds. `independent_float_check.py` separately uses native NumPy and an independently implemented integer sqrt enclosure, and independently recomputes every output field. `claim_guard.py` blocks scientific promotion and malformed records. `adversarial_qa.py` rejects 22 specific false-claim/identity mutations. 19 source-free synthetic tests exercise rounding, interpolation identities, rational square-root bounds and invalid inputs.

The protected release contains both SHA-locked parent archives, full resultant JSONs, code, tests and a SHA256/CRC manifest. Its public GitHub draft carries *only* standalone source, synthetic tests, and this scope note; no protected original March source or data and no physical equations are committed. The exact-root code is a postprocessing audit, not a source-law proof.

## 4. Actual next mathematical/physical gate

If the scientific objective is the historical **numerical** computation, its returned roots have now been reconciled to the original 180-sample residual interpolation. Further arbitrary-radius error bounds require choosing a *new* explicit off-grid original-source computation and bounding its upstream NumPy/SciPy, disk quadrature and shadow-density steps; that would be a different mathematical object. If the objective is physical lensing, a separately authorized same-source covariant density and Weyl response plus no-refit observational validation are still required. An independent Bessel interval engine and the selected smooth H root-count theorem remain separate tasks.
