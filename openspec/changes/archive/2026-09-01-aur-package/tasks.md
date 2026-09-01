## 1. Package definition

- [x] 1.1 Write `PKGBUILD` sourcing the GitHub release tarball, and verify `makepkg -f` builds cleanly
- [x] 1.2 Generate `.SRCINFO` via `makepkg --printsrcinfo` and verify it matches `PKGBUILD`
- [x] 1.3 Install the built package and verify `org-roam-to-obsidian --help` runs; verify `namcap` reports no issues on the package or the `PKGBUILD`

## 2. Documentation split

- [x] 2.1 Create `INSTALL.md` covering AUR, Docker, Nix, and from-source, ordered native-package-manager-first per `rules/packaging.md`
- [x] 2.2 Trim `README.md`'s Installation section to a pointer at `INSTALL.md`
- [x] 2.3 Add `INSTALL.md` to `prose.yml`'s LTeX file list (it's an explicit list, not a glob) and verify the workflow checks it
- [x] 2.4 Add `AUR` to both prose vocabularies (`styles/config/vocabularies/House/accept.txt`, `.ltex.json`) and verify Vale/LTeX pass on the new bare-prose uses
- [x] 2.5 Document the manual AUR release-sync steps in `CONTRIBUTING.md`
- [x] 2.6 Exclude `PKGBUILD`/`.SRCINFO` from the Docker build context in `.dockerignore`

## 3. Publish

- [x] 3.1 Push `PKGBUILD`/`.SRCINFO` to `ssh://aur@aur.archlinux.org/org-roam-to-obsidian.git` using the `aur-ci` deploy key, and verify the package page at `aur.archlinux.org/packages/org-roam-to-obsidian` returns 200
