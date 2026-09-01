## 1. Standard files

- [x] 1.1 Add `.gitattributes` and verify `git check-attr -a bun.lock` reports `text: auto`, `eol: lf`, `diff: unset` (#120)
- [x] 1.2 Add `SECURITY.md` and verify `gh api repos/alrayyes/org-roam-to-obsidian/private-vulnerability-reporting` reports enabled (#121)
- [x] 1.3 Add `.github/ISSUE_TEMPLATE/{bug_report,feature_request}.yml` and `PULL_REQUEST_TEMPLATE.md` and verify the GitHub new-issue picker shows both forms (#122)

## 2. CI checks

- [x] 2.1 Add PR-title linting (`amannn/action-semantic-pull-request` on `pull_request_target`) and verify a non-conventional PR title fails the check while a Conventional Commits title passes (#123)
- [x] 2.2 Add a `pip-audit` job scanning `requirements-dev.txt` and verify it's green in CI (#124)
- [x] 2.3 Add `actions/attest-build-provenance` to the image-publish job and verify with `gh attestation verify oci://ghcr.io/alrayyes/org-roam-to-obsidian:latest --owner alrayyes` (#126)
- [x] 2.4 Add `actions/dependency-review-action` on pull requests and verify it's green in CI (#128)

## 3. Local hooks

- [x] 3.1 Add a scoped `docker build` to lefthook's `pre-commit` (fires only when `Dockerfile`/`convert.py` is staged) and an unconditional one to `pre-push`, and document both in `CONTRIBUTING.md` (#125)

## 4. Release correctness

- [x] 4.1 Wire `flake.nix`'s version into release-please's generic `extra-files` updater and verify the next release PR bumps it to match `pyproject.toml`/`package.json` (#129 — verified against the 3.8.1 release)

## 5. Documentation and label cleanup

- [x] 5.1 Remove `README.md`'s stale "not by design" section referencing closed issues #17/#18, with no `xfail` tests left to back the claim (#140)
- [x] 5.2 Apply labels to the 21 issues (#15-#83) that had none, from the repo's existing stock label set — decided against a `kind/`+`topic/` migration (#127)
