# 0004. ファイル情報の保持に dataclasses を採用し、pydantic は見送る

- Status: Accepted
- Date: 2026-09-24

## Context
ファイルリスト取得（#17）を拡張し、ファイル名に加えてファイルサイズ・最終更新日時も構造化データに含めることになった。複数の値をまとめて返すデータ構造として、標準ライブラリの `dataclasses` と、サードパーティの `pydantic` のどちらを使うか検討した。

## Decision
現時点では標準ライブラリの `dataclasses.dataclass` を採用し、`FileInfo(name, size, mtime)` のような単純な値の保持に使う。`pydantic` は導入せず、実際に JSON テンプレートへの出力・スキーマ検証を行う段階で採用を再検討する。

## Consequences
- 現時点で新たな依存を追加せずに実装できる
- バリデーションや JSON 変換といった `pydantic` の機能は今は使えないが、単純な値の保持には不要
- 将来 `pydantic` の導入を検討する際は、このADRを振り返ることで判断基準を再確認できる
