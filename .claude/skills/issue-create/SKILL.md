---
name: issue-create
description: テンプレート準拠の命令書 Issue を作成する。新機能・改善は feature テンプレ、バグは bug テンプレを使用。--review フラグで Issue 作成後に Codex 品質レビューを自動実行できる。
disable-model-invocation: true
argument-hint: [feature|bug] タイトル [--review]
allowed-tools: Read, Grep, Glob, Bash(gh *), Bash(./os_scripts/codex_session.sh *), Bash(mktemp), Bash(cat *), Bash(rm *), Bash(ls *), Bash(date *)
---

# Issue 命令書の作成

Issue は「命令書」として機能させる（P2: Issue-Driven Development）。
Issue の品質が実装の成功率を決める。

## ステップ 1: 引数を解析する

`$ARGUMENTS` から以下を取得する：

- **種別**: 最初の単語が `feature` or `bug` → テンプレートを決定
  - `feature` → `.github/ISSUE_TEMPLATE/feature.md` を参照
  - `bug` → `.github/ISSUE_TEMPLATE/bug.md` を参照
  - 未指定 → ユーザーに確認
- **タイトル**: 種別の後の文字列（`--review` フラグは除く）
- **`--review` フラグ**: 引数に `--review` が含まれるか確認する

## ステップ 2: Issue を作成する

`CLAUDE.md` §ISSUE作成ルール に従う：

- **再現・方針・AC・Non-goals・Commit Plan** が明記されていること
- Acceptance Criteria が **Yes/No で判定できる形** になっていること
- Commit Plan で実装を **1〜3コミット** に分割していること

テンプレートの **全セクションを埋める**（空のまま残さない）

`gh issue create` で Issue を作成する：
- タイトルは日本語（共通ルール §2）
- ラベルは種別に応じて `feature` または `bug` を付与

Issue が作成されたら、Issue 番号と URL を報告する。

## ステップ 3: Codex レビューを実行する（`--review` フラグがある場合のみ）

`--review` フラグが指定されていない場合はここで終了する。

### 事前確認

```bash
ls os_scripts/codex_session.sh
```

存在しない場合は以下を出力して **Codex レビューをスキップ**：

```
⚠️ Codex セッション基盤 (os_scripts/codex_session.sh) が見つかりません。
Codex レビューをスキップします（Issue #94 の実装が完了しているか確認してください）。
```

### コンテキストファイルを作成する

作成した Issue の内容を取得して一時ファイルに書き込む：

```bash
ISSUE_CONTENT=$(gh issue view <作成したIssue番号>)
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

### セッション開始・質疑・終了

```bash
SESSION_ID="issue-lint-$(date +%s)"
./os_scripts/codex_session.sh start "${SESSION_ID}" "${CONTEXT_FILE}"
```

Codex の応答を読み、質問があれば回答する（最大 5 往復）：

| 質問の種類 | 対応方法 |
|---|---|
| AC の意図・背景 | Issue 本文の Background / Approach を参照して補足 |
| 他 Issue との関係 | `gh issue view <関連番号>` で確認して回答 |
| 用語・ドメイン知識 | `CLAUDE.md` や `os_docs/` を参照して補足 |
| Commit Plan の実現可能性 | Issue の Scope と照合して回答 |

```bash
./os_scripts/codex_session.sh reply "${SESSION_ID}" "<回答内容>"
```

5 往復を超えた場合は以下を reply して終了：

```
調査済みの情報で結論を出してください。これ以上の追加情報は提供できません。
```

### 評価レポートを整形して投稿する

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

セッションを終了してクリーンアップする：

```bash
./os_scripts/codex_session.sh end "${SESSION_ID}"
rm "${CONTEXT_FILE}"
```

## ルール

- `--review` フラグがない場合は Codex レビューを実行しない（従来の動作を維持）
- `codex_session.sh` が存在しない場合は Codex レビューをスキップする（エラーにしない）
- 評価レポートは **必ず日本語** で出力する
- セッション終了（`end`）は途中エラーが発生しても **必ず実行する**
- 一時コンテキストファイルはセッション終了後に削除する
