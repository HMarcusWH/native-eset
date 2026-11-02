# HIST-001D — first original March density knot, exact-rational Bessel cancellation audit (DRAFT)

**Research status: NONPROMOTING MATHEMATICAL CANDIDATE — independent external peer review not performed.** The complete source-bound archive is retained off GitHub. Public repository additions are source-only code, source-free unit tests and this scope contract; no old 46+3 original source files, six 180-node numerical arrays, new observational data or physical providers are imported.

## Defined mathematical comparison

The original March six fitted development lenses use 180 source radial nodes, with first two radii exactly the original binary64 0.02 and 0.6902793296089386... kpc. Interpret the original recorded positive first-node shadow density, source FOUR_PI coefficient and first radius as *exact stored IEEE754 dyadics*. The comparison mathematical object is the separately defined smooth continuation of the source's historical acceleration-equivalent shadow mass:

    y=R/(2Rd); F(y)=I0(y)*K0(y)-I1(y)*K1(y)
    A(R)=Mb*R^2/(R+a)^2+Md*y^3*F(y)
    f(R)=R^n/(R^n+r0^n); G(R)=delta*f/(1-delta*f)
    M(R)=A(R)*G(R); rho_smooth(R)=M'(R)/(FOUR_PI_source*R^2)

No SciPy Bessel/NumPy float is used to establish mathematical enclosures for the new target. Rational log bounds use dyadic range reduction and arctanh with positive remainder; gamma uses a bounded Euler–Maclaurin harmonic-number term; I0,I1,K0,K1 use positive series and harmonic-index tails; fractional powers use explicitly bounded exponential Taylor series. All arithmetic outward quantized to rational dyadics. An independently implemented verifier uses 160-bit precision, longer series, a cancellation-combined F identity and separately authenticated original-source values.

**New conditional exact result:** for each of the six original 180-node source records the stored first density divided by the smooth derivative density is STRICTLY GREATER than the certified integer floors 6,796,810; 7,715,532; 11,331,479; 4,316,684; 10,836,740; 7,827,416. The stored first-node mathematical gradient FOUR_PI_stored R0^2 rho_source differs from the exact selected-smooth-mass secant [M(R1)-M(R0)]/(R1-R0) by LESS THAN 3e-6 solar masses per kpc. The latter is an **a posteriori fixed-input stored-result discrepancy**, not a general error bound for original SciPy/NumPy operations.

The dominant gap is between the original wide-cell ideal finite-difference secant and the selected exact mathematical derivative at the inner radius. It does NOT imply the true physical shadow field is that smooth continuation, or that first-node error dominates the integrated lensing mass or root position.

## Verification and claims

The complete standalone 11-member archive SHA256 is recorded in issue #19, with nested original 46+3 source lock, producer/independent/18-case QA results, source-free tests, manifest and replay verifier. The result passes two independently written strict rational analyses, nineteen expected source/claim tamper rejections including the original archive SHA precondition, and fifteen local mathematical tests. The repository-only CI tests do NOT replay private original source data.

Original historical March fitted 6/6 and distinct regenerated 11,520-node D2d numerical 3/6 remain different model identities. No all-node floating error, all-real M''/M''' close bound, original physical continuous shadow density, original March 180x120 offgrid root uniqueness, complete H root transfer, current Native ESET v1.7.2 same-solution Weyl, CDM removal, independent observational holdout, empirical validation, production scoring, physical provider, or canonical Theory-State v0.16.39 graph promotion.

Source-math references (not physics endorsement): NIST DLMF 10.31 (integer-order modified Bessel power series), DLMF 10.32 (integrals); https://link.springer.com/article/10.1186/s13660-019-2104-9 for harmonic-number/Euler-constant remainder bounds.
