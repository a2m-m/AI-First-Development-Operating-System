# **02\_OS\_Template\_Spec**

## **0\. 目的 / スコープ**

### **0.1 目的**

本書は、**OS Template Repo**（以後 Template）を **一度作って育て**、各プロジェクトはそれを **複製（＝Instance化）して使い回す**ための仕様書である。

* Templateは “運用を始められる最小の仕組み” を **言語非依存**で提供する。  
* Instance（プロジェクト側）は Template を複製したのち、**プロジェクト固有の差分（言語/コマンド/環境）だけを設定**して稼働させる。

### **0.2 スコープ**

本書が定義するもの：

* Template Repo に含める **ファイル/ディレクトリ**、**テンプレ本文**、**CI/ガードレール**、**init手順**、**運用規約**  
* Template → Instance 化の **コントラクト（不変/可変の境界）**  
* **受け入れ基準（Acceptance Criteria）**

本書が定義しないもの（ただし拡張は許可）：

* 特定言語の標準ツール（例：pytest, eslint, go test）の選定  
* アプリのアーキテクチャそのもの

---

## **1\. 用語定義**

* **Template Repo（Template）**：GitHub Template として作る「OSの型」。一度作って継続的に改善する。  
* **Instance Repo（Instance）**：Templateから複製され、特定プロジェクトとして動くリポジトリ。  
* **Invariant（不変）**：Templateで固定し、Instanceで原則変更しないもの。  
* **Variant（可変）**：Instanceで埋める差分。主に言語・コマンド・CI実行環境など。  
* **Contract（コントラクト）**：Templateが提供し、Instanceが満たすべき約束事（設定・実行口・結果形式）。

---

## **2\. 基本思想（OSの原則）**

Templateは「良い行動をお願いする」のではなく、**良い行動が自然に起きる導線**として実装する。

* **Context-as-Code**：重要な背景/判断/状態は repo に残す（口頭やチャットを前提にしない）  
* **Issue-Driven**：Issueは命令書。成功率はIssue品質で決まる  
* **Gates**：pre-push / CI などの関門で品質を自動担保する  
* **Guardrail teaches humans**：仕組みのガードが学習を生む  
* **Small, sharp feedback**：フィードバックは最大3点、優先度つき、次の一手が明確

---

## **3\. Template vs Instance の境界（最重要）**

### **3.1 Template の Invariants（不変）**

Templateに必ず含め、Instanceでも構造として維持する：

* リポジトリ構造（`docs/`, `.github/`, `scripts/` など）  
* Issue/PRテンプレのフォーマット  
* 「言語差分を閉じ込める」ための設定ファイルと実行口（後述の Contract）  
* CIワークフローの骨格（実行口を叩くだけにする）  
* secrets検知などのセキュリティ基盤  
* `.ai-context.md` / `.ai-instructions.md` のフォーマット

### **3.2 Instance の Variants（可変）**

Instanceで埋める・変更してよいものは **これだけ**に絞る：

* プロジェクト識別情報（名前/owner/リポ説明）  
* コマンド定義（lint/test/typecheck/format/build 等）  
* CI実行モード（docker / host）とセットアップ  
* 追加の言語/フレームワーク固有ファイル（例：package.json, pyproject.toml）  
* 任意機能のON/OFF（guardrail, lcg 等）

原則：**Templateのワークフローやスクリプト本体をプロジェクトごとに改造しない。**  
変更したい時は Template 側へ改善提案し、テンプレ進化として取り込む。

---

## **4\. 言語まちまち前提の設計（Contract）**

言語/ツールが混在しても Template を固定化するため、Templateは以下のコントラクトを提供する。

### **4.1 `os-template.yml`（Instance設定の唯一の入口）**

* Instanceはこの設定ファイルに **差分だけ**を記載する。  
* CIとローカル実行は **このファイルの commands を叩く**ことで統一される。

#### **4.1.1 スキーマ（必須キー）**

schema\_version: "1"

project:  
  name: "YOUR\_PROJECT\_NAME"  
  owner: "YOUR\_TEAM\_OR\_OWNER"  
  description: "..."

runtime:  
  mode: "docker"          \# "docker" | "host"  
  docker\_image: ""        \# mode=docker の場合必須  
  host\_setup\_steps: \[\]    \# mode=host の場合推奨（例: \["python \-m venv .venv", "..."\])

commands:  
  format: ""      \# optional  
  lint: ""        \# required (can be "echo 'skip'" でも可だが理由必須)  
  typecheck: ""   \# optional/requiredはプロジェクト事情。未使用なら空でOK  
  test: ""        \# required (最初は smoke でもよい)  
  build: ""       \# optional  
  ci: ""          \# optional: 明示したい場合。空なら run が lint/typecheck/test を順に実行

features:  
  secret\_scan: true  
  dependency\_scan: true  
  guardrail: true  
  lcg: false

policy:  
  allow\_skip\_typecheck: true   \# true の場合、空でもOK（READMEに理由を記載）  
  max\_diff\_warning: 1200       \# 行数目安（警告のみ）  
  max\_file\_warning: 30         \# ファイル数目安（警告のみ）

#### **4.1.2 運用ルール**

* Instanceはまず `commands.lint` と `commands.test` を必ず埋める（空は禁止）  
* typecheck がない言語は空でOK。その代わり `.ai-context.md` に「typecheck無しの理由」を書く  
* `runtime.mode=docker` を推奨（言語差分吸収が最も安定）

---

### **4.2 `scripts/run`（唯一の実行口）**

人もCIも **これだけ叩けばよい**を実現する。

#### **4.2.1 サブコマンド**

* `scripts/run format`  
* `scripts/run lint`  
* `scripts/run typecheck`  
* `scripts/run test`  
* `scripts/run build`  
* `scripts/run ci`（標準：lint → typecheck（あれば）→ test）  
* `scripts/run doctor`（設定不足/環境不足を診断）  
* `scripts/run print-config`（最終的に解釈された設定を表示）

#### **4.2.2 期待される振る舞い（重要）**

* `os-template.yml` がない/壊れている場合：**何が不足かを表示して非0終了**  
* command が空の場合：`doctor` で不足一覧表示、CIでは失敗扱い  
* `runtime.mode=docker` の場合：  
  * `docker run` でコマンドを実行（マウント・workdir は標準化）  
* `runtime.mode=host` の場合：  
  * `host_setup_steps` を表示（または実行オプションを提供）  
* 出力は短く：CIログで読めることを最優先

実装言語はTemplate側で固定してよい（bash/python/nodeなど）。  
ただし「Templateの実行にそれが必要」という矛盾が出ないよう、可能なら **bash \+ yq など軽量**、または **python単体**で完結させる。

---

### **4.3 `scripts/init`（Instance化の儀式）**

Template複製後、最初に叩く。

#### **4.3.1 目的**

* “OSが動き始める最低限”を最短で整える  
* 変更点は **設定ファイルとプレースホルダ置換**に限定する

#### **4.3.2 入力（推奨）**

* 対話形式 or 引数  
  * `--project-name`  
  * `--owner`  
  * `--description`  
  * `--runtime-mode (docker|host)`  
  * `--docker-image`（dockerの場合）

#### **4.3.3 出力（必須）**

* `os-template.yml` を生成/更新  
* READMEのプレースホルダ置換（プロジェクト名など）  
* `.ai-context.md` の Commands セクションを初期化（未設定なら TODO 明示）  
* “最初のPRでCIを通す最短手順”を表示（コピーして実行できる形）

#### **4.3.4 失敗時**

* 必ず「不足項目」と「次の1手」を箇条書きで表示して非0終了

---

## **5\. Repo Manifest（Templateが提供する全生成物）**

MUST \= 必須 / SHOULD \= 推奨（ただし可能なら入れる）

### **5.1 ルート**

* MUST `README.md`  
* MUST `.ai-instructions.md`  
* MUST `.ai-context.md`  
* MUST `os-template.yml`（テンプレに“例＋TODO”で同梱）  
* MUST `scripts/`  
* MUST `.github/`  
* MUST `docs/`  
* SHOULD `CHANGELOG.md`  
* SHOULD `LICENSE`

### **5.2 `docs/`**

* MUST `docs/vision.md`  
* MUST `docs/architecture.md`  
* MUST `docs/decisions/README.md`（ADR運用ルール）  
* SHOULD `docs/decisions/0001-template-contract.md`（コントラクトの初期ADR）  
* SHOULD `docs/learning/README.md`  
* SHOULD `docs/learning/commits/.gitkeep`（LCG資産化用）

### **5.3 `.github/`**

* MUST `.github/PULL_REQUEST_TEMPLATE.md`  
* MUST `.github/ISSUE_TEMPLATE/feature.md`  
* MUST `.github/ISSUE_TEMPLATE/bug.md`  
* MUST `.github/workflows/ci.yml`  
* MUST `.github/workflows/secrets.yml`  
* SHOULD `.github/workflows/dependency-scan.yml`  
* SHOULD `.github/workflows/guardrail.yml`  
* SHOULD `.github/workflows/lcg.yml`  
* SHOULD `.github/CODEOWNERS`

### **5.4 `scripts/`**

* MUST `scripts/run`  
* MUST `scripts/init`  
* SHOULD `scripts/hooks/pre-push`（導入しやすい場合）  
* SHOULD `scripts/lib/`（共通関数）

### **5.5 `.claude/`**

* MUST `.claude/CLAUDE.md`（Claude Code 固有ルール）  
* SHOULD `.claude/skills/`（反復作業のモジュール化）  
* SHOULD `.claude/skills/<name>/SKILL.md`（各スキルの定義）

---

## **6\. 各ファイル仕様（テンプレ本文レベルで固定）**

### **6.1 `README.md`（必須構成）**

最低限この章立てを固定する：

1. このリポは何か（OS Template / Instance）  
2. Quickstart（複製→init→最初のPR）  
3. Contract（`os-template.yml` / `scripts/run`）  
4. Day-1 flow（Issue→PR→CI→merge）  
5. Troubleshooting（doctor、よくある詰まり）  
6. OSの運用（DoD、Maintenance）

Quickstart例（テンプレに入れる）：

\# 1\) Templateからリポを作成（GitHub UI）  
\# 2\) clone  
\# 3\) init  
./scripts/init \--project-name YOUR\_PROJECT \--owner YOUR\_TEAM \--runtime-mode docker \--docker-image your-image:tag

\# 4\) 設定確認  
./scripts/run doctor  
./scripts/run ci

### **6.2 `.ai-instructions.md`（必須）**

* AIにやらせる時の規約（出力先、変更方針、禁止事項）  
* 「Templateのコントラクトを壊さない」ことを明記  
* 生成物は “小さく分けてPR” を推奨  
* 例：IssueのACを満たす／勝手に巨大改修しない／設定は `os-template.yml` に寄せる

### **6.3 `.ai-context.md`（必須：固定フォーマット）**

テンプレとして **枠を完全固定**する（Instanceで埋める）。

推奨フォーマット：

* Status（works/broken）  
* Active Issues（リンク/要点）  
* Decisions（なぜそうした）  
* Next actions（優先度順）  
* Known pitfalls（罠）  
* Commands（format/lint/typecheck/test/build）  
* CI Notes（落ちた時の典型原因）

### **6.4 Issue テンプレ（命令書）**

#### **6.4.1 feature.md**

* Background / Why  
* Scope / Out of Scope  
* Approach（方針）  
* Acceptance Criteria（Yes/No）  
* Risks / Rollback  
* Test plan  
* Commit Plan（Commit 1/2/3 まで）

#### **6.4.2 bug.md**

* Repro steps  
* Expected / Actual  
* Root cause hypothesis（仮）  
* Fix approach  
* AC  
* Test plan  
* Commit plan

### **6.5 PR テンプレ**

* What / Why（Issueリンク）  
* How to test（`scripts/run ...` を書く）  
* Risk / Rollback  
* Screenshots / Logs（任意）  
* “今回やらないこと”（未来のIssueへ）

---

## **7\. CI / Workflows 仕様（言語非依存）**

### **7.1 `ci.yml`（必須）**

* PR と main push で起動  
* やることは固定：  
  1. checkout  
  2. `./scripts/run doctor`  
  3. `./scripts/run ci`

これでCIは言語を知らずに済む。言語差分は `os-template.yml` へ。

### **7.2 `secrets.yml`（必須）**

* PRで必ず起動  
* 見つけたら fail（または最初は warn モードも可。ただし最終的には fail 推奨）  
* 結果はPRで見える

### **7.3 dependency scan（推奨）**

* 可能ならGitHub標準（Dependabot等）や軽量スキャンを使う  
* 言語依存が強い場合は “枠だけ”を用意し、`os-template.yml.features.dependency_scan` でON/OFF

### **7.4 guardrail / lcg（推奨）**

* 導入は段階的（最初はコメントのみ、BLOCKER/HIGHのみブロック）  
* 同じ指摘が続いたら「人を責めずにテンプレを改善」

---

### **7.5 Skills（AI行動のモジュール化）**

Iteration Cycle（①〜⑥）で反復する作業を **Claude Code Skills** としてモジュール化する。

* スキルは `.claude/skills/<name>/SKILL.md` に配置する  
* Template に含むスキル（不変）と、Instance で追加するスキル（可変）を区別する  
* Template のスキルを Instance で改造しない（改善は Template へ還元）  
* **スキル化の判断基準**：同じ作業を3回やったらスキル化を検討する  
* 新しいスキルの作成は `/skill-create` スキルで行う

---

## **8\. Guardrail コメント規格（推奨）**

PRにコメントする場合は統一フォーマット：

* Severity: BLOCKER / HIGH / MEDIUM / LOW / NIT  
* Finding: 何が問題か  
* Why: なぜ問題か（比喩OK）  
* Fix direction: 直し方の方向性  
* Example: 最小例（長文禁止）  
* Learn more: 参考（任意）

原則：

* BLOCKER/HIGH だけブロック、それ以外は学習用コメント

---

## **9\. LCG（Learning by Commit Guide）仕様（推奨）**

目的：diffを教材に変換して、継続的にチームの筋肉を増やす。

出力（最大3問まで）：

* Summary（短く）  
* Deep dive（最大N項目）  
* Quiz（最大3）  
* Explore next（次に見るべき観点）

保存先：

* 軽量：PRコメントだけ  
* 資産化：`docs/learning/commits/<hash>.md`

---

## **10\. 運用（Definition of Done / Maintenance）**

### **10.1 DoD（最小）**

* CIが緑  
* ACを満たす  
* テスト追加 or 追加できない合理的理由がPRにある  
* Risk/Rollbackが書かれている

### **10.2 Maintenance（推奨：週次30分でもOK）**

* CI落ち原因トップを潰す  
* Guardrailで同じ指摘が続くなら Template 側を改善  
* Template自体のChangelog更新

---

## **11\. 受け入れ基準（Acceptance Criteria）**

Template Repo 完成の判定は、以下を満たすこと。

### **11.1 Template レベル（Template単体）**

* 本書の Repo Manifest の MUST が全て存在する  
* `os-template.yml` がテンプレとして同梱されている（例＋TODOでも良い）  
* `scripts/run doctor` が「不足項目」を一覧で出せる  
* `scripts/run ci` が（設定が埋まれば） lint/test を実行できる  
* GitHub Actions がPRで起動し、`./scripts/run doctor` と `./scripts/run ci` を走らせる  
* secretsスキャンのworkflowがPRで起動する  
* `.ai-context.md` が固定フォーマットで存在する  
* Issue/PRテンプレが存在し、Commit Plan 欄がある

### **11.2 Instance レベル（複製して動かせる）**

* `scripts/init` で `os-template.yml` が埋まり、Quickstart通りに `scripts/run ci` が実行できる  
* 未設定がある場合でも `doctor` が次の一手を提示する（“何をどこに書くか”まで）  
* 最初のPRでCIが動く（成功/失敗どちらでも理由が明確）

---

## **12\. Template の進化ルール（超重要）**

* Instance側でテンプレ構造を変えるのは例外扱い（原則禁止）  
* 変更が必要なら Template にIssueを切り、Template側で直して次回から全員が得する形にする  
* Templateは「壊れにくさ」を最優先し、段階導入（warn→block）を許容する

---

## **13\. 付録：テンプレに埋めるプレースホルダ一覧**

* `YOUR_PROJECT_NAME`  
* `YOUR_TEAM_OR_OWNER`  
* `your-image:tag`（dockerの場合）  
* `commands.*` の TODO