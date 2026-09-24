from pathlib import Path

from json_schema_mapper.file_lister import list_files

FIXTURES_DIR = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_folder"
)


def test_list_files_returns_all_file_names():
    result = list_files(FIXTURES_DIR)

    assert len(result) == 12
    assert "notes.txt" in result
    assert ".hidden_config" in result


def test_list_files_returns_sorted_names():
    result = list_files(FIXTURES_DIR)

    assert result == sorted(result)


def test_list_files_excludes_directories():
    result = list_files(FIXTURES_DIR.parent)

    assert "sample_folder" not in result
