---
name: ci-failure-triage
description: CI失敗ログを解析し、原因を特定してbugテンプレートでIssueを自動作成する。失敗を教材として記録する。
disable-model-invocation: true
argument-hint: [run-id（省略時は最新）]
allowed-tools: Bash(gh run view *, gh run list *, gh issue create *, gh issue list *), Read
---

# CI Failure Triage

CI失敗を放置せず、原因をIssue化して教材として残す（§5: CI失敗・テスト失敗）。

## 手順

1. Run ID を取得する
   - `$ARGUMENTS[0]` が指定されていれば使用
   - 省略時: `gh run list --limit 5 --status failure` で一覧表示し最新を選択

2. `gh run view <run-id> --log-failed` で失敗ログを取得する

3. ログを解析して以下を特定する：
   - **失敗ステップ**: どのジョブ・ステップで失敗したか
   - **エラー種別**: lint / test / build / typecheck / deploy のどれか
   - **エラーメッセージ**: 具体的なエラー内容（抜粋）
   - **Root Cause 仮説**: ログから読み取れる原因の推測

4. bugテンプレートを使って Issue を作成する
   ```
   gh issue create \
     --title "[Bug] CI失敗: <失敗ステップ> - <エラー概要>" \
     --label "bug,ci" \
     --body "<以下のフォーマットで本文を作成>"
   ```

## Issue 本文フォーマット（bugテンプレート準拠）

```markdown
## Repro Steps（再現手順）
1. `git push` or PRの作成
2. GitHub Actions の <ジョブ名> ステップを確認

## Expected（期待値）
CI が全ステップ PASS する

## Actual（実際）
<ステップ名> で失敗。エラー:
\`\`\`
<エラーログ抜粋（50行以内）>
\`\`\`

## Root Cause Hypothesis（仮説）
<ログから読み取れる原因>

## Fix Approach（修正方針）
<提案する修正方針>

## Acceptance Criteria
- [ ] 同じ操作でCIがPASSする
- [ ] リグレッションテストが追加されている（該当する場合）

## Test Plan
ローカルで `./os_scripts/run ci` を実行して確認

## Commit Plan
- Commit 1: 原因箇所の修正
- Commit 2: テスト追加（任意）
```

## 出力フォーマット

```
## CI Triage 完了

- Run ID: <id>
- 失敗ステップ: <ステップ名>
- 推定原因: <概要>
- Issue 作成: #<番号> <タイトル>
  URL: <issue-url>
```

## ルール

- ログが長い場合は関連部分（エラー周辺50行）のみ抽出する
- 同じ失敗が既存Issueに存在する場合は新規作成せず、既存にコメントを追加する
  - `gh issue list --label ci --state open` で確認
- 出力は日本語
