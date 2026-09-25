"""ファイル名からルールベースで各項目を抽出するモジュール。"""

import re
from datetime import datetime
from pathlib import Path

_DATE_PATTERNS = [
    r"(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)",
    r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)",
]

_DOCUMENT_EXTENSIONS = {".md", ".txt", ".pdf", ".docx", ".xlsx"}
_IMAGE_EXTENSIONS = {".jpg", ".png"}
_ARCHIVE_EXTENSIONS = {".gz"}

_WORD_SEPARATOR_PATTERN = r"[_\-\s]+"
_VERSION_SUFFIX_PATTERN = r"_v\d+\b"
_DUPLICATE_INDEX_PATTERN = r"\((\d+)\)"
_SEPARATOR_RUN_PATTERN = r"([_\-\s])[_\-\s]*"


def _find_date_match(filename: str) -> re.Match[str] | None:
    """ファイル名から実在する日付にマッチする箇所を探す。

    `extract_date` と `normalize_title` の両方から利用する内部ヘルパー。
    """
    for pattern in _DATE_PATTERNS:
        for match in re.finditer(pattern, filename):
            year, month, day = match.groups()
            try:
                datetime(int(year), int(month), int(day))
            except ValueError:
                continue
            return match
    return None


def extract_date(filename: str) -> str | None:
    """ファイル名に埋め込まれた日付を抽出する。

    `YYYYMMDD` 形式・`YYYY-MM-DD` 形式のいずれかで埋め込まれた日付を検出する。
    実在しない日付（不正な月日）や、年月のみなど日が確定できない場合は
    検出しない。

    Args:
        filename: 判定対象のファイル名。

    Returns:
        検出した日付（`YYYY-MM-DD` 形式の文字列）。見つからない場合は None。
    """
    match = _find_date_match(filename)
    if match is None:
        return None
    year, month, day = match.groups()
    return datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")


def categorize(filename: str) -> str:
    """拡張子からファイルの種別を分類する。

    複数の拡張子を持つファイル（例: `archive.tar.gz`）は、`Path.suffix` で
    取れる最後の拡張子（`.gz`）で判定する。

    Unix の慣習に従い、先頭のドット1つは隠しファイルの印であり拡張子の
    区切りとはみなさない（`Path.suffix` の挙動）。例えば `.hidden_config`
    はドットが1つしかないため拡張子なし（`category="other"`）になる。一方
    `.config.json` のように2つ目のドットがあれば、それ以降（`.json`）は
    通常どおり拡張子として扱われる。

    Args:
        filename: 判定対象のファイル名。

    Returns:
        `"document"` / `"image"` / `"archive"` / `"other"` のいずれか。
    """
    extension = Path(filename).suffix.lower()
    if extension in _DOCUMENT_EXTENSIONS:
        return "document"
    if extension in _IMAGE_EXTENSIONS:
        return "image"
    if extension in _ARCHIVE_EXTENSIONS:
        return "archive"
    return "other"


def is_hidden(filename: str) -> bool:
    """ファイル名が `.` で始まる隠しファイルかどうかを判定する。

    Args:
        filename: 判定対象のファイル名。

    Returns:
        `.` で始まる場合は True。
    """
    return filename.startswith(".")


def count_words(filename: str) -> int:
    """ファイル名をアンダースコア・ハイフン・スペースで分割した単語数を数える。

    Args:
        filename: 判定対象のファイル名。

    Returns:
        区切り文字で分割した単語数。
    """
    words = [w for w in re.split(_WORD_SEPARATOR_PATTERN, filename) if w]
    return len(words)


def has_version_suffix(filename: str) -> bool:
    """ファイル名に `_v1` `_v10` のようなバージョン表記が含まれるかを判定する。

    小文字の `v` に続く数字（例: `_v1`, `_v10`）のみを検出する。

    Args:
        filename: 判定対象のファイル名。

    Returns:
        バージョン表記が含まれる場合は True。
    """
    return re.search(_VERSION_SUFFIX_PATTERN, filename) is not None


def extract_duplicate_index(filename: str) -> int | None:
    """ファイル名に含まれる `(数字)` 形式の連番を抽出する。

    OS がファイルを複製・保存する際に自動的に付与する連番
    （例: `photo (1).png`）を検出する。`_v1` のような意図的な
    バージョン表記（`has_version_suffix`）とは異なる概念として扱う。

    Args:
        filename: 判定対象のファイル名。

    Returns:
        検出した連番。見つからない場合は None。
    """
    match = re.search(_DUPLICATE_INDEX_PATTERN, filename)
    if match is None:
        return None
    return int(match.group(1))


def determine_separator_style(filename: str) -> str:
    """ファイル名で使われている区切り文字の種類を判定する。

    Args:
        filename: 判定対象のファイル名。

    Returns:
        `"underscore"` / `"hyphen"` / `"space"` / `"mixed"` /
        `"none"` のいずれか。複数種類の区切り文字が混在する場合は
        `"mixed"`、いずれも含まない場合は `"none"`。
    """
    has_underscore = "_" in filename
    has_hyphen = "-" in filename
    has_space = " " in filename
    kinds_used = sum([has_underscore, has_hyphen, has_space])

    if kinds_used == 0:
        return "none"
    if kinds_used > 1:
        return "mixed"
    if has_underscore:
        return "underscore"
    if has_hyphen:
        return "hyphen"
    return "space"


def normalize_title(filename: str) -> str:
    """拡張子・日付・バージョン表記・連番を取り除いた実質的なタイトルを
    抜き出す。

    `extract_date` / `has_version_suffix` / `extract_duplicate_index` が
    実際に検出した箇所のみを取り除く。時刻（`HHMMSS`）や年月のみの日付
    など、対応する検出ロジックが存在しないものは取り除かない
    （例: `IMG_20260210_143022.jpg` → `IMG_143022`）。大文字小文字・
    残りの区切り文字の種類は変更しない。

    Args:
        filename: 判定対象のファイル名。

    Returns:
        実質的なタイトル部分。
    """
    title = filename
    while Path(title).suffix:
        title = Path(title).stem

    date_match = _find_date_match(title)
    if date_match is not None:
        title = title[: date_match.start()] + title[date_match.end() :]

    version_match = re.search(_VERSION_SUFFIX_PATTERN, title)
    if version_match is not None:
        title = title[: version_match.start()] + title[version_match.end() :]

    duplicate_match = re.search(_DUPLICATE_INDEX_PATTERN, title)
    if duplicate_match is not None:
        start, end = duplicate_match.start(), duplicate_match.end()
        title = title[:start] + title[end:]

    title = re.sub(_SEPARATOR_RUN_PATTERN, r"\1", title)
    return title.strip("_- ")
