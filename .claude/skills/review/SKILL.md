---
name: review
description: Codex 主導で PR / Issue / コードをレビューする。コンテキストを整形して Codex セッションを起動し、双方向質疑を経て Severity 区分レビュー結果を出力・コメント投稿する。
argument-hint: [PR番号 または Issue番号]
allowed-tools: Read, Grep, Glob, Bash(gh *), Bash(./os_scripts/codex_session.sh *), Bash(mktemp), Bash(cat *), Bash(rm *), Bash(ls *), Bash(date *)
---

# Codex 主導レビュー

## ステップ 0: 事前確認

`os_scripts/codex_session.sh` の存在を確認する：

```bash
ls os_scripts/codex_session.sh
```

存在しない場合は以下を出力して**停止する**：

```
Error: Codex セッション基盤 (os_scripts/codex_session.sh) が見つかりません。
Issue #94 の実装が完了しているか確認してください。
```

## ステップ 1: レビュー対象を特定する

引数 `$ARGUMENTS` を解析する（`#` プレフィックスは除去する）：

1. `gh pr view <番号>` を試みる
   - 成功 → PR レビューフロー（ステップ 2-A）へ
   - 失敗 → `gh issue view <番号>` を試みる
     - 成功 → Issue レビューフロー（ステップ 2-B）へ
     - 失敗 → エラーを出力して停止

## ステップ 2-A: PR のコンテキストを整形する

以下を順に取得する：

```bash
# PR 基本情報
gh pr view <PR番号> --json number,title,body,headRefName,baseRefName

# PR 差分
gh pr diff <PR番号>

# 紐づく Issue を探す（PR 本文の "Closes #N" / "Fixes #N" から番号を抽出）
gh issue view <Issue番号>
```

一時ファイルにコンテキストを書き込む：

```
# レビュー対象: PR #<N> — <タイトル>

## PR 本文
<PR 本文>

## 関連 Issue の Acceptance Criteria
<Issue 本文の ## Acceptance Criteria セクション>

## Non-goals
<Issue 本文の ## Out of Scope セクション>

## 差分
<gh pr diff の全出力>
```

## ステップ 2-B: Issue のコンテキストを整形する

```bash
gh issue view <Issue番号>
```

### 関連コードの収集手順

以下の優先順でキーワード（1〜3 語）を抽出する：

1. `## Scope` で始まる見出し（例: `## Scope（やること）`）が存在する → そのセクションからキーワードを抽出
2. なければ `## Fix Approach` セクションからキーワードを抽出
3. どちらもなければ Issue タイトルからキーワードを抽出

抽出したキーワードで Grep し、関連コードを収集する：

```bash
# キーワードで Grep し、ヒットしたファイルのうち上位 3 件を選ぶ
```

収集条件（コンテキスト肥大化防止）：
- **最大ファイル数**: 3 件（Grep の結果順で上位 3 件）
- **1 ファイルあたりの最大行数**: 50 行（最初のヒット箇所を起点に前後 25 行を Read）
- **収集対象外**: lock ファイル・バイナリ

一時ファイルにコンテキストを書き込む：

```
# レビュー対象: Issue #<N> — <タイトル>

## Issue 本文
<Issue 全文>

## 関連コード
### <ファイルパス>（<マッチ行数>行）
<ファイル内容の関連箇所（最大 50 行）>

### <ファイルパス>（<マッチ行数>行）
<ファイル内容の関連箇所（最大 50 行）>
```

関連コードが見つからない場合は `## 関連コード` セクションを省略する。

---

## ステップ 3: Codex セッションを開始する

```bash
SESSION_ID="review-$(date +%s)"
./os_scripts/codex_session.sh start "${SESSION_ID}" "${CONTEXT_FILE}"
```

> **注意**: `start` コマンドが成功した後にエラーが発生した場合は、必ず「エラー時クリーンアップ手順」を実行してから停止すること。

Codex の初回応答を読み、以下を判断する：

- **質問を含む** → ステップ 4（双方向質疑）へ
- **質問なし・レビュー結果を直接出力** → ステップ 5（結果整形）へ

## ステップ 4: Codex と双方向質疑を行う

Codex の質問に対して Claude が調査・回答する。質問の種類別対応：

| 質問の種類 | 対応方法 |
|---|---|
| コードの挙動・実装詳細 | 対象ファイルを Read / Grep して回答 |
| 設計方針・ルール | `CLAUDE.md` や Issue を参照して回答 |
| テストの存在 | `gh pr diff` や Glob で確認して回答 |
| AC との整合 | Issue の Acceptance Criteria と照合して回答 |

```bash
./os_scripts/codex_session.sh reply "${SESSION_ID}" "<回答内容>"
```

**最大 5 往復** で質疑を打ち切る。5 往復を超えた場合は以下を reply して終了：

```
調査済みの情報で結論を出してください。これ以上の追加情報は提供できません。
```

Codex が「レビュー完了」「以上がレビュー結果です」等のシグナルを出したら質疑終了。

## ステップ 5: レビュー結果を整形する

Codex の最終出力を以下の Guardrail コメント規格で整形する：

```
### Severity: [BLOCKER|HIGH|MEDIUM|LOW|NIT]

**Finding**: 何が問題か
**Why**: なぜ問題か
**Fix direction**: 直し方の方向性
**Example**: 最小例（長文禁止）
```

判定基準：

- **BLOCKER**: AC を満たしていない・セキュリティ上の欠陥・データ破損リスク
- **HIGH**: 仕様逸脱・重大なロジックバグ・スコープ外の変更
- **MEDIUM**: 可読性・保守性の問題・軽微なロジックの懸念
- **LOW**: コーディングスタイル・命名の改善
- **NIT**: 好みの問題・任意の改善

**最終判定**：

- BLOCKER / HIGH が 1 件以上 → **「マージ不可」** と明言する
- MEDIUM 以下のみ → **「問題なし、マージ可」** と明言する
- 指摘ゼロ → **「問題なし、マージ可」** と明言する

## ステップ 6: セッションを終了してコメント投稿する

```bash
./os_scripts/codex_session.sh end "${SESSION_ID}"
```

### PR の場合

```bash
gh pr comment <PR番号> --body "<レビュー結果全文>"
```

### Issue の場合

```bash
gh issue comment <Issue番号> --body "<レビュー結果全文>"
```

セッション終了後、一時コンテキストファイルを削除する：

```bash
rm "${CONTEXT_FILE}"
```

## エラー時クリーンアップ手順

`./os_scripts/codex_session.sh start` が成功した後にエラーが発生した場合は、以下を必ず実行してから停止すること：

```bash
./os_scripts/codex_session.sh end "${SESSION_ID}"
rm "${CONTEXT_FILE}"
```

その後、エラー内容をユーザーに報告する。

## ルール

- `os_scripts/codex_session.sh` が存在しない場合は **必ずエラーを出して停止する**（Codex 基盤なしでは動作不可）
- Codex への質問応答は **最大 5 往復** とする
- レビュー結果は **必ず日本語** で出力する
- セッション終了（`end`）は途中エラーが発生しても **必ず実行する**（エラー時クリーンアップ手順を参照）
- 一時コンテキストファイルはセッション終了後に削除する
