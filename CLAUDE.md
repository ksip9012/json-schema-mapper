# json-schema-mapper

## Git 運用

GitHub Flow で運用する。

- `main` への直接 push は禁止。変更は必ずブランチを切って作業し、PR 経由でマージする。
- ブランチ作成時は `github-branch` skill を使用する（Issue 番号からブランチ名を自動生成し、`main` を最新化してから切る）。
- Issue 作成時は `github-issue-create` skill を使用する。
- push 後に作業が未完了の場合は `github-issue-comment` skill で関連 Issue にコメントする。
- 作業完了後は `github-pr` skill で PR を作成し、関連 Issue をクローズする。
