## Purpose

Maps a single org property/value onto a boolean frontmatter flag, so a static-site generator's publish-subset feature can be driven from org-roam without hand-editing every note afterward.

## ADDED Requirements

### Requirement: A matching property value sets the publish flag to true

When `--publish-when PROPERTY=VALUE` is supplied and a note carries that org property with a value that includes `VALUE` (the property may hold several space-separated values), the frontmatter SHALL gain a boolean flag set to `true`, under the `publish` key by default or the key named by `--publish-key`. A note whose property value doesn't match, or that lacks the property entirely, SHALL get no flag at all, never an explicit `false`. An exporter treats a missing flag as unpublished, and a page full of explicit `false`s would bury the ones that matter. Without `--publish-when` supplied at all, no flag is ever added, regardless of what properties a note carries.

#### Scenario: A matching property sets the flag

- **WHEN** converting `#+title: T\n#+category: public\n\nBody.` with `--publish-when category=public`
- **THEN** the frontmatter contains `publish: true`

#### Scenario: A non-matching value sets nothing

- **WHEN** converting `#+title: T\n#+category: draft\n\nBody.` with `--publish-when category=public`
- **THEN** the output contains no `publish` key at all

#### Scenario: A missing property sets nothing

- **WHEN** converting `#+title: T\n\nBody.` with `--publish-when category=public`
- **THEN** the output contains no `publish` key at all

#### Scenario: The value can be one of several in the property

- **WHEN** converting `#+title: T\n#+category: draft public\n\nBody.` with `--publish-when category=public`
- **THEN** the frontmatter contains `publish: true`

#### Scenario: The flag key can be renamed

- **WHEN** converting the same matching note with `--publish-when category=public --publish-key published`
- **THEN** the frontmatter contains `published: true`, not `publish:`

#### Scenario: Nothing happens without the option

- **WHEN** converting `#+title: T\n#+category: public\n\nBody.` with no `--publish-when` passed at all
- **THEN** the output contains no `publish` key
