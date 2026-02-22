# Architecture Decision Records (ADR)

このディレクトリは、プロジェクトにおける重要なアーキテクチャの意思決定 (Architecture Decision Records) を管理するための場所です。

## 命名規則
ADRファイルは以下の命名規則に従って作成してください：
`NNNN-title.md` (例: `0001-template-contract.md`)

- `NNNN`: 4桁の連番 (0001から開始)
- `title`: 決定内容を簡潔に表す英語のケバブケース (kebab-case) 文字列

## ADR の書き方テンプレート

新規にADRを追加する際は、以下の構成を推奨します（[MADR](https://adr.github.io/madr/) をベースとした軽量形式）。

```markdown
# [Title] (タイトル)

## Status (ステータス)
Proposed (提案中) / Accepted (承認済) / Deprecated (非推奨) / Superseded (代替済)

## Context (背景)
なぜこの決定が必要になったのか。どのような技術的・ビジネス的な制約や課題があるのか。

## Decision (決定事項)
具体的に何をすることに決めたか。

## Consequences (結果)
この決定によってもたらされる良い影響（メリット）と悪い影響（デメリット・トレードオフ）。
```

## 一覧管理ルール
新しいADRを追加した際は、必要に応じて `docs/architecture.md` からの参照リンクを追加し、システム全体からアクセスしやすい状態を保ってください。
