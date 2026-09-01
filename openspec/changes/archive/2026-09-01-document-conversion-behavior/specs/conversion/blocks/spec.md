## Purpose

Converts org-mode's `#+BEGIN_*`/`#+END_*` block syntax to Markdown's equivalents, and drops the one block type (`#+RESULTS:`) that has no Markdown equivalent worth keeping.

## ADDED Requirements

### Requirement: Quote blocks become Markdown blockquotes

A `#+begin_quote`/`#+end_quote` block (either case) SHALL become a Markdown blockquote, with every line, including blank ones, prefixed with `>`.

#### Scenario: A quote block becomes a blockquote

- **WHEN** converting `#+BEGIN_QUOTE\nSomething worth quoting.\n#+END_QUOTE`
- **THEN** the output is `> Something worth quoting.`

#### Scenario: Lowercase delimiters are recognized

- **WHEN** converting `#+begin_quote\nSomething worth quoting.\n#+end_quote`
- **THEN** the output is `> Something worth quoting.`

#### Scenario: Every line of a multi-line quote is prefixed

- **WHEN** converting `#+begin_quote\nFirst line.\nSecond line.\n#+end_quote`
- **THEN** the output is `> First line.\n> Second line.`

#### Scenario: A blank line inside a quote keeps the marker

- **WHEN** converting `#+begin_quote\nFirst.\n\nSecond.\n#+end_quote`
- **THEN** the output is `> First.\n>\n> Second.`

#### Scenario: Links inside a quote are still converted

- **WHEN** converting `#+begin_quote\nSaid by [[id:abc-123][Ike]].\n#+end_quote` where `abc-123` resolves to `Eisenhower`
- **THEN** the output is `> Said by [[Eisenhower]].`

### Requirement: Example blocks become plain fenced code blocks

A `#+begin_example`/`#+end_example` block (either case) SHALL become a fenced code block with no language tag, and org syntax inside it (headings, tables) SHALL NOT be interpreted.

#### Scenario: An example block becomes a fenced block

- **WHEN** converting `#+begin_example\nliteral text\n#+end_example`
- **THEN** the output is ` ```\nliteral text\n``` `

#### Scenario: Uppercase delimiters are recognized

- **WHEN** converting `#+BEGIN_EXAMPLE\nliteral text\n#+END_EXAMPLE`
- **THEN** the output is ` ```\nliteral text\n``` `

#### Scenario: Org syntax inside an example is left alone

- **WHEN** converting `#+begin_example\n* not a heading\n#+end_example`
- **THEN** the output is ` ```\n* not a heading\n``` `, not a converted heading

### Requirement: Source blocks become fenced code blocks tagged with their language

A `#+begin_src <language>`/`#+end_src` block (either case) SHALL become a fenced code block tagged with that language, and asterisks inside it SHALL NOT be read as headings.

#### Scenario: A source block keeps its language tag

- **WHEN** converting `#+BEGIN_SRC python\nprint('hi')\n#+END_SRC`
- **THEN** the output is ` ```python\nprint('hi')\n``` `

#### Scenario: Lowercase source-block delimiters are recognized

- **WHEN** converting `#+begin_src sh\necho hi\n#+end_src`
- **THEN** the output is ` ```sh\necho hi\n``` `

#### Scenario: Asterisks inside a source block are not headings

- **WHEN** converting `#+BEGIN_SRC text\n* not a heading\n#+END_SRC`
- **THEN** the output is ` ```text\n* not a heading\n``` `

### Requirement: A RESULTS block is dropped entirely

Everything between `#+RESULTS:` and the next blank line SHALL be removed from the output, since it holds Emacs's cached evaluation of a source block rather than authored content.

#### Scenario: A RESULTS block leaves no trace

- **WHEN** converting `#+BEGIN_SRC sh\necho hi\n#+END_SRC\n\n#+RESULTS:\n: hi\n\nAfter.`
- **THEN** the output contains neither `RESULTS` nor `: hi`, and ends with `After.`

### Requirement: An unrecognized block loses its delimiters but keeps its content

A `#+begin_*`/`#+end_*` block whose type isn't one of quote, example or src SHALL have its delimiter lines removed, leaving the content as plain text.

#### Scenario: An unhandled block type is unwrapped

- **WHEN** converting `#+begin_verse\nRoses are red\n#+end_verse`
- **THEN** the output is `Roses are red`
