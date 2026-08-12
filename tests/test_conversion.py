"""Unit tests for the org-mode to Markdown conversion.

These exercise the converter through the two entry points a caller has:
``convert_org_to_markdown`` for a document's body, and the small helpers that
read metadata off a file. Tests marked ``xfail`` describe behaviour the README
promises but the converter does not yet deliver; each names the issue tracking
it, and the fix removes the marker rather than editing the expectation.
"""

import pytest

from convert import OrgRoamConverter, extract_id_and_title


@pytest.fixture
def converter(tmp_path):
    return OrgRoamConverter(str(tmp_path / "source"), str(tmp_path / "target"))


class TestHeadings:
    def test_top_level_heading_becomes_h1_without_a_title(self, converter):
        assert converter.convert_org_to_markdown("* Introduction") == "# Introduction"

    def test_nesting_depth_is_preserved_without_a_title(self, converter):
        org = "* One\n** Two\n*** Three"

        assert converter.convert_org_to_markdown(org) == "# One\n## Two\n### Three"

    def test_headings_shift_down_when_a_title_takes_the_h1(self, converter):
        org = "#+title: My Note\n\n* Overview\n** Detail"

        markdown = converter.convert_org_to_markdown(org)

        assert markdown.endswith("# My Note\n\n## Overview\n### Detail")

    def test_only_one_h1_survives_a_titled_note(self, converter):
        org = "#+title: My Note\n\n* One\n* Two"

        markdown = converter.convert_org_to_markdown(org)

        assert [line for line in markdown.split("\n") if line.startswith("# ")] == ["# My Note"]

    def test_the_sixth_level_does_not_overflow(self, converter):
        org = "#+title: My Note\n\n****** Deep"

        markdown = converter.convert_org_to_markdown(org)

        assert markdown.endswith("###### Deep")


class TestQuoteAndExampleBlocks:
    def test_quote_block_becomes_a_blockquote(self, converter):
        org = "#+BEGIN_QUOTE\nSomething worth quoting.\n#+END_QUOTE"

        assert converter.convert_org_to_markdown(org) == "> Something worth quoting."

    def test_lowercase_quote_block_is_recognised(self, converter):
        org = "#+begin_quote\nSomething worth quoting.\n#+end_quote"

        assert converter.convert_org_to_markdown(org) == "> Something worth quoting."

    def test_every_line_of_a_quote_is_prefixed(self, converter):
        org = "#+begin_quote\nFirst line.\nSecond line.\n#+end_quote"

        assert converter.convert_org_to_markdown(org) == "> First line.\n> Second line."

    def test_blank_lines_inside_a_quote_keep_the_marker(self, converter):
        org = "#+begin_quote\nFirst.\n\nSecond.\n#+end_quote"

        assert converter.convert_org_to_markdown(org) == "> First.\n>\n> Second."

    def test_example_block_becomes_a_plain_fenced_block(self, converter):
        org = "#+begin_example\nliteral text\n#+end_example"

        assert converter.convert_org_to_markdown(org) == "```\nliteral text\n```"

    def test_uppercase_example_block_is_recognised(self, converter):
        org = "#+BEGIN_EXAMPLE\nliteral text\n#+END_EXAMPLE"

        assert converter.convert_org_to_markdown(org) == "```\nliteral text\n```"

    def test_org_syntax_inside_an_example_is_left_alone(self, converter):
        org = "#+begin_example\n* not a heading\n#+end_example"

        assert converter.convert_org_to_markdown(org) == "```\n* not a heading\n```"

    def test_links_inside_a_quote_are_still_converted(self, converter):
        converter.id_to_title["abc-123"] = "Eisenhower"
        org = "#+begin_quote\nSaid by [[id:abc-123][Ike]].\n#+end_quote"

        assert converter.convert_org_to_markdown(org) == "> Said by [[Eisenhower]]."

    def test_an_unhandled_block_loses_its_delimiters_but_keeps_its_text(self, converter):
        org = "#+begin_verse\nRoses are red\n#+end_verse"

        assert converter.convert_org_to_markdown(org) == "Roses are red"


class TestCodeBlocks:
    def test_src_block_becomes_a_fenced_block_with_its_language(self, converter):
        org = "#+BEGIN_SRC python\nprint('hi')\n#+END_SRC"

        assert converter.convert_org_to_markdown(org) == "```python\nprint('hi')\n```"

    def test_lowercase_block_delimiters_are_recognised(self, converter):
        org = "#+begin_src sh\necho hi\n#+end_src"

        assert converter.convert_org_to_markdown(org) == "```sh\necho hi\n```"

    def test_asterisks_inside_a_block_are_not_read_as_headings(self, converter):
        org = "#+BEGIN_SRC text\n* not a heading\n#+END_SRC"

        assert converter.convert_org_to_markdown(org) == "```text\n* not a heading\n```"

    def test_asterisks_inside_a_lowercase_block_are_not_read_as_headings(self, converter):
        org = "#+begin_src text\n* not a heading\n#+end_src"

        assert converter.convert_org_to_markdown(org) == "```text\n* not a heading\n```"

    def test_results_blocks_are_dropped(self, converter):
        org = "#+BEGIN_SRC sh\necho hi\n#+END_SRC\n\n#+RESULTS:\n: hi\n\nAfter."

        markdown = converter.convert_org_to_markdown(org)

        assert "RESULTS" not in markdown
        assert ": hi" not in markdown
        assert markdown.endswith("After.")


class TestLinks:
    def test_id_link_resolves_to_the_target_note_title(self, converter):
        converter.id_to_title["abc-123"] = "Real Title"

        markdown = converter.convert_org_to_markdown("See [[id:abc-123][stale label]].")

        assert markdown == "See [[Real Title]]."

    def test_unknown_id_falls_back_to_the_link_text(self, converter):
        markdown = converter.convert_org_to_markdown("See [[id:abc-123][Other Note]].")

        assert markdown == "See [[Other Note]]."

    def test_described_external_link_becomes_an_inline_link(self, converter):
        markdown = converter.convert_org_to_markdown("See [[https://example.com][Example]].")

        assert markdown == "See [Example](https://example.com)."

    def test_bare_external_link_becomes_a_self_titled_link(self, converter):
        markdown = converter.convert_org_to_markdown("See [[https://example.com]].")

        assert markdown == "See [https://example.com](https://example.com)."

    def test_link_inside_a_heading_is_converted(self, converter):
        converter.id_to_title["abc-123"] = "Gitlab"

        markdown = converter.convert_org_to_markdown("** [[id:abc-123][Gitlab]]")

        assert markdown == "## [[Gitlab]]"

    def test_link_surrounded_by_heading_text_is_converted(self, converter):
        converter.id_to_title["abc-123"] = "promise"

        markdown = converter.convert_org_to_markdown("** Fulfilling a [[id:abc-123][promise]]")

        assert markdown == "## Fulfilling a [[promise]]"

    def test_external_link_inside_a_heading_is_converted(self, converter):
        markdown = converter.convert_org_to_markdown("* See [[https://example.com][the docs]]")

        assert markdown == "# See [the docs](https://example.com)"

    def test_internal_anchor_link_becomes_an_inline_link(self, converter):
        markdown = converter.convert_org_to_markdown("See [[#intro][Intro]].")

        assert markdown == "See [Intro](#intro)."


class TestUnreferencedFootnotes:
    def test_a_definition_nothing_refers_to_becomes_plain_text(self, converter):
        """Markdown renders no footnote unless something references it."""
        org = "* Footnotes\n[fn:doc]https://example.com"

        markdown = converter.convert_org_to_markdown(org)

        assert markdown == "# Footnotes\nhttps://example.com"

    def test_a_referenced_definition_stays_a_footnote(self, converter):
        org = "Body[fn:doc] text.\n\n[fn:doc]https://example.com"

        markdown = converter.convert_org_to_markdown(org)

        assert "Body[^doc] text." in markdown
        assert "[^doc]: https://example.com" in markdown

    def test_only_the_unreferenced_one_is_flattened(self, converter):
        org = "Body[fn:used] text.\n\n[fn:used]used.\n[fn:spare]spare."

        markdown = converter.convert_org_to_markdown(org)

        assert "[^used]: used." in markdown
        assert "[^spare]" not in markdown
        assert "spare." in markdown


class TestTables:
    def test_separator_row_becomes_the_markdown_form(self, converter):
        org = "| A | B |\n|---+---|\n| 1 | 2 |"

        assert converter.convert_org_to_markdown(org) == "| A | B |\n|---|---|\n| 1 | 2 |"

    def test_a_separator_without_pluses_is_left_alone(self, converter):
        org = "| A | B |\n|---------|\n| 1 | 2 |"

        assert converter.convert_org_to_markdown(org) == "| A | B |\n|---------|\n| 1 | 2 |"

    def test_body_rows_are_untouched(self, converter):
        org = "| Country | Share |\n|---------+-------|\n| USSR    |   57% |"

        markdown = converter.convert_org_to_markdown(org)

        assert markdown.endswith("| USSR    |   57% |")
        assert "|---------|-------|" in markdown

    def test_an_indented_table_is_converted(self, converter):
        org = "Body.\n  | A | B |\n  |---+---|"

        assert converter.convert_org_to_markdown(org) == "Body.\n  | A | B |\n  |---|---|"

    def test_a_plus_in_prose_is_not_a_table(self, converter):
        org = "Use a+b for the sum."

        assert converter.convert_org_to_markdown(org) == "Use a+b for the sum."

    def test_a_table_inside_a_code_block_is_left_alone(self, converter):
        org = "#+begin_src text\n|---+---|\n#+end_src"

        assert converter.convert_org_to_markdown(org) == "```text\n|---+---|\n```"


class TestFootnotes:
    def test_inline_reference_becomes_a_markdown_footnote(self, converter):
        org = "A Promise[fn:footnote] is asynchronous."

        assert converter.convert_org_to_markdown(org) == "A Promise[^footnote] is asynchronous."

    def test_definition_gains_the_colon_and_space_markdown_needs(self, converter):
        org = "Body[fn:footnote].\n\n[fn:footnote]https://example.com"

        assert converter.convert_org_to_markdown(org).endswith("[^footnote]: https://example.com")

    def test_definition_already_spaced_is_handled(self, converter):
        org = "Body[fn:doc].\n\n[fn:doc] See the manual."

        assert converter.convert_org_to_markdown(org).endswith("[^doc]: See the manual.")

    def test_hyphenated_labels_survive(self, converter):
        org = "Async[fn:async-functions] is new."

        assert converter.convert_org_to_markdown(org) == "Async[^async-functions] is new."

    def test_footnote_inside_a_heading_is_converted(self, converter):
        assert converter.convert_org_to_markdown("* British[fn:british]") == "# British[^british]"

    def test_footnotes_inside_a_code_block_are_left_alone(self, converter):
        org = "#+begin_src text\nliteral[fn:x] text\n#+end_src"

        assert converter.convert_org_to_markdown(org) == "```text\nliteral[fn:x] text\n```"

    def test_a_reference_and_its_definition_convert_together(self, converter):
        org = "Body[fn:a] text.\n\n[fn:a]The note."

        assert converter.convert_org_to_markdown(org) == "Body[^a] text.\n\n[^a]: The note."


class TestFrontmatter:
    def test_title_becomes_frontmatter_and_an_h1(self, converter):
        markdown = converter.convert_org_to_markdown("#+title: My Note\n\nBody.")

        assert markdown == "---\ntitle: My Note\n---\n\n# My Note\n\nBody."

    def test_uppercase_title_directive_is_recognised(self, converter):
        markdown = converter.convert_org_to_markdown("#+TITLE: My Note\n\nBody.")

        assert markdown == "---\ntitle: My Note\n---\n\n# My Note\n\nBody."

    def test_a_document_without_metadata_gets_no_frontmatter(self, converter):
        assert converter.convert_org_to_markdown("Just body text.") == "Just body text."

    def test_multi_valued_property_is_written_as_a_list(self, tmp_path):
        converter = OrgRoamConverter(str(tmp_path), str(tmp_path), properties=["filetags"])

        markdown = converter.convert_org_to_markdown("#+filetags: :one:two:\n\nBody.")

        assert "filetags:\n  - one\n  - two" in markdown

    def test_single_valued_property_is_written_as_a_scalar(self, tmp_path):
        converter = OrgRoamConverter(str(tmp_path), str(tmp_path), properties=["filetags"])

        markdown = converter.convert_org_to_markdown("#+filetags: :solo:\n\nBody.")

        assert "filetags: solo" in markdown

    def test_unrequested_properties_are_dropped(self, converter):
        markdown = converter.convert_org_to_markdown("#+filetags: :one:\n\nBody.")

        assert markdown == "Body."

    def test_url_valued_property_survives_intact(self, tmp_path):
        converter = OrgRoamConverter(str(tmp_path), str(tmp_path), properties=["roam_refs"])

        markdown = converter.convert_org_to_markdown("#+roam_refs: https://example.com\n\nBody.")

        assert "roam_refs: https://example.com" in markdown

    def test_several_urls_become_a_list(self, tmp_path):
        converter = OrgRoamConverter(str(tmp_path), str(tmp_path), properties=["roam_refs"])
        org = "#+roam_refs: https://example.com https://other.example\n\nBody."

        markdown = converter.convert_org_to_markdown(org)

        assert "roam_refs:\n  - https://example.com\n  - https://other.example" in markdown

    def test_colon_wrapped_tags_are_still_split(self, tmp_path):
        converter = OrgRoamConverter(str(tmp_path), str(tmp_path), properties=["filetags"])

        markdown = converter.convert_org_to_markdown("#+filetags: :one:two:\n\nBody.")

        assert "filetags:\n  - one\n  - two" in markdown

    def test_modified_follows_created(self, converter):
        markdown = converter.convert_org_to_markdown(
            "#+title: My Note", "2020-06-13T17:05:32", "2024-04-01T18:42:09"
        )

        assert markdown.startswith(
            "---\ntitle: My Note\ncreated: 2020-06-13T17:05:32\nmodified: 2024-04-01T18:42:09\n---"
        )

    def test_no_modified_key_when_there_is_no_timestamp(self, converter):
        markdown = converter.convert_org_to_markdown("#+title: My Note", "2020-06-13T17:05:32")

        assert "modified:" not in markdown

    def test_created_timestamp_is_placed_below_the_title(self, converter):
        markdown = converter.convert_org_to_markdown("#+title: My Note", "2020-06-13T17:05:32")

        assert markdown.startswith("---\ntitle: My Note\ncreated: 2020-06-13T17:05:32\n---")


class TestRemovedContent:
    def test_properties_drawer_is_dropped(self, converter):
        org = ":PROPERTIES:\n:ID:       abc-123\n:END:\nBody."

        assert converter.convert_org_to_markdown(org) == "Body."

    def test_unrecognised_directives_are_dropped(self, converter):
        org = "#+startup: overview\n#+options: toc:nil\nBody."

        assert converter.convert_org_to_markdown(org) == "Body."

    def test_toc_heading_is_dropped(self, converter):
        org = "* Table of Contents :TOC_2:noexport:\n\n* Intro\nBody."

        assert "Table of Contents" not in converter.convert_org_to_markdown(org)

    def test_toc_entries_are_dropped(self, converter):
        org = (
            "* Table of Contents :TOC_2:noexport:\n"
            "- [[#intro][Intro]]\n"
            "- [[#usage][Usage]]\n"
            "\n"
            "* Intro\n"
            "Body."
        )

        assert converter.convert_org_to_markdown(org) == "# Intro\nBody."

    def test_a_toc_section_ends_at_the_next_top_level_heading(self, converter):
        org = (
            "* Table of Contents :TOC_2:noexport:\n"
            "- [[#intro][Intro]]\n"
            "\n"
            "* Intro\n"
            "Body.\n"
            "** Detail\n"
            "More."
        )

        assert converter.convert_org_to_markdown(org) == "# Intro\nBody.\n## Detail\nMore."

    def test_content_before_a_toc_survives(self, converter):
        org = "* Intro\nBody.\n* Contents :TOC_2:noexport:\n- [[#intro][Intro]]"

        assert converter.convert_org_to_markdown(org) == "# Intro\nBody."


class TestReadingMetadataFromDisk:
    def test_id_and_title_are_read_from_the_file(self, tmp_path):
        org_file = tmp_path / "note.org"
        org_file.write_text(
            ":PROPERTIES:\n:ID:       abc-123\n:END:\n#+title: My Note\n\nBody.\n",
            encoding="utf-8",
        )

        assert extract_id_and_title(org_file) == ("abc-123", "My Note")

    def test_an_uppercase_title_is_read_from_the_file(self, tmp_path):
        org_file = tmp_path / "note.org"
        org_file.write_text(
            ":PROPERTIES:\n:ID:       abc-123\n:END:\n#+TITLE: My Note\n\nBody.\n",
            encoding="utf-8",
        )

        assert extract_id_and_title(org_file) == ("abc-123", "My Note")

    def test_a_file_without_metadata_yields_nothing(self, tmp_path):
        org_file = tmp_path / "note.org"
        org_file.write_text("Just body text.\n", encoding="utf-8")

        assert extract_id_and_title(org_file) == (None, None)

    def test_created_timestamp_is_read_from_the_filename(self, converter, tmp_path):
        org_file = tmp_path / "20200613170532-my_note.org"

        assert converter.extract_created_timestamp(org_file, "") == "2020-06-13T17:05:32"

    def test_an_untimestamped_filename_yields_no_timestamp(self, converter, tmp_path):
        org_file = tmp_path / "my_note.org"

        assert converter.extract_created_timestamp(org_file, "") is None

    def test_a_configured_property_takes_precedence_over_the_filename(self, tmp_path):
        converter = OrgRoamConverter(str(tmp_path), str(tmp_path), created_property="date_created")
        org_file = tmp_path / "20200613170532-my_note.org"

        created = converter.extract_created_timestamp(org_file, "#+date_created: 2021-01-01\n")

        assert created == "2021-01-01"

    def test_the_filename_is_the_fallback_when_the_property_is_absent(self, tmp_path):
        converter = OrgRoamConverter(str(tmp_path), str(tmp_path), created_property="date_created")
        org_file = tmp_path / "20200613170532-my_note.org"

        assert converter.extract_created_timestamp(org_file, "Body.\n") == "2020-06-13T17:05:32"
