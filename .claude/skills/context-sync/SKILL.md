---
name: context-sync
description: 作業開始時に .ai-context.md と active Issues を読んで現在の状態を把握する。作業終了時にコンテキストを更新する。
user-invocable: false
allowed-tools: Read, Grep, Glob, Bash(gh issue list *)
---

# コンテキスト同期

ハンドオフ・プロトコル（01_OS Overview §7）に従い、文脈断絶を防ぐ。

## 作業開始時

1. `.ai-context.md` を読んで以下を把握する：
   - Status（works / broken）
   - Active Issues とその要点
   - 前回の Decisions
   - Next actions（優先度順）
   - Known pitfalls
   - CI Notes

2. `gh issue list --state open` で現在のオープン Issue を確認する

3. 把握した情報を作業の文脈として保持し、実装の判断に活用する

## 作業終了時

以下の情報で `.ai-context.md` を更新する：

- 今回の作業で変更した内容
- 新たに発生した Decision
- 次にやるべきこと（Next actions）— **scope ごとにセクション分けして書く（下記フォーマット参照）**
- 踏んだ罠や注意点（Known pitfalls）
- CI の状態変化

## Next actions フォーマット

`## 4. Next actions` は scope（機能グループ）ごとのサブセクションで構造化する。

```markdown
## 4. Next actions

### scope/xxx（グループ名）
- [ ] #N タイトル ← 次の着手点
- [ ] #M タイトル（#N 完了後）
- [ ] #P タイトル（#N #M 完了後）

### 単発タスク
- [ ] <Issue に紐づかない手順や確認事項>
```

**ルール：**
- `scope/xxx` ラベルを持つ Issue は対応するサブセクションにまとめる
- ラベルのない Issue や手順は `### 単発タスク` に入れる
- 次に着手すべきものに `← 次の着手点` を付ける
- 完了した Issue は削除（または `- [x]`）する

## ルール

- `.ai-context.md` が存在しない場合は、固定フォーマット（02_OS_Template_Spec §6.3）で新規作成する
- 情報が不明な場合は `TODO` と明記し、推測で埋めない
