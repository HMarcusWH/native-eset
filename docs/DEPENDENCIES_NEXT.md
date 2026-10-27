# Upstream adapter roadmap

The registry `config/upstream_adapters.json` tracks planned source packages. **No revisions or licenses are asserted verified until fetched and audited**, and no third-party code is bundled.

- CLASS: independent GR/ΛCDM Boltzmann reference. Legacy `computed=True` shim disabled because it exported no physical arrays.
- SUNDIALS: candidate stiff differential-algebraic numerical engine.
- PRIMAT/HYREC-2: BBN and recombination reference interfaces. Source-preserved neutrino/thermal collision physics required before calling an output fully physically coupled.
- Cobaya: separate inference/likelihood roles; never mix fitted and heldout evidence.
- TreeCorr and lenstronomy: independent observational operator references, not native ESET lensing law.

Before adding any adapter, pin exact commit/artifact, license, API version, input/output unit and domain, reference control, negative controls, and reproducibility receipt.
