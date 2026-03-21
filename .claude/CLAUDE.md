# Claude Code ルール

---

## ISSUE 作成ルール（最重要）

**ISSUE を作成する際は、必ず `.github/ISSUE_TEMPLATE/` のテンプレートを使うこと。**

- 新機能・改善 → `.github/ISSUE_TEMPLATE/feature.md` を使う
- バグ修正 → `.github/ISSUE_TEMPLATE/bug.md` を使う
- テンプレートの全セクションを埋める（空のまま残さない）
- `gh issue create` を使う場合は `--template` オプションでテンプレートを指定するか、テンプレートの内容を `--body` に反映する

### ISSUE は"命令書"として機能させる

ISSUE の品質が実装の成功率を決める（P2: Issue-Driven Development）。
以下が揃った ISSUE を作ること：

- **再現・方針・AC・Non-goals・Commit Plan** が明記されている
- Acceptance Criteria が Yes/No で判定できる形になっている
- Commit Plan で実装を 1〜3 コミットに分割している

---

## 言語ルール

**GitHub 上のすべての記述は日本語で統一すること。**

対象：
- コミットメッセージ（タイトル・本文ともに日本語。フォーマット等の規約は `docs/commit_strategy.md` に従うこと）
- Issue タイトル・本文
- PR タイトル・本文
- コードレビューコメント・Issue コメント

例外：
- コード・変数名・コマンド・固有名詞（ライブラリ名、ブランチ名など）はそのまま英語でよい
- ログ出力やエラーメッセージなど、実装上英語が必要な箇所は除く

---

## CRITICAL ルール（スキップ禁止）

- **セッション開始時に `context-sync` を実行すること**
- **実装後は必ず `/review` を実行してからコミットすること**（実装バイアスを排除し品質を守るため）
- **スコープ外の実装は絶対に行わないこと**
- **3回修正しても解消しない問題は Issue 化して停止すること**（無限ループを防ぎ失敗を教材として残すため）

---

## 作業開始チェックリスト

1. `context-sync` を実行し `.ai-context.md` の「次の手」セクションと open Issues を確認すること
2. アクティブ Issue の AC・Non-goals・Commit Plan を読むこと
3. Issue が `/issue-lint` チェック済みかを確認すること
4. 初回または CI 失敗後は `./os_scripts/run doctor` で環境を確認すること

---

## 責務

### Executor（実装）

- アクティブな Issue の AC を確認し、それに忠実な実装をすること
- Issue の Commit Plan に沿ってアトミックなコミットを作成すること
- スコープ外の変更を発見した場合:
  1. 変更を加えない
  2. `/issue-create feature <内容>` で別 Issue を起票する
  3. 現在の Issue の作業に戻る
- ユーザーにターミナル操作を求めず、テスト・lint・ビルド等含めすべて自分で直接実行すること（ユーザーブロッキングを防ぐため）
- Git 操作（ブランチ作成・コミット・push）も自分で実施すること
- 反復作業はスキル化を検討すること（同じ手順を3回以上繰り返したら `/skill-create` でスキル化する）
- コミット規約: `docs/commit_strategy.md` 参照

### QA/Architect（レビュー・ゲート）

- **実装後は必ず `/review` を実行してからコミットすること**（自己レビュースキップ禁止）
- **Pre-push**: `/gate` を実行すること
- **Post-push**: `gh run watch` で CI 結果を確認し、失敗時は `/ci-failure-triage` を実行すること
- PR 作成前に `/review` で自己レビューを実施すること

### テスト・lint 自律修正ループ

- 失敗時は原因を特定し、修正→再実行を繰り返すこと
- **3 回修正しても解消しない場合は Issue 化してユーザーに報告し、作業を止めること**（無限ループを防ぎ失敗を教材として残すため）

---

## 実装ルール

- **Template のコントラクトを壊さない**：ワークフロー・スクリプト本体を勝手に改造しない
- **Issue の AC を満たす実装をする**：スコープを逸脱しない
- **設定は `project_config.yml` に寄せる**：言語・ツール固有の差分はここで吸収する
- **勝手に巨大改修をしない**：Issue に書かれていないことは実装しない
- **Skills は Template 還元が原則**：Instance で Template のスキルを改造しない

---

## PR ルール

- **小さく分けて PR**：1PR = 1 Issue を原則とする
- **PR は Issue に紐づける**：`Closes #<issue番号>` を本文に記載する
- **Template のコントラクトを壊さない**

---

## コンテキスト管理

- **作業開始前**：`.ai-context.md` を読んで現在の状態・次の手を把握する
- **作業終了後**：`.ai-context.md` を更新し、次のセッションが迷子にならない状態にする
- **OS Template Repo では雛形を維持**：このリポジトリ自体が Template Repo の場合、`.ai-context.md` に個別案件の Issue / PR 状態を書き込まない
- **決定事項**：仕様・方針の決定は Issue へ記録する
- **CI 失敗・テスト失敗**：原因を Issue に残し、教材として活用する（消さない）

---

## 設計原則

### SRP（単一責任原則）

- 1 関数 / クラス / モジュールの責務が膨らんでいると感じたら分割を検討すること（ただし過分割は避ける）
- 1 スキル = 1 責務を目安とし、複数の目的を詰め込まないこと
- **1 PR = 1 Issue**：複数の変更を一度に混ぜないこと
- 既存コードの責務境界を壊す変更を発見した場合は、別 Issue として起票すること

### コンテキスト肥大化の防止

- **必要なファイルだけを読む**：関係のないファイルを広範囲に読み込まないこと
- 並列探索・大量ファイル調査など isolated context が必要な場合のみサブエージェントを使うこと（過剰委譲しない）
- セッションが長くなった場合はユーザーに `/compact` の実行を依頼すること
- 1 セッション = 1 Issue を原則とし、複数 Issue を並走させないこと

---

## 自己レビューサイクル

**実装後は以下の手順を必ず踏むこと（スキップ禁止）：**

1. Issue AC を確認 → **実装前にタスク種別に応じた検証方法を決める**（Executor モード）
   - バグ修正 → 再現テストを先に書いてから修正する
   - 仕様実装 → AC の期待出力・期待動作を先に確認する
   - リファクタ → 既存テストがグリーンのまま終わることを確認手段とする
2. 実装（Executor モード）
3. `/review [Issue番号 または PR番号]` を実行（QA/Architect モード）— **必須ステップ**
4. BLOCKER/HIGH 指摘があれば修正（`/review` 出力の Severity 区分）
5. `/gate`（`./os_scripts/run ci`）
6. コミット・プッシュ・PR 作成

---

## 完了の定義

- [ ] `/review` 実行済み・BLOCKER/HIGH 指摘なし
- [ ] `/gate` PASS
- [ ] PR に `Closes #<issue番号>` 記載
- [ ] `/pr-complete <PR番号>` で `.ai-context.md` 更新済み

---

## エスカレーション基準

以下の場合は作業を止め、ユーザーに報告すること：

1. 3 回修正しても解消しない問題 → Issue 化して停止 **(ESCALATE)**
2. Issue の AC が矛盾・不明確 → Issue にコメントして確認依頼し停止 **(ESCALATE)**
3. 破壊的操作（`--force`、`reset --hard` 等）が必要に見える → 実行せずユーザー確認 **(CONFIRM)**

---

## 禁止事項

- ISSUE テンプレートを使わずに Issue を作ること
- 日本語以外の言語でコミットメッセージ・Issue・PR を書くこと
- Template のワークフロー・スクリプト本体を改造すること
- `project_config.yml` 以外の場所に設定を散在させること
- Issue に書かれていないスコープの実装を勝手に行うこと
- `.ai-context.md` を更新せずに作業を終了すること

---

## ルールファイルの更新基準

ユーザーからルールの追加・修正を求められた場合、このファイル（`.claude/CLAUDE.md`）を編集すること。

---

## GitHub 公開方針

**git ではすべてのファイルを追跡することを原則とする。**
GitHub（リモート）に何を上げるかはリポジトリの公開設定によって変わる。

### 公開リポジトリ（public）

**GitHub に上げてよいもの（限定列挙）:**
- `.github/`（ワークフロー・テンプレート）
- プロジェクト固有のソースコード・ドキュメント
- `project_config.yml`

**必ず GitHub から除外するもの:**
- OS インフラ: `.claude/`, `os_scripts/`, `os_docs/`
- 秘匿情報: `.env`, `*.env.*`, `*.key`, `*.pem`, credentials 系ファイル
- ローカル設定: `*.local.*`, `settings.local.json`
- ログ: `*.log`

**ローカル全追跡ブランチの運用:**

```
local/full  ← 全ファイルを追跡（GitHub には絶対に push しない）
main        ← 公開物のみ（GitHub に push する）
```

- `local/full` ブランチは **絶対に GitHub に push しない**
- OS インフラの変更は `local/full` にコミットする
- プロジェクトの公開コード変更は `main` と `local/full` の両方にコミットする

### 非公開リポジトリ（private）

秘匿情報を除いて基本的に全てコミット・push してよい。

**必ず除外するもの（private でも絶対に上げない）:**
- `.env`, `*.env.*`（環境変数・APIキー）
- `*.key`, `*.pem`（秘密鍵）
- credentials 系ファイル

### 共通ルール（公開・非公開問わず）

- 開発中に新しいファイルが生まれたら、`git add` する前に公開・非公開を確認する
- `.gitignore` はリポジトリ共通の除外設定（GitHub に上げる）
- ローカルのみの除外ルールは `.git/info/exclude` を使う

---

## Skills

以下のスキルは `/スキル名` で起動する。Claude 専用のものはユーザーが呼ばない。

| コマンド | 用途 | 引数例 | 起動者 |
|---|---|---|---|
| `/plan` | Issue AC 確認 → コード探索 → 実装計画立案 | — | Claude（自動） |
| `/issue-create` | テンプレ準拠の命令書 Issue を作成 | `feature <タイトル>` | ユーザー |
| `/issue-lint` | Issue の品質チェック（AC・Commit Plan・空セクション） | `[Issue番号]` | ユーザー |
| `/review` | Issue AC に基づく PR / 成果物レビュー | `[Issue番号 または PR番号]` | ユーザー / Claude（自己レビュー） |
| `/gate` | Pre-Push Gate 実行 + 結果解釈 | — | ユーザー / Claude（自動） |
| `/commit-lint` | コミットメッセージ規約チェック | — | ユーザー |
| `/pr-complete` | PR マージ後に `.ai-context.md` を更新 | `<PR番号>` | ユーザー |
| `/ci-failure-triage` | CI 失敗を解析して Bug Issue を自動作成 | — | ユーザー |
| `/release-notes` | タグ間の変更からリリースノートを生成 | — | ユーザー |
| `/skill-create` | 反復作業を新しいスキルとして定義 | `<名前> <理由>` | ユーザー |
| `/project-setup` | テンプレ複製後の初期セットアップ確認（初期化・資材・公開物・GitHub接続） | — | ユーザー |
| `/istart` | 次に着手すべき Issue を自動判断してブランチ作成・計画立案まで一気通貫で実行 | — | ユーザー |
| `context-sync` | `.ai-context.md` を読んで状態同期 | — | **Claude 専用（セッション開始時に自動実行）** |

---

## 参照ドキュメント

| ドキュメント | 用途 |
|---|---|
| `01_OS Overview.md` | OS の思想・原則・全体像（地図） |
| `02_OS_Template_Spec.md` | Template Repo の仕様（設計図） |
| `03_Project_Instance_Guide.md` | Instance の立ち上げ手順（手順書） |
| `docs/commit_strategy.md` | コミットメッセージ規約と巨大 diff 警告の仕様 |
| `.github/ISSUE_TEMPLATE/feature.md` | 新機能・改善 ISSUE のテンプレート |
| `.github/ISSUE_TEMPLATE/bug.md` | バグ修正 ISSUE のテンプレート |
| `.ai-context.md` | 現在の状態・進行中 Issue・次の手 |

---

## 環境前提

以下が利用可能であることを前提とする：

- `./os_scripts/run`（lint / test / ci / doctor）
- `gh` CLI（認証済み）
- `git`
- Python 3
