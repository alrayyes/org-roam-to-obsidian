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

    assert "2/2 files converted successfully" in output


def test_timestamp_prefixes_are_stripped_from_filenames(vault):
    source, target = vault

    run_convert("-i", str(source), "-o", str(target))

    assert sorted(p.name for p in target.iterdir()) == ["first_note.md", "second_note.md"]


def test_the_output_directory_is_created_if_missing(vault):
    source, target = vault
    assert not target.exists()

    run_convert("-i", str(source), "-o", str(target))

    assert target.is_dir()


def test_a_note_carries_its_title_and_created_date(vault):
    source, target = vault

    run_convert("-i", str(source), "-o", str(target))

    assert (
        (target / "second_note.md")
        .read_text(encoding="utf-8")
        .startswith("---\ntitle: Second Note\ncreated: 2021-01-01T12:00:00\n---\n\n# Second Note\n")
    )


def test_created_dates_are_omitted_when_disabled(vault):
    source, target = vault

    run_convert("-i", str(source), "-o", str(target), "--no-created")

    assert "created:" not in (target / "second_note.md").read_text(encoding="utf-8")


def test_only_requested_properties_reach_the_frontmatter(vault):
    source, target = vault

    run_convert("-i", str(source), "-o", str(target), "-p", "filetags")

    assert "filetags:\n  - python\n  - notes" in (target / "first_note.md").read_text(
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

    assert "created: 2019-05-04T09:00:00" in (target / "dated.md").read_text(encoding="utf-8")


@pytest.mark.xfail(
    strict=True,
    reason="the bare-link substitution rewrites the wikilink it just produced, "
    "https://github.com/alrayyes/org-roam-to-obsidian/issues/15",
)
def test_a_link_between_notes_becomes_a_wikilink(vault):
    source, target = vault

    run_convert("-i", str(source), "-o", str(target))

    assert "[[Second Note]]" in (target / "first_note.md").read_text(encoding="utf-8")


def test_an_empty_source_directory_is_not_an_error(tmp_path):
    source = tmp_path / "empty"
    source.mkdir()

    output = run_convert("-i", str(source), "-o", str(tmp_path / "out"))

    assert "0/0 files converted successfully" in output
