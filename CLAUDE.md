<!--
Maintainer note (stripped before this file enters context, so it costs nothing).
Keep this to what the global preferences don't already say. Everything here is
about one thing: the unit tests are not sufficient evidence for this project.
-->

# org-roam-to-obsidian

## Verify against the real vault

`pytest` passing is not enough to call a conversion change done. After a change
merges, run the converter over the real vault and check the output:

```bash
.venv/bin/python convert.py -i ~/Documents/slip-box -o /tmp/slipbox-check -p filetags roam_refs
```

Then assert there are no issues in what it wrote. These should all be zero:

- lines still starting with `#+`
- `[[id:` links left unconverted
- `[fn:` footnotes left unconverted
- org table separator rows, `|---+---|`
- `[X](X)` self-links, which mean a link was rewritten twice
- files written fewer than files read, which means notes were silently
  overwritten

Check the counts moved the right way, not just that the suite is green. A count
going the wrong way is a regression even when every test passes.

<!--
Why this earns its place: the suite was green while the vault showed 91% of
wikilinks dead, nine notes silently overwritten, 514 files with duplicate H1s
and 212 unconverted footnotes. Hand-written fixtures only contain the
constructs someone thought to write down.
-->

- Count files written against files read. The summary line counts files _read_,
  so a collision is invisible in it.
- Compare against the previous `convert.py` over the same vault when the change
  is behavioural. That diff is what catches a fix trading one defect for
  another.
- Never convert over `output/`. Use a scratch directory.
