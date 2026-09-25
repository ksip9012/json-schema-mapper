# 0006. schema.json の項目構成を決定する

- Status: Accepted
- Date: 2026-09-25

## Context
ADR 0005 で jsonschema による検証方針を決めた後、`schema.json`（#25）にどの項目を含めるかを検討した。

候補として、`FileInfo`（#21）の値をそのまま転記する項目（`file_name`, `size_bytes`, `modified_at` など）と、ファイル名に対してルールベースの解析を必要とする項目（`extracted_date`, `category`, `is_hidden`, `word_count`, `has_version_suffix`, `duplicate_index`, `separator_style`, `normalized_title` など）を挙げた。

## Decision
両方のタイプの項目を `schema.json` に含める。

- 転記のみの項目（`file_name`, `extension`, `is_multi_extension`, `size_bytes`, `modified_at`）は、出力データとして必要な基本情報として残す
- ルールベースの解析が必要な項目（`extracted_date`, `category`, `is_hidden`, `word_count`, `has_version_suffix`, `duplicate_index`, `separator_style`, `normalized_title`）は、`fixtures/sample_folder` の表記揺らぎ（日付書式・区切り文字・バージョン表記・連番表記など）を活かして、正規表現や文字列処理のルール設計を練習する目的で追加する

転記のみの項目は単体では学習効果が薄いが、最終的な構造化データとしての完成度・README での見せ方を考慮して残すことにした。

## Consequences
- 項目数が多くなり（13項目）、実装（#25 以降の各抽出ロジック）も複数の Issue に分割して進める必要がある
- 各項目の抽出ロジックが `fixtures/sample_folder` のデータパターンに依存しているため、fixtures の内容を変更する際はこのスキーマとの整合性を確認する必要がある
