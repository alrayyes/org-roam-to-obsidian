# conversion/headings Specification

## Purpose

Converts org-mode's asterisk heading syntax to Markdown's `#` syntax, shifted down one level whenever a title claims the H1 so the note has exactly one top-level heading.

## Requirements

### Requirement: Heading level maps directly to asterisk count with no title

When a document has no `#+title:` directive, each heading's Markdown level SHALL equal its org nesting depth (one `*` becomes `#`, two becomes `##`, and so on).

#### Scenario: Top-level heading with no title

- **WHEN** converting `* Introduction` with no title directive
- **THEN** the output is `# Introduction`

#### Scenario: Nesting depth preserved with no title

- **WHEN** converting `* One\n** Two\n*** Three` with no title directive
- **THEN** the output is `# One\n## Two\n### Three`

### Requirement: Headings shift down one level when a title claims the H1

When a document has a `#+title:` directive, every heading SHALL render one Markdown level below its org nesting depth, and no line in the output SHALL be a level-1 (single `#`) heading — the renderer displays the title as the page's H1, so a body H1 too would show it twice.

#### Scenario: Headings shift down under a title

- **WHEN** converting `#+title: My Note\n\n* Overview\n** Detail`
- **THEN** the output ends with `## Overview\n### Detail`

#### Scenario: No body H1 survives a titled note

- **WHEN** converting `#+title: My Note\n\n* One\n* Two`
- **THEN** no line in the output is a level-1 heading

### Requirement: Heading level never exceeds Markdown's six-level cap

A heading whose shifted level would exceed six `#` characters SHALL be capped at six.

#### Scenario: A sixth org level under a title does not overflow

- **WHEN** converting `#+title: My Note\n\n****** Deep` (six asterisks, shifted down one)
- **THEN** the output ends with `###### Deep`, not seven `#` characters
