---
name: project-setup
description: テンプレート複製後のプロジェクト初期セットアップを確認・案内する。初期化状態・資材の存在・公開物の整理・GitHub接続を順にチェックする。
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(gh *)
---

# project-setup

テンプレートを複製して新しいプロジェクトを始める際の初回セットアップスキル。
削除・上書きは行わず、**状態確認と案内**に徹する。

## 実行フロー

以下の4フェーズを順番に実行し、各フェーズの結果を報告する。

---

### Phase 1: 初期化チェック

**目的:** `scripts/init` が実行済みか、プロジェクト固有情報が設定されているかを確認する。

1. `os-template.yml` を読み、以下のプレースホルダが残っていないか確認する：
   - `name: "YOUR_PROJECT_NAME"` → 未置換なら **❌ 未初期化**
   - `owner: "YOUR_TEAM_OR_OWNER"` → 未置換なら **❌ 未初期化**
   - `docker_image: "your-image:tag"` → 未置換なら **⚠️ 要確認**

2. `.ai-context.md` を読み、テンプレ固有の不要情報が混入していないか確認する：
   - Active Issues テーブルが空（テンプレ由来のIssueが残っていない）
   - Known pitfalls にテンプレ用の内容が残っていない
   - Status が `works` または適切な初期状態になっている

**未初期化の場合の案内:**
```
./scripts/init を実行してプレースホルダを置換してください。
  ./scripts/init  （対話モード）
```

---

### Phase 2: 資材チェック

**目的:** 開発効率化・安定化の資材が新プロジェクトでも機能する状態にあるかを確認する。

以下のファイル・ディレクトリの存在を確認する：

| 資材 | パス | 重要度 |
|---|---|---|
| スキル群 | `.claude/skills/` | 必須 |
| Guardrailワークフロー | `.github/workflows/guardrail.yml` | 必須 |
| CIワークフロー | `.github/workflows/ci.yml` | 必須 |
| LCGワークフロー | `.github/workflows/lcg.yml` | 必須 |
| Secretsチェック | `.github/workflows/secrets.yml` | 必須 |
| 依存スキャン | `.github/workflows/dependency-scan.yml` | 推奨 |
| run スクリプト | `scripts/run` | 必須 |
| git hooks | `scripts/hooks/` | 推奨 |
| Issueテンプレート | `.github/ISSUE_TEMPLATE/` | 必須 |
| AIルール | `.ai-instructions.md` | 必須 |
| Claude設定 | `.claude/CLAUDE.md` | 必須 |

存在しないものは **❌ 欠損** として報告する。

---

### Phase 3: 公開物チェック

**目的:** リポジトリを公開・配布する際に、置くべきものと置かないものが整理されているかを確認する。

#### 3-1. .gitignore チェック

以下が `.gitignore` に含まれているか確認する：

```
# 必須エントリ
.env
.env.*
.claude/settings.local.json

# 推奨エントリ（言語により異なる）
*.pyc / __pycache__    # Python
node_modules/          # Node.js
*.log
```

不足しているエントリがあれば **⚠️ 要追加** として列挙する。

#### 3-2. 秘匿ファイルの混入チェック

以下のファイルがリポジトリに存在しかつ `.gitignore` に含まれていないものがないかを確認する：

```bash
git ls-files | grep -E '(\.env$|\.env\.|credentials|secret|private_key|\.pem$|\.key$)'
```

検出されたファイルは **🚨 危険: コミット済みの秘匿ファイルの可能性** として警告する。

#### 3-3. 配布物の確認

公開リポジトリに**置くべきもの**（存在を確認）：
- `README.md` — プロジェクト概要・セットアップ手順
- `LICENSE` — ライセンス明記（なければ ⚠️ 要追加を案内）
- `os-template.yml` — プロジェクト設定の唯一の入口

公開リポジトリに**置かないもの**（もし存在する場合は案内）：
- `docs/01_OS Overview.md` 等のテンプレOS設計ドキュメント → プロジェクト固有の `docs/` に置き換える
- テンプレ由来の `docs/vision.md` / `docs/architecture.md` のTODO状態 → 記入を促す

---

### Phase 4: GitHub接続チェック

**目的:** 元リポジトリの remote が残っていないか確認し、新プロジェクト用の接続状態に整理する。

1. `git remote -v` を実行して現在の remote を確認する

2. **remote が設定済みの場合（フォルダコピー由来の可能性がある）:**

   - URL が元のテンプレートリポジトリ（`AI-First-Development-Operating-System` 等）を指していないか確認する
   - 元リポジトリを向いている場合は **⚠️ 旧リポジトリへの接続が残っています** と警告し、以下を案内する：

   ```bash
   # 旧 remote を削除する
   git remote remove origin

   # 新しいリポジトリを作成して接続する場合
   gh repo create <新プロジェクト名> --public   # または --private
   git remote add origin <新リポジトリのURL>
   git push -u origin main

   # 既存の別リポジトリに接続する場合
   git remote add origin <接続先URL>
   git push -u origin main
   ```

3. **remote未設定の場合:**
   ```bash
   # 新しいリポジトリを作成して接続する場合
   gh repo create <新プロジェクト名> --public   # または --private
   git remote add origin <URL>
   git push -u origin main

   # 既存リポジトリに接続する場合
   git remote add origin <接続先URL>
   git push -u origin main
   ```

4. **remote が正しく設定済みの場合:**
   - `git log --oneline -3` で直近のコミット履歴を確認し、コピー元の履歴が混入していないか提示する（情報提示のみ。削除は行わない）

5. `gh auth status` を実行してgh CLIの認証状態を確認する

---

## 出力フォーマット

```
## project-setup チェック結果

### Phase 1: 初期化
- os-template.yml: [✅ 初期化済み | ❌ 未初期化]
- .ai-context.md: [✅ クリーン | ⚠️ 要確認: <内容>]

### Phase 2: 資材
- スキル群: [✅ 存在 | ❌ 欠損]
- ワークフロー: [✅ 全て存在 | ❌ 欠損: <ファイル名>]
- ...

### Phase 3: 公開物
- .gitignore: [✅ 適切 | ⚠️ 不足: <エントリ>]
- 秘匿ファイル: [✅ なし | 🚨 検出: <ファイル名>]
- README: [✅ 存在 | ❌ 欠損]
- LICENSE: [✅ 存在 | ⚠️ 未設定]

### Phase 4: GitHub接続
- remote: [✅ 新リポジトリに接続済み (<URL>) | ⚠️ 元リポジトリへの接続が残存 (<URL>) | ❌ 未設定]
- gh CLI: [✅ 認証済み | ❌ 未認証]

---

### 対応が必要な項目
1. ...（❌/🚨/⚠️ の項目のみ列挙し、対処手順を案内）

### 次のステップ
...（全てクリアな場合は最初のIssue作成を促す）
```

## ルール

- ファイルの削除・上書きは行わない（読み取り専用）
- 問題を検出した場合はコマンドを提示するが、実行はユーザーの判断に委ねる
- 全チェック通過後は `/issue-create feature <最初の機能>` で開発開始を促す
