# B2 and subsequent releases — strict reproducibility

1. Import original B0 unchanged to the future GitHub repository in its first historical Git commit; preserve `provenance/B0_2026-10-27_original.zip` and original SHA manifest.
2. Work on a versioned branch. Freeze referenced scientific source hash, model family, output scope, input data-use roles and exact acceptance tests before modifying source.
3. Validate package syntax/tests/CLI and the source manifest; test an installed wheel and actual cross-platform CI when connected to GitHub. Never claim those have run if only the local tests were executed.
4. Graph release checks must load all 31 exact source partitions and reproduce authority digest/partitions; synthetic tests cannot replace the full gate.
5. Make run receipt and outputs immutable, with unique IDs keyed by model, code, RunSpec and source/input hashes. New data or physics requires a new run/model ID; do not overwrite prior results.
6. Emit explicit gate ledger statuses `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN` and the scope. Never automatically upgrade claims based on a green numerical test.
7. Write a new release ZIP and SHA sidecar. Upload it to the authorized Drive folder and read the bytes back, verifying the exact SHA-256 before changing the one living START_HERE pointer.
8. If a write, CI, source-lock or scientific check fails, retain the previous known-good release; report a bounded failure with exact source and steps to recover.

**Privacy**: the Bootstrap Drive folder currently allows link-reader access. Do not put unpublished protected source, full sealed graph corpus, credentials, private catalogs or unlicensed third-party code into that folder without changing permissions explicitly.

**Publication**: B2 is infrastructure only. A GitHub README is not scientific validation; ESET Physics backends are the next project stage.

## Final-build checks

Bind actual environment to run IDs. Retain raw and LF-normalized resolver output hashes separately. Verify the ZIP with its externally retained SHA, then check its independent artifact inventory and source manifest. Build and install a wheel outside the checkout; compare included package source bytes with the source distribution. Keep Ruff/GitHub/Windows statuses NOT_RUN until their real commands execute. A local predeployment final build is not automatically a deployment-approved release.
