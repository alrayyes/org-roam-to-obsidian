## 1. Drop the token

- [x] 1.1 Remove `token: ${{ secrets.RELEASE_TOKEN }}` from `release.yml`'s `release-please-action` step
- [x] 1.2 Collapse `auto-merge.yml` back to one step on `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`

## 2. Verify the removal holds

- [ ] 2.1 On the next release-please PR, verify its checks run with no manual approval
- [ ] 2.2 Verify its merge produces a real tag + GitHub Release with no manual backfill

## 3. If verified, clean up

- [ ] 3.1 Delete the `RELEASE_TOKEN` repo secret
- [ ] 3.2 Revoke the backing PAT
