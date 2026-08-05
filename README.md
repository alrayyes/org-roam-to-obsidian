# Org-Roam to Obsidian Converter

Convert your org-roam notes to Obsidian-compatible Markdown format.

## Features

- Converts org-mode syntax to Markdown
- Transforms org-roam ID links (`[[id:...][title]]`) to Obsidian wikilinks (`[[title]]`)
- Extracts org-mode properties and adds them to Obsidian YAML frontmatter
- Removes org-mode metadata and directives
- Converts code blocks to Markdown fenced code blocks
- Removes timestamp prefixes from filenames
- Preserves note titles and content structure

## Requirements

- Python 3.8+
- No external dependencies required (uses only the standard library)

## Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/org-roam-to-obsidian.git
cd org-roam-to-obsidian
```

Make the script executable:

```bash
chmod +x convert.py
```

### Development Setup

For contributing or development:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python development tools
pip install ruff

# Install Node.js dependencies (for commitlint) using Bun
bun install

# Install lefthook for git hooks (optional but recommended)
# On macOS: brew install lefthook
# On Arch Linux: yay -S lefthook
# Or download from: https://github.com/evilmartians/lefthook/releases

# Initialize git hooks
lefthook install

# Run linter and formatter manually
ruff check .
ruff format .

# Test commit message format
echo "feat: add new feature" | bunx commitlint
```

#### Git Hooks

This project uses [lefthook](https://github.com/evilmartians/lefthook) to manage git hooks:

- **pre-commit**: Automatically runs `ruff format` and `ruff check --fix` on staged Python files
- **commit-msg**: Validates commit messages with [commitlint](https://commitlint.js.org/) following [Conventional Commits](https://www.conventionalcommits.org/)

**Commit message format:**

```text
<type>[optional scope]: <description>

Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
```

**Examples:**

```text
feat: add support for org-mode tables
fix(parser): handle empty code blocks correctly
docs: update installation instructions
```

Configuration is in `.commitlintrc.json` and follows `@commitlint/config-conventional`.

## Usage

Basic usage with default directories:

```bash
./convert.py
```

This will convert files from `~/Documents/slip-box` to `./output`.

Specify custom input and output directories:

```bash
./convert.py -i /path/to/org-roam -o /path/to/output
```

Extract org-mode properties to frontmatter:

```bash
./convert.py -p filetags roam_refs
```

### Options

- `-i, --input`: Input directory containing org-roam files (default: `~/Documents/slip-box`)
- `-o, --output`: Output directory for Markdown files (default: `./output`)
- `-p, --properties`: Org-mode properties to extract (e.g., `filetags`, `roam_refs`)
- `-h, --help`: Show help message

## Example

```bash
# Convert with custom directories
./convert.py --input ~/my-notes --output ~/obsidian-vault/imported

# Use short flags
./convert.py -i ~/org-roam -o ~/obsidian

# Extract filetags and roam_refs properties to frontmatter
./convert.py -i ~/org-roam -o ~/obsidian -p filetags roam_refs
```

## What Gets Converted

### Org-mode to Markdown

- Headers: `* Header` → `# Header`
- Code blocks: `#+BEGIN_SRC lang` → ` ```lang `
- ID links: `[[id:abc-123][Title]]` → `[[Title]]`
- External links: `[[url][text]]` → `[text](url)`
- Properties: `#+filetags: :tag1:tag2:` → YAML frontmatter

### Frontmatter Generation

When properties are extracted with `-p`, they are added to YAML frontmatter. Properties with a single value use the scalar format, while properties with multiple values use the array format:

```yaml
---
title: Note Title
filetags:
  - tag1
  - tag2
custom_tag: custom_value
roam_refs: https://example.com
---
```

### Removed Content

- `:PROPERTIES:` blocks
- `:ID:` fields
- `#+title:` directives (converted to frontmatter and H1 header)
- Property directives (converted to frontmatter if specified with `-p`)
- `#+RESULTS:` blocks
- Table of Contents (`:TOC_:` sections)
- Timestamp filename prefixes (e.g., `20200613170532-` → removed)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Known Limitations

- Does not require or use the org-roam database
- Assumes standard org-roam file structure
- Best effort conversion - complex org-mode features may not convert perfectly
