from pathlib import Path

import pytest

from json_schema_mapper.mapper import map_file

FIXTURES_DIR = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_folder"
)


@pytest.mark.parametrize(
    "filename",
    [
        "20260115_meeting-notes.md",
        "invoice_2026-03.pdf",
        "IMG_20260210_143022.jpg",
        "report_final_v2.docx",
        "budget planning.xlsx",
        "notes.txt",
        ".hidden_config",
        "archive.tar.gz",
        "2026-04-01-daily-log.md",
        "photo (1).png",
        "draft_v1.md",
        "draft_v10.md",
    ],
)
def test_map_file_validates_against_schema(filename):
    result = map_file(FIXTURES_DIR / filename)

    assert result["file_name"] == filename


def test_map_file_fields_for_versioned_file():
    result = map_file(FIXTURES_DIR / "draft_v1.md")

    assert result["extension"] == ".md"
    assert result["is_multi_extension"] is False
    assert result["category"] == "document"
    assert result["is_hidden"] is False
    assert result["has_version_suffix"] is True
    assert result["duplicate_index"] is None
    assert result["separator_style"] == "underscore"
    assert result["normalized_title"] == "draft"


def test_map_file_fields_for_multi_extension_file():
    result = map_file(FIXTURES_DIR / "archive.tar.gz")

    assert result["extension"] == ".gz"
    assert result["is_multi_extension"] is True
    assert result["category"] == "archive"
