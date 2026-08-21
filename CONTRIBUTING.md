# Contributing

How to work on the converter. If you only want to run it, the
[README](README.md) has everything you need and none of this.

The short version: the linters are opinionated, they run in git hooks and in CI
on the same commands, and every one of them is here for a reason recorded below.

## What you need

Running the converter needs Python and nothing else. Working on it needs:

- **[bun](https://bun.sh)** for the Node-shaped tooling: commitlint, Biome, Prettier,
  markdownlint-cli2 and lefthook. Not npm. The lockfile is `bun.lock`.
- **ruff** and **pytest**, both pinned in `requirements-dev.txt`.
- **[Vale](https://vale.sh)**, optional. The hooks skip it when it isn't on your `PATH`, and CI
  runs it either way.

## Getting set up

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python development tools — ruff and pytest (pinned in requirements-dev.txt)
pip install -r requirements-dev.txt

# Install the Node-shaped tooling with Bun. This also installs the git hooks:
# lefthook is pinned in package.json and the `prepare` script runs it for you.
bun install

# Run linter and formatter manually
ruff check .
ruff format .

# Test commit message format
echo "feat: add new feature" | bunx commitlint
```

## Tests

Run the suite with `pytest`. There are two layers and no more, because a
single-file CLI with no database and no network has nowhere else to hide.

`tests/test_cli.py` runs `convert.py` as a subprocess over a throwaway org-roam
directory, so argument parsing, output filenames and the two-pass conversion
all get covered in one journey. `tests/test_conversion.py` takes the org-mode
constructs one at a time: headings, source blocks, links, properties, and the
content the converter strips out.

Some tests are marked `xfail`. They describe behaviour the README promises, but
the converter doesn't deliver yet, and each one names the issue that tracks it.
When you fix the bug, delete the marker. Don't edit the expectation to match
what the code happens to do. The marker is strict, so a test that starts passing
by accident fails the build until someone removes its marker.

The suite runs on `pre-push`, and in CI against Python 3.14.

## Git hooks

This project uses [lefthook](https://github.com/evilmartians/lefthook) to manage git hooks. It's
pinned in `package.json` like every other tool here, so `bun install` puts the hooks in place and
everyone gets the same version of them:

- **pre-commit**: Fixes staged files in place. `ruff format` and `ruff check --fix` on Python,
  `prettier --write` then `markdownlint-cli2 --fix` on Markdown, `prettier --write` on YAML, and
  `biome check --write` on JSON
- **commit-msg**: Validates commit messages with [commitlint](https://commitlint.js.org/) following [Conventional Commits](https://www.conventionalcommits.org/)
- **pre-push**: Runs `pytest`, then re-runs all of the above across the whole repository in check
  mode, so nothing reaches the remote that CI would reject

The hooks and the GitHub Actions workflows run the same commands on purpose. The hook catches a
problem early; CI is the gate you can't skip. You can run the checks yourself with
`bun run format:md`, `bun run lint:md`, `bun run lint:yaml` and `bun run lint:json`. Each one has
a `:fix` counterpart that writes instead of complaining.

Markdown gets two tools because they answer different questions. Prettier owns the layout, and
it's the only thing here that aligns a table's pipes and pads its cells. markdownlint-cli2 then
judges the structure of what Prettier produced: heading levels, list markers, dead links.

The order matters, which is why both the hook and CI run Prettier first. The other way round,
markdownlint spends its effort fixing something Prettier is about to overwrite. Where the two
disagree about a character, the markdownlint rule comes off in `.markdownlint-cli2.jsonc` instead
of being left to fight.

Prettier runs with `proseWrap: "preserve"`, so it never reflows a paragraph you wrote. It leaves
`CHANGELOG.md` alone too, because release-please owns that file.

JSON belongs to [Biome](https://biomejs.dev), not Prettier. Biome leads on every file type it
supports, and Prettier is only here to fill the gaps it leaves. Today those gaps are Markdown and
YAML. `.prettierignore` lists the extensions Biome owns, so nobody later reads Prettier's presence
as permission to hand it the JavaScript, and the day Biome ships a YAML formatter that list grows
by one line. `biome.json` turns on comments and trailing commas for the parser, because
`.markdownlint-cli2.jsonc` uses both, and it skips `bun.lock`.

## Prose

Layout and structure are one thing. Whether the prose reads well is another, and two more tools
cover that. They check different things, so they're deployed alongside each other rather than one
instead of the other.

[Vale](https://vale.sh) checks style: house voice, weasel words, corporate speak. It uses the
Google and proselint packages, which `vale sync` downloads rather than the repo committing them.
So install Vale (`yay -S vale` on Arch, `brew install vale` on macOS) and run `vale sync` once
before `bun run lint:prose` will work. The git hooks run Vale when it's on your `PATH` and quietly
skip it when it isn't. CI runs it either way and reports rather than blocks, because a merge
stopped by an opinion teaches people to reach for `--no-verify`.

[ltex-cli-plus](https://github.com/ltex-plus/ltex-ls-plus) checks mechanics: grammar, spelling and
punctuation, by wrapping LanguageTool. This one does fail the build, because mechanics have a
right answer. It stays out of the git hooks, since it's a ~300 MB download shipping its own Java
runtime and that's more than a commit should wait on. Run the same engine in your editor over LSP
(`ltex-ls-plus`, or `harper-ls` if you want something lighter) and CI becomes the fallback instead
of the first time you hear about a typo.

`styles/House/` holds the rules no published style guide covers. `Filler.yml` catches the
vocabulary that says nothing, and `EmDash.yml` complains when a paragraph leans on more than one
em-dash where a full stop would do.

Where the two tools overlap, the rule comes off on one side. `PASSIVE_VOICE` is disabled in
`.ltex.json` because Vale's styles already flag it. A few others are off for reasons worth
recording, since a JSON config file can't say so itself:

- `UPPERCASE_SENTENCE_START`, because the README opens with `# org-roam to Obsidian converter`
  and org-roam is spelled lowercase.
- `LICENCE_LICENSE_NOUN_SINGULAR`, because the prose is British English but the GNU General Public
  License and the `LICENSE` file are named with an s, and neither is ours to respell.
- `Google.Spelling`, for the same British-English reason in the other direction.
- `Google.EmDash`, which wants em-dashes closed up. The house style spaces them.

Project vocabulary lives in two places, one per tool: `styles/config/vocabularies/House/accept.txt`
for Vale, and `ltex.dictionary` in `.ltex.json` for LTeX. Add new jargon to both. Vale's copy also
pins the casing, because `Vale.Terms` is on: spell a product name any other way and it says so.

## Commit messages

Commits follow [Conventional Commits](https://www.conventionalcommits.org/),
checked by commitlint on `commit-msg`:

```text
<type>[optional scope]: <description>

Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
```

Examples:

```text
feat: add support for org-mode tables
fix(parser): handle empty code blocks correctly
docs: update installation instructions
```

Configuration is in `.commitlintrc.json` and follows `@commitlint/config-conventional`.
