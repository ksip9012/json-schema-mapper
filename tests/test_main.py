import json
from pathlib import Path

import pytest

from json_schema_mapper.__main__ import main

FIXTURES_DIR = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_folder"
)


def test_main_prints_json_array_for_folder(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["json_schema_mapper", str(FIXTURES_DIR)])

    main()

    output = json.loads(capsys.readouterr().out)
    assert len(output) == 12
    assert {item["file_name"] for item in output} == {
        p.name for p in FIXTURES_DIR.iterdir()
    }


def test_main_exits_with_error_for_missing_folder(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv", ["json_schema_mapper", "no-such-folder"]
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    assert "no-such-folder" in capsys.readouterr().err
