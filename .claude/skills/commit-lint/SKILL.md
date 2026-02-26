---
name: commit-lint
description: コミットメッセージが規約（Conventional Commits + 日本語）に準拠しているかチェックする。push前の品質ゲートとして使う。
disable-model-invocation: true
argument-hint: [コミット数（デフォルト: 1）| HEAD~N..HEAD]
allowed-tools: Bash(git log *)
---

# Commit Lint

コミットメッセージが `docs/commit_strategy.md` の規約に準拠しているか検査する（P4: Gates over Hope）。

## 手順

1. 対象コミットを取得する
   - `$ARGUMENTS[0]` が数値（例: `3`）→ `git log -3 --format="%H %s"` で直近N件
   - `$ARGUMENTS[0]` が範囲（例: `HEAD~3..HEAD`）→ その範囲を使用
   - 省略時: `git log -1 --format="%H %s"` で直近1件

2. 各コミットメッセージを以下のルールで検査する

### チェックルール

| ID | ルール | 合格条件 |
|---|---|---|
| C1 | Type 形式 | `type: ` または `type(scope): ` で始まる |
| C2 | Type 値 | feat / fix / docs / style / refactor / perf / test / build / ci / chore / revert のいずれか |
| C3 | 日本語 | Subject（タイトル）が日本語で書かれている（コード・固有名詞は除く） |
| C4 | 長さ | Subject が72文字以内 |
| C5 | 命令形回避 | 「する」「した」の体言止めではなく「〜を追加」「〜を修正」等の説明形 |

3. 結果を出力フォーマットで報告する

## 出力フォーマット

```
## Commit Lint 結果

| コミット | メッセージ | 結果 | 不備 |
|---|---|---|---|
| abc1234 | feat: ユーザー認証を追加 | ✅ | - |
| def5678 | update login | ❌ | C1: type形式なし, C3: 日本語なし |

### 修正提案
- def5678: `feat: ログイン処理を更新` に修正する
  （`git commit --amend` または `git rebase -i` で修正）
```

## ルール

- FAIL が1件でもある場合は全体を FAIL と報告し、修正方法を必ず提案する
- Merge commit（`Merge branch ...`）はチェック対象外
- `--amend` による修正提案は未pushコミットのみ行う（push済みは rebase -i を案内）
- 出力は日本語
