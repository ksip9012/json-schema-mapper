"""指定フォルダ内のファイル一覧を取得するモジュール。"""

from pathlib import Path


def list_files(folder: str | Path) -> list[str]:
    """指定フォルダ直下にあるファイルの名前一覧を取得する。

    サブディレクトリは再帰的に探索せず、ディレクトリ自体は結果に含めない。
    隠しファイル（`.` 始まり）は除外せず結果に含める。

    Args:
        folder: 走査対象のフォルダパス。

    Returns:
        ファイル名（拡張子を含む）を昇順にソートしたリスト。
    """
    folder_path = Path(folder)
    return sorted(p.name for p in folder_path.iterdir() if p.is_file())
