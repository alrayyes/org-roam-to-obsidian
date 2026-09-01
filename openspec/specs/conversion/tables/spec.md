# conversion/tables Specification

## Purpose

Normalizes org-mode's `+`-jointed table separator row to the `|`-only form Markdown expects; everything else about a table passes through untouched.

## Requirements

### Requirement: A `+`-jointed separator row converts to Markdown's form

A table separator row using `+` to join its cells (`|---+---|`) SHALL have every `+` replaced with `|`. A separator row with no `+` (already `|`-only) SHALL be left exactly as it was. Indentation before a table SHALL be preserved.

#### Scenario: A plus-jointed separator converts

- **WHEN** converting `| A | B |\n|---+---|\n| 1 | 2 |`
- **THEN** the output is `| A | B |\n|---|---|\n| 1 | 2 |`

#### Scenario: A separator with no pluses is left alone

- **WHEN** converting `| A | B |\n|---------|\n| 1 | 2 |`
- **THEN** the output is unchanged

#### Scenario: An indented table is converted with its indentation kept

- **WHEN** converting `Body.\n  | A | B |\n  |---+---|`
- **THEN** the output is `Body.\n  | A | B |\n  |---|---|`

### Requirement: Table body rows and non-table text are never touched

A table's header and data rows SHALL pass through unchanged. A `+` appearing in ordinary prose (not a separator row) SHALL NOT be converted, and a table-separator-shaped line inside a fenced code block SHALL NOT be converted either.

#### Scenario: Body rows are untouched

- **WHEN** converting `| Country | Share |\n|---------+-------|\n| USSR    |   57% |`
- **THEN** the output ends with `| USSR    |   57% |` and contains the converted separator `|---------|-------|`

#### Scenario: A plus in prose is not mistaken for a table

- **WHEN** converting `Use a+b for the sum.`
- **THEN** the output is unchanged

#### Scenario: A separator-shaped line inside a code block is left alone

- **WHEN** converting `#+begin_src text\n|---+---|\n#+end_src`
- **THEN** the output is ` ```text\n|---+---|\n``` ` with the `+` characters untouched
