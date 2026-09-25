# json-schema-mapper

LLM を使わず、ルールベースでユーザー入力を JSON テンプレートに構造化するマッパー。

## デモ

`fixtures/sample_folder/draft_v1.md` を `map_file()` に渡すと、以下のように構造化される。

```pycon
>>> from json_schema_mapper.mapper import map_file
>>> map_file("fixtures/sample_folder/draft_v1.md")
{
    "file_name": "draft_v1.md",
    "extension": ".md",
    "is_multi_extension": False,
    "size_bytes": 0,
    "modified_at": "2026-09-25T21:30:00.123456",
    "extracted_date": None,
    "category": "document",
    "is_hidden": False,
    "word_count": 2,
    "has_version_suffix": True,
    "duplicate_index": None,
    "separator_style": "underscore",
    "normalized_title": "draft",
}
```

フォルダ全体の一覧化・CLI などはまだ未実装（下記「今後の展望」参照）。

## 背景・課題

「自由入力をどう構造化データに落とし込むか」を学ぶことを目的としたプロジェクト。以下の3段階のステップを想定しており、本プロジェクトはその入り口（ステップ1）にあたる。

1. **本プロジェクト**: LLM を使わず、ルールベースで入力を JSON に構造化する
2. LLM の Structured Output を使って構造化する
3. 自由入力を LLM を使って構造化する

まずルールベースでの実装を通して、構造化のための入力の扱い方・マッピングの設計を理解する。

## 主な機能

- フォルダ内の1ファイルを受け取り、[`schema.json`](./schema.json) に定義した13項目の構造化データに変換する（`map_file()`）
- ファイル名から日付・カテゴリ・バージョン表記・連番・区切り文字の種類・実質的なタイトルなどをルールベースで抽出する（LLM は使用しない）
- 組み立てた結果を `schema.json` に対して検証する
- 入力データソース（フォルダのファイルリスト）や各項目の抽出ルールの選定理由は [`decisions/`](./decisions) に ADR として記録している

## アーキテクチャ・技術スタック

- 言語: Python 3.12
- スキーマ定義・検証: [jsonschema](https://pypi.org/project/jsonschema/)（[`schema.json`](./schema.json), JSON Schema draft 2020-12）
- Lint: ruff（[`ruff.toml`](./ruff.toml) で PEP-8 準拠のルールを明示的に有効化）
- テスト: pytest
- CI: GitHub Actions

モジュール構成:

- [`json_schema_mapper/file_lister.py`](./json_schema_mapper/file_lister.py): フォルダ内のファイル一覧・ファイル情報（`FileInfo`）の取得
- [`json_schema_mapper/rules.py`](./json_schema_mapper/rules.py): ファイル名からのルールベースの各項目抽出
- [`json_schema_mapper/mapper.py`](./json_schema_mapper/mapper.py): 上記を組み合わせて `schema.json` に準拠した辞書を組み立て・検証する（`map_file()`）

## 技術選定理由

主な技術選定は [`decisions/`](./decisions) に ADR として記録している。

- [0001](./decisions/0001-use-python.md): 開発言語に Python を採用
- [0003](./decisions/0003-use-folder-file-list.md): データソースにフォルダ内ファイルリストを採用
- [0004](./decisions/0004-use-dataclasses-defer-pydantic.md): ファイル情報の保持に dataclasses を採用
- [0005](./decisions/0005-use-jsonschema.md): 出力 JSON テンプレートの定義・検証に jsonschema を採用
- [0006](./decisions/0006-schema-field-selection.md): schema.json の項目構成の決定理由

## セットアップ手順

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install ruff pytest jsonschema
```

## 使い方

```python
from json_schema_mapper.mapper import map_file

result = map_file("fixtures/sample_folder/draft_v1.md")
```

## テストの実行方法

```bash
pip install ruff pytest jsonschema
ruff check .
pytest
```

## 今後の展望・既知の制約

- 本プロジェクトは学習ロードマップのステップ1であり、ルールベースゆえに対応できる入力パターンには限界がある
- フォルダ全体をまとめて処理する関数（一覧の一括構造化）や、実際にフォルダを指定して実行する CLI は未実装
- 次のステップとして、LLM の Structured Output を使った構造化への発展を予定している
