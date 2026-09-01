# conversion/links Specification

## Purpose

Converts org-roam's `[[id:...][...]]` links to Obsidian wikilinks resolved against the real note title, external and anchor links to Markdown's inline form, and reports any link that resolves nowhere so it can be fixed by hand.

## Requirements

### Requirement: An ID link resolves to its target note's real title

An `[[id:<id>][<label>]]` link SHALL become an Obsidian wikilink `[[<title>]]` using the target note's actual title where it's known, regardless of what label the link carried — since a stale label shouldn't survive the conversion when the real title is available.

#### Scenario: A known ID resolves to the real title

- **WHEN** converting `See [[id:abc-123][stale label]].` where `abc-123` is known to resolve to `Real Title`
- **THEN** the output is `See [[Real Title]].`

#### Scenario: An unknown ID falls back to the link's own text

- **WHEN** converting `See [[id:abc-123][Other Note]].` where `abc-123` resolves to nothing
- **THEN** the output is `See [[Other Note]].`

### Requirement: External and anchor links become Markdown inline links

A `[[<url>][<label>]]` link to an external URL SHALL become `[<label>](<url>)`; a bare `[[<url>]]` SHALL become `[<url>](<url>)`; an internal anchor link `[[#<anchor>][<label>]]` SHALL become `[<label>](#<anchor>)`.

#### Scenario: A described external link becomes an inline link

- **WHEN** converting `See [[https://example.com][Example]].`
- **THEN** the output is `See [Example](https://example.com).`

#### Scenario: A bare external link becomes a self-titled link

- **WHEN** converting `See [[https://example.com]].`
- **THEN** the output is `See [https://example.com](https://example.com).`

#### Scenario: An internal anchor link becomes an inline link

- **WHEN** converting `See [[#intro][Intro]].`
- **THEN** the output is `See [Intro](#intro).`

### Requirement: Links inside a heading are converted the same as in body text

A link of any kind (ID, external) appearing on a heading line SHALL be converted using the same rules as body text, whether it is the entire heading or surrounded by other heading text.

#### Scenario: An ID link that is the whole heading converts

- **WHEN** converting `** [[id:abc-123][Gitlab]]` where `abc-123` resolves to `Gitlab`
- **THEN** the output is `## [[Gitlab]]`

#### Scenario: An ID link surrounded by heading text converts

- **WHEN** converting `** Fulfilling a [[id:abc-123][promise]]` where `abc-123` resolves to `promise`
- **THEN** the output is `## Fulfilling a [[promise]]`

#### Scenario: An external link inside a heading converts

- **WHEN** converting `* See [[https://example.com][the docs]]`
- **THEN** the output is `# See [the docs](https://example.com)`

### Requirement: A wikilink whose target file doesn't exist is reported, not silently dropped

After conversion, every written note SHALL be checked against the set of files actually written; a wikilink pointing at a title matching neither a written file nor a known alias SHALL be listed in the run's output, naming the source file and the unresolved link. A link a title's own alias resolves SHALL NOT be reported, and a `[[...]]`-shaped construct inside a fenced code block SHALL NOT be treated as a link at all.

#### Scenario: A link with no matching file is reported

- **WHEN** a note's `[[id:...][Gravity Falls]]` link resolves to no known ID, so its written output carries the wikilink `[[Gravity Falls]]`, and no written file is titled `Gravity Falls`
- **THEN** the run's output names the source file and `[[Gravity Falls]]` as pointing nowhere

#### Scenario: A link matching a written file is not reported

- **WHEN** a note links to a title that matches a file actually written
- **THEN** the run's output does not report that link as pointing nowhere

#### Scenario: A link resolved by an alias is not reported

- **WHEN** a note's filename was sanitized (for example `Box<T>` written as `Box T.md`) and carries `Box<T>` as an alias, and another note's written output carries the wikilink `[[Box<T>]]`
- **THEN** the run's output does not report that link as pointing nowhere

#### Scenario: A bracket pair inside a code block is not treated as a link

- **WHEN** a note contains `#+begin_src js\nflatMap((x) => [[x]])\n#+end_src`
- **THEN** the run's output does not report `[[x]]` as pointing nowhere

#### Scenario: The report counts every broken link in a run

- **WHEN** a run's notes contain two links that each resolve nowhere
- **THEN** the run's output states that two links point nowhere

### Requirement: A wikilink pointing nowhere is unwrapped by default

Once every note is written and the full set of resolvable titles and aliases is known, a wikilink whose target resolves nowhere SHALL, by default, be rewritten in the file on disk to drop the `[[` and `]]` and keep only the words — since Obsidian would otherwise render it as a dead link. Passing `--keep-dead-links` SHALL leave the file's link syntax untouched instead. Either way, the run's report is still printed; only which explanatory line follows it, and whether the file changed, differs.

#### Scenario: A dead link is unwrapped by default

- **WHEN** a note's `[[id:...][Gravity Falls]]` link resolves to no known ID, no written file is titled `Gravity Falls`, and `--keep-dead-links` is not passed
- **THEN** the written file contains `Gravity Falls` with the `[[` and `]]` removed, and the run's report says the link syntax was removed and the words kept

#### Scenario: `--keep-dead-links` leaves the file untouched

- **WHEN** the same note (whose link resolves to no known ID and no matching file) is converted with `--keep-dead-links`
- **THEN** the written file still contains `[[Gravity Falls]]` unchanged, and the run's report says Obsidian will show it as unresolved

#### Scenario: Unwrapping skips fenced code

- **WHEN** a broken-looking `[[...]]` construct appears inside a fenced code block in a written file
- **THEN** unwrapping does not touch it, the same way detecting it as a link in the first place does not
