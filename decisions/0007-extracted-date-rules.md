# 0007. extracted_date の抽出ルールを決定する

- Status: Accepted
- Date: 2026-09-26

## Context
schema.json（#25）の `extracted_date` を、ファイル名からルールベースで抽出する実装（#28）にあたり、検出するパターンと、日付として確定できない場合の扱いを検討した。

`fixtures/sample_folder` には `20260115_meeting-notes.md`（`YYYYMMDD`）、`2026-04-01-daily-log.md`（`YYYY-MM-DD`）、`invoice_2026-03.pdf`（年月のみ、日を含まない）など複数のパターンが含まれている。

年月のみのパターンについては、以下の2案を検討した。
- `null` にする: 日が確定できない以上、未検出として扱う
- 日を補完する: 例えば `YYYY-MM-01` として、暦日を1日目とみなす

## Decision
検出パターンは `YYYYMMDD` と `YYYY-MM-DD` の2種類とし、実在しない日付（不正な月日）は無視する。

年月のみなど日が確定できないパターンは `null` とする。日を補完する案は、実際には存在しない情報（架空の日付）を作り出すことになるため採用しない。

## Consequences
- `invoice_2026-03.pdf` のような年月のみのファイルは `extracted_date` が `null` になり、日付による分類・ソートの対象外になる
- 将来、年月のみの情報を別途保持したくなった場合は、`extracted_date` とは別の項目（例: `extracted_year_month`）を追加する形で対応する
