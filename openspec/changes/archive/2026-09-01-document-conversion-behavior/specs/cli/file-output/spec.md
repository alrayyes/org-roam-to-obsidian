## Purpose

Turns a directory of org-roam `.org` files into a directory of Obsidian-ready `.md` files: naming each after its title rather than its org-roam filename, handling filesystem-unsafe characters and title collisions without losing a note, and reporting what happened.

## ADDED Requirements

### Requirement: A note is named after its title, not its org-roam filename

The converter SHALL write each note as `<title>.md`, stripping the org-roam timestamp prefix (`YYYYMMDDHHMMSS-`) — because a wikilink is written as the target's title, and a file named after the org filename instead would never resolve. A note carrying no title SHALL fall back to its org filename (prefix stripped) instead.

#### Scenario: A note is named after its title

- **WHEN** converting a note titled `JavaScript Arrays`
- **THEN** the output directory contains `JavaScript Arrays.md`

#### Scenario: Timestamp prefixes are stripped from every filename

- **WHEN** converting a vault of notes with `YYYYMMDDHHMMSS-` filename prefixes
- **THEN** none of the written filenames carry that prefix

#### Scenario: A title-less note falls back to its filename

- **WHEN** converting `20200101000000-no_title.org` with no `#+title:` directive
- **THEN** the output directory contains `no_title.md`

### Requirement: A title with filesystem-unsafe characters is sanitized, with the original kept as an alias

A character a filesystem can't safely hold in a filename SHALL be replaced when deriving the written filename. The note's frontmatter SHALL then carry the original, unsanitized title as an `aliases` entry, so an existing wikilink written against the real title still resolves. A title needing no sanitization SHALL get no `aliases` key at all.

#### Scenario: An unsafe character is replaced in the filename

- **WHEN** converting a note titled `Binding / Variables in JavaScript`
- **THEN** the output directory contains `Binding - Variables in JavaScript.md`

#### Scenario: The original title survives as an alias

- **WHEN** converting a note titled `Box<T>` (written as `Box T.md`)
- **THEN** that file's frontmatter contains `aliases:\n  - Box<T>`

#### Scenario: An untouched title gets no alias

- **WHEN** converting a note titled `Plain Title` (no unsafe characters)
- **THEN** that file's frontmatter contains no `aliases` key

### Requirement: A title collision is reported and neither note is lost

When two or more notes' titles collapse to the same filename, the run SHALL warn, naming every source `.org` file involved in the collision, and every note SHALL still be written — the first (by sorted source filename) keeps the title-derived name, and each other falls back to its own org filename. Processing order SHALL be deterministic (sorted), so the same vault produces the same result on every run.

#### Scenario: A collision is warned about by name

- **WHEN** two notes with different filenames both title themselves `Arrays`
- **THEN** the run's output contains a warning naming both source `.org` files

#### Scenario: Both notes survive a title clash

- **WHEN** two notes both title themselves `Same`, sorted so `a.org` precedes `b.org`
- **THEN** the output directory contains both `Same.md` (from `a.org`) and `b.md` (from `b.org`, falling back to its own filename)

#### Scenario: The summary counts collisions separately from files

- **WHEN** two notes collide on one title
- **THEN** the run's summary reports 2 files written from 2 notes and 1 name collision

### Requirement: An ID link between two notes becomes a wikilink resolvable in the written output

An `[[id:...]]` link from one note to another SHALL resolve to the target's actual written filename's stem (its title, sanitized name aside), so the link works as a real Obsidian wikilink once both files exist on disk.

#### Scenario: A link between two converted notes resolves

- **WHEN** converting a vault where one note links by ID to another titled `Second Note`
- **THEN** the linking note's written file contains `[[Second Note]]`, and `Second Note.md` exists

### Requirement: The run reports what it did, and only warns when something needs attention

After conversion, the run SHALL print how many files were written and how many notes were read — counting files actually written, not notes read, since a title collision means those two numbers can differ. A run with no collisions and no broken links SHALL print no `Warning`. The output directory SHALL be created if it doesn't already exist. An empty source directory SHALL be handled without erroring, reporting zero files from zero notes.

#### Scenario: The summary counts files written, not notes read

- **WHEN** converting a vault where a collision causes one note to fall back to a different filename
- **THEN** the summary still reports files written against notes read accurately, so a silent overwrite would show as fewer files than notes

#### Scenario: A clean run prints no warnings

- **WHEN** converting a vault with no title collisions and no broken links
- **THEN** the run's output contains no `Warning` and does report the count of files written

#### Scenario: The output directory is created if missing

- **WHEN** the configured output directory doesn't exist yet
- **THEN** after the run, that directory exists

#### Scenario: An empty source directory is not an error

- **WHEN** the input directory contains no `.org` files
- **THEN** the run completes and reports 0 files written from 0 notes

### Requirement: A note's ID and title are read from its `:PROPERTIES:` drawer and title directive

Reading a note's metadata off disk (before conversion, to build the ID-to-title map every other note's links resolve against) SHALL extract the `:ID:` value and the `#+title:`/`#+TITLE:` value. A file with neither SHALL yield no ID and no title, not an error.

#### Scenario: ID and title are read from a well-formed file

- **WHEN** reading a file containing `:PROPERTIES:\n:ID:       abc-123\n:END:\n#+title: My Note\n\nBody.`
- **THEN** its ID reads as `abc-123` and its title as `My Note`

#### Scenario: An uppercase title directive is read the same way

- **WHEN** reading a file using `#+TITLE:` instead of `#+title:`
- **THEN** the title still reads as the directive's value

#### Scenario: A file with no metadata yields nothing

- **WHEN** reading a file containing only body text, no drawer and no title directive
- **THEN** both the ID and the title read as absent

### Requirement: A created timestamp comes from the filename by default, or a configured property when present

The created timestamp SHALL be parsed from the org-roam filename prefix (`YYYYMMDDHHMMSS-`) by default. When `--created-property` names a property, a note carrying that property SHALL use its value instead; a note without that property SHALL still fall back to the filename. A filename with no timestamp prefix SHALL yield no created timestamp at all.

#### Scenario: The created timestamp is read from the filename

- **WHEN** reading `20200613170532-my_note.org`
- **THEN** the created timestamp is `2020-06-13T17:05:32`

#### Scenario: An untimestamped filename yields no created timestamp

- **WHEN** reading a file with no timestamp prefix in its name
- **THEN** no created timestamp is produced

#### Scenario: A configured property takes precedence over the filename

- **WHEN** `--created-property date_created` is set and the note carries `#+date_created: 2021-01-01`
- **THEN** the created timestamp is `2021-01-01`, not the value implied by the filename

#### Scenario: The filename is the fallback when the configured property is absent

- **WHEN** `--created-property date_created` is set but the note carries no such property
- **THEN** the created timestamp falls back to the one implied by the filename

### Requirement: The modified timestamp comes from the org file's own filesystem mtime

By default, each note's modified timestamp SHALL be its `.org` file's last-modified time on disk, since org-roam records creation but not last edit. Passing `--no-modified` SHALL omit it entirely, and passing `--no-created` SHALL omit the created timestamp entirely (independently of the modified one).

#### Scenario: The modified timestamp comes from the file's mtime

- **WHEN** an org file's filesystem mtime is a known instant
- **THEN** the written note's `modified:` value reflects that instant

#### Scenario: `--no-modified` omits the modified timestamp

- **WHEN** converting with `--no-modified`
- **THEN** the written note contains no `modified:` key

#### Scenario: `--no-created` omits the created timestamp

- **WHEN** converting with `--no-created`
- **THEN** the written note contains no `created:` key

### Requirement: Only explicitly requested properties reach a written note's frontmatter

Passing `-p`/`--properties` SHALL scope which org properties are extracted into frontmatter for the whole run; a property not named SHALL never appear in any written note, even if the org file carries it.

#### Scenario: An unrequested property never reaches a written file

- **WHEN** converting with `-p filetags` and a note also carries an org property not named
- **THEN** the written file's frontmatter contains the requested property and not the other one
