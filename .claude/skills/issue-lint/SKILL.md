---
name: issue-lint
description: Issue の品質チェック。AC の Yes/No 判定可能性・空セクション・Commit Plan・Non-goals の有無を検査し、不備を一覧で報告する。Codex による品質評価レポートも実行し Issue コメントとして投稿する。
disable-model-invocation: true
argument-hint: [Issue番号]
allowed-tools: Bash(gh issue view *), Bash(gh issue comment *), Bash(gh issue list *), Bash(./os_scripts/codex_session.sh *), Bash(mktemp), Bash(cat *), Bash(rm *), Bash(ls *), Bash(date *), Read
---

# Issue Lint

Issue が「命令書」として機能する品質基準を満たしているか検査する（P2: Issue-Driven Development）。

ルールベースチェックに加えて、Codex が AC の曖昧さ・Commit Plan の妥当性・スコープ膨張を評価する。

## ステップ 1: Issue を取得する

`$ARGUMENTS` から Issue 番号を取得する：
- 番号が指定されている → `gh issue view <番号> --json number,title,body,labels` で取得
- 省略された場合 → `gh issue list --state open` の一覧を表示してユーザーに選ばせる

## ステップ 2: ルールベースチェック（従来動作・後方互換）

以下のチェックリストを検査する：

### チェック項目

| ID | 項目 | 合格条件 |
|---|---|---|
| L1 | タイトル形式 | `[Feature]` or `[Bug]` プレフィックスがある |
| L2 | テンプレート使用 | Feature: Background/Scope/Out of Scope/AC/Commit Plan, Bug: Repro/Expected/Actual/AC/Commit Plan が存在する |
| L3 | 空セクション | コメント行（`<!-- ... -->`）だけで本文が空のセクションがない |
| L4 | Acceptance Criteria | 各ACが `[ ]` チェックボックス形式で、Yes/No 判定できる文になっている |
| L5 | Commit Plan | 少なくとも1件の Commit が記載されている |
| L6 | Out of Scope / Non-goals | Feature の場合、明示的に「やらないこと」が書かれている |

### 結果を出力する

```
## Issue Lint: #<番号> <タイトル>

### ルールベースチェック結果: [PASS ✅ | FAIL ❌ | WARN ⚠️]

| ID | 項目 | 結果 | 詳細 |
|---|---|---|---|
| L1 | タイトル形式 | ✅ | - |
| L2 | テンプレート使用 | ❌ | "Commit Plan" セクションが存在しない |
| ... | | | |

### 修正提案
- L2: `## Commit Plan` セクションを追加し、コミット分割計画を記載する
```

- FAIL が1件でもある場合は全体結果を FAIL にする
- WARN は構造はあるが内容が薄い場合（例：ACが1件しかない）

## ステップ 3: Codex レビューセッションを開始する

### 事前確認

```bash
ls os_scripts/codex_session.sh
```

存在しない場合は以下を出力して **Codex レビューをスキップ**（ルールベース結果のみ返す）：

```
⚠️ Codex セッション基盤 (os_scripts/codex_session.sh) が見つかりません。
Codex レビューをスキップします（Issue #94 の実装が完了しているか確認してください）。
```

### コンテキストファイルを作成する

```bash
ISSUE_CONTENT=$(gh issue view <番号>)
CONTEXT_FILE=$(mktemp)
cat > "${CONTEXT_FILE}" << 'HEADER_EOF'
# Issue 品質レビュー依頼

あなたは Issue レビュアーです。以下の Issue を読み、品質を評価してください。

## 評価観点

1. **AC の明確さ**: 各 Acceptance Criteria が Yes/No で判定できるか。曖昧な表現がないか。
2. **Commit Plan の妥当性**: 実装を適切な粒度（1〜3コミット）に分割できているか。
3. **スコープの適切さ**: Out of Scope / Non-goals が明示されているか。スコープが膨張していないか。
4. **依存関係の明示**: 他 Issue への依存がある場合、明記されているか。
5. **実装可能性**: この Issue だけで実装に着手できる十分な情報があるか。

## Issue 内容
HEADER_EOF
echo "${ISSUE_CONTENT}" >> "${CONTEXT_FILE}"
```

### セッション開始

```bash
SESSION_ID="issue-lint-$(date +%s)"
./os_scripts/codex_session.sh start "${SESSION_ID}" "${CONTEXT_FILE}"
```

> **注意**: `start` コマンドが成功した後にエラーが発生した場合は、必ず「エラー時クリーンアップ手順」を実行してから停止すること。

## ステップ 4: Codex と双方向質疑を行う

Codex の初回応答を読み：

- **質問を含む** → 以下のテーブルに従って調査・回答する
- **質問なし・評価を直接出力** → ステップ 5 へ

| 質問の種類 | 対応方法 |
|---|---|
| AC の意図・背景 | Issue 本文の Background / Approach を参照して補足 |
| 他 Issue との関係 | `gh issue view <関連番号>` で確認して回答 |
| 用語・ドメイン知識 | `CLAUDE.md` や `os_docs/` を参照して補足 |
| Commit Plan の実現可能性 | Issue の Scope と照合して回答 |

```bash
./os_scripts/codex_session.sh reply "${SESSION_ID}" "<回答内容>"
```

**最大 5 往復** で質疑を打ち切る。超えた場合は以下を reply して終了：

```
調査済みの情報で結論を出してください。これ以上の追加情報は提供できません。
```

Codex が「評価完了」「以上が評価結果です」等のシグナルを出したら質疑終了。

## ステップ 5: Codex 評価レポートを整形して投稿する

Codex の最終出力を以下の形式で整形する：

```
## Codex Issue 品質評価レポート

### 総合評価: [PASS ✅ | WARN ⚠️ | FAIL ❌]

| 観点 | 評価 | コメント |
|---|---|---|
| AC の明確さ | ✅ / ⚠️ / ❌ | <具体的な指摘> |
| Commit Plan の妥当性 | ✅ / ⚠️ / ❌ | <具体的な指摘> |
| スコープの適切さ | ✅ / ⚠️ / ❌ | <具体的な指摘> |
| 依存関係の明示 | ✅ / ⚠️ / ❌ | <具体的な指摘> |
| 実装可能性 | ✅ / ⚠️ / ❌ | <具体的な指摘> |

### 改善提案
- <具体的な改善点>

---
*このレポートは Codex による自動品質評価です。*
```

Issue コメントとして投稿する：

```bash
gh issue comment <Issue番号> --body "<整形した評価レポート>"
```

## ステップ 6: セッションを終了してクリーンアップする

```bash
./os_scripts/codex_session.sh end "${SESSION_ID}"
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

- ルールベースチェック（ステップ 2）は **常に実行する**（Codex の有無によらず）
- `codex_session.sh` が存在しない場合は Codex レビューをスキップし、ルールベース結果のみ返す
- Codex への質問応答は **最大 5 往復** とする
- 評価レポートは **必ず日本語** で出力する
- セッション終了（`end`）は途中エラーが発生しても **必ず実行する**（エラー時クリーンアップ手順を参照）
- 一時コンテキストファイルはセッション終了後に削除する
- 出力は日本語
