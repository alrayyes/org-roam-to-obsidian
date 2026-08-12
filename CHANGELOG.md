# Changelog

## [3.5.0](https://github.com/alrayyes/org-roam-to-obsidian/compare/v3.4.0...v3.5.0) (2026-08-12)


### Features

* add a modified timestamp to the frontmatter ([659f501](https://github.com/alrayyes/org-roam-to-obsidian/commit/659f50168c463ca7fd5a358470c6f24d3ff0471e))

## [3.4.0](https://github.com/alrayyes/org-roam-to-obsidian/compare/v3.3.0...v3.4.0) (2026-08-12)


### Features

* report links that point nowhere ([9627edc](https://github.com/alrayyes/org-roam-to-obsidian/commit/9627edc315c66d094a7e2c38910e07b8fa051f55))


### Documentation

* remove duplicated changelog entries ([bf25e27](https://github.com/alrayyes/org-roam-to-obsidian/commit/bf25e271877ca2cb67d0fa3dec5d02c9ead1666b))

## [3.3.0](https://github.com/alrayyes/org-roam-to-obsidian/compare/v3.2.0...v3.3.0) (2026-08-12)


### Features

* name files after the note title ([f552b17](https://github.com/alrayyes/org-roam-to-obsidian/commit/f552b17c310294d4f935cedaf380e5c0e96450d3))
* publish a Docker image to ghcr ([2308230](https://github.com/alrayyes/org-roam-to-obsidian/commit/23082302bf04cf82cf7a873dbe33814acfa0a0f5))


### Bug Fixes

* let the image write as the invoking user ([8a1c01a](https://github.com/alrayyes/org-roam-to-obsidian/commit/8a1c01a169905f1b5c4b0defe86cc87ed17c3a9f))
* make the image build on arm64 ([90b21cc](https://github.com/alrayyes/org-roam-to-obsidian/commit/90b21cc7c246197b3b5e319341fba214605370d9))
* report collisions instead of losing notes quietly ([e93ac67](https://github.com/alrayyes/org-roam-to-obsidian/commit/e93ac677eacd550bee973f69e3fc0bb41b6038ac))


### Documentation

* require a vault run after merging ([3bc69ed](https://github.com/alrayyes/org-roam-to-obsidian/commit/3bc69ed735f71b6e4b2308f559c1c4155c8fc42d))

## [3.2.0](https://github.com/alrayyes/org-roam-to-obsidian/compare/v3.1.3...v3.2.0) (2026-08-12)


### Features

* convert org footnotes ([1d04141](https://github.com/alrayyes/org-roam-to-obsidian/commit/1d04141a4358f3c4f747acf64b19a5568c4ed7e7))
* convert org table separators ([1006f70](https://github.com/alrayyes/org-roam-to-obsidian/commit/1006f7085f9197f86e2402690655fe4cd0d0acc1))


### Bug Fixes

* convert links inside headings ([5c32902](https://github.com/alrayyes/org-roam-to-obsidian/commit/5c32902533c697876256bad8563baf53fc68ba80))
* convert quote and example blocks ([a143fe5](https://github.com/alrayyes/org-roam-to-obsidian/commit/a143fe5180bf01d1c067190947fc18f33631f5bc))
* drop the whole table of contents ([a350cc4](https://github.com/alrayyes/org-roam-to-obsidian/commit/a350cc43e336edee4aee7efc212dc9c3bfb95fca))
* keep colons in property values ([9655944](https://github.com/alrayyes/org-roam-to-obsidian/commit/9655944265d51967696e3dc8a80aa39bcf0e8aa5))
* read #+TITLE: in either case ([c328703](https://github.com/alrayyes/org-roam-to-obsidian/commit/c3287035dff187b73a4c84c27c43ae1f81107b72))
* shift headings below the title ([9747d14](https://github.com/alrayyes/org-roam-to-obsidian/commit/9747d145983845bd3b5e225001424fde8699fa98))

## [3.1.3](https://github.com/alrayyes/org-roam-to-obsidian/compare/v3.1.2...v3.1.3) (2026-08-12)


### Bug Fixes

* convert each org link in a single pass ([1171b99](https://github.com/alrayyes/org-roam-to-obsidian/commit/1171b997ee42fcb0c3ff9187ffa9e18f8d36766b))
* recognise org directives in either case ([050d437](https://github.com/alrayyes/org-roam-to-obsidian/commit/050d437b0b999b6eb2de5448bee8e828cf2aff19))


### Documentation

* move dev guide out of the README ([13ecbc8](https://github.com/alrayyes/org-roam-to-obsidian/commit/13ecbc8283ccd6030c4ce7c33b6a57afda629bad))

## [3.1.2](https://github.com/alrayyes/org-roam-to-obsidian/compare/v3.1.1...v3.1.2) (2026-08-12)


### Documentation

* add badges to the README ([1facec3](https://github.com/alrayyes/org-roam-to-obsidian/commit/1facec38b6b90e3343a039deeca5c9b9abb1db16))
* bring the README up to standard ([0f8c73b](https://github.com/alrayyes/org-roam-to-obsidian/commit/0f8c73bb607ca8e49a89a2153ac89819431047c3))
* record the broken features ([87121c3](https://github.com/alrayyes/org-roam-to-obsidian/commit/87121c3660498a99c1bf55da456992aa43563333))
* state the real requirements ([9e3a85b](https://github.com/alrayyes/org-roam-to-obsidian/commit/9e3a85b68aa35864ed9258ff79a817666b653aa8))

## [3.1.1](https://github.com/alrayyes/org-roam-to-obsidian/compare/v3.1.0...v3.1.1) (2026-08-09)


### Documentation

* describe the hooks lefthook actually runs ([806952b](https://github.com/alrayyes/org-roam-to-obsidian/commit/806952b595d0692539e91cfa0a45127857329d96))

## [3.1.0](https://github.com/alrayyes/org-roam-to-obsidian/compare/v3.0.0...v3.1.0) (2026-08-05)


### Features

* add support for customizing created timestamp extraction ([996b198](https://github.com/alrayyes/org-roam-to-obsidian/commit/996b198a5e0ba29668e352d8f5bd0bfb4652f932))
* add support for extracting org-mode properties to YAML frontmatter ([7315350](https://github.com/alrayyes/org-roam-to-obsidian/commit/73153507c6aa6f1845639ec533d5c238b1936803))

## [3.0.0](https://github.com/alrayyes/org-roam-to-obsidian/compare/v2.0.0...v3.0.0) (2026-08-04)


### ⚠ BREAKING CHANGES

* initial stable release

### Features

* add auto-merge workflow for release PRs ([55d18fa](https://github.com/alrayyes/org-roam-to-obsidian/commit/55d18faa53ec67ed9095b6e4c6ae094b4b7ae44e))
* add automated release setup with Release Please and GitHub Actions ([3af30b9](https://github.com/alrayyes/org-roam-to-obsidian/commit/3af30b99a3994d5801a9d5e00fbc9ee6d8b87593))
* add commitlint, lefthook setup, and Node.js support for commit message validation ([422700f](https://github.com/alrayyes/org-roam-to-obsidian/commit/422700fb5c558f946d847acedebe9152f2ee30d5))
* add EditorConfig and enhance pre-push hooks ([d1885dc](https://github.com/alrayyes/org-roam-to-obsidian/commit/d1885dc31734dfb850f0d6df88d6f872c1ba22d4))
* add GitHub Actions workflow for linting and commit message validation ([6535e4b](https://github.com/alrayyes/org-roam-to-obsidian/commit/6535e4bc1396ba6f354eda0ad569116d5cfeb6b7))
* add org-roam to Obsidian converter script and .gitignore for typical Python project files ([fa4b9c7](https://github.com/alrayyes/org-roam-to-obsidian/commit/fa4b9c72f0d382f662f567cb7c2808a55ddba572))
* add Prettier integration for YAML and JSON files ([09aaf7f](https://github.com/alrayyes/org-roam-to-obsidian/commit/09aaf7fcdc010a906658c1e925eead68d2caea3d))
* add project config, linting setup, and update script for consistency ([9c25b79](https://github.com/alrayyes/org-roam-to-obsidian/commit/9c25b792df5d3e6217cbdb415a3c8bae39642afb))
* enable auto-merge for Dependabot PRs ([fc7bf66](https://github.com/alrayyes/org-roam-to-obsidian/commit/fc7bf66fa8346302618dc7867a71495d2787905e))
* enhance release workflow with version tagging ([317bba4](https://github.com/alrayyes/org-roam-to-obsidian/commit/317bba44b79184ddeda1e8316305c5db0660b08c))
* integrate markdownlint for linting Markdown files ([abd52d4](https://github.com/alrayyes/org-roam-to-obsidian/commit/abd52d415a1512c608766e8aca5f889686d42b93))


### Documentation

* add README with usage, features, and examples ([2bf8cae](https://github.com/alrayyes/org-roam-to-obsidian/commit/2bf8caea2e40bf19f30a6727af80b7e9ab4ae4f1))
* remove redundant author section from README ([776fb8b](https://github.com/alrayyes/org-roam-to-obsidian/commit/776fb8bad74f23d7e04f94c6e120675e5aa4cd4e))


### Miscellaneous Chores

* release version 1.0.0 ([491f39c](https://github.com/alrayyes/org-roam-to-obsidian/commit/491f39c09feef41fa5f99c263b49f9720ea7a6ac))

## [2.0.0](https://github.com/alrayyes/org-roam-to-obsidian/compare/org-roam-to-obsidian-v1.1.0...org-roam-to-obsidian-v2.0.0) (2026-08-04)


### ⚠ BREAKING CHANGES

* initial stable release

### Features

* add auto-merge workflow for release PRs ([55d18fa](https://github.com/alrayyes/org-roam-to-obsidian/commit/55d18faa53ec67ed9095b6e4c6ae094b4b7ae44e))
* add automated release setup with Release Please and GitHub Actions ([3af30b9](https://github.com/alrayyes/org-roam-to-obsidian/commit/3af30b99a3994d5801a9d5e00fbc9ee6d8b87593))
* add commitlint, lefthook setup, and Node.js support for commit message validation ([422700f](https://github.com/alrayyes/org-roam-to-obsidian/commit/422700fb5c558f946d847acedebe9152f2ee30d5))
* add EditorConfig and enhance pre-push hooks ([d1885dc](https://github.com/alrayyes/org-roam-to-obsidian/commit/d1885dc31734dfb850f0d6df88d6f872c1ba22d4))
* add GitHub Actions workflow for linting and commit message validation ([6535e4b](https://github.com/alrayyes/org-roam-to-obsidian/commit/6535e4bc1396ba6f354eda0ad569116d5cfeb6b7))
* add org-roam to Obsidian converter script and .gitignore for typical Python project files ([fa4b9c7](https://github.com/alrayyes/org-roam-to-obsidian/commit/fa4b9c72f0d382f662f567cb7c2808a55ddba572))
* add Prettier integration for YAML and JSON files ([09aaf7f](https://github.com/alrayyes/org-roam-to-obsidian/commit/09aaf7fcdc010a906658c1e925eead68d2caea3d))
* add project config, linting setup, and update script for consistency ([9c25b79](https://github.com/alrayyes/org-roam-to-obsidian/commit/9c25b792df5d3e6217cbdb415a3c8bae39642afb))
* enable auto-merge for Dependabot PRs ([fc7bf66](https://github.com/alrayyes/org-roam-to-obsidian/commit/fc7bf66fa8346302618dc7867a71495d2787905e))
* enhance release workflow with version tagging ([317bba4](https://github.com/alrayyes/org-roam-to-obsidian/commit/317bba44b79184ddeda1e8316305c5db0660b08c))
* integrate markdownlint for linting Markdown files ([abd52d4](https://github.com/alrayyes/org-roam-to-obsidian/commit/abd52d415a1512c608766e8aca5f889686d42b93))


### Documentation

* add README with usage, features, and examples ([2bf8cae](https://github.com/alrayyes/org-roam-to-obsidian/commit/2bf8caea2e40bf19f30a6727af80b7e9ab4ae4f1))
* remove redundant author section from README ([776fb8b](https://github.com/alrayyes/org-roam-to-obsidian/commit/776fb8bad74f23d7e04f94c6e120675e5aa4cd4e))


### Miscellaneous Chores

* release version 1.0.0 ([491f39c](https://github.com/alrayyes/org-roam-to-obsidian/commit/491f39c09feef41fa5f99c263b49f9720ea7a6ac))

## [1.1.0](https://github.com/alrayyes/org-roam-to-obsidian/compare/v1.0.0...v1.1.0) (2026-08-04)


### Features

* integrate markdownlint for linting Markdown files ([abd52d4](https://github.com/alrayyes/org-roam-to-obsidian/commit/abd52d415a1512c608766e8aca5f889686d42b93))

## 1.0.0 (2026-08-04)


### ⚠ BREAKING CHANGES

* initial stable release

### Features

* add auto-merge workflow for release PRs ([55d18fa](https://github.com/alrayyes/org-roam-to-obsidian/commit/55d18faa53ec67ed9095b6e4c6ae094b4b7ae44e))
* add automated release setup with Release Please and GitHub Actions ([3af30b9](https://github.com/alrayyes/org-roam-to-obsidian/commit/3af30b99a3994d5801a9d5e00fbc9ee6d8b87593))
* add commitlint, lefthook setup, and Node.js support for commit message validation ([422700f](https://github.com/alrayyes/org-roam-to-obsidian/commit/422700fb5c558f946d847acedebe9152f2ee30d5))
* add GitHub Actions workflow for linting and commit message validation ([6535e4b](https://github.com/alrayyes/org-roam-to-obsidian/commit/6535e4bc1396ba6f354eda0ad569116d5cfeb6b7))
* add org-roam to Obsidian converter script and .gitignore for typical Python project files ([fa4b9c7](https://github.com/alrayyes/org-roam-to-obsidian/commit/fa4b9c72f0d382f662f567cb7c2808a55ddba572))
* add project config, linting setup, and update script for consistency ([9c25b79](https://github.com/alrayyes/org-roam-to-obsidian/commit/9c25b792df5d3e6217cbdb415a3c8bae39642afb))
* enable auto-merge for Dependabot PRs ([fc7bf66](https://github.com/alrayyes/org-roam-to-obsidian/commit/fc7bf66fa8346302618dc7867a71495d2787905e))
* enhance release workflow with version tagging ([317bba4](https://github.com/alrayyes/org-roam-to-obsidian/commit/317bba44b79184ddeda1e8316305c5db0660b08c))


### Miscellaneous Chores

* release version 1.0.0 ([491f39c](https://github.com/alrayyes/org-roam-to-obsidian/commit/491f39c09feef41fa5f99c263b49f9720ea7a6ac))

## 1.0.0 (2026-08-04)


### ⚠ BREAKING CHANGES

* initial stable release

### Features

* add auto-merge workflow for release PRs ([55d18fa](https://github.com/alrayyes/org-roam-to-obsidian/commit/55d18faa53ec67ed9095b6e4c6ae094b4b7ae44e))
* add automated release setup with Release Please and GitHub Actions ([3af30b9](https://github.com/alrayyes/org-roam-to-obsidian/commit/3af30b99a3994d5801a9d5e00fbc9ee6d8b87593))
* add commitlint, lefthook setup, and Node.js support for commit message validation ([422700f](https://github.com/alrayyes/org-roam-to-obsidian/commit/422700fb5c558f946d847acedebe9152f2ee30d5))
* add GitHub Actions workflow for linting and commit message validation ([6535e4b](https://github.com/alrayyes/org-roam-to-obsidian/commit/6535e4bc1396ba6f354eda0ad569116d5cfeb6b7))
* add org-roam to Obsidian converter script and .gitignore for typical Python project files ([fa4b9c7](https://github.com/alrayyes/org-roam-to-obsidian/commit/fa4b9c72f0d382f662f567cb7c2808a55ddba572))
* add project config, linting setup, and update script for consistency ([9c25b79](https://github.com/alrayyes/org-roam-to-obsidian/commit/9c25b792df5d3e6217cbdb415a3c8bae39642afb))
* enhance release workflow with version tagging ([317bba4](https://github.com/alrayyes/org-roam-to-obsidian/commit/317bba44b79184ddeda1e8316305c5db0660b08c))


### Miscellaneous Chores

* release version 1.0.0 ([491f39c](https://github.com/alrayyes/org-roam-to-obsidian/commit/491f39c09feef41fa5f99c263b49f9720ea7a6ac))
