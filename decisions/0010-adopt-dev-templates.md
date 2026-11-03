# 0010. 開発環境を作者の dotfiles のひな形の形にそろえる

- Status: Accepted
- Date: 2026-11-03

## Context
このリポジトリには依存を書いたファイルがなく、セットアップも CI も `pip install ruff pytest jsonschema` だけだった。手元と CI で Python やライブラリの版がそろっておらず、型チェックもしていなかった。

作者の dotfiles に、新しいプロジェクトの開発のひな形（[ksip9012/dotfiles の templates/](https://github.com/ksip9012/dotfiles/tree/main/templates)）と、その決めごと（同じリポジトリの `decisions/0001`〜`0008`）ができた。

## Decision
開発環境をひな形の形にそろえる。

- 版: Python と uv は `mise.toml` に書き、依存は `pyproject.toml` に下限だけを書いて `uv.lock` で固定する
- チェック: ruff check・ruff format・pyright・pytest を `mise run check` にまとめ、手元・pre-commit・CI で同じコマンドを動かす。CI の YAML は `mise run check` を呼ぶだけにする
- 厳しさ: ruff のルールは今のまま（E・W・F）、pyright は basic から始める。ひな形と同じ厳しさ（ruff のルールを増やす、pyright を strict にする）にするのは別に行う
- パッケージとして配らないので、`pyproject.toml` で `package = false` にし、リポジトリの直下の `json_schema_mapper/` をそのまま使う（ひな形の src レイアウトには移さない）

## Consequences
- 手元・CI・ほかの PC で、Python とライブラリの版がそろう
- 型チェックが入り、`__doc__` が `None` になりうる 2か所を直した
- ruff format を初めて通したので、2 ファイルの折り返しが変わった（中身は変わらない）
- ひな形と同じ厳しさにするまでは、ひな形から作った新しいプロジェクトより、チェックがゆるい
