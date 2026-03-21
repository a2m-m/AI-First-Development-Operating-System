---
name: istart
description: 次に着手すべき Issue を自動判断して作業を開始する。コンテキスト同期・Issue選定・ブランチ作成・計画立案まで一気通貫で行う。
disable-model-invocation: true
allowed-tools: Read, Bash(gh issue list *), Bash(gh issue view *), Bash(git checkout *), Bash(git pull *), EnterPlanMode
---

# Issue スタート

次に着手すべき Issue を自動判断して、作業を即開始する。

## 手順

### 1. コンテキスト把握

`.ai-context.md` を読んで以下を確認する：
- 現在の Status（works / broken）
- Active Issues（すでに進行中のものがないか）
- Completed（完了済みの Issue 番号）
- Next actions（推奨されている次の手）

### 2. オープン Issue を取得

```
gh issue list --state open --limit 50 --json number,title,labels,milestone,assignees
```

取得したリストから **着手すべき Issue** を以下の優先順位で選ぶ：

1. `.ai-context.md` の `Next actions` に明示されているもの
2. 依存 Issue がすべて完了しているもの（本文の "依存" / "Depends on" を確認）
3. Issue 番号が若いもの（小さい数字 = 古い Issue = 先行依存を満たしている可能性が高い）

**スキップ条件（以下は選ばない）**：
- すでに Active Issues に含まれている（進行中）
- PR が作成済みでマージ待ち
- ラベルに `blocked` や `wontfix` がついている
- タイトルや本文に「依存：#N」があり、#N が未完了

### 3. 選定した Issue の詳細を読む

```
gh issue view <number>
```

Issue の以下を把握する：
- 概要・背景
- Acceptance Criteria（AC）
- Non-goals
- Commit Plan（実装コミット分割）

### 4. ブランチを作成して作業開始

```bash
# main を最新化
git checkout main && git pull origin main

# feature ブランチを作成
git checkout -b feature/issue-<number>
```

### 5. 計画を立案してユーザーに提示

`/plan` モードに入り、以下を提示する：

- **対象 Issue**: #番号 タイトル
- **AC まとめ**: 何を満たせば完了か
- **実装方針**: どのファイルを変更するか、アーキテクチャ上の注意点
- **Commit Plan**: 何を何回のコミットに分けるか
- **懸念事項**: Known pitfalls に関連するリスク

ユーザーの承認を得てから実装に入る。

## 出力フォーマット

```
## istart: Issue #<N> を開始します

### 選定理由
- <なぜこの Issue を選んだか>

### Issue 概要
- タイトル: ...
- AC:
  - [ ] ...
  - [ ] ...

### 実装計画
...

### ブランチ
`feature/issue-<N>` を作成済み

---
計画に問題がなければ実装を始めます。修正があれば教えてください。
```

## ルール

- **Active Issues がすでに存在する場合**は、その Issue の状態（PR作成済み？マージ待ち？）を確認し、ユーザーに報告してから次の Issue を選ぶ
- 着手すべき Issue が見つからない場合（全部 blocked / 全完了）は、ユーザーにその旨を報告して止まる
- Issue を選んだ理由は必ず明示する（ブラックボックスにしない）
- ブランチが既に存在する場合は `git checkout feature/issue-<N>` で切り替え（強制削除しない）
- 計画提示後、ユーザーの承認なしに実装を始めない
