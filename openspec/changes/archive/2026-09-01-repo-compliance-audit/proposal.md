## Why

An audit against `~/.config/claude/CLAUDE.md` and its `rules/*.md` found the
repo missing several standard pieces every repo under those conventions is
expected to carry: no `.gitattributes`, no `SECURITY.md`, no GitHub issue
forms, no PR-title linting despite squash-merging, no dependency
vulnerability scanning, no local proof the Docker image still builds, no
build provenance on the published image, and a stale README section
describing two bugs that were actually fixed weeks earlier. `dependency-review-action`
had also been skipped on the assumption the repo was private, which it no
longer is.

## What Changes

- Add `.gitattributes` (line-ending normalization, a `-diff` marker on
  `bun.lock`).
- Add `SECURITY.md` and enable GitHub's private vulnerability reporting.
- Add `.github/ISSUE_TEMPLATE/{bug_report,feature_request}.yml` and
  `.github/PULL_REQUEST_TEMPLATE.md`.
- Add a `pull_request_target`-triggered PR-title-lint workflow
  (`amannn/action-semantic-pull-request`), since commitlint never sees the
  PR title and this repo squash-merges.
- Add a `pip-audit` job scanning `requirements-dev.txt`.
- Add a `docker build` step to `lefthook`'s `pre-commit` (scoped to
  `Dockerfile`/`convert.py`) and `pre-push` (unconditional) — CI already
  builds the image, but nothing did locally before a push.
- Add `actions/attest-build-provenance` to the image-publish job.
- Add `actions/dependency-review-action` on pull requests, now that the
  repo is public.
- Fix `flake.nix`'s hand-maintained version (already drifted) by wiring it
  into release-please's generic `extra-files` updater.
- Remove `README.md`'s stale "not by design" section referencing two issues
  (#17, #18) that were closed as fixed weeks earlier, with no `xfail` tests
  left to back the claim.
- Apply labels to 21 issues that had none, from the repo's existing
  stock label set (not a new `kind/`+`topic/` taxonomy — decided against
  migrating, per the maintainer).

## Capabilities

No capability spec changes — every item here is CI/tooling/docs/hygiene
work. It changes how the repo is built, checked, and released, not any
externally observable behavior of `convert.py` itself. `skip_specs: true`
is set in this change's `.openspec.yaml` accordingly.

## Impact

- New files: `.gitattributes`, `SECURITY.md`,
  `.github/ISSUE_TEMPLATE/bug_report.yml`,
  `.github/ISSUE_TEMPLATE/feature_request.yml`,
  `.github/PULL_REQUEST_TEMPLATE.md`.
- Modified: `.github/workflows/lint.yml` (pip-audit),
  `.github/workflows/docker.yml` (provenance attestation),
  `.github/workflows/dependency-review.yml` (new workflow), `lefthook.yml`
  (docker-build hooks), `flake.nix` + `release-please-config.json`
  (version sync), `README.md` (stale section removed), `CONTRIBUTING.md`
  (docker-build hook documented).
- GitHub repo setting: private vulnerability reporting enabled.
- No change to `convert.py` or its CLI behavior.

Shipped as GitHub issues #120-#129 and #140, all closed, via pull requests #130-#137, #139 and #141.
