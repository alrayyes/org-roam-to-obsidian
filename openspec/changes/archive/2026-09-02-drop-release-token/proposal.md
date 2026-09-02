## Why

`release-please-token` (archived) gave `release.yml` and `auto-merge.yml`
a fine-grained PAT (`RELEASE_TOKEN`) to work around a `GITHUB_TOKEN`
anti-recursion symptom: release-please's PR stuck needing manual approval,
and merges producing no tag. Since then, `backup-git-repos` and
`washy-washy-cli` have run the identical release-please + native-auto-merge
pipeline on plain `GITHUB_TOKEN`, no PAT, with neither symptom -- and this
repo's own branch protection already has `required_approving_review_count`
at 0. There's nothing left for a PAT to be working around that a fresh
`GITHUB_TOKEN` wouldn't already satisfy.

## What Changes

- `release.yml`'s `release-please-action` step drops the `token:` input,
  back to the default `GITHUB_TOKEN`.
- `auto-merge.yml` collapses back to a single step for both the release PR
  and the Dependabot PR, both on `GITHUB_TOKEN`.
- If the next release-please cycle regresses (stuck approval, or a merge
  with no tag), revert and keep `RELEASE_TOKEN` -- this change is a test,
  not a foregone conclusion.

## Capabilities

No capability spec changes -- release-pipeline plumbing, not observable
behavior of `convert.py`. `skip_specs: true` is set in this change's
`.openspec.yaml`.

## Impact

- Modified: `.github/workflows/release.yml`, `.github/workflows/auto-merge.yml`.
- Candidate for removal once verified: the `RELEASE_TOKEN` repo secret and
  its backing PAT.

Tracked as GitHub issue #166.

## Result: reverted

Not confirmed by a real release-please cycle before movie-planner and
tempus-fugit independently hit the exact symptom this change assumed was
gone -- a release PR authored by GITHUB_TOKEN sitting at `action_required`
with zero jobs run, needing a manual approval click. Reverted back to
`RELEASE_TOKEN` on both `release.yml` and `auto-merge.yml`.
`backup-git-repos` and `washy-washy-cli` still work fine without a PAT and
the actual differentiator is still unknown -- tracked in
`alrayyes/dotfiles#483`.
