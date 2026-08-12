# org-roam to Obsidian converter

[![Test](https://github.com/alrayyes/org-roam-to-obsidian/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/alrayyes/org-roam-to-obsidian/actions/workflows/test.yml)
[![Lint](https://github.com/alrayyes/org-roam-to-obsidian/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/alrayyes/org-roam-to-obsidian/actions/workflows/lint.yml)
[![Prose](https://github.com/alrayyes/org-roam-to-obsidian/actions/workflows/prose.yml/badge.svg?branch=main)](https://github.com/alrayyes/org-roam-to-obsidian/actions/workflows/prose.yml)
[![Docker](https://github.com/alrayyes/org-roam-to-obsidian/actions/workflows/docker.yml/badge.svg?branch=main)](https://github.com/alrayyes/org-roam-to-obsidian/actions/workflows/docker.yml)
[![Release](https://img.shields.io/github/v/release/alrayyes/org-roam-to-obsidian)](https://github.com/alrayyes/org-roam-to-obsidian/releases)
[![Licence](https://img.shields.io/github/license/alrayyes/org-roam-to-obsidian)](LICENSE)

Convert your org-roam notes to Obsidian-compatible Markdown format.

## Features

- Converts org-mode syntax to Markdown
- Transforms org-roam ID links (`[[id:...][title]]`) to Obsidian wikilinks (`[[title]]`)
- Extracts org-mode properties and adds them to Obsidian YAML frontmatter
- Removes org-mode metadata and directives
- Converts code blocks to Markdown fenced code blocks
- Removes timestamp prefixes from filenames
- Preserves note titles and content structure

## Requirements

To run the converter you need **Python 3.8 or newer** and nothing else. `convert.py` imports only
the standard library, so there's no `pip install` step and no virtual environment to create. It
runs anywhere Python does. The paths in the examples are written for Linux and macOS.

You also need a directory of org-roam `.org` files you can read, and somewhere to write Markdown
to. The converter never opens the org-roam SQLite database, so Emacs doesn't have to be running,
and the database doesn't have to be up-to-date.

Working on the converter needs more than running it does. That list is in
[docs/development.md](docs/development.md).

## Installation

Clone this repository:

```bash
git clone https://github.com/alrayyes/org-roam-to-obsidian.git
cd org-roam-to-obsidian
```

Make the script executable:

```bash
chmod +x convert.py
```

### Docker

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

That's the whole installation. If you're going to work on the converter rather than run it, the
virtual environment, the linters and the git hooks are all in
[docs/development.md](docs/development.md).

## Usage

Basic usage with default directories:

```bash
./convert.py
```

This will convert files from `~/Documents/slip-box` to `./output`.

Specify custom input and output directories:

```bash
./convert.py -i /path/to/org-roam -o /path/to/output
```

Extract org-mode properties to frontmatter:

```bash
./convert.py -p filetags roam_refs
```

### Options

- `-i, --input`: Input directory containing org-roam files (default: `~/Documents/slip-box`)
- `-o, --output`: Output directory for Markdown files (default: `./output`)
- `-p, --properties`: org-mode properties to extract, for example `filetags` or `roam_refs`
- `--no-created`: Disable adding created timestamp from filename
- `--no-modified`: Disable adding the modified timestamp from the org file's mtime
- `--publish-when`: mark a note for publishing when it carries this org property value, for example `category=public`
- `--publish-key`: name of the frontmatter key that carries the flag (default: `publish`)
- `--created-key`: one or more frontmatter keys for the created timestamp (default: `created`)
- `--modified-key`: one or more frontmatter keys for the modified timestamp (default: `modified`)
- `--created-property`: Use a specific org-mode property for created timestamp instead of filename
- `-h, --help`: Show help message

## Example

```bash
# Convert with custom directories
./convert.py --input ~/my-notes --output ~/obsidian-vault/imported

# Use short flags
./convert.py -i ~/org-roam -o ~/obsidian

# Extract filetags and roam_refs properties to frontmatter
./convert.py -i ~/org-roam -o ~/obsidian -p filetags roam_refs

# Disable created timestamp extraction
./convert.py --no-created

# Use a custom property for created timestamp instead of filename
./convert.py --created-property date_created
```

## What Gets Converted

### org-mode to Markdown

- Headers: `* Header` → `# Header`
- Code blocks: `#+BEGIN_SRC lang` → ` ```lang `
- ID links: `[[id:abc-123][Title]]` → `[[Title]]`
- External links: `[[url][text]]` → `[text](url)`
- Properties: `#+filetags: :tag1:tag2:` → YAML frontmatter

### Generating frontmatter

When properties are extracted with `-p`, they are added to YAML frontmatter. Properties with a single value use the scalar format, while properties with multiple values use the array format.

By default, a `created` timestamp is extracted from the org-roam filename (format: `YYYYMMDDHHMMSS-`) and added to the frontmatter. This can be disabled with `--no-created` or sourced from a custom property with `--created-property`.

A `modified` timestamp comes from the org file's own modification time, because org-roam records when a
note was created but not when it was last edited. Disable it with `--no-modified`.

If you publish the vault with a static site generator, that second date matters more than it looks.
Quartz reads `modified`, `lastmod`, `updated` or `last-modified`, and when it finds none of them it
falls back to git or the filesystem, which means the date it shows is the day you last exported. Every
page ends up stamped with the same date. Which of the two a page displays is your generator's choice:
Quartz picks it with `defaultDateType`, where `modified` shows the last edit and `created` shows the
org-roam creation date.

Generators disagree about what to call those keys, so you can set them. Quartz reads `created`,
`created_at` or `date` for one and `modified`, `lastmod`, `updated` or `last-modified` for the
other, and passing several names writes the same timestamp under each:

```bash
./convert.py --created-key created date --modified-key modified lastmod
```

The defaults are `created` and `modified`, so output only changes if you ask for it.

### Publishing a subset

If you publish part of the vault rather than all of it, `--publish-when` maps an org property onto
the flag the exporter reads. Obsidian's Quartz exporter looks for `publish`:

```bash
./convert.py --publish-when category=public
```

A note carrying `#+category: public` gets `publish: true` in its frontmatter. A note without it gets
no flag at all, rather than `publish: false`. Exporters treat a missing flag as unpublished, and
writing one out for every other note would bury the ones you meant to publish. The property can hold
several values, so `#+category: draft public` still matches. Use `--publish-key` if your setup wants
a different name.

```yaml
---
title: Note Title
created: 2020-06-13T17:05:32
modified: 2024-04-01T18:42:09
filetags:
  - tag1
  - tag2
custom_tag: custom_value
roam_refs: https://example.com
---
```

### Removed Content

- `:PROPERTIES:` blocks
- `:ID:` fields
- `#+title:` directives (converted to frontmatter and H1 header)
- Property directives (converted to frontmatter if specified with `-p`)
- `#+RESULTS:` blocks
- Table of Contents (`:TOC_:` sections)
- Timestamp filename prefixes, for example `20200613170532-`

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome. Open a pull request.

Read [docs/development.md](docs/development.md) first. It covers the setup, how to run the tests,
and what each linter is for, which saves you finding out from a failing hook.

## Known limitations

By design:

- The org-roam database is neither required nor read. Everything is worked out from the `.org`
  files themselves.
- A standard org-roam file layout is assumed: one directory of `.org` files, each carrying its
  own `:ID:` inside a `:PROPERTIES:` block.
- Conversion is best-effort. Complex org-mode constructs may not survive intact.

Not by design. Some of the features listed at the top of this file don't work today. Each one has
a test in the suite marked `xfail` and an open issue:

- A property value containing a colon gets split on it, turning `roam_refs: https://example.com`
  into a two-item list ([#17](https://github.com/alrayyes/org-roam-to-obsidian/issues/17)).
- A Table of Contents loses its heading but keeps its entries
  ([#18](https://github.com/alrayyes/org-roam-to-obsidian/issues/18)).
