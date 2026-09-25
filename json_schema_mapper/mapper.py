"""FileInfo とルールベースの抽出結果を組み合わせ、schema.json に準拠した
辞書を構築するモジュール。"""

import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from json_schema_mapper.file_lister import get_file_info, list_files
from json_schema_mapper.rules import (
    categorize,
    count_words,
    determine_separator_style,
    extract_date,
    extract_duplicate_index,
    has_version_suffix,
    is_hidden,
    normalize_title,
)

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.json"
_SCHEMA = json.loads(_SCHEMA_PATH.read_text())


def map_file(path: str | Path) -> dict[str, Any]:
    """1つのファイルを schema.json に準拠した辞書に構造化する。

    FileInfo からの転記項目（file_name, extension, is_multi_extension,
    size_bytes, modified_at）と、ルールベースの抽出項目（rules.py の
    各関数）を組み合わせ、組み立てた結果を schema.json に対して検証する。

    Args:
        path: 対象ファイルのパス。

    Returns:
        schema.json のプロパティに対応するキーを持つ辞書。
    """
    info = get_file_info(path)
    name = info.name

    result: dict[str, Any] = {
        "file_name": name,
        "extension": Path(name).suffix,
        "is_multi_extension": len(Path(name).suffixes) > 1,
        "size_bytes": info.size,
        "modified_at": info.mtime.isoformat(),
        "extracted_date": extract_date(name),
        "category": categorize(name),
        "is_hidden": is_hidden(name),
        "word_count": count_words(name),
        "has_version_suffix": has_version_suffix(name),
        "duplicate_index": extract_duplicate_index(name),
        "separator_style": determine_separator_style(name),
        "normalized_title": normalize_title(name),
    }

    validate(instance=result, schema=_SCHEMA)
    return result


def map_folder(folder: str | Path) -> list[dict[str, Any]]:
    """フォルダ直下にあるファイルを、それぞれ schema.json に準拠した
    辞書に構造化したリストを取得する。

    Args:
        folder: 対象フォルダのパス。

    Returns:
        `map_file` の戻り値をファイル名の昇順に並べたリスト。
    """
    folder_path = Path(folder)
    return [map_file(folder_path / name) for name in list_files(folder_path)]
