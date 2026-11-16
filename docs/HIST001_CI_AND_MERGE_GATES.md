# HIST-001 CI concurrency and merge gates

This file documents **software release governance**, not scientific validation.
A passing source-free GitHub Actions run does not prove an original March
numerical statement, a physical Weyl map, held-out observational agreement,
or eligibility for a Native ESET canonical Theory-State provider.

## Superseded PR runs

`.github/workflows/ci.yaml` keeps the six existing Ubuntu/Windows ×
Python 3.10/3.12/3.13 matrix jobs and all the existing replay steps.
Workflow-level concurrency groups by PR number so a newer exact-head commit
cancels only older in-flight runs for **the same PR**. Different PRs continue
independently. The main push event instead groups by unique `github.run_id`,
so every postmerge run is retained. This does **not** retroactively cancel
GitHub Actions runs that were queued before this workflow is merged.

## Administrator-only GitHub configuration

On 16 November 2026 GitHub's accessible branch metadata showed
`main.protected=false` and the repository ruleset list was empty.
The connected integration cannot create or enforce branch-protection
rulesets; no protection is claimed from merely publishing this file.

A repository administrator must use **Settings → Rules → Rulesets** (or
branch protection) to set up an active rule targeting `main`:

1. Require pull requests before merging, at least one qualified independent
   reviewer, and dismissal of stale approvals after new commits.
2. Require the exact six matrix check contexts from a completed
   `bootstrap-contracts-offline` run (select their real names from GitHub's
   status-check picker rather than guessing context strings).
3. Prevent force pushes and branch deletion, and restrict bypass rights.
4. Disallow direct pushes to `main`; require the chosen merge strategy
   to preserve the audited candidate history and an exact release manifest.
5. Verify the rule is **active** and test that an intentionally failing
   draft or otherwise unapproved PR cannot merge.

## Source and authority gates

Before changing a PR from draft: inspect the exact head/base SHAs, isolate
candidate model identity, review the file diff, confirm the exact archive SHA
and root manifest, and obtain applicable code/security/license review.
For theorem-bearing artifacts require appropriate independent mathematical
review separately from CI. Do not copy restricted original March data or
private source-bound receipts into public Git.

For each integration: merge only an approved PR in declared dependency order,
reconcile `MANIFEST_SHA256.json` against the **actual merged tree**, rerun the
full six-platform matrix on the resulting `main` SHA, and record evidence
in issue #68. Distinct finite-proxy, exact-real, selected smooth-Mstar and
original sampled March models must retain distinct claim identities.

A green CI run is not mathematical proof, external peer review, observational
validation, dark-matter replacement, or physical provider admission. Preserve
`physical_provider_admitted=false`, `empirical_validation=NOT_ESTABLISHED`,
and nonpromotion until their independent admission gates are satisfied.
