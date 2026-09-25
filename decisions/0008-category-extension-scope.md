# 0008. category の分類対象拡張子の範囲を決定する

- Status: Accepted
- Date: 2026-09-26

## Context
category の分類ロジック（#31）を実装する際、拡張子の判定リストを次のどちらにするか検討した。

- `fixtures/sample_folder` に実際にある拡張子（`.md`, `.txt`, `.pdf`, `.docx`, `.xlsx`, `.jpg`, `.png`, `.gz`）のみに絞る
- `.doc`, `.xls`, `.ppt`, `.csv`, `.gif`, `.bmp`, `.svg`, `.webp`, `.zip`, `.tar`, `.rar`, `.7z`, `.bz2` など、一般的にありそうな拡張子も広く含める

## Decision
`fixtures/sample_folder` に実際にある拡張子のみに絞る。

これまでの方針（pydantic を必要になるまで見送るなど、ADR 0004）と同様に、まだテストで検証されていない拡張子を先取りして追加しない。実際に必要な拡張子が出てきた時点で、fixtures にサンプルを追加した上でリストを拡張する。

## Consequences
- 現時点で fixtures にない拡張子のファイルは category が `other` になる
- 拡張子リストを広げる際は、対応する fixtures のサンプルファイルとテストケースも合わせて追加する
