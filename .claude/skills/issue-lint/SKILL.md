---
name: issue-lint
description: Issue の品質チェック。AC の Yes/No 判定可能性・空セクション・Commit Plan・Non-goals の有無を検査し、不備を一覧で報告する。
disable-model-invocation: true
argument-hint: [Issue番号]
allowed-tools: Bash(gh issue view *), Read
---

# Issue Lint

Issue が「命令書」として機能する品質基準を満たしているか検査する（P2: Issue-Driven Development）。

## 手順

1. `gh issue view $ARGUMENTS[0] --json title,body,labels` で Issue の内容を取得する

2. 以下のチェックリストを検査する

### チェック項目

| ID | 項目 | 合格条件 |
|---|---|---|
| L1 | タイトル形式 | `[Feature]` or `[Bug]` プレフィックスがある |
| L2 | テンプレート使用 | Feature: Background/Scope/Out of Scope/AC/Commit Plan, Bug: Repro/Expected/Actual/AC/Commit Plan が存在する |
| L3 | 空セクション | コメント行（`<!-- ... -->`）だけで本文が空のセクションがない |
| L4 | Acceptance Criteria | 各ACが `[ ]` チェックボックス形式で、Yes/No 判定できる文になっている |
| L5 | Commit Plan | 少なくとも1件の Commit が記載されている |
| L6 | Out of Scope / Non-goals | Feature の場合、明示的に「やらないこと」が書かれている |

3. 結果を出力フォーマットで報告する

## 出力フォーマット

```
## Issue Lint: #<番号> <タイトル>

### 結果: [PASS ✅ | FAIL ❌ | WARN ⚠️]

| ID | 項目 | 結果 | 詳細 |
|---|---|---|---|
| L1 | タイトル形式 | ✅ | - |
| L2 | テンプレート使用 | ❌ | "Commit Plan" セクションが存在しない |
| ... | | | |

### 修正提案
- L2: `## Commit Plan` セクションを追加し、コミット分割計画を記載する
```

## ルール

- FAIL が1件でもある場合は全体結果を FAIL にする
- WARN は構造はあるが内容が薄い場合（例：ACが1件しかない）
- Issue 番号が省略された場合は `gh issue list --state open` の一覧を表示してユーザーに選ばせる
- 出力は日本語
