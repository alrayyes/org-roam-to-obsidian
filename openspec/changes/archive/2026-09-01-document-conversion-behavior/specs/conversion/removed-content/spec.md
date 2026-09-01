## Purpose

Drops org-roam and Emacs bookkeeping that has no Markdown equivalent and no reason to survive into the converted note: property drawers, directives nothing here reads, and org-roam's own generated table-of-contents section.

## ADDED Requirements

### Requirement: A `:PROPERTIES:` drawer is dropped entirely

A `:PROPERTIES:`/`:END:` drawer, including everything between the markers such as the `:ID:` line, SHALL be removed from the output.

#### Scenario: A properties drawer leaves no trace

- **WHEN** converting `:PROPERTIES:\n:ID:       abc-123\n:END:\nBody.`
- **THEN** the output is exactly `Body.`

### Requirement: An unrecognized `#+` directive is dropped

A `#+<name>: <value>` directive whose name isn't `title` and wasn't requested via `-p`/`--properties` SHALL be removed from the output, not left as stray text.

#### Scenario: Unrecognized directives are dropped

- **WHEN** converting `#+startup: overview\n#+options: toc:nil\nBody.`
- **THEN** the output is exactly `Body.`

### Requirement: An org-roam-generated table-of-contents section is removed

A heading tagged `:TOC_<n>:noexport:` SHALL be dropped along with its entire section, meaning the heading line itself and everything under it, up to the next top-level heading or the end of the document. Content before the TOC heading SHALL survive untouched.

#### Scenario: A TOC heading is dropped

- **WHEN** converting `* Table of Contents :TOC_2:noexport:\n\n* Intro\nBody.`
- **THEN** the output does not contain `Table of Contents`

#### Scenario: TOC entries under the heading are dropped with it

- **WHEN** converting a document whose TOC section lists `[[#intro][Intro]]` and `[[#usage][Usage]]`, followed by `* Intro\nBody.`
- **THEN** the output is exactly `# Intro\nBody.`

#### Scenario: A TOC section ends at the next top-level heading, not before

- **WHEN** a TOC section is followed by `* Intro\nBody.\n** Detail\nMore.`
- **THEN** the output is `# Intro\nBody.\n## Detail\nMore.` — the `** Detail` subsection survives because it belongs to `* Intro`, not to the TOC

#### Scenario: Content before a TOC section survives

- **WHEN** converting `* Intro\nBody.\n* Contents :TOC_2:noexport:\n- [[#intro][Intro]]`
- **THEN** the output is `# Intro\nBody.`
