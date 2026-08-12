#!/usr/bin/env python3
"""
Convert org-roam files to Obsidian Markdown format.
"""

import argparse
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# An org link is [[target]] or [[target][description]]. Both halves stop at the
# first closing bracket, which is what org itself allows.
ORG_LINK = re.compile(r"\[\[([^\]]+)](?:\[([^\]]+)])?]")


def parse_property_value(value: str) -> List[str]:
    """Split a ``#+property:`` value into its parts.

    Org writes tags wrapped in colons, ``:one:two:``, and everything else
    separated by whitespace. Splitting on every colon handles the first and
    destroys the second, because a URL is full of them.
    """
    if len(value) > 1 and value.startswith(":") and value.endswith(":"):
        return [tag for tag in value.split(":") if tag]

    return value.split()


def extract_id_and_title(filepath: Path) -> Tuple[str, str]:
    """Extract the ID and title from an org file."""
    file_id = None
    title = None

    with open(filepath, encoding="utf-8") as f:
        in_properties = False
        for line in f:
            if line.strip() == ":PROPERTIES:":
                in_properties = True
            elif line.strip() == ":END:":
                in_properties = False
            elif in_properties and line.startswith(":ID:"):
                file_id = line.split(":ID:")[1].strip()
            elif line.lower().startswith("#+title:"):
                title = line.split(":", 1)[1].strip()

            if file_id and title:
                break

    return file_id, title


class OrgRoamConverter:
    def __init__(
        self,
        source_dir: str,
        target_dir: str,
        properties: List[str] = None,
        add_created: bool = True,
        created_property: str = None,
    ):
        self.source_dir = Path(source_dir).expanduser()
        self.target_dir = Path(target_dir)
        self.id_to_title: Dict[str, str] = {}
        self.properties = properties or []
        self.add_created = add_created
        self.created_property = created_property

    def build_id_map(self):
        """Build a mapping of IDs to titles from all org files."""
        print("Building ID to title mapping...")
        for org_file in self.source_dir.glob("*.org"):
            file_id, title = extract_id_and_title(org_file)
            if file_id and title:
                self.id_to_title[file_id] = title
        print(f"Found {len(self.id_to_title)} files with IDs")

    def convert_link(self, match: "re.Match") -> str:
        """Render one org link as Markdown.

        Every link form is handled in this single pass. Substituting them one
        pattern at a time cannot work: once an ID link has become [[Title]] it
        is indistinguishable from an org link whose target is literally
        "Title", so the pass that handles the second rewrites the first.
        """
        target, description = match.group(1), match.group(2)

        if target.startswith("id:"):
            file_id = target[len("id:") :]
            return f"[[{self.id_to_title.get(file_id, description or file_id)}]]"

        return f"[{description or target}]({target})"

    def convert_org_to_markdown(self, content: str, created_timestamp: str = None) -> str:
        """Convert org-mode syntax to Markdown."""
        lines = content.split("\n")
        result = []
        in_properties_block = False
        in_src_block = False
        in_quote_block = False
        skip_toc = False
        title = None
        frontmatter_props = {}

        for line in lines:
            # Skip properties block
            if line.strip() == ":PROPERTIES:":
                in_properties_block = True
                continue
            elif line.strip() == ":END:":
                in_properties_block = False
                continue
            elif in_properties_block:
                continue

            # Extract title. Org accepts either case and older files often use
            # #+TITLE:, which used to fall through to the directive-drop rule and
            # take the note's title with it.
            if line.lower().startswith("#+title:"):
                title = line.split(":", 1)[1].strip()
                continue

            # Extract configured properties (skip created_property if it's being used)
            for prop in self.properties:
                if prop == self.created_property:
                    continue
                if line.startswith(f"#+{prop}:"):
                    prop_value = line.split(f"#+{prop}:", 1)[1].strip()
                    frontmatter_props[prop] = parse_property_value(prop_value)
                    break

            # Org accepts either case for its directives, and org-insert-
            # structure-template writes the lowercase form, so every #+ test
            # below works on a folded copy of the line.
            directive = line.lower()

            # Skip other org-mode directives
            if (
                directive.startswith("#+")
                and not directive.startswith("#+begin")
                and not directive.startswith("#+end")
            ):
                continue

            # Skip TOC sections
            if ":TOC_" in line and ":noexport:" in line:
                skip_toc = True
                continue

            # Convert code blocks
            if directive.startswith("#+begin_src"):
                lang = line.split()[-1] if len(line.split()) > 1 else ""
                result.append(f"```{lang}")
                in_src_block = True
                continue
            elif directive.startswith("#+end_src"):
                result.append("```")
                in_src_block = False
                continue
            elif directive.startswith("#+begin_example"):
                result.append("```")
                in_src_block = True
                continue
            elif directive.startswith("#+end_example"):
                result.append("```")
                in_src_block = False
                continue
            elif directive.startswith("#+begin_quote"):
                in_quote_block = True
                continue
            elif directive.startswith("#+end_quote"):
                in_quote_block = False
                continue
            elif directive.startswith("#+results:"):
                continue
            elif directive.startswith("#+begin") or directive.startswith("#+end"):
                # A block we have no rendering for. Drop the delimiters and keep
                # the text, which is what happened to every lowercase block
                # before the directive test stopped being case-sensitive.
                continue

            if in_quote_block:
                # Links inside a quote need converting like any other prose, so
                # this runs the substitution rather than short-circuiting past it.
                # A blank line still needs the marker, or the quote ends there and
                # the rest becomes an ordinary paragraph.
                quoted = ORG_LINK.sub(self.convert_link, line)
                result.append(f"> {quoted}" if quoted.strip() else ">")
                continue

            # Skip content in results blocks (lines starting with: after RESULTS)
            if not in_src_block and line.startswith(": "):
                continue

            # Everything under a TOC heading belongs to the table of contents,
            # not just the sub-headings. The section runs until the next
            # top-level heading, which is where org itself ends it.
            if skip_toc:
                if line.startswith("*") and not line.startswith("**"):
                    skip_toc = False
                else:
                    continue

            # Convert headers
            if line.startswith("*") and not in_src_block:
                level = len(line) - len(line.lstrip("*"))
                header_text = line.lstrip("* ").strip()
                # Heading text is prose like any other line, so it gets the same
                # link substitution. Appending it raw is what left org syntax
                # sitting in headings.
                header_text = ORG_LINK.sub(self.convert_link, header_text)
                result.append(f"{'#' * level} {header_text}")
                continue

            line = ORG_LINK.sub(self.convert_link, line)

            result.append(line)

        # Add YAML frontmatter if title or properties are found
        markdown_content = "\n".join(result).strip()

        if title or frontmatter_props or created_timestamp:
            frontmatter = ["---"]
            if title:
                frontmatter.append(f"title: {title}")
            if created_timestamp:
                frontmatter.append(f"created: {created_timestamp}")
            for prop_name, prop_values in frontmatter_props.items():
                if len(prop_values) == 1:
                    # Single value: use scalar format
                    frontmatter.append(f"{prop_name}: {prop_values[0]}")
                else:
                    # Multiple values: use array format
                    frontmatter.append(f"{prop_name}:")
                    for val in prop_values:
                        frontmatter.append(f"  - {val}")
            frontmatter.append("---")
            frontmatter_str = "\n".join(frontmatter)

            if title:
                return f"{frontmatter_str}\n\n# {title}\n\n{markdown_content}"
            else:
                return f"{frontmatter_str}\n\n{markdown_content}"

        return markdown_content

    def extract_created_timestamp(self, org_file: Path, content: str) -> str:
        """Extract created timestamp from filename or specified property."""
        if self.created_property:
            # Extract from specified property
            lines = content.split("\n")
            for line in lines:
                if line.startswith(f"#+{self.created_property}:"):
                    return line.split(f"#+{self.created_property}:")[1].strip()

        # Extract from filename timestamp (format: YYYYMMDDHHMMSS)
        filename = org_file.stem
        timestamp_match = re.match(r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})-", filename)
        if timestamp_match:
            year, month, day, hour, minute, second = timestamp_match.groups()
            return f"{year}-{month}-{day}T{hour}:{minute}:{second}"

        return None

    def convert_file(self, org_file: Path) -> bool:
        """Convert a single org file to Markdown."""
        try:
            with open(org_file, encoding="utf-8") as f:
                content = f.read()

            # Extract created timestamp if enabled
            created_timestamp = None
            if self.add_created:
                created_timestamp = self.extract_created_timestamp(org_file, content)

            markdown_content = self.convert_org_to_markdown(content, created_timestamp)

            # Create the output filename (remove timestamp prefix, change extension)
            filename = org_file.stem
            # Remove the timestamp prefix (20YYMMDDHHMMSS-)
            if re.match(r"^\d{14}-", filename):
                filename = filename[15:]

            output_file = self.target_dir / f"{filename}.md"

            with open(output_file, "w", encoding="utf-8") as f:
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

        print(
            f"\nConversion complete: {success_count}/{len(org_files)} files converted successfully"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Convert org-roam files to Obsidian markdown format"
    )
    parser.add_argument(
        "-i",
        "--input",
        default=os.path.expanduser("~/Documents/slip-box"),
        help="Input directory containing org-roam files (default: ~/Documents/slip-box)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=os.path.join(os.getcwd(), "output"),
        help="Output directory for markdown files (default: ./output)",
    )
    parser.add_argument(
        "-p",
        "--properties",
        nargs="+",
        default=[],
        help="Org-mode properties to extract (e.g., filetags roam_refs)",
    )
    parser.add_argument(
        "--no-created",
        action="store_true",
        help="Disable adding created timestamp from filename",
    )
    parser.add_argument(
        "--created-property",
        type=str,
        help="Use a specific org-mode property for created timestamp instead of filename",
    )

    args = parser.parse_args()

    print(f"Converting org-roam files from: {args.input}")
    print(f"Output directory: {args.output}")
    if args.properties:
        print(f"Extracting properties: {', '.join(args.properties)}")
    if not args.no_created:
        if args.created_property:
            print(f"Using created timestamp from property: {args.created_property}")
        else:
            print("Extracting created timestamp from filename")

    converter = OrgRoamConverter(
        args.input,
        args.output,
        args.properties,
        add_created=not args.no_created,
        created_property=args.created_property,
    )
    converter.convert_all()


if __name__ == "__main__":
    main()
