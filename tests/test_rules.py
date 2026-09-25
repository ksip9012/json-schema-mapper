import pytest

from json_schema_mapper.rules import categorize, extract_date, is_hidden


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("20260115_meeting-notes.md", "2026-01-15"),
        ("invoice_2026-03.pdf", None),
        ("IMG_20260210_143022.jpg", "2026-02-10"),
        ("report_final_v2.docx", None),
        ("budget planning.xlsx", None),
        ("notes.txt", None),
        (".hidden_config", None),
        ("archive.tar.gz", None),
        ("2026-04-01-daily-log.md", "2026-04-01"),
        ("photo (1).png", None),
        ("draft_v1.md", None),
        ("draft_v10.md", None),
    ],
)
def test_extract_date(filename, expected):
    assert extract_date(filename) == expected


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("20260115_meeting-notes.md", "document"),
        ("invoice_2026-03.pdf", "document"),
        ("IMG_20260210_143022.jpg", "image"),
        ("report_final_v2.docx", "document"),
        ("budget planning.xlsx", "document"),
        ("notes.txt", "document"),
        (".hidden_config", "other"),
        ("archive.tar.gz", "archive"),
        ("2026-04-01-daily-log.md", "document"),
        ("photo (1).png", "image"),
        ("draft_v1.md", "document"),
        ("draft_v10.md", "document"),
    ],
)
def test_categorize(filename, expected):
    assert categorize(filename) == expected


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("20260115_meeting-notes.md", False),
        ("invoice_2026-03.pdf", False),
        ("IMG_20260210_143022.jpg", False),
        ("report_final_v2.docx", False),
        ("budget planning.xlsx", False),
        ("notes.txt", False),
        (".hidden_config", True),
        ("archive.tar.gz", False),
        ("2026-04-01-daily-log.md", False),
        ("photo (1).png", False),
        ("draft_v1.md", False),
        ("draft_v10.md", False),
    ],
)
def test_is_hidden(filename, expected):
    assert is_hidden(filename) == expected
