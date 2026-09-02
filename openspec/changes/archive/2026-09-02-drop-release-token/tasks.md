## 1. Drop the token

- [x] 1.1 Remove `token: ${{ secrets.RELEASE_TOKEN }}` from `release.yml`'s `release-please-action` step
- [x] 1.2 Collapse `auto-merge.yml` back to one step on `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`

## 2. Verify the removal holds

- [x] 2.1 On the next release-please PR, verify its checks run with no manual approval -- **failed**: no release-please PR landed before the pattern was independently disproved on movie-planner and tempus-fugit
- [x] 2.2 Verify its merge produces a real tag + GitHub Release with no manual backfill -- **not reached**, see 2.1

## 3. Revert

- [x] 3.1 Restore `token: ${{ secrets.RELEASE_TOKEN }}` on `release.yml`'s `release-please-action` step
- [x] 3.2 Restore `auto-merge.yml`'s two-step split (release PR on `RELEASE_TOKEN`, Dependabot PR on `GITHUB_TOKEN`)
- [x] 3.3 File `alrayyes/dotfiles#483` to investigate the actual differentiator, rather than re-attempt this blind
