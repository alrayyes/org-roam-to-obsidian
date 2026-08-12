"""End-to-end tests that drive ``convert.py`` the way a user does.

Each one runs the script as a subprocess over a throwaway org-roam directory
and reads the Markdown that lands on disk, so argument parsing, file naming and
the two-pass conversion are all covered as a single journey.
"""

import subprocess
import sys
from pathlib import Path

import pytest

CONVERT = Path(__file__).resolve().parent.parent / "convert.py"


def run_convert(*args):
    result = subprocess.run(
        [sys.executable, str(CONVERT), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


@pytest.fixture
def vault(tmp_path):
    """An org-roam directory holding two notes, one linking to the other."""
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200613170532-first_note.org").write_text(
        ":PROPERTIES:\n"
        ":ID:       11111111-1111-1111-1111-111111111111\n"
        ":END:\n"
        "#+title: First Note\n"
        "#+filetags: :python:notes:\n"
        "\n"
        "* Overview\n"
        "Links to [[id:22222222-2222-2222-2222-222222222222][Second Note]].\n",
        encoding="utf-8",
    )
    (source / "20210101120000-second_note.org").write_text(
        ":PROPERTIES:\n"
        ":ID:       22222222-2222-2222-2222-222222222222\n"
        ":END:\n"
        "#+title: Second Note\n"
        "\n"
        "Body.\n",
        encoding="utf-8",
    )
    return source, tmp_path / "out"


def test_every_note_is_converted(vault):
    source, target = vault

    output = run_convert("-i", str(source), "-o", str(target))

    assert "2 files written from 2 notes" in output


def test_timestamp_prefixes_are_stripped_from_filenames(vault):
    source, target = vault

    run_convert("-i", str(source), "-o", str(target))

    assert sorted(p.name for p in target.iterdir()) == ["First Note.md", "Second Note.md"]


def test_the_output_directory_is_created_if_missing(vault):
    source, target = vault
    assert not target.exists()

    run_convert("-i", str(source), "-o", str(target))

    assert target.is_dir()


def test_a_note_carries_its_title_and_created_date(vault):
    source, target = vault

    run_convert("-i", str(source), "-o", str(target))

    assert (
        (target / "Second Note.md")
        .read_text(encoding="utf-8")
        .startswith("---\ntitle: Second Note\ncreated: 2021-01-01T12:00:00\n---\n\n# Second Note\n")
    )


def test_created_dates_are_omitted_when_disabled(vault):
    source, target = vault

    run_convert("-i", str(source), "-o", str(target), "--no-created")

    assert "created:" not in (target / "Second Note.md").read_text(encoding="utf-8")


def test_only_requested_properties_reach_the_frontmatter(vault):
    source, target = vault

    run_convert("-i", str(source), "-o", str(target), "-p", "filetags")

    assert "filetags:\n  - python\n  - notes" in (target / "First Note.md").read_text(
        encoding="utf-8"
    )


def test_a_custom_property_can_supply_the_created_date(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200613170532-dated.org").write_text(
        "#+title: Dated\n#+date_created: 2019-05-04T09:00:00\n\nBody.\n",
        encoding="utf-8",
    )
    target = tmp_path / "out"

    run_convert("-i", str(source), "-o", str(target), "--created-property", "date_created")

    assert "created: 2019-05-04T09:00:00" in (target / "Dated.md").read_text(encoding="utf-8")


def test_a_link_between_notes_becomes_a_wikilink(vault):
    source, target = vault

    run_convert("-i", str(source), "-o", str(target))

    assert "[[Second Note]]" in (target / "First Note.md").read_text(encoding="utf-8")


def test_a_collision_warns_and_names_both_notes(tmp_path):
    """Two notes whose filenames collapse to one must not vanish quietly."""
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200101000000-a.org").write_text("#+title: Arrays\n", encoding="utf-8")
    (source / "20200202000000-b.org").write_text("#+title: Arrays\n", encoding="utf-8")

    output = run_convert("-i", str(source), "-o", str(tmp_path / "out"))

    assert "Warning" in output
    assert "20200101000000-a.org" in output
    assert "20200202000000-b.org" in output


def test_the_summary_counts_files_written_not_read(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200101000000-a.org").write_text("#+title: Same\n", encoding="utf-8")
    (source / "20200202000000-b.org").write_text("#+title: Same\n", encoding="utf-8")

    output = run_convert("-i", str(source), "-o", str(tmp_path / "out"))

    assert "2 files written from 2 notes" in output
    assert "1 name collision" in output


def test_a_title_clash_keeps_both_notes(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200101000000-a.org").write_text("#+title: Same\n", encoding="utf-8")
    (source / "20200202000000-b.org").write_text("#+title: Same\n", encoding="utf-8")
    target = tmp_path / "out"

    run_convert("-i", str(source), "-o", str(target))

    # Neither note is lost: the second keeps the name its org file had. Files
    # are processed in sorted order, so a.org claims the title and b.org falls
    # back, the same way on every run.
    assert sorted(f.name for f in target.glob("*.md")) == ["Same.md", "b.md"]


def test_a_clean_run_says_so_without_warnings(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200101000000-one.org").write_text("#+title: One\n", encoding="utf-8")
    (source / "20200202000000-two.org").write_text("#+title: Two\n", encoding="utf-8")

    output = run_convert("-i", str(source), "-o", str(tmp_path / "out"))

    assert "Warning" not in output
    assert "2 files written" in output


def _note(source, stamp, title, body="Body.\n"):
    (source / f"{stamp}-slug.org").write_text(f"#+title: {title}\n\n{body}", encoding="utf-8")


def test_a_note_is_named_after_its_title(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    _note(source, "20200101000000", "JavaScript Arrays")
    target = tmp_path / "out"

    run_convert("-i", str(source), "-o", str(target))

    assert (target / "JavaScript Arrays.md").is_file()


def test_a_title_the_filesystem_rejects_is_made_safe(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    _note(source, "20200101000000", "Binding / Variables in JavaScript")
    target = tmp_path / "out"

    run_convert("-i", str(source), "-o", str(target))

    assert (target / "Binding - Variables in JavaScript.md").is_file()


def test_a_sanitised_name_keeps_the_title_as_an_alias(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    _note(source, "20200101000000", "Box<T>")
    target = tmp_path / "out"

    run_convert("-i", str(source), "-o", str(target))

    written = (target / "Box T.md").read_text(encoding="utf-8")
    assert "aliases:\n  - Box<T>" in written


def test_an_untouched_title_gets_no_alias(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    _note(source, "20200101000000", "Plain Title")
    target = tmp_path / "out"

    run_convert("-i", str(source), "-o", str(target))

    assert "aliases" not in (target / "Plain Title.md").read_text(encoding="utf-8")


def test_a_note_without_a_title_falls_back_to_its_filename(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200101000000-no_title.org").write_text("Body only.\n", encoding="utf-8")
    target = tmp_path / "out"

    run_convert("-i", str(source), "-o", str(target))

    assert (target / "no_title.md").is_file()


def test_two_notes_sharing_a_title_both_survive(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200101000000-a.org").write_text("#+title: TypeScript\n", encoding="utf-8")
    (source / "20200202000000-b.org").write_text("#+title: TypeScript\n", encoding="utf-8")
    target = tmp_path / "out"

    output = run_convert("-i", str(source), "-o", str(target))

    assert len(list(target.glob("*.md"))) == 2
    assert "Warning" in output


def test_links_resolve_to_the_files_that_are_written(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200101000000-a.org").write_text(
        ":PROPERTIES:\n:ID:       aaa\n:END:\n#+title: Target Note\n", encoding="utf-8"
    )
    (source / "20200202000000-b.org").write_text(
        "#+title: Source Note\n\nSee [[id:aaa][x]].\n", encoding="utf-8"
    )
    target = tmp_path / "out"

    run_convert("-i", str(source), "-o", str(target))

    assert "[[Target Note]]" in (target / "Source Note.md").read_text(encoding="utf-8")
    assert (target / "Target Note.md").is_file()


def test_a_wikilink_pointing_nowhere_is_reported(tmp_path):
    """The point of the report: what to go and fix once the run is done."""
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200101000000-a.org").write_text(
        "#+title: Source Note\n\nSee [[id:missing-id][Gravity Falls]].\n", encoding="utf-8"
    )

    output = run_convert("-i", str(source), "-o", str(tmp_path / "out"))

    assert "Source Note.md" in output
    assert "[[Gravity Falls]]" in output


def test_a_resolvable_link_is_not_reported(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200101000000-a.org").write_text(
        ":PROPERTIES:\n:ID:       aaa\n:END:\n#+title: Target\n", encoding="utf-8"
    )
    (source / "20200202000000-b.org").write_text(
        "#+title: Source\n\nSee [[id:aaa][x]].\n", encoding="utf-8"
    )

    output = run_convert("-i", str(source), "-o", str(tmp_path / "out"))

    assert "point nowhere" not in output


def test_a_link_resolved_by_an_alias_is_not_reported(tmp_path):
    """The file is named Box T.md but the link says [[Box<T>]]; the alias covers it."""
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200101000000-a.org").write_text(
        ":PROPERTIES:\n:ID:       aaa\n:END:\n#+title: Box<T>\n", encoding="utf-8"
    )
    (source / "20200202000000-b.org").write_text(
        "#+title: Source\n\nSee [[id:aaa][x]].\n", encoding="utf-8"
    )

    output = run_convert("-i", str(source), "-o", str(tmp_path / "out"))

    assert "point nowhere" not in output


def test_a_link_inside_a_code_block_is_not_reported(tmp_path):
    """[[x]] in a JavaScript array is not a link and must not be flagged."""
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200101000000-a.org").write_text(
        "#+title: Code\n\n#+begin_src js\nflatMap((x) => [[x]])\n#+end_src\n", encoding="utf-8"
    )

    output = run_convert("-i", str(source), "-o", str(tmp_path / "out"))

    assert "point nowhere" not in output


def test_the_report_counts_every_broken_link(tmp_path):
    source = tmp_path / "slip-box"
    source.mkdir()
    (source / "20200101000000-a.org").write_text(
        "#+title: A\n\n[[id:gone][One]] and [[id:alsogone][Two]].\n", encoding="utf-8"
    )

    output = run_convert("-i", str(source), "-o", str(tmp_path / "out"))

    assert "2 links point nowhere" in output


def test_an_empty_source_directory_is_not_an_error(tmp_path):
    source = tmp_path / "empty"
    source.mkdir()

    output = run_convert("-i", str(source), "-o", str(tmp_path / "out"))

    assert "0 files written from 0 notes" in output
