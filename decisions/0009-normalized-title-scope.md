# 0009. normalized_title のスコープを既存ルールの再利用に限定する

- Status: Accepted
- Date: 2026-09-26

## Context
normalized_title（#46）の実装にあたり、`IMG_20260210_143022.jpg` のような時刻（`HHMMSS`）を含むファイル名や、`invoice_2026-03.pdf` のような年月のみの日付表記について、これらも「意味のないタイトル部分」として取り除くべきかを検討した。

いずれも `extract_date` / `has_version_suffix` / `extract_duplicate_index` のどの既存ルールにも対応しない、未検出のパターンである。

## Decision
normalized_title は、`extract_date` / `has_version_suffix` / `extract_duplicate_index` が実際に検出した部分のみを取り除く。時刻や年月のみの日付を取り除くための専用ロジックは、この Issue の範囲では追加しない。

理由は、これらを取り除くには `normalized_title` だけのための特別な検出ロジックが必要になり、「他のルールが正式に検出したものだけを取り除く」という現在の一貫した設計方針から外れるため。時刻を扱いたい場合は、`extracted_time` のような独立した schema.json の項目として正式に設計すべきという結論に至った。

## Consequences
- `IMG_20260210_143022.jpg` の normalized_title は `IMG_143022` となり、時刻部分が残る
- `invoice_2026-03.pdf` の normalized_title は `invoice_2026-03` のままで、年月部分が残る
- 将来、時刻や年月のみの日付を本当に扱いたくなった場合は、対応する schema.json の項目（例: `extracted_time`）を新設した上で、normalized_title の削除ロジックにもそのルールを追加する
