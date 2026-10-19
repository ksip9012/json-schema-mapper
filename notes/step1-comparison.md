# Step1 シリーズの横断比較（精度・コスト・処理時間）

「自由入力をどう構造化データに落とし込むか」を3つの方法で解いた Step1 シリーズを、同じ物差しで並べる。

| Step | リポジトリ | 方法 | スキーマ | LLM の呼び出し/件 |
| --- | --- | --- | --- | --- |
| A1 | [json-schema-mapper](https://github.com/ksip9012/json-schema-mapper) | ルールベース（正規表現・条件分岐） | 人が決める（`schema.json`） | 0回 |
| A2 | [llm-structured-output-extractor](https://github.com/ksip9012/llm-structured-output-extractor) | Gemini の Structured Output | 人が決める（A1 と同じ） | 1回 |
| B | [llm-json-extractor](https://github.com/ksip9012/llm-json-extractor) | Gemini にスキーマを設計させてから抽出 | LLM が決める | 2回（設計 → 抽出） |

## 測り方（2026-10-19）

- 入力: それぞれの `fixtures/` をそのまま使う
  - A1・A2: ファイル名 12件（`fixtures/sample_folder`。A2 は A1 と同じもの）
  - B: 種類の違う個人メモ 7件（`fixtures/sample_notes`）。B は自由に書かれたメモを相手にする設計なので、ファイル名ではなく本来の入力で測った
  - 入力が違うので、B の数字は A1・A2 と「1件あたり」で並べる
- 回数: A1 は 100回、A2・B は 3回（実際の API を呼ぶので料金がかかるため）
- モデル: `gemini-3.8-flash`（Vertex AI、`location=global`）
- 処理時間: 1件を構造化する関数（A1・A2 は `map_file`、B は `map_note`）の呼び出し前後を `time.perf_counter` で測る。スキーマの検証（`jsonschema.validate`）も含む
- トークン数: 応答の `usage_metadata` から、入力（`prompt_token_count`）・出力（`candidates_token_count`）・思考（`thoughts_token_count`）を分けて取る
- 料金: Gemini 3.8 Flash の Standard の料金（100万トークンあたり入力 $0.75、出力 $3.75。出力には思考トークンを含む。2026-12-31 までの価格で、2027-01-01 からは倍になる）。[公式の料金表](https://ai.google.dev/gemini-api/docs/pricing)で 2026-10-19 に確認した
- 再試行の扱い: SDK の自動の再試行は切り、504 などの一時的なエラーはスクリプト側で待ってから試し直した。待った時間と失敗した試行は処理時間に含めず、回数だけ記録した（A2: 36回中 3回、B: 21回中 5回。すべて 504）
  - SDK の再試行を残したまま測ると、待ち時間が混ざって 1件 100秒を超える回が出たため
  - 1回の呼び出しには 120秒の上限を付けた。上限なしでは、1件で返事が返らないまま 6分以上止まったことがあった

## 結果

### 1件あたりの処理時間・トークン数・料金

| Step | 成功 | LLM 呼び出し/件 | 処理時間 中央値 | 処理時間 p90 | 入力トークン/件 | 出力トークン/件 | 思考トークン/件 | 料金/件 | 料金/1,000件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | 1200/1200 | 0 | 1.7 ms | 1.7 ms | 0 | 0 | 0 | $0 | $0 |
| A2 | 36/36 | 1 | 5.79 s | 17.69 s | 453 | 53 | 378 | $0.0020 | $1.95 |
| B | 21/21 | 2 | 32.21 s | 70.86 s | 616 | 432 | 1,084 | $0.0061 | $6.15 |

- 処理時間: 中央値で比べると、A1 は A2 のおよそ 3,400分の1。A2 と B は 1回の呼び出しでも 2〜60秒と幅が大きく、中央値より p90 を見たほうが実際の待ち時間に近い
  - 1回の呼び出しあたりの中央値は A2 が 5.9秒、B が 16.1秒。B は呼び出しが2回あるうえ、1回ごとの出力（スキーマの設計と、入れ子のある抽出結果）も長い
  - 計測は平日の夜（JST 20:30〜21:05）の 1回分で、504 も出ていた。時間帯によって変わるので、絶対値より A2 と B の比を見る
- トークンと料金: 思考トークンが出力の大半を占める。A2 では出力 53 に対して思考が 378 あり、料金の 7割ほどが思考トークンの分。料金を下げるなら、まず思考の量（`thinking_config`）を見直すのがよい
- B は A2 のおよそ 3倍の料金で、入力 1件の長さ（メモ本文）も、出力（スキーマ＋データ）も長い

### 精度

**A2（A1 を正解とする。12件 × 3回 = 36件）**

| 項目 | 一致 | 一致しなかったファイル |
| --- | --- | --- |
| `extracted_date` | 34/36 | `invoice_2026-03.pdf` |
| `category` | 36/36 | - |
| `is_hidden` | 36/36 | - |
| `word_count` | 36/36 | - |
| `has_version_suffix` | 36/36 | - |
| `duplicate_index` | 36/36 | - |
| `separator_style` | 36/36 | - |
| `normalized_title` | 27/36 | `.hidden_config`, `IMG_20260210_143022.jpg`, `invoice_2026-03.pdf` |

- `normalized_title` の 3件は 3回とも同じ答えで、2026-09-27 の検証（llm-structured-output-extractor の [notes/step1a1-vs-step1a2-accuracy.md](https://github.com/ksip9012/llm-structured-output-extractor/blob/main/notes/step1a1-vs-step1a2-accuracy.md)）と同じ傾向だった。LLM は「日付っぽいもの」「隠しファイルの先頭のドット」を、A1 のルールより広く解釈して削る
- `extracted_date` は新しく見つかった差。A1 は年と月だけの `2026-03` を日付にしない（null）が、A2 は 3回のうち 2回で `2026-03-01` と日を補った。2026-09-27 の 1回の検証では 12件すべて一致していたので、**同じ入力でも回によって答えが変わる**ことが、回数を重ねて初めて見えた

**B（答え合わせはできないので、検証を通ったかで見る）**

- 7件 × 3回 = 21件すべてで、設計したスキーマが妥当な JSON Schema で、抽出したデータがそのスキーマに従っていた
- B は「正解のスキーマ」がない課題なので、A2 と同じ一致率では比べられない。設計されたスキーマの中身の傾向は、llm-json-extractor の [notes/schema-design-observations.md](https://github.com/ksip9012/llm-json-extractor/blob/main/notes/schema-design-observations.md) に書いた

## 使い分け

| こんなとき | 向いている方法 | 理由 |
| --- | --- | --- |
| 入力の形が決まっていて、ルールに書き下せる | A1 | 速くて（1件 2ms 弱）、無料で、毎回同じ答えになる。ルールに書いた範囲しか扱えない |
| 出力の形は決まっているが、入力の言い回しがばらつく | A2 | ルールを書かずに済む。意味をくみ取りすぎて、仕様より広く解釈することがあり、答えが回によって揺れることもある。1件数秒・1,000件で約 $2 |
| 出力の形も、入力を見るまで決められない | B | 入力ごとに構造を作れる。答えの「正しさ」は検証でしか担保できず、1件数十秒・1,000件で約 $6 と、いちばん重い |

- LLM を使う A2・B は、A1 に比べて桁違いに遅く、待ち時間のばらつきも大きい。大量のデータを処理するなら、並列化・再試行・タイムアウトの設計が、精度と同じくらい大事になる
- A2 で揺れた項目（`normalized_title`、`extracted_date`）は、どれも「何をタイトル・日付とみなすか」を説明文だけに頼っていた（`extracted_date` は形式は守れていて、年と月だけのものを日付とみなすかで揺れた）。`enum`・真偽値・整数のように答えの幅が狭い項目は揺れなかった。LLM に任せる項目ほど、答えの幅をスキーマで狭め、境目の例を説明文に書いておくのがよい

## 再現方法

各リポジトリの `scripts/benchmark.py` が 1件・1回ごとに 1行の JSON Lines を出し、このリポジトリの `scripts/summarize_benchmark.py` が表にまとめる。結果の生データは各リポジトリの `notes/benchmark/` に置いた。

```bash
# A1（このリポジトリ）
python scripts/benchmark.py --runs 100 > notes/benchmark/a1.jsonl

# A2・B（それぞれのリポジトリで。Vertex AI の認証が必要で、料金がかかる）
python scripts/benchmark.py --runs 3 > notes/benchmark/a2.jsonl  # A2
python scripts/benchmark.py --runs 3 > notes/benchmark/b.jsonl   # B

# まとめ（このリポジトリで）
python scripts/summarize_benchmark.py notes/benchmark/a1.jsonl \
  ../llm-structured-output-extractor/notes/benchmark/a2.jsonl \
  ../llm-json-extractor/notes/benchmark/b.jsonl
```
