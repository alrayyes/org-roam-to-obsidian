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
    def test_top_level_heading_becomes_h1(self, converter):
        assert converter.convert_org_to_markdown("* Introduction") == "# Introduction"

    def test_nesting_depth_is_preserved(self, converter):
        org = "* One\n** Two\n*** Three"

        assert converter.convert_org_to_markdown(org) == "# One\n## Two\n### Three"


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

    def test_internal_anchor_link_becomes_an_inline_link(self, converter):
        markdown = converter.convert_org_to_markdown("See [[#intro][Intro]].")

        assert markdown == "See [Intro](#intro)."


class TestFrontmatter:
    def test_title_becomes_frontmatter_and_an_h1(self, converter):
        markdown = converter.convert_org_to_markdown("#+title: My Note\n\nBody.")

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

    @pytest.mark.xfail(
        strict=True,
        reason="only headings are skipped inside a TOC section, "
        "https://github.com/alrayyes/org-roam-to-obsidian/issues/18",
    )
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


class TestReadingMetadataFromDisk:
    def test_id_and_title_are_read_from_the_file(self, tmp_path):
        org_file = tmp_path / "note.org"
        org_file.write_text(
            ":PROPERTIES:\n:ID:       abc-123\n:END:\n#+title: My Note\n\nBody.\n",
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
