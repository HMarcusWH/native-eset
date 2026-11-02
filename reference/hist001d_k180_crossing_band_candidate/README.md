# HIST-001D original March K180 — whole crossing-aperture band audit

**DRAFT / mathematical candidate / nonpromoting (2026-11-02).**

This directory provides source-only reusable code. Its protected original 46+3 March source files, original frozen six-by-180 binary64 arrays and all numerical result JSON files remain outside GitHub. For the mathematical scope, exact identities, interval inequalities and explicit non-claims, read `docs/HIST001D_K180_SIX_CROSSING_BANDS_SCOPE.md`.

Modules:

- `crossing_band_certifier.py`: source SHA locks, exact source q/R/A geometry, exact outward 512-bit Bessel mass evaluations, whole-band curvature ceiling, convex Q tangent/continuum chord+curvature lower bounds, adaptive complete partition, fail-closed unresolved status.
- `verify_band_witness.py`: independent exact-rational recomputation of saved panel quadratic minima and gap-free topology; no claim of independent Bessel code.
- `assemble_receipt.py`: source-locked six-lens identity readback, aggregate six-lens result, 16 adversarial tamper rejections and no physical promotion.

The fixed-A PR #53 and saturation PR #51 are upstream. This branch must remain a separate draft until CI and mathematical/source review pass. All results refer only to the selected historical smooth acceleration-equivalent mathematical mass, **not** a physically admitted lensing source or root proof. `physical_provider_admitted=false`; `empirical_validation=NOT_ESTABLISHED`.
