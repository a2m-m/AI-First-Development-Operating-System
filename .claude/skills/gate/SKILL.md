---
name: gate
description: Pre-Push Gate を実行する。lint / typecheck / test を走らせ、結果を解釈して次の手を提示する。
disable-model-invocation: true
allowed-tools: Bash(./scripts/run *), Read
---

# Pre-Push Gate

push 前に品質ゲートを通す（P4: Gates over Hope）。

## 手順

1. `./scripts/run ci` を実行する（lint → typecheck → test）

2. 結果を解釈する：
   - **全て成功** → 「Gate PASS: push 可能です」と報告
   - **失敗あり** → 以下を分析して報告：
     - どのステップで失敗したか
     - エラーの原因（可能な範囲で特定）
     - 修正方針の提案

3. 失敗時、修正が明確な場合は修正を提案する（ただし実行はしない）

## 出力フォーマット

```
## Gate 結果: [PASS ✅ | FAIL ❌]

### 実行結果
- lint: [OK|FAIL]
- typecheck: [OK|FAIL|SKIP]
- test: [OK|FAIL]

### （失敗時のみ）原因と修正方針
- 原因: ...
- 修正方針: ...
```

## ルール

- `scripts/run` が存在しない場合は `./scripts/run doctor` の実行を提案する
- typecheck が空（skip）の場合は警告しない（プロジェクト事情として許容）
