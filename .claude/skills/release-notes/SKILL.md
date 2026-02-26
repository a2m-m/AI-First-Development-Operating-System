---
name: release-notes
description: 2つのタグ間のPR・コミット一覧からリリースノートを自動生成する。feat/fix/docs等のtypeでグルーピングして見やすい形式で出力する。
disable-model-invocation: true
argument-hint: [前タグ] [新タグ（省略時はHEAD）]
allowed-tools: Bash(git log *, git tag *, gh pr list *), Write
---

# Release Notes

2タグ間の変更をグルーピングしてリリースノートを生成する。

## 手順

1. タグを確認する
   - `$ARGUMENTS[0]` = 前タグ（必須）。省略時は `git tag --sort=-creatordate | head -2` から推定
   - `$ARGUMENTS[1]` = 新タグ（省略時は HEAD）

2. 対象コミットを取得する
   ```
   git log <前タグ>..<新タグ> --format="%H %s" --no-merges
   ```

3. コミットを Conventional Commits の type でグルーピングする
   - `feat` → 新機能
   - `fix` → バグ修正
   - `docs` → ドキュメント
   - `refactor` → リファクタリング
   - `perf` → パフォーマンス改善
   - `ci` / `build` / `chore` → その他
   - type なし → 未分類

4. リリースノートを生成して出力する（ファイル保存は任意）

## 出力フォーマット

```markdown
# リリースノート: <新タグ>

リリース日: <YYYY-MM-DD>
対象範囲: <前タグ>...<新タグ>

## 新機能
- <Issue/PR番号> <説明> （コミット: abc1234）

## バグ修正
- <Issue/PR番号> <説明> （コミット: def5678）

## ドキュメント
- <説明>

## その他
- <refactor / chore 等>

---
コミット数: N件 | 変更ファイル数: M件
```

## ルール

- スコープ（`feat(auth): ...` の `auth`）があれば `**[auth]**` としてタグ付けする
- 関連するIssue番号があれば `#N` リンクを付与する（コミットメッセージから抽出）
- ファイル保存が必要な場合は `docs/releases/<新タグ>.md` に書き出す
- 出力は日本語
