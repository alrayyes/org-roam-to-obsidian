# conversion/footnotes Specification

## Purpose

Converts org-mode's `[fn:label]` footnote references and definitions to Markdown's `[^label]` form, and drops a definition nothing in the document actually references.

## Requirements

### Requirement: A footnote reference becomes Markdown's caret form

An inline `[fn:<label>]` reference SHALL become `[^<label>]`, including labels containing hyphens, wherever it appears — including inside a heading.

#### Scenario: An inline reference converts

- **WHEN** converting `A Promise[fn:footnote] is asynchronous.`
- **THEN** the output is `A Promise[^footnote] is asynchronous.`

#### Scenario: A hyphenated label survives

- **WHEN** converting `Async[fn:async-functions] is new.`
- **THEN** the output is `Async[^async-functions] is new.`

#### Scenario: A reference inside a heading converts

- **WHEN** converting `* British[fn:british]`
- **THEN** the output is `# British[^british]`

### Requirement: A referenced footnote's definition becomes Markdown's colon form

A `[fn:<label>]<text>` definition SHALL become `[^<label>]: <text>`, whether or not the source already had a space after the closing bracket, as long as something in the document references that label.

#### Scenario: A reference and its definition convert together

- **WHEN** converting `Body[fn:a] text.\n\n[fn:a]The note.`
- **THEN** the output is `Body[^a] text.\n\n[^a]: The note.`

#### Scenario: A definition with no space gains one

- **WHEN** converting a document referencing `[fn:footnote]` with the definition `[fn:footnote]https://example.com`
- **THEN** the output ends with `[^footnote]: https://example.com`

#### Scenario: A definition already spaced is left correctly spaced

- **WHEN** converting a document referencing `[fn:doc]` with the definition `[fn:doc] See the manual.`
- **THEN** the output ends with `[^doc]: See the manual.`

### Requirement: A footnote definition nothing references is flattened to plain text

Markdown renders no footnote marker unless something references it, so a `[fn:<label>]<text>` definition with no matching `[fn:<label>]` reference elsewhere in the document SHALL have its footnote syntax removed entirely, leaving just the text.

#### Scenario: An unreferenced definition becomes plain text

- **WHEN** converting `* Footnotes\n[fn:doc]https://example.com` (nothing references `doc`)
- **THEN** the output is `# Footnotes\nhttps://example.com`

#### Scenario: Only the unreferenced definition among several is flattened

- **WHEN** converting `Body[fn:used] text.\n\n[fn:used]used.\n[fn:spare]spare.` (only `used` is referenced)
- **THEN** the output contains `[^used]: used.` but not `[^spare]`, and still contains the word `spare.`

### Requirement: Footnote syntax inside a fenced code block is left alone

A `[fn:...]`-shaped construct inside a `#+begin_src`/`#+end_src` block SHALL NOT be converted.

#### Scenario: Footnote-shaped text inside code is untouched

- **WHEN** converting `#+begin_src text\nliteral[fn:x] text\n#+end_src`
- **THEN** the output is unchanged fenced text: ` ```text\nliteral[fn:x] text\n``` `
