## Purpose

Lets Arch Linux users install and keep the converter up to date through
their system package manager instead of a manual clone or a container.

## ADDED Requirements

### Requirement: Installable via the AUR

The system SHALL be published on the AUR as `org-roam-to-obsidian`,
installable with a standard AUR helper or `makepkg -si`, providing an
`org-roam-to-obsidian` executable on `$PATH`.

#### Scenario: Install with an AUR helper

- **WHEN** a user runs `yay -S org-roam-to-obsidian`
- **THEN** the package builds and installs, and `org-roam-to-obsidian --help`
  runs successfully afterward

#### Scenario: Build and install with makepkg directly

- **WHEN** a user clones `aur.archlinux.org/org-roam-to-obsidian.git` and
  runs `makepkg -si`
- **THEN** the package builds without error and installs the same
  executable

### Requirement: AUR package tracks tagged releases

The `PKGBUILD`'s `pkgver` SHALL match a real, existing GitHub release tag,
and its `sha256sums` SHALL be the actual checksum of that tag's source
tarball.

#### Scenario: Source tarball resolves and verifies

- **WHEN** `makepkg` downloads the source named in `PKGBUILD`
- **THEN** the download succeeds and its checksum matches `sha256sums`

### Requirement: Install documentation covers every method in one place

Once more than one install method exists, install instructions SHALL live
in a single `INSTALL.md`, not scattered across `README.md`.

#### Scenario: README points to INSTALL.md

- **WHEN** a reader opens `README.md`'s Installation section
- **THEN** it links to `INSTALL.md` rather than duplicating install steps
  for every method
