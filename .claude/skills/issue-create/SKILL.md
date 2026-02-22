---
name: issue-create
description: テンプレート準拠の命令書 Issue を作成する。新機能・改善は feature テンプレ、バグは bug テンプレを使用。
disable-model-invocation: true
argument-hint: [feature|bug] タイトル
allowed-tools: Read, Grep, Glob, Bash(gh *)
---

# Issue 命令書の作成

Issue は「命令書」として機能させる（P2: Issue-Driven Development）。
Issue の品質が実装の成功率を決める。

## 手順

1. 引数の最初の単語で種別を判定する
   - `feature` → `.github/ISSUE_TEMPLATE/feature.md` を参照
   - `bug` → `.github/ISSUE_TEMPLATE/bug.md` を参照
   - 未指定 → ユーザーに確認

2. `.ai-instructions.md` §1 のルールに従う：
   - **再現・方針・AC・Non-goals・Commit Plan** が明記されていること
   - Acceptance Criteria が **Yes/No で判定できる形** になっていること
   - Commit Plan で実装を **1〜3コミット** に分割していること

3. テンプレートの **全セクションを埋める**（空のまま残さない）

4. `gh issue create` で Issue を作成する：
   - タイトルは日本語（共通ルール §2）
   - ラベルは種別に応じて `feature` または `bug` を付与

## 出力

- Issue が作成されたら、Issue 番号と URL を報告する
- 判断に迷った点があれば、その旨をユーザーに伝える
