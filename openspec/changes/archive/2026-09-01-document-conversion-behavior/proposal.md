## Why

The only capability spec in the repo covers AUR packaging — none of `convert.py`'s actual conversion behavior, which is the whole point of the project, has a spec behind it. It's implemented and covered by 109 passing tests, but per the repo's own OpenSpec convention every capability needs a spec, not just a ticket: a ticket carries the what-and-why, a spec carries the what-the-system-must-do. This backfills that for behavior that already shipped, sourced from the test suite (the authoritative, already-verified contract) rather than re-deriving it from memory or the closed issues that originally requested each piece.

## What Changes

No behavior changes — this only adds specs for what `convert.py` already does. Nothing here should ever fail against the current test suite; if it does, either the spec is wrong or a real regression exists.

## Capabilities

### New Capabilities

- `conversion/headings`: heading-level shifting driven by whether a title claims the H1, and the six-level cap.
- `conversion/blocks`: quote, example and source blocks, `#+RESULTS:` removal, and the fallback for a block type the converter doesn't specifically handle.
- `conversion/links`: ID-link resolution to wikilinks, external links, anchor links, links inside headings, and reporting a link that resolves nowhere.
- `conversion/footnotes`: inline footnote references and definitions, and dropping a definition nothing refers to.
- `conversion/tables`: normalizing an org table's `+`-jointed separator row to Markdown's form.
- `conversion/frontmatter`: the title, arbitrary extracted properties, and created/modified timestamps with configurable keys.
- `conversion/publish-flag`: mapping an org property onto a boolean publish flag in frontmatter.
- `conversion/removed-content`: dropping `:PROPERTIES:` drawers, unrecognized `#+` directives, and org-roam's generated table-of-contents sections.
- `cli/file-output`: turning notes into files — title-derived filenames, filesystem-unsafe character handling with an alias, collision handling, and the run summary.

### Modified Capabilities

None.

## Impact

- No code changes. Every requirement below is already implemented in
  `convert.py` and already covered by `tests/test_conversion.py` and
  `tests/test_cli.py` (109 passing tests).
- This is a documentation backfill, not new work — sourced from the test
  suite rather than the dozens of individual closed issues that
  historically requested each piece, since re-deriving from the tests is
  precise and re-deriving from issue titles alone would not be.
