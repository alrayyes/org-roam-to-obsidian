# conversion/frontmatter Specification

## Purpose

Extracts a note's title, explicitly requested org properties, and created/modified timestamps into Obsidian YAML frontmatter, so a renderer can show them without the body repeating them.

## Requirements

### Requirement: The title goes in the frontmatter and nowhere else in the body

A `#+title:` (or `#+TITLE:`) directive SHALL become a `title:` key in YAML frontmatter, and SHALL NOT also appear as a body heading — Obsidian and Quartz already render the frontmatter title above the note. Passing `--title-heading` SHALL additionally repeat it as a body H1, for a renderer that shows no title of its own.

#### Scenario: The title appears only in frontmatter by default

- **WHEN** converting `#+title: My Note\n\nBody.`
- **THEN** the output is `---\ntitle: My Note\n---\n\nBody.`

#### Scenario: `--title-heading` adds a body H1

- **WHEN** converting the same document with the title-heading option enabled
- **THEN** the output is `---\ntitle: My Note\n---\n\n# My Note\n\nBody.`

#### Scenario: An uppercase title directive is recognized

- **WHEN** converting `#+TITLE: My Note\n\nBody.`
- **THEN** the output is `---\ntitle: My Note\n---\n\nBody.`

### Requirement: A document with no metadata gets no frontmatter block at all

A document carrying neither a title nor any requested property SHALL be converted with no `---`-delimited frontmatter block, not an empty one.

#### Scenario: Plain body text gets no frontmatter

- **WHEN** converting `Just body text.`
- **THEN** the output is exactly `Just body text.`

### Requirement: Only explicitly requested properties reach the frontmatter

An org property directive (`#+<name>: <value>`) SHALL be added to frontmatter only when `<name>` was passed via `-p`/`--properties`; any other property directive SHALL be dropped from the output entirely, not just left out of frontmatter.

#### Scenario: An unrequested property is dropped

- **WHEN** converting `#+filetags: :one:\n\nBody.` with no `-p filetags` passed
- **THEN** the output is exactly `Body.`

### Requirement: A property with one value becomes a scalar; more than one becomes a list

A requested property carrying org-mode's colon-wrapped tag syntax (`:one:two:`) or space-separated values SHALL become a YAML list when it holds more than one value, and a plain scalar when it holds exactly one.

#### Scenario: A single-valued property becomes a scalar

- **WHEN** converting `#+filetags: :solo:\n\nBody.` with `filetags` requested
- **THEN** the frontmatter contains `filetags: solo`

#### Scenario: A multi-valued colon-wrapped property becomes a list

- **WHEN** converting `#+filetags: :one:two:\n\nBody.` with `filetags` requested
- **THEN** the frontmatter contains `filetags:\n  - one\n  - two`

#### Scenario: A URL-valued property survives intact as a scalar

- **WHEN** converting `#+roam_refs: https://example.com\n\nBody.` with `roam_refs` requested
- **THEN** the frontmatter contains `roam_refs: https://example.com`, not a value split on its colons

#### Scenario: Several space-separated URLs become a list

- **WHEN** converting `#+roam_refs: https://example.com https://other.example\n\nBody.` with `roam_refs` requested
- **THEN** the frontmatter contains `roam_refs:\n  - https://example.com\n  - https://other.example`

### Requirement: Created and modified timestamps are written under configurable keys

When a created and/or modified timestamp is supplied to the converter, each SHALL be written to frontmatter under its configured key or keys, `created`/`modified` by default. Each can be renamed, and written under several keys at once, so more than one static-site generator's convention is satisfied in one pass. A timestamp that wasn't supplied SHALL NOT produce a key at all. The created timestamp, when present, SHALL appear directly below the title.

#### Scenario: Both timestamps appear under their default keys

- **WHEN** converting `#+title: My Note` with created `2020-06-13T17:05:32` and modified `2024-04-01T18:42:09`
- **THEN** the frontmatter starts with `title: My Note\ncreated: 2020-06-13T17:05:32\nmodified: 2024-04-01T18:42:09`

#### Scenario: A missing modified timestamp produces no modified key

- **WHEN** converting with a created timestamp but no modified timestamp supplied
- **THEN** the output contains no `modified:` key

#### Scenario: The created key can be renamed

- **WHEN** converting with `created_keys=["date"]`
- **THEN** the frontmatter contains `date: <timestamp>` and no `created:` key

#### Scenario: A timestamp can be written under several keys at once

- **WHEN** converting with `created_keys=["created", "created_at", "date"]`
- **THEN** the frontmatter contains all three keys, each carrying the same timestamp

#### Scenario: The modified key can be renamed without a false match on "modified"

- **WHEN** converting with `modified_keys=["lastmod", "last-modified"]`
- **THEN** the frontmatter contains `lastmod:` and `last-modified:`, and no line starts with the bare key `modified:`
