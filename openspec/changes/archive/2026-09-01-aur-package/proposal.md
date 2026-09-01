## Why

`convert.py` is a single-file CLI with no dependencies outside the standard
library — exactly the shape `rules/packaging.md` says belongs on OS-level
packaging (AUR, apt, an RPM repo) rather than requiring a `pip install`
step or a container just to run it. The only install paths were git-clone,
Docker, and Nix; Arch Linux users had no native package manager option.

## What Changes

- Publish `org-roam-to-obsidian` on the AUR
  (`aur.archlinux.org/packages/org-roam-to-obsidian`), installable with any
  AUR helper (`yay -S org-roam-to-obsidian`) or `makepkg -si` directly.
- Add `PKGBUILD` and `.SRCINFO` at the repo root, sourcing the GitHub
  release tarball.
- Split installation docs into a dedicated `INSTALL.md` (AUR, Docker, Nix,
  from-source) per `rules/packaging.md`'s rule that more than one install
  method needs its own file rather than a growing README section.
  `README.md`'s Installation section is now a one-line pointer.
- Document the manual release-sync steps (bump `pkgver`, `updpkgsums`,
  regenerate `.SRCINFO`, push to the separate AUR git repo) in
  `CONTRIBUTING.md`.

## Capabilities

### New Capabilities

- `packaging/aur`: the converter is installable via the AUR as a system
  package that wraps `convert.py` on `$PATH`, kept in sync with tagged
  GitHub releases.

## Impact

- New files: `PKGBUILD`, `.SRCINFO`, `INSTALL.md`.
- Modified: `README.md` (Installation section trimmed to a pointer),
  `CONTRIBUTING.md` (AUR release-sync steps), `.dockerignore` (excludes
  `PKGBUILD`/`.SRCINFO` from the build context), `.github/workflows/prose.yml`
  (LTeX's explicit file list gains `INSTALL.md`), both prose vocabularies
  (`AUR` added — bare uses in headings/prose would otherwise fail spelling).
- A separate git remote now exists outside this repo:
  `ssh://aur@aur.archlinux.org/org-roam-to-obsidian.git`, holding just the
  `PKGBUILD`/`.SRCINFO` pair. Publishing there needs the `aur-ci` SSH
  deploy key (chezmoi-managed, documented in global CLAUDE.md's
  Credentials section) — not a secret this repo's own CI holds.
- No change to `convert.py`'s behavior; verified locally before publishing
  (`makepkg -f` builds, the package installs and runs, `namcap` clean on
  both the package and the `PKGBUILD`).

Shipped as GitHub issue #143 (closed) — PR #147.
