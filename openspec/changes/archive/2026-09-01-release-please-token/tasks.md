## 1. Fix the token

- [x] 1.1 Add `token: ${{ secrets.RELEASE_TOKEN }}` to `release.yml`'s `release-please-action` step
- [x] 1.2 Swap `auto-merge.yml`'s `GITHUB_TOKEN` environment variable for `GH_TOKEN: ${{ secrets.RELEASE_TOKEN }}`
- [x] 1.3 Add the `RELEASE_TOKEN` repo secret and verify with `gh secret list`

## 2. Fill in the missed releases

- [x] 2.1 Create the `v3.8.2` tag and GitHub Release, and flip PR #142's `autorelease:` label to `tagged`
- [x] 2.2 Create the `v3.9.0` tag and GitHub Release, and flip PR #148's `autorelease:` label to `tagged`

## 3. Verify the fix holds

- [x] 3.1 On the next release-please PR after this ships, verify its checks run with no manual approval and its merge produces a real tag + GitHub Release with no manual backfill — confirmed on PR #152 (`chore(main): release 3.9.1`): all checks `SUCCESS`, no `action_required`, `v3.9.1` tagged and released with no manual intervention
