# Org-Roam to Obsidian Converter

Convert your org-roam notes to Obsidian-compatible Markdown format.

## Features

- Converts org-mode syntax to Markdown
- Transforms org-roam ID links (`[[id:...][title]]`) to Obsidian wikilinks (`[[title]]`)
- Removes org-mode metadata and directives
- Converts code blocks to Markdown fenced code blocks
- Removes timestamp prefixes from filenames
- Preserves note titles and content structure

## Requirements

- Python 3.6+
- No external dependencies required (uses only standard library)

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

### Options

- `-i, --input`: Input directory containing org-roam files (default: `~/Documents/slip-box`)
- `-o, --output`: Output directory for markdown files (default: `./output`)
- `-h, --help`: Show help message

## Example

```bash
# Convert with custom directories
./convert.py --input ~/my-notes --output ~/obsidian-vault/imported

# Use short flags
./convert.py -i ~/org-roam -o ~/obsidian
```

## What Gets Converted

### Org-mode to Markdown

- Headers: `* Header` → `# Header`
- Code blocks: `#+BEGIN_SRC lang` → ` ```lang `
- ID links: `[[id:abc-123][Title]]` → `[[Title]]`
- External links: `[[url][text]]` → `[text](url)`

### Removed Content

- `:PROPERTIES:` blocks
- `:ID:` fields
- `#+title:` directives
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

## Author

Created for converting personal org-roam notes to Obsidian format.
