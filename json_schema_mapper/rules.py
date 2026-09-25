"""ファイル名からルールベースで各項目を抽出するモジュール。"""

import re
from datetime import datetime

_DATE_PATTERNS = [
    r"(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)",
    r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)",
]


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
    for pattern in _DATE_PATTERNS:
        for match in re.finditer(pattern, filename):
            year, month, day = match.groups()
            try:
                date = datetime(int(year), int(month), int(day))
            except ValueError:
                continue
            return date.strftime("%Y-%m-%d")
    return None
