---
name: pr-complete
description: PRマージ後の後片付け。.ai-context.md を更新し、次のエージェントが迷子にならない状態にする。
disable-model-invocation: true
argument-hint: [PR番号]
allowed-tools: Bash(gh pr view *, gh issue list *), Read, Edit
---

# PR Complete

PRマージ後に `.ai-context.md` を更新する（§5: コンテキスト管理）。

## 手順

1. `gh pr view $ARGUMENTS[0] --json title,body,mergedAt,headRefName,closingIssuesReferences` でPR情報を取得する

2. `gh issue list --state closed --limit 5` でクローズされた関連Issueを確認する

3. コンテキストファイルを読んで現在の状態を把握する：
   - `.ai-context.local.md` が存在する場合 → **`.ai-context.local.md` を読む**
   - 存在しない場合 → **`.ai-context.md` を読む**

4. 読んだファイルを以下の観点で更新する（読んだのと同じファイルを更新すること）：
   - **Status**: 今回のPRで何が変わったか（works / broken / partial）
   - **Active Issues**: クローズされたIssueを削除、新規Issueがあれば追記
   - **Decisions**: マージによって確定した技術的決定事項
   - **Next actions**: 次にやるべきこと（優先度順）
   - **Known pitfalls**: 今回の実装で踏んだ罠・注意点
   - **CI Notes**: CIの状態に変化があれば更新

5. 更新内容のサマリーを報告する

## 出力フォーマット

```
## PR Complete: #<番号> <タイトル>

### .ai-context.md 更新内容
- Status: works に更新
- Closed: #42 <Issue タイトル>
- Next actions: #45 <次のIssue> が最優先
- Known pitfalls: <あれば記載>

更新が完了しました。次の作業は #45 を参照してください。
```

## ルール

- `.ai-context.local.md` が存在する場合 → 読取・更新ともにそちらを対象にし、`.ai-context.md` は雛形のまま触らない
- `.ai-context.md` が存在しない場合は `02_OS_Template_Spec.md §6.3` のフォーマットで新規作成する
- PR番号が省略された場合は `gh pr list --state merged --limit 5` で直近をリストして選ばせる
- 情報が不明な場合は `TODO` と明記し、推測で埋めない
- 出力は日本語
