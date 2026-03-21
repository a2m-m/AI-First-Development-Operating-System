---
name: project-setup
description: テンプレート複製後のプロジェクト初期セットアップを確認・修正する。初期化状態・資材の存在・公開物の整理・GitHub接続を順にチェックし、問題があれば自動修正する。
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# project-setup

テンプレートを複製して新しいプロジェクトを始める際の初回セットアップスキル。
**チェックして問題があれば自動修正する。あるべき姿に初期化することが目的。**

## 対象ディレクトリ

**スキルは現在の作業ディレクトリ（`pwd`）を対象として実行する。**
このスキルはテンプレートを複製した新プロジェクトのディレクトリで実行すること。

## 実行フロー

以下の順に実行する。**Bashコマンドは逐次実行**（並列実行しない）。

---

### Step 0: remote 切り離し（問答無用）

**このステップは条件なしに必ず実行する。**

1. `pwd` と `git remote -v` を確認してユーザーに現状を提示する
2. remote が存在する場合、**理由を問わず即座に切り離す**：
   ```bash
   git remote remove origin
   ```
3. remote が存在しない場合もそのまま次へ進む（スキップしない）

切り離し後、ユーザーに以下を一度に確認する：

```
remote を切り離しました。新しいプロジェクトの情報を教えてください:
1. プロジェクト名（project_config.yml の name に設定します）
2. チーム / オーナー名（project_config.yml の owner に設定します）
3. 新しい GitHub リポジトリ名（例: my-project）
4. 公開 / 非公開（public / private）
```

情報が揃ったら以降のフェーズを実行する。

---

### Phase 1: プレースホルダ置換

**目的:** `project_config.yml` のプレースホルダをプロジェクト固有情報に置換する。

チェック対象：
- `name: "YOUR_PROJECT_NAME"` → ユーザーが入力したプロジェクト名に置換
- `owner: "YOUR_TEAM_OR_OWNER"` → ユーザーが入力したオーナー名に置換
- `docker_image: "your-image:tag"` → 未置換なら **⚠️ 要確認** として報告（自動置換はしない）

置換後に `.ai-context.md` を確認し、テンプレ由来のTODOコメントのみで埋まっている場合は
以下のクリーンな初期状態に上書きする（`<!-- TODO:` で始まる全コメントをクリア）：

```markdown
# .ai-context.md

AIエージェントが作業開始時に現在の状態・進行中Issue・次の手を把握するためのコンテキストファイル。
**Project Instance では作業開始前に必ず読むこと。作業終了時に必ず更新すること。**

---

## 1. Status

works（初期セットアップ完了）

---

## 2. Active Issues

| Issue | 要点 | 担当 |
|---|---|---|

---

## 3. Decisions

| 日付 | 決定事項 | 理由 | 関連Issue |
|---|---|---|---|

---

## 4. Next actions

1. `/issue-create feature <最初の機能>` で最初の Issue を作成する

---

## 5. Known pitfalls

---

## 6. Commands

（`project_config.yml` の `commands.*` に従う）

---

## 7. CI Notes

| 典型原因 | 対処法 | 最終発生 |
|---|---|---|
```

---

### Phase 2: 資材チェック・修正

**目的:** 必要な資材を揃える。

以下を1件ずつ逐次確認し、欠損していれば対処する：

```bash
test -e .claude/skills/ && echo "exist" || echo "missing"
test -e .github/workflows/guardrail.yml && echo "exist" || echo "missing"
# ...（以下同様）
```

| 資材 | パス | 重要度 | 欠損時の対処 |
|---|---|---|---|
| スキル群 | `.claude/skills/` | 必須 | テンプレ元から `cp -r` を案内。パスが分かる場合は自動コピー |
| Guardrailワークフロー | `.github/workflows/guardrail.yml` | 必須 | 同上 |
| CIワークフロー | `.github/workflows/ci.yml` | 必須 | 同上 |
| LCGワークフロー | `.github/workflows/lcg.yml` | 必須 | 同上 |
| Secretsチェック | `.github/workflows/secrets.yml` | 必須 | 同上 |
| 依存スキャン | `.github/workflows/dependency-scan.yml` | 推奨 | 同上 |
| CI ランナー | `.github/scripts/run` | 必須 | 同上 |
| run スクリプト（ローカル） | `os_scripts/run` | 推奨 | 同上 |
| git hooks | `os_scripts/hooks/` | 推奨 | 同上 |
| Issueテンプレート | `.github/ISSUE_TEMPLATE/` | 必須 | 同上 |
| Claude設定 | `.claude/CLAUDE.md` | 必須 | 同上 |

**テンプレ元からのコピー方法（テンプレリポジトリのパスが判明している場合）:**
```bash
TMPL_DIR="<テンプレートリポジトリのパス>"
cp -r "$TMPL_DIR/.claude/skills" .claude/
cp "$TMPL_DIR/.github/workflows/guardrail.yml" .github/workflows/
# ... 必要なファイルを個別にコピー
```

テンプレートリポジトリのパスが不明な場合はユーザーに確認する。

---

### Phase 3: 公開物の修正

**公開・非公開で処理が異なる。Step 0 で取得した公開設定に従うこと。**

#### 3-1a. 公開リポジトリ（public）の場合：`local/full` ブランチ戦略

**原則: git では全ファイルを追跡する。GitHub に何を上げるかで公開・非公開を分ける。**

```
local/full  ← 全ファイルを追跡（GitHub には絶対に push しない）
main        ← 公開物のみ（GitHub に push する）
```

**手順:**

1. 現在のブランチを `local/full` として保存する：
   ```bash
   git checkout -b local/full
   git add -A
   git commit -m "chore: ローカル全ファイルのスナップショット" 2>/dev/null || true
   ```

2. `main` ブランチを作成し、公開物のみに絞る：
   ```bash
   git checkout -b main
   ```

3. `main` の `.gitignore` に以下を追記し、GitHub から除外するファイルを定義する：
   ```
   # OS Infrastructure（GitHub には上げない）
   .claude/
   os_scripts/
   os_docs/

   # 秘匿情報（public / private 問わず絶対に上げない）
   .env
   .env.*
   *.key
   *.pem
   credentials*
   *.local.*
   .claude/settings.local.json

   # ログ
   *.log
   ```

4. すでに tracked なファイルを `main` から除外する：
   ```bash
   git rm -r --cached .claude/ os_scripts/ os_docs/ 2>/dev/null || true
   ```

5. `.gitignore` の変更とセットでコミットする：
   ```bash
   git add .gitignore
   git add -u
   git commit -m "chore: 公開リポジトリ向け .gitignore 設定・OS インフラを untrack"
   ```

6. GitHub には `main` のみ push する（`local/full` は push しない）：
   ```bash
   git push -u origin main
   # ⚠️ local/full は絶対に push しないこと
   ```

**`local/full` ブランチの運用ルール:**
- OS インフラの変更（スキル更新・スクリプト修正等）は `local/full` にコミットする
- プロジェクトの公開コード変更は `main` と `local/full` の両方にコミットする
- `local/full` を誤って push しそうになった場合は即座に中断する

#### 3-1b. 非公開リポジトリ（private）の場合

**秘匿情報のみ除外し、それ以外は全てコミット・push してよい。**

`.gitignore` に以下を追記する：

```
# 秘匿情報（private でも絶対に上げない）
.env
.env.*
*.key
*.pem
credentials*
*.local.*
.claude/settings.local.json

# ログ
*.log
```

```bash
git add .gitignore
git commit -m "chore: 秘匿情報を .gitignore に追加"
git push -u origin main
```

#### 3-2. 秘匿ファイルの混入チェック

```bash
git ls-files | grep -E '(\.env$|\.env\.[^/]+$|credentials[^/]*$|private_key[^/]*$|\.pem$|\.key$)' || echo "none"
```

`.github/workflows/` 配下のファイルはワークフロー定義のため除外して判定する。
それ以外で検出されたファイルは **🚨 危険** として報告し、対処を案内する（自動削除はしない）。

#### 3-3. README・LICENSE の確認

- `README.md` がなければ最小限のテンプレを生成する
- `LICENSE` がなければライセンス種別をユーザーに確認し、生成する

---

### Phase 4: GitHub 接続

**目的:** Step 0 で切り離した remote を新プロジェクト用に接続する。

Step 0 で取得したリポジトリ名・公開設定を使い、以下を順に実行する：

1. `gh auth status` で認証状態を確認する（未認証なら `gh auth login` を案内して停止）

2. 新リポジトリを作成して接続する：
   ```bash
   gh repo create <新プロジェクト名> --public  # または --private
   git remote add origin <新リポジトリのURL>
   git push -u origin main
   ```

3. `git remote -v` で接続を確認する

---

## 出力フォーマット

```
## project-setup 完了レポート

### Phase 1: プレースホルダ置換
- project_config.yml: [✅ 置換済み | ⚠️ 一部未置換: <項目>]
- .ai-context.md: [✅ クリーン状態に初期化 | ✅ 既にクリーン]

### Phase 2: 資材
- スキル群: [✅ 存在 | ✅ コピー済み | ❌ 欠損（要手動対応）]
- ワークフロー: [✅ 全て存在 | ✅ コピー済み | ❌ 欠損: <ファイル名>]
- ...

### Phase 3: 公開物
- リポジトリ種別: [public | private]
- （public）local/full ブランチ: [✅ 作成済み | ❌ 未作成]
- （public）main の .gitignore: [✅ OS インフラ・秘匿情報を除外済み | ✅ 追記済み]
- （private）.gitignore: [✅ 秘匿情報を除外済み | ✅ 追記済み]
- 秘匿ファイル混入チェック: [✅ なし | 🚨 検出: <ファイル名>（要手動対応）]
- README: [✅ 存在 | ✅ 生成済み]
- LICENSE: [✅ 存在 | ✅ 生成済み | ⚠️ 未設定（ユーザー判断待ち）]

### Phase 4: GitHub接続
- remote: [✅ 新リポジトリに接続済み (<URL>) | ✅ 切り替え済み | ❌ 未設定]
- gh CLI: [✅ 認証済み | ❌ 未認証]
- push 済みブランチ: main のみ（local/full は push していない）

---

### 残タスク（自動修正できなかった項目）
1. ...

### 次のステップ
- 全て完了: `/issue-create feature <最初の機能>` で開発を開始する
```

## 修正の原則

- **自動修正してよいもの**: プレースホルダ置換、`.gitignore` への秘匿・OS インフラエントリ追記、`local/full` ブランチ作成（public の場合）、`git rm --cached`（public の `main` から OS インフラを除外）、`.ai-context.md` リセット、資材のコピー（テンプレパス判明時）、GitHub remote の切り替え
- **ユーザー確認が必要なもの**: 秘匿ファイルの削除・git履歴の書き換え、`docker_image` 等プロジェクト固有の設定値
- **実行前に確認すること**: `git remote remove` / `gh repo create` / `git push` など外部に影響する操作は実行前にユーザーに内容を提示し承認を得る
