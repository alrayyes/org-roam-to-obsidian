#!/usr/bin/env python3
"""
Convert org-roam files to Obsidian Markdown format.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, Tuple


def extract_id_and_title(filepath: Path) -> Tuple[str, str]:
    """Extract the ID and title from an org file."""
    file_id = None
    title = None

    with open(filepath, 'r', encoding='utf-8') as f:
        in_properties = False
        for line in f:
            if line.strip() == ":PROPERTIES:":
                in_properties = True
            elif line.strip() == ":END:":
                in_properties = False
            elif in_properties and line.startswith(":ID:"):
                file_id = line.split(":ID:")[1].strip()
            elif line.startswith("#+title:"):
                title = line.split("#+title:")[1].strip()

            if file_id and title:
                break

    return file_id, title


class OrgRoamConverter:
    def __init__(self, source_dir: str, target_dir: str):
        self.source_dir = Path(source_dir).expanduser()
        self.target_dir = Path(target_dir)
        self.id_to_title: Dict[str, str] = {}

    def build_id_map(self):
        """Build a mapping of IDs to titles from all org files."""
        print("Building ID to title mapping...")
        for org_file in self.source_dir.glob("*.org"):
            file_id, title = extract_id_and_title(org_file)
            if file_id and title:
                self.id_to_title[file_id] = title
        print(f"Found {len(self.id_to_title)} files with IDs")

    def convert_org_to_markdown(self, content: str) -> str:
        """Convert org-mode syntax to Markdown."""
        lines = content.split('\n')
        result = []
        in_properties = False
        in_src_block = False
        skip_toc = False
        title = None

        for line in lines:
            # Skip properties block
            if line.strip() == ":PROPERTIES:":
                in_properties = True
                continue
            elif line.strip() == ":END:":
                in_properties = False
                continue
            elif in_properties:
                continue

            # Extract title
            if line.startswith("#+title:"):
                title = line.split("#+title:")[1].strip()
                continue

            # Skip other org-mode directives
            if line.startswith("#+") and not line.startswith("#+BEGIN") and not line.startswith("#+END"):
                continue

            # Skip TOC sections
            if ":TOC_" in line and ":noexport:" in line:
                skip_toc = True
                continue

            # Convert code blocks
            if line.startswith("#+BEGIN_SRC") or line.startswith("#+begin_src"):
                lang = line.split()[-1] if len(line.split()) > 1 else ""
                result.append(f"```{lang}")
                in_src_block = True
                continue
            elif line.startswith("#+END_SRC") or line.startswith("#+end_src"):
                result.append("```")
                in_src_block = False
                continue
            elif line.startswith("#+RESULTS:") or line.startswith("#+results:"):
                continue

            # Skip content in results blocks (lines starting with: after RESULTS)
            if not in_src_block and line.startswith(": "):
                continue

            # Convert headers
            if line.startswith("*") and not in_src_block:
                # Check if this is a TOC line that should be skipped
                if skip_toc:
                    if line.startswith("*") and not line.startswith("**"):
                        skip_toc = False
                    else:
                        continue

                level = len(line) - len(line.lstrip("*"))
                header_text = line.lstrip("* ").strip()
                result.append(f"{'#' * level} {header_text}")
                continue

            # Convert org-mode links [[id:...][title]] or [[url][title]]
            line = re.sub(
                r'\[\[id:([a-f0-9-]+)]\[([^]]+)]]',
                lambda m: f"[[{self.id_to_title.get(m.group(1), m.group(2))}]]",
                line
            )

            # Convert [[url][title]] to [title](url)
            line = re.sub(
                r'\[\[([^:\]]+)]\[([^]]+)]]',
                r'[\2](\1)',
                line
            )

            # Convert [[url]] to [url](url)
            line = re.sub(
                r'\[\[([^:\]]+)]]',
                r'[\1](\1)',
                line
            )

            result.append(line)

        # Add title as front matter if found
        if title:
            markdown_content = '\n'.join(result).strip()
            return f"# {title}\n\n{markdown_content}"

        return '\n'.join(result).strip()

    def convert_file(self, org_file: Path) -> bool:
        """Convert a single org file to Markdown."""
        try:
            with open(org_file, 'r', encoding='utf-8') as f:
                content = f.read()

            markdown_content = self.convert_org_to_markdown(content)

            # Create the output filename (remove timestamp prefix, change extension)
            filename = org_file.stem
            # Remove the timestamp prefix (20YYMMDDHHMMSS-)
            if re.match(r'^\d{14}-', filename):
                filename = filename[15:]

            output_file = self.target_dir / f"{filename}.md"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            print(f"Converted: {org_file.name} -> {output_file.name}")
            return True

        except Exception as e:
            print(f"Error converting {org_file.name}: {e}")
            return False

    def convert_all(self):
        """Convert all org files in the source directory."""
        # Create a target directory if it doesn't exist
        self.target_dir.mkdir(parents=True, exist_ok=True)

        # First pass: build ID to title mapping
        self.build_id_map()

        # Second pass: convert all files
        print("\nConverting files...")
        org_files = list(self.source_dir.glob("*.org"))
        success_count = 0

        for org_file in org_files:
            if self.convert_file(org_file):
                success_count += 1

        print(f"\nConversion complete: {success_count}/{len(org_files)} files converted successfully")


def main():
    parser = argparse.ArgumentParser(
        description="Convert org-roam files to Obsidian markdown format"
    )
    parser.add_argument(
        "-i", "--input",
        default=os.path.expanduser("~/Documents/slip-box"),
        help="Input directory containing org-roam files (default: ~/Documents/slip-box)"
    )
    parser.add_argument(
        "-o", "--output",
        default=os.path.join(os.getcwd(), "output"),
        help="Output directory for markdown files (default: ./output)"
    )

    args = parser.parse_args()

    print(f"Converting org-roam files from: {args.input}")
    print(f"Output directory: {args.output}")

    converter = OrgRoamConverter(args.input, args.output)
    converter.convert_all()


if __name__ == "__main__":
    main()
