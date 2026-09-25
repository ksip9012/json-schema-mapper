import pytest

from json_schema_mapper.rules import extract_date


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
