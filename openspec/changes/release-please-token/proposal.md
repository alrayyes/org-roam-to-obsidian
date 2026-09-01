## Why

`release-please-action` and the auto-merge workflow both authenticated with
the default `GITHUB_TOKEN`. GitHub's anti-recursion guard on
`GITHUB_TOKEN`-authored events left every release-please PR stuck needing
manual approval to run its checks, and the same guard on the auto-merge
step's completion meant the follow-up push to `main` didn't reliably
trigger the tag/GitHub-Release step — `v3.8.2` and `v3.9.0` both merged
with neither a git tag nor a GitHub Release to show for it.

## What Changes

- `release.yml`'s `release-please-action` step authenticates with a
  `RELEASE_TOKEN` repo secret (a fine-grained PAT scoped to this repo,
  `Contents: write` + `Pull requests: write`) instead of `GITHUB_TOKEN`.
- `auto-merge.yml`'s `gh pr merge --auto` step does the same, via `GH_TOKEN`.
- The two releases that landed with no tag or GitHub Release
  (`v3.8.2`, `v3.9.0`) got both filled in by hand, and their PRs'
  `autorelease:` label flipped from `pending` to `tagged` to match.

## Capabilities

No capability spec changes — this is release-pipeline plumbing, not
observable behavior of `convert.py`. `skip_specs: true` is set in this
change's `.openspec.yaml`.

## Impact

- Modified: `.github/workflows/release.yml`, `.github/workflows/auto-merge.yml`.
- New repo secret: `RELEASE_TOKEN`.
- Filled-in git tags/releases: `v3.8.2`, `v3.9.0`.
- Root cause and fix confirmed against two sibling repos (movie-planner,
  `washy-washy-cli`) that independently hit and fixed the identical symptom.
- Still open, not part of this change: the moving `v3`/`v3.8` tags are
  stale from before this fix landed — updating them needs deleting the
  existing remote tags first, which this session's permission classifier
  blocked as destructive.

Shipped as GitHub issue #146 (closed) — PR #149.
