# Repository architecture and migration design

## Authority layers

1. External immutable historical corpus and published current paper (read-only source records).
2. Scientific model identities: action, constitutive functions, species, initial conditions, physical parameters, toggle and boundary conventions.
3. Numerical implementations and all algorithm/mesh/integration settings.
4. Execution artifacts with residuals, field constraints, unit normalization, and reproducibility receipts.
5. **Separate** provider admission and empirical frozen holdout/validation decisions.

Historical ESET 3/June 4 and current v1.7.2 remain different theory backends until someone proves an equivalence map on a specified domain. Numerical agreement alone is not such a proof.

## Design rule

`Sources -> Theory registry -> Versioned physics backend -> Constraint & solver audit -> Physical provider adapter (only if admitted) -> Observation map -> Frozen likelihood/holdout`.

## No silent parameters

Every parameter change creates a new run identity. Equation/function/field/source changes require a new *theory or finite physical model identity*, not a metadata or `float` patch. A difference in residuals or observational curves between backends is evidence about those **specific** defined theories.

## Priorities

P0: recover frozen June J2141/Set A executable source and trusted hashes; reproduce GR/off and data/geometry sign tests as existing historical regression, without overwriting old source.
P1: replay source-frozen P1R VC1 and BG8/P2 successor independently; add scoped provider boundaries and interfaces.
P2: connect untouched CLASS as independent GR/ΛCDM control; connect PRIMAT 2026 via carefully selected lawful background/NEVO interface and preserve missing physics as OPEN.
P3: complete actual ESET P3 Einstein-Boltzmann-χ-material-MEM source and original-source neutrino collision coupling; certify domain/cutoff and solver/constraint tolerances.
P4: only after P3 or narrowly scoped physical provider admission, compute survey products; use Cobaya + lensing data infrastructure for preregistered/no-refit tests.
