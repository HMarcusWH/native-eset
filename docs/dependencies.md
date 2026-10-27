# Scientific upstreams — copy policy and versioning

The source-code repositories below are *candidates*. The bootstrap carries none of their code. Check exact upstream LICENSE/COPYING and the selected Git SHA before redistributing or altering any source. Use separately installed versioned adapters by default.

| Repo | Role | Verified licensing note (2026-10-27) | Admissibility |
| --- | --- | --- | --- |
| [CLASS](https://github.com/lesgourg/class_public) | GR/ΛCDM Boltzmann reference; possible future ESET perturbation extension | No GitHub-recognized license/no license file at root; citation-use statement. Check permission before vendoring | Not an ESET provider |
| [hi_class](https://github.com/hiclass-code/hi_class_public) | Historical variable-Planck scalar–tensor reference | GitHub metadata does not declare SPDX license; check source terms | Not v1.7.2 material+MEM |
| [PRIMAT](https://github.com/CyrilPitrou/primat) | BBN nuclear/reaction and thermo computation | GPL-3.0-or-later from `LICENCE` | Custom-background file path disables incomplete neutrino decoupling; use source-aware Background/NEVO interfaces only after proof |
| [HYREC-2](https://github.com/nanoomlee/HYREC-2) | Recombination, available through CLASS | No GitHub-recognized license at root, check terms | Component input, not P3 |
| [Cobaya](https://github.com/CobayaSampler/cobaya) | Likelihood and inference | LGPL-3-or-later with additional publication/bug terms | Independent observation layer |
| [CAMB](https://github.com/cmbant/CAMB) | Independent GR cross-check | LGPL-3-or-later with additional publication/bug terms and notices | Not native ESET provider |
| [TreeCorr](https://github.com/rmjarvis/TreeCorr) | KiDS weak-lensing correlation machinery | Custom BSD-like notice (see `TreeCorr_LICENSE`) | Measurement processing, not physics |
| [lenstronomy](https://github.com/lenstronomy/lenstronomy) | Strong-lens models and profiles | BSD-3-Clause | Observational reference |
| [CCL / pyccl](https://github.com/LSSTDESC/CCL) | Tracers, transfer projections, LSS observables | BSD-3-Clause | Needs valid native transfer inputs |
| [SUNDIALS](https://github.com/LLNL/sundials) | Stiff ODE/DAE integration | BSD-3-Clause | Numerical machinery, not a physical closure |
| [nudec_BSM](https://github.com/MiguelEA/nudec_BSM) | Neutrino decoupling reference | GPL-3 | Not automatic full three-flavour ESET coupled kinetics |
| [FEniCSx](https://github.com/FEniCS/dolfinx) | Spatial finite-element PDEs | LGPL-3-or-later | Later, for source-derived DM-A finite domains |
| [QuTiP](https://github.com/qutip/qutip) | Optional QREG density/state/channel tests | Inspect pinned version's license before copying | Not quantum gravity |

Third-party executables should be run with exact versions and original source notices. The license conclusion for a *combined redistributed derivative work* depends on actual linkage and code copied; this is a cautionary research audit, not legal advice.
