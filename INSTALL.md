# Installing org-roam-to-obsidian

Pick whichever fits how you already work. All four end up running the same
`convert.py` — see the [README](README.md) for usage once it's installed.

## AUR (Arch Linux)

```bash
yay -S org-roam-to-obsidian
```

Or any other AUR helper, or `git clone
https://aur.archlinux.org/org-roam-to-obsidian.git` and `makepkg -si`
directly. The package installs a single `python` dependency and wraps
`convert.py` as `org-roam-to-obsidian` on `$PATH`.

## Docker

If you'd rather not have Python on the machine at all, there's an image on the GitHub Container
Registry. Mount your notes at `/input` and somewhere to write at `/output`:

```bash
docker run --rm \
  -v ~/Documents/slip-box:/input:ro \
  -v ~/obsidian-vault/imported:/output \
  ghcr.io/alrayyes/org-roam-to-obsidian:latest
```

Every flag below still works, appended to that command:

```bash
docker run --rm -v ~/notes:/input:ro -v ~/out:/output \
  ghcr.io/alrayyes/org-roam-to-obsidian:latest -p filetags roam_refs
```

The input mount is read-only because the converter never writes to it, and there's no reason to
hand a container write access to your notes.

The image runs as UID 1000 rather than root, so the files it writes belong to a real user instead
of a directory you need `sudo` to delete. If your own UID isn't 1000, the container won't be able
to write to the output mount, and you'll get `Permission denied`. Tell Docker who you are:

```bash
docker run --rm --user "$(id -u):$(id -g)" \
  -v ~/Documents/slip-box:/input:ro \
  -v ~/obsidian-vault/imported:/output \
  ghcr.io/alrayyes/org-roam-to-obsidian:latest
```

`latest` follows `main`; released versions are tagged `3`, `3.2` and `3.2.0`.

## Nix / NixOS

```bash
nix run github:alrayyes/org-roam-to-obsidian -- --help
```

Or add it as a flake input, or `nix profile install
github:alrayyes/org-roam-to-obsidian` to install it into your profile. Builds
straight from this repo's own `flake.nix` — no nixpkgs submission, so
nothing to wait on there.

## From source

Clone this repository:

```bash
git clone https://github.com/alrayyes/org-roam-to-obsidian.git
cd org-roam-to-obsidian
```

Make the script executable:

```bash
chmod +x convert.py
```

That's the whole installation — `convert.py` imports only the standard library, so there's no
`pip install` step and no virtual environment to create for running it. If you're going to work on
the converter rather than run it, the virtual environment, the linters and the git hooks are all in
[CONTRIBUTING.md](CONTRIBUTING.md).
