"""fixtures の各ファイルを構造化し、1件あたりの処理時間を JSON Lines で
出力するベンチマーク。

Step1 シリーズ（A1 / A2 / B）の横断比較用。3リポジトリで同じ形式の行を
出力し、`scripts/summarize_benchmark.py` でまとめる
（notes/step1-comparison.md 参照）。

使い方:
    python scripts/benchmark.py --runs 100 > notes/benchmark/a1.jsonl
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from json_schema_mapper.file_lister import list_files  # noqa: E402
from json_schema_mapper.mapper import map_file  # noqa: E402

_FIXTURES = Path(__file__).resolve().parent.parent / "fixtures/sample_folder"


def main() -> None:
    """各ファイルを runs 回ずつ構造化し、1回ごとに1行を出力する。"""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=100)
    args = parser.parse_args()

    for run in range(1, args.runs + 1):
        for name in list_files(_FIXTURES):
            start = time.perf_counter()
            result = map_file(_FIXTURES / name)
            latency_ms = (time.perf_counter() - start) * 1000
            row = {
                "step": "A1",
                "model": None,
                "run": run,
                "file": name,
                "ok": True,
                "error": None,
                "latency_ms": round(latency_ms, 3),
                "llm_calls": 0,
                "prompt_tokens": 0,
                "output_tokens": 0,
                "thoughts_tokens": 0,
                "retries": 0,
                "retry_codes": [],
                "result": result,
            }
            print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
