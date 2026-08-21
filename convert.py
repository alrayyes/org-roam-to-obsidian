#!/usr/bin/env python3
"""
Convert org-roam files to Obsidian Markdown format.
"""

import argparse
import os
import re
from datetime import datetime
from pathlib import Path

# An org link is [[target]] or [[target][description]]. Both halves stop at the
# first closing bracket, which is what org itself allows.
ORG_LINK = re.compile(r"\[\[([^\]]+)](?:\[([^\]]+)])?]")

# Org footnotes are [fn:label], both where they are referenced and where they
# are defined. A definition starts its line; anything else is a reference.
ORG_FOOTNOTE_DEFINITION = re.compile(r"^\[fn:([^\]]+)]\s*")
ORG_FOOTNOTE_REFERENCE = re.compile(r"\[fn:([^\]]+)]")


def convert_footnotes(line: str) -> str:
    """Rewrite org footnotes as the Markdown form Obsidian understands.

    A definition sits at the start of its line and needs the colon and space
    Markdown wants; org writes the text hard against the bracket. Everything
    else is a reference and only loses the ``fn:``.
    """
    definition = ORG_FOOTNOTE_DEFINITION.match(line)
    if definition:
        rest = line[definition.end() :]
        return f"[^{definition.group(1)}]: {rest}"

    return ORG_FOOTNOTE_REFERENCE.sub(r"[^\1]", line)


# Org and Markdown tables differ only in the separator row: org joins the dashes
# with + where Markdown wants |. Everything else already lines up.
ORG_TABLE_SEPARATOR = re.compile(r"^(\s*)\|[-+]+\|\s*$")


def convert_table_separator(line: str) -> str:
    """Turn an org table's separator row into the Markdown one.

    Only the separator differs between the two dialects, so a row that isn't one
    comes back untouched and the table's alignment survives.
    """
    if not ORG_TABLE_SEPARATOR.match(line):
        return line

    return line.replace("+", "|")


# Characters no common filesystem accepts in a name, and which Obsidian also
# refuses. A title carrying one keeps it as an alias so links still resolve.
UNSAFE_IN_FILENAME = re.compile(r'[\\/:*?"<>|]+')


def safe_filename(title: str) -> str:
    """Turn a note title into something a filesystem will accept.

    Obsidian resolves a wikilink by filename, so the file wants to be named
    after the title. Where the title contains a character a filename cannot,
    the caller keeps the original as an alias.
    """
    cleaned = UNSAFE_IN_FILENAME.sub(" ", title)
    # A slash usually separates words, so the space it leaves reads better with
    # a dash between them than as a double gap.
    cleaned = re.sub(r"\s+-\s+|\s{2,}", " - " if " / " in title else " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip(" .")


# A wikilink in the generated Markdown. Obsidian also accepts [[target|label]]
# and [[target#heading]], so only the part before either is the target.
WIKILINK = re.compile(r"\[\[([^\]|#]+)")


def wikilinks_outside_code(markdown: str) -> list[str]:
    """Every wikilink target in a converted note, ignoring fenced code.

    A JavaScript nested array reads as ``[[x]]`` and is not a link, so scanning
    the whole file would report code samples as broken links.
    """
    targets = []
    in_fence = False
    for line in markdown.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            targets.extend(match.group(1).strip() for match in WIKILINK.finditer(line))
    return targets


def modified_timestamp_of(org_file: Path) -> str:
    """When the note was last edited, from the org file's own mtime.

    org-roam records a creation time in the filename but nothing for edits, so
    the filesystem is the only signal there is. Publishing without it leaves a
    site dating every page at export time, because that is all it can see.
    """
    return datetime.fromtimestamp(org_file.stat().st_mtime).strftime("%Y-%m-%dT%H:%M:%S")


def parse_property_value(value: str) -> list[str]:
    """Split a ``#+property:`` value into its parts.

    Org writes tags wrapped in colons, ``:one:two:``, and everything else
    separated by whitespace. Splitting on every colon handles the first and
    destroys the second, because a URL is full of them.
    """
    if len(value) > 1 and value.startswith(":") and value.endswith(":"):
        return [tag for tag in value.split(":") if tag]

    return value.split()


def extract_id_and_title(filepath: Path) -> tuple[str, str]:
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
        properties: list[str] = None,
        add_created: bool = True,
        created_property: str = None,
        add_modified: bool = True,
        created_keys: list[str] = None,
        modified_keys: list[str] = None,
        publish_when: tuple[str, str] = None,
        publish_key: str = "publish",
        remove_dead_links: bool = True,
        title_heading: bool = False,
    ):
        self.source_dir = Path(source_dir).expanduser()
        self.target_dir = Path(target_dir)
        self.id_to_title: dict[str, str] = {}
        self.properties = properties or []
        self.add_created = add_created
        self.created_property = created_property
        self.add_modified = add_modified
        # Which frontmatter names carry the timestamps. Generators disagree:
        # Quartz reads created, created_at or date for one and modified,
        # lastmod, updated or last-modified for the other, so the same value can
        # go out under several names rather than forcing a post-process.
        self.created_keys = created_keys or ["created"]
        self.modified_keys = modified_keys or ["modified"]
        # (property, value) that marks a note for publishing, and the key to
        # write it under. Notes that do not match get nothing rather than
        # "false", because an exporter treats a missing flag as unpublished and
        # writing it out would bury the ones that are.
        self.publish_when = publish_when
        self.publish_key = publish_key
        self.remove_dead_links = remove_dead_links
        # Obsidian and Quartz both show the title above the body, so repeating
        # it as an H1 renders it twice. Off unless something asks for it.
        self.title_heading = title_heading
        # Output paths already written this run, so a second note claiming the
        # same name is noticed rather than silently replacing the first.
        self.written: dict[Path, str] = {}
        self.collisions = 0

    def build_id_map(self):
        """Build a mapping of IDs to titles from all org files."""
        print("Building ID to title mapping...")
        for org_file in self.source_dir.glob("*.org"):
            file_id, title = extract_id_and_title(org_file)
            if file_id and title:
                self.id_to_title[file_id] = title
        print(f"Found {len(self.id_to_title)} files with IDs")

    def convert_link(self, match: re.Match) -> str:
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

    def convert_org_to_markdown(
        self, content: str, created_timestamp: str = None, modified_timestamp: str = None
    ) -> str:
        """Convert org-mode syntax to Markdown."""
        lines = content.split("\n")
        result = []
        in_properties_block = False
        in_src_block = False
        in_quote_block = False
        skip_toc = False
        heading_indices = []
        publish = False
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

            if self.publish_when:
                prop, wanted = self.publish_when
                if line.lower().startswith(f"#+{prop.lower()}:"):
                    publish = wanted in parse_property_value(line.split(":", 1)[1].strip())

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
                quoted = convert_footnotes(quoted)
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
                # substitutions. Appending it raw is what left org syntax
                # sitting in headings.
                header_text = ORG_LINK.sub(self.convert_link, header_text)
                header_text = convert_footnotes(header_text)
                heading_indices.append(len(result))
                result.append(f"{'#' * level} {header_text}")
                continue

            # Inside a source block the text is code, not prose, so links,
            # footnotes and table separators are left as the author wrote them.
            if not in_src_block:
                line = ORG_LINK.sub(self.convert_link, line)
                line = convert_footnotes(line)
                line = convert_table_separator(line)

            result.append(line)

        # Markdown only renders a footnote where something references it, so a
        # definition nobody refers to would leave an empty Footnotes section.
        # Org shows those, so the text is kept as an ordinary line instead.
        body = "\n".join(result)
        referenced = set(re.findall(r"\[\^([^\]]+)\](?!:)", body))
        for index, line in enumerate(result):
            definition = re.match(r"^\[\^([^\]]+)\]: ?(.*)$", line)
            if definition and definition.group(1) not in referenced:
                result[index] = definition.group(2)

        # The title becomes the document's H1, so org's own headings move down a
        # level to sit under it. Without this every note has at least two H1s and
        # the outline in Obsidian reads flat. Recorded by index rather than
        # rewritten in place, so a # inside a code block is never touched.
        if title:
            for index in heading_indices:
                heading = result[index]
                level = len(heading) - len(heading.lstrip("#"))
                # Markdown stops at six, so the deepest level absorbs the shift
                # rather than emitting a heading no renderer understands.
                result[index] = "#" + heading if level < 6 else heading

        # Add YAML frontmatter if title or properties are found
        markdown_content = "\n".join(result).strip()

        if title or frontmatter_props or created_timestamp or modified_timestamp or publish:
            frontmatter = ["---"]
            if title:
                frontmatter.append(f"title: {title}")
                # The file is named after the title, so when the title contains
                # something a filename cannot, the original goes in as an alias
                # or every [[wikilink]] pointing here stops resolving.
                if safe_filename(title) != title:
                    frontmatter.append("aliases:")
                    frontmatter.append(f"  - {title}")
            if created_timestamp:
                for key in self.created_keys:
                    frontmatter.append(f"{key}: {created_timestamp}")
            if modified_timestamp:
                for key in self.modified_keys:
                    frontmatter.append(f"{key}: {modified_timestamp}")
            if publish:
                frontmatter.append(f"{self.publish_key}: true")
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

            if title and self.title_heading:
                return f"{frontmatter_str}\n\n# {title}\n\n{markdown_content}"
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
        """Convert a single org file to Markdown.

        Returns True when a file was written. A note whose output name is
        already taken still overwrites, because losing the later note would be
        no better, but it says so rather than doing it quietly.
        """
        try:
            with open(org_file, encoding="utf-8") as f:
                content = f.read()

            # Extract created timestamp if enabled
            created_timestamp = None
            if self.add_created:
                created_timestamp = self.extract_created_timestamp(org_file, content)

            modified_timestamp = None
            if self.add_modified:
                modified_timestamp = modified_timestamp_of(org_file)

            markdown_content = self.convert_org_to_markdown(
                content, created_timestamp, modified_timestamp
            )

            # The filename is what Obsidian resolves a [[wikilink]] against, and
            # the links carry titles, so the file is named after the title. The
            # org filename is the fallback for a note that has no title.
            fallback = org_file.stem
            if re.match(r"^\d{14}-", fallback):
                fallback = fallback[15:]

            _, title = extract_id_and_title(org_file)
            filename = safe_filename(title) if title else fallback
            if not filename:
                filename = fallback

            output_file = self.target_dir / f"{filename}.md"

            if output_file in self.written:
                # Two notes genuinely share a title. Keeping the org filename for
                # the second loses neither, which overwriting would.
                alternative = self.target_dir / f"{fallback}.md"
                print(
                    f"Warning: {org_file.name} and {self.written[output_file]} both convert to "
                    f"{output_file.name}. Writing {alternative.name} instead."
                )
                self.collisions += 1
                output_file = alternative

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            self.written[output_file] = org_file.name
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
        # Sorted so a rerun produces the same vault. Glob order is filesystem
        # order, which decides who wins a title clash and would otherwise make
        # two runs over the same notes differ.
        org_files = sorted(self.source_dir.glob("*.org"))

        for org_file in org_files:
            self.convert_file(org_file)

        # Counting notes read hides a collision entirely: nine of them can go
        # missing while the summary still reports every file as converted.
        written = len(self.written)
        summary = (
            f"\nConversion complete: {written} file{'' if written == 1 else 's'} written "
            f"from {len(org_files)} note{'' if len(org_files) == 1 else 's'}"
        )
        if self.collisions:
            plural = "" if self.collisions == 1 else "s"
            summary += f" ({self.collisions} name collision{plural}, kept under the org filename)"
        print(summary)

        self.report_broken_links()

    def strip_dead_links(self, broken_by_file: dict[Path, list[str]]):
        """Unwrap wikilinks whose target does not exist, keeping the words.

        Runs once every note is written, because only then is the full set of
        filenames and aliases known. Fenced code is skipped: a JavaScript
        nested array reads as [[x]] and is not a link.
        """
        for path, targets in broken_by_file.items():
            lines = path.read_text(encoding="utf-8").split("\n")
            in_fence = False
            for index, line in enumerate(lines):
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for target in targets:
                    lines[index] = lines[index].replace(f"[[{target}]]", target)
            path.write_text("\n".join(lines), encoding="utf-8")

    def report_broken_links(self):
        """Name every wikilink in the output that resolves to nothing.

        Checked against what was actually written rather than against the notes
        that were read, because the filename is what Obsidian resolves against.
        A note reached only through an alias counts as resolvable.
        """
        resolvable = {path.stem for path in self.written}
        for path in self.written:
            for alias in re.findall(r"^  - (.+)$", path.read_text(encoding="utf-8"), re.M):
                resolvable.add(alias.strip())

        broken = []
        by_file: dict[Path, list[str]] = {}
        for path in sorted(self.written):
            for target in wikilinks_outside_code(path.read_text(encoding="utf-8")):
                if target not in resolvable:
                    broken.append((path.name, target))
                    by_file.setdefault(path, []).append(target)

        if not broken:
            return

        if self.remove_dead_links:
            self.strip_dead_links(by_file)

        if len(broken) == 1:
            heading = "1 link points nowhere"
        else:
            heading = f"{len(broken)} links point nowhere"
        tail = (
            "The link syntax was removed and the words kept; --keep-dead-links leaves them:"
            if self.remove_dead_links
            else "Obsidian shows these as unresolved, so they are worth fixing:"
        )
        print(f"\n{heading}. {tail}")
        for note, target in broken:
            print(f"  {note}: [[{target}]]")


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
        "--title-heading",
        action="store_true",
        help="Repeat the title as an H1 at the top of the body. Off by default, because "
        "Obsidian and Quartz already show it",
    )
    parser.add_argument(
        "--keep-dead-links",
        action="store_true",
        help="Keep wikilinks whose target does not exist, instead of unwrapping them",
    )
    parser.add_argument(
        "--publish-when",
        metavar="PROPERTY=VALUE",
        help="Mark a note for publishing when it carries this org property value, "
        "for example category=public",
    )
    parser.add_argument(
        "--publish-key",
        default="publish",
        metavar="KEY",
        help="Frontmatter key for the publish flag (default: publish)",
    )
    parser.add_argument(
        "--created-key",
        nargs="+",
        default=["created"],
        metavar="KEY",
        help="One or more frontmatter keys for the created timestamp (default: created). "
        "Quartz also reads created_at and date",
    )
    parser.add_argument(
        "--modified-key",
        nargs="+",
        default=["modified"],
        metavar="KEY",
        help="One or more frontmatter keys for the modified timestamp (default: modified). "
        "Quartz also reads lastmod, updated and last-modified",
    )
    parser.add_argument(
        "--no-modified",
        action="store_true",
        help="Disable adding the modified timestamp from the org file's mtime",
    )
    parser.add_argument(
        "--created-property",
        type=str,
        help="Use a specific org-mode property for created timestamp instead of filename",
    )

    args = parser.parse_args()

    publish_when = None
    if args.publish_when:
        if "=" not in args.publish_when:
            parser.error("--publish-when takes PROPERTY=VALUE, for example category=public")
        prop, _, value = args.publish_when.partition("=")
        publish_when = (prop.strip(), value.strip())

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
        add_modified=not args.no_modified,
        created_keys=args.created_key,
        modified_keys=args.modified_key,
        publish_when=publish_when,
        publish_key=args.publish_key,
        remove_dead_links=not args.keep_dead_links,
        title_heading=args.title_heading,
    )
    converter.convert_all()


if __name__ == "__main__":
    main()
