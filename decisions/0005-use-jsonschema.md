# 0005. 出力 JSON テンプレートの定義・検証に jsonschema を採用する

- Status: Accepted
- Date: 2026-09-25

## Context
ADR 0004 で、ファイル情報の保持には `dataclasses` を使い、JSON テンプレートへの出力・スキーマ検証の段階で `pydantic` の採用を再検討することにしていた。その段階に達したため、出力テンプレートの定義・検証方法を決める。

比較した選択肢:
- `pydantic`: モデル定義と型バリデーション・JSON 変換が一体化していて便利
- `jsonschema` パッケージ: JSON Schema (json-schema.org) の仕様に忠実に `schema.json` を定義し、そのスキーマ自体を検証に使う
- バリデーションなし（`dataclasses` のみ）: 追加の依存を増やさない

## Decision
`jsonschema` パッケージを採用し、JSON Schema の仕様に沿った `schema.json` を定義してマッピング結果を検証する。

学習ロードマップのステップ2（LLM の Structured Output）は JSON Schema を LLM に渡して出力形式を制約する仕組みであるため、ここで JSON Schema の書き方・検証の考え方を学んでおくことが次のステップへの直接的な準備になる。プロジェクト名（json-schema-mapper）が示す本題でもある。

## Consequences
- `jsonschema` という新しい依存が増える（`pydantic` よりは軽量・単機能）
- モデル定義と検証が分離するため、`pydantic` に比べるとやや手数が増える
- 次のステップ（LLM Structured Output）で使う JSON Schema の知識・書き方をこの段階で習得できる
