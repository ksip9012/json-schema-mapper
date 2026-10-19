"""Step1 シリーズ（A1 / A2 / B）のベンチマーク結果をまとめ、Markdown の
表を標準出力に出力する。

各リポジトリの `scripts/benchmark.py` が出力した JSON Lines を読み、
1件あたりの処理時間・トークン数・料金と、A1 を正解とした A2 の項目ごとの
一致率を出す（notes/step1-comparison.md 参照）。

使い方:
    python scripts/summarize_benchmark.py \\
        notes/benchmark/a1.jsonl notes/benchmark/a2.jsonl \\
        notes/benchmark/b.jsonl
"""

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

# Gemini 3.8 Flash の Standard の料金（USD / 100万トークン、2026-12-31 まで）。
# 出力には思考トークンを含む。2026-10-19 に
# https://ai.google.dev/gemini-api/docs/pricing で確認した。
_INPUT_USD_PER_M = 0.75
_OUTPUT_USD_PER_M = 3.75

# FileInfo から転記する項目。A1 と A2 で同じコードが算出するので、
# 一致率の比較からは外す。
_FILE_INFO_FIELDS = {
    "file_name",
    "extension",
    "is_multi_extension",
    "size_bytes",
    "modified_at",
}


def _load(paths: list[str]) -> dict[str, list[dict[str, Any]]]:
    """JSON Lines を読み、step ごとの行のリストにする。"""
    rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in paths:
        for line in Path(path).read_text().splitlines():
            row = json.loads(line)
            rows[row["step"]].append(row)
    return rows


def _cost_usd(row: dict[str, Any]) -> float:
    """1行（1件・1回）の料金を USD で返す。"""
    output = row["output_tokens"] + row["thoughts_tokens"]
    return (
        row["prompt_tokens"] * _INPUT_USD_PER_M
        + output * _OUTPUT_USD_PER_M
    ) / 1_000_000


def _percentile(values: list[float], q: int) -> float:
    """values の q パーセンタイルを返す（値が1つなら、その値）。"""
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=100, method="inclusive")[q - 1]


def _summary_table(rows: dict[str, list[dict[str, Any]]]) -> str:
    """step ごとの処理時間・トークン数・料金の表を作る。"""
    lines = [
        "| Step | モデル | 入力 | 回数 | 成功 | LLM 呼び出し/件 "
        "| 処理時間 中央値 | 処理時間 p90 "
        "| 入力トークン/件 | 出力トークン/件 | 思考トークン/件 "
        "| 料金/件 | 料金/1,000件 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- "
        "| --- | --- | --- | --- | --- |",
    ]
    for step, step_rows in sorted(rows.items()):
        n = len(step_rows)
        files = len({r["file"] for r in step_rows})
        runs = len({r["run"] for r in step_rows})
        ok = sum(r["ok"] for r in step_rows)
        latencies = [r["latency_ms"] for r in step_rows]
        cost = statistics.mean(_cost_usd(r) for r in step_rows)

        def mean(key: str) -> float:
            return statistics.mean(r[key] for r in step_rows)

        lines.append(
            f"| {step} | {step_rows[0]['model'] or '-'} | {files}件 "
            f"| {runs} | {ok}/{n} | {mean('llm_calls'):.0f} "
            f"| {_format_ms(statistics.median(latencies))} "
            f"| {_format_ms(_percentile(latencies, 90))} "
            f"| {mean('prompt_tokens'):.0f} | {mean('output_tokens'):.0f} "
            f"| {mean('thoughts_tokens'):.0f} "
            f"| ${cost:.6f} | ${cost * 1000:.3f} |"
        )
    return "\n".join(lines)


def _format_ms(ms: float) -> str:
    """ミリ秒を、桁に合った単位の文字列にする。"""
    if ms < 1:
        return f"{ms * 1000:.0f} µs"
    if ms < 1000:
        return f"{ms:.1f} ms"
    return f"{ms / 1000:.2f} s"


def _accuracy_table(
    expected_rows: list[dict[str, Any]], actual_rows: list[dict[str, Any]]
) -> str:
    """A1 の出力を正解として、A2 の項目ごとの一致率の表を作る。"""
    expected = {r["file"]: r["result"] for r in expected_rows}
    fields = [
        f for f in next(iter(expected.values())) if f not in _FILE_INFO_FIELDS
    ]
    matched: dict[str, int] = defaultdict(int)
    mismatches: dict[str, set[str]] = defaultdict(set)
    compared = [r for r in actual_rows if r["ok"]]
    for row in compared:
        for field in fields:
            if row["result"].get(field) == expected[row["file"]][field]:
                matched[field] += 1
            else:
                mismatches[field].add(row["file"])

    lines = [
        "| 項目 | 一致 | 一致しなかったファイル |",
        "| --- | --- | --- |",
    ]
    for field in fields:
        files = ", ".join(f"`{f}`" for f in sorted(mismatches[field]))
        lines.append(
            f"| `{field}` | {matched[field]}/{len(compared)} "
            f"| {files or '-'} |"
        )
    return "\n".join(lines)


def main() -> None:
    """ベンチマーク結果を読み、Markdown の表を出力する。"""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="+", help="benchmark.py の出力")
    args = parser.parse_args()

    rows = _load(args.paths)
    print("## 1件あたりの処理時間・トークン数・料金\n")
    print(_summary_table(rows))
    if "A1" in rows and "A2" in rows:
        print("\n## A2 の項目ごとの一致率（A1 を正解とする）\n")
        print(_accuracy_table(rows["A1"], rows["A2"]))


if __name__ == "__main__":
    main()
