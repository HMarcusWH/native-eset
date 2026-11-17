# HIST-001D — original March first-node exact-rational Bessel discrepancy (CANDIDATE)

Date: 2026-11-02. **NONPROMOTING / NOT peer-reviewed / NOT original source float error theorem.**

## Scope and source identities

The original frozen March 180-radial grid begins at R0 = stored IEEE-754 binary64(0.02) kpc and its next node is 0.6902793296089386 kpc. The first original 180-node 3D shadow-density record is an independently SHA-locked *binary64 output of the original source*, not a physical density measurement. Original historical 46 source files and three archived negative controls are individually SHA-locked, composite `fa7e77300d7a6e5f095d3781c23eb96bc57fea4c38f76b155278079d7f19913a`.

This package compares that exact stored first-node density rho_grid to the derivative of the **separately defined smooth mathematical continuation** of the same frozen historical acceleration-equivalent mass law:

    y=R/(2 Rd)
    F(y)=I0(y) K0(y) - I1(y) K1(y)
    M_bar_acc=Mb R^2/(R+a)^2 + Md y^3 F(y)
    f=R^n/(R^n+r0^n)
    G=delta*f/(1-delta*f)
    M_sh_smooth=M_bar_acc*G
    rho_smooth(R)=M_sh_smooth'(R)/(stored_binary64_4pi*R^2)

**All stored binary64 parameters are regarded as exact dyadics in this defined mathematical target.** The source's first density is the source's finite-grid gradient/clipping output; the smooth derivative is a new diagnostic, not the actual historical off-grid floating implementation or a physically sourced Weyl/Native v1.7.2 density.

For the first node, two independent exact-rational outward arithmetic routes establish rho_grid/rho_smooth >= the following integer floors:

| Frozen development lens | Rigorous ratio floor |
|---|---:|
| J0822+1828 | 6,796,810 |
| J0915+4211 | 7,715,532 |
| J0930+2855 | 11,331,479 |
| J1021+2028 | 4,316,684 |
| J1111+2234 | 10,836,740 |
| J1135+3720 | 7,827,416 |

### Original first-node secant isolated

The original source's second stored radius is **0.6902793296089386 kpc**. The same rational Bessel/log/power intervals also evaluate M_sh_smooth at these TWO exact source radii and bound their exact mathematical first forward secant

    S_ideal=[M_sh_smooth(r1)-M_sh_smooth(r0)]/(r1-r0).

Independently interpreting the actual first archived binary64 density, radius, and original binary64 FOUR_PI as exact rational stored operands yields

    D_stored = (FOUR_PI_source)*r0^2*rho_shadow_source_first_node.

For **every one of the six source lenses**, two implementations prove the separate, strict **a posteriori fixed-input discrepancy**

    |D_stored-S_ideal| < 3/1,000,000 M_sun/kpc.

This differs in scope from a blanket guarantee for original SciPy/NumPy functions, source rounding behavior on new inputs, or off-grid derivative evaluation. The combined facts show that the original *stored* first-node gradient is extremely close to the exact ideal finite secant, while the ideal finite secant is millions of times the source-derived smooth derivative at r0. The large mathematical discrepancy is thus demonstrably the first-cell finite-difference truncation effect in this selected mass model, rather than a comparably large stored-result versus secant discrepancy.

**No replacement 11,520-node data** are ever substituted into this original 180-node calculation.

## Proof arithmetic — no SciPy Bessel or exponent values as proof

1. The original-source integer-order I/K identity is enclosed at the exact rational first-node argument using *positive* power series for I0/I1 and the harmonic-number logarithmic expansions for K0/K1:

       K0(y)= -(log(y/2)+gamma)*I0(y) + sum_{k>=1} H_k*(y^2/4)^k/(k!)^2
       K1(y)= I0(y)/y +(log(y/2)+gamma)*I1(y)
              -(2/y)*sum_{k>=1} k H_k*(y^2/4)^k/(k!)^2

   Each omitted positive tail has an explicit geometric-ratio upper bound; no raw infinite-series truncation is treated as exact. To reduce subtraction, the **independent verifier** computes F via the fully combined algebraic identity, rather than subtracting two independently evaluated K products.
2. Rational log bounds use dyadic range reduction x=2^e u, 1<=u<2, followed by atanh series (t=(u-1)/(u+1)<=1/3) and its exact positive remainder bound.
3. Euler gamma is enclosed using the Euler–Maclaurin harmonic-number inequality, with H_500 for producer and H_700 for checker:

       H_N-log(N)-1/(2N)+1/(12N^2)-1/(120N^4) <= gamma
       gamma <= H_N-log(N)-1/(2N)+1/(12N^2)

   Mathematical authority for the inequality: https://link.springer.com/article/10.1186/s13660-019-2104-9 . Integer-order I/K series are classical consequences of the modified Bessel differential equation and DLMF 10.31 (https://dlmf.nist.gov/10.31). All implementation statements need independent mathematical review.
4. The real noninteger power in f is enclosed by log/exp using exact rational Taylor series with positive tail bounds and power-of-two argument reduction. Hence the Bessel and gate calculus never relies on a SciPy `iv/kv`, NumPy `gradient`, or a float `pow` value as proof input.
5. The derivative algebra uses F' = 2*(I1*K0 - I0*K1 + I1*K1/y), M'_sh=M'_bar*G+M_bar*G', and f'=n*f*(1-f)/R. All intermediate arithmetic is outward-quantized to rational dyadic endpoints. The numerator is strictly positive and the stored-source numerator strictly exceeds its certified upper endpoint in every lens.
6. Different rigorous checker: independent code (not importing producer) uses H_700, 120-term dyadic atanh, 45 terms of Bessel power series, 160-bit outward quantization, a cancellation-reduced F expression and separate exponential reduction.

The source-free 90-digit mpmath comparison is a *sanity check only*, not the proof.

## Audit and forbidden transfers

Replay on Python >=3.10, using the bundled exact SHA-locked parent ZIP:

    python first_node_certificate.py
    python independent_first_node.py
    python adversarial_first_node.py
    python -m pytest -q test_first_node_source_free.py
    python verify_archive.py --replay

The integrity verifier checks all ZIP members and result SHA digests. Full replay can be split across commands; failures remain FAIL_CLOSED. The scripts use the Python standard library except the optional separate pytest test runner.

**NOT ESTABLISHED:** original source float-operation error; original source off-grid clip branch; mathematical/physical source equivalence; all-R M''/M''' accuracy; global original 180x120 H numerical error/root count; true continuum shadow density; same-solution physical Weyl lensing; Native ESET v1.7.2 equivalence; held-out empirical validation; CDM removal; or canonical Theory-State/provider promotion. The original source 180-grid fitted 6/6 and independently defined 11,520-node D2d numeric 3/6 remain distinct. Canonical scientific graph v0.16.39 and controlling G4b.1b software release unchanged.
