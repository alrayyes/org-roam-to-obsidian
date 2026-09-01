## 1. Write the capability specs

- [x] 1.1 `conversion/headings` — verify every scenario matches `tests/test_conversion.py::TestHeadings`
- [x] 1.2 `conversion/blocks` — verify every scenario matches `TestQuoteAndExampleBlocks` and `TestCodeBlocks`
- [x] 1.3 `conversion/links` — verify every scenario matches `TestLinks` plus the dead-link CLI tests; the unwrap-by-default requirement is sourced from `convert.py` directly since it has no test coverage (see task 2.1)
- [x] 1.4 `conversion/footnotes` — verify every scenario matches `TestUnreferencedFootnotes` and `TestFootnotes`
- [x] 1.5 `conversion/tables` — verify every scenario matches `TestTables`
- [x] 1.6 `conversion/frontmatter` — verify every scenario matches `TestFrontmatter`
- [x] 1.7 `conversion/publish-flag` — verify every scenario matches `TestPublishFlag`
- [x] 1.8 `conversion/removed-content` — verify every scenario matches `TestRemovedContent`
- [x] 1.9 `cli/file-output` — verify every scenario matches `tests/test_cli.py` and `TestReadingMetadataFromDisk`

## 2. Gaps found while writing these

- [x] 2.1 File a ticket: the default dead-link-unwrapping behavior (`--keep-dead-links` off) and the `--keep-dead-links` flag itself have zero test coverage — confirmed by grepping `tests/*.py` for `keep_dead_links`/`unwrap`, no matches. The spec requirement is sourced from reading `convert.py` directly, not from a passing test. Filed as #156.
