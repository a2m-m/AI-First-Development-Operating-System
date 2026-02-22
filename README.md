# AI-First Development Operating System

> **YOUR_PROJECT_NAME** — YOUR_TEAM_OR_OWNER

## 1. このリポジトリは何か

本リポジトリは **AI-First Development Operating System**（以下 OS）である。

OS は AI（Claude Code / Antigravity）× GitHub を前提に、速度と安全性を両立しながら学習も自然に生まれる**開発エコシステム**を提供する。以下の **Docs（ガイド）** と **Artifacts（実体）** で構成される。

### Docs（読むもの）

| ドキュメント | 役割 |
|-------------|------|
| `01_OS Overview.md` | OS の思想・原則・フェーズ設計・全体像（**地図**） |
| `02_OS_Template_Spec.md` | Template Repo の構成・コントラクト・CI の仕様（**設計図**） |
| `03_Project_Instance_Guide.md` | Instance 立ち上げの実践ガイド — Interview Mode・Phase 0 到達手順（**攻略本**） |

### Artifacts（動くもの）

| 実体 | 説明 |
|------|------|
| **OS Template Repo（本リポ）** | プロジェクトの起点となる「OS の型」。Docs + CI + Issue/PR テンプレ + スクリプト等を含む |
| **Project Instance** | Template を複製し、プロジェクト固有の差分だけを設定して稼働させる実体 |

```
本リポ（OS Template）
  ├─ 01/02/03 Docs        … OS の思想・仕様・手順
  ├─ scripts/            … 実行口（run / init）
  ├─ .github/            … CI / Issue・PR テンプレート
  ├─ .claude/skills/     … Claude Code Skills（反復作業のモジュール化）
  ├─ docs/               … プロジェクト固有ドキュメントの雛形
  ├─ os-template.yml     … 差分設定の唯一の入口
  └─ .ai-*               … AI エージェント向けコンテキスト
        │
        └─ 複製 → Project Instance（各プロジェクト）
                    差分（言語・コマンド・環境）だけを設定して稼働
```

### Template と Instance の境界

| 区分 | 説明 |
|------|------|
| **Template（不変）** | リポ構造、Issue/PR テンプレ、CI ワークフロー骨格、`scripts/` の実行口、`.ai-context.md` のフォーマット |
| **Instance（可変）** | プロジェクト名・owner、コマンド定義（lint/test 等）、CI 実行モード（docker/host）、言語固有ファイル |

> **原則**：Template のワークフローやスクリプト本体をプロジェクトごとに改造しない。変更したい場合は Template 側へ Issue を切り、テンプレ進化として取り込む。

---

## 2. Quickstart

Template から新しいプロジェクトを始める手順。

### 2.1 リポジトリを作成

1. GitHub で本リポの **"Use this template"** → **"Create a new repository"** をクリック
2. リポジトリ名・可視性を設定して作成
3. ローカルに clone する

```bash
git clone https://github.com/YOUR_TEAM_OR_OWNER/YOUR_PROJECT_NAME.git
cd YOUR_PROJECT_NAME
```

### 2.2 初期化

```bash
# Instance の初期化（プレースホルダ置換・os-template.yml 生成）
./scripts/init \
  --project-name YOUR_PROJECT_NAME \
  --owner YOUR_TEAM_OR_OWNER \
  --description "プロジェクトの説明" \
  --runtime-mode docker \
  --docker-image your-image:tag
```

### 2.3 設定確認

```bash
# 環境・設定の診断
./scripts/run doctor

# CI と同等のチェックをローカルで実行
./scripts/run ci
```

### 2.4 最初の PR を作成

```bash
git checkout -b setup/init
git add -A
git commit -m "初期セットアップ: scripts/init による Instance 初期化"
git push origin setup/init
```

GitHub で PR を作成し、CI が通ることを確認して merge する。

---

## 3. Contract

Template が提供し、Instance が満たすべき約束事（コントラクト）。

### 3.1 `os-template.yml` — 設定の唯一の入口

Instance はこのファイルに**差分だけ**を記載する。CI とローカル実行はこのファイルの `commands` を参照して統一される。

```yaml
schema_version: "1"

project:
  name: "YOUR_PROJECT_NAME"
  owner: "YOUR_TEAM_OR_OWNER"
  description: "プロジェクトの説明"

runtime:
  mode: "docker"            # "docker" | "host"
  docker_image: ""          # mode=docker の場合必須
  host_setup_steps: []      # mode=host の場合推奨（例: ["python -m venv .venv", "..."]）

commands:
  format: ""                # 任意
  lint: ""                  # 必須（空は禁止）
  typecheck: ""             # 任意（無い場合は理由を .ai-context.md に記載）
  test: ""                  # 必須（空は禁止）
  build: ""                 # 任意
  ci: ""                    # 任意（空なら lint → typecheck → test を順に実行）

features:
  secret_scan: true
  dependency_scan: true
  guardrail: true
  lcg: false                # Learning Content Generator（コミット教材化）

policy:
  allow_skip_typecheck: true  # true の場合、typecheck 空でも OK（.ai-context.md に理由を記載）
  max_diff_warning: 1200      # 行数目安（警告のみ）
  max_file_warning: 30        # ファイル数目安（警告のみ）
```

> **運用ルール**：`commands.lint` と `commands.test` は必ず埋める。`typecheck` が無い言語は空で OK（理由を `.ai-context.md` に記載）。`runtime.mode=docker` を推奨。

### 3.2 `scripts/run` — 唯一の実行口

人も CI も `scripts/run` だけ叩けばよい。

| サブコマンド | 説明 |
|-------------|------|
| `./scripts/run format` | コードフォーマット |
| `./scripts/run lint` | リンター実行 |
| `./scripts/run typecheck` | 型チェック |
| `./scripts/run test` | テスト実行 |
| `./scripts/run build` | ビルド |
| `./scripts/run ci` | 標準 CI（lint → typecheck → test） |
| `./scripts/run doctor` | 設定不足・環境不足の診断 |
| `./scripts/run print-config` | 最終的に解釈された設定を表示 |

---

## 4. Day-1 Flow

プロジェクト運用開始後の標準的な開発サイクル。

```
① Issue作成 → ② 実装 → ③ Pre-Push Gate → ④ PR・CI・レビュー → ⑤ Merge
     ↑                                                              |
     └──────────── 改善・次の Issue ←────────────────────────────────┘
```

### 4.1 Issue を作成する（命令書）

- 新機能・改善 → `.github/ISSUE_TEMPLATE/feature.md` を使用
- バグ修正 → `.github/ISSUE_TEMPLATE/bug.md` を使用
- **必須項目**：Background / Scope / AC（Yes/No 判定可能） / Commit Plan

### 4.2 実装する

- Issue の AC と Commit Plan に従って実装
- コミットは小さく分ける（1 Issue = 1〜3 コミット）

### 4.3 Pre-Push Gate

```bash
./scripts/run ci   # lint / typecheck / test を実行
```

### 4.4 PR を作成し、レビュー・CI を通す

- PR テンプレ（`.github/PULL_REQUEST_TEMPLATE.md`）に従って記載
- **必須項目**：What / Why（Issue リンク） / How to test / Risk / Rollback
- CI（GitHub Actions）が `./scripts/run doctor` → `./scripts/run ci` を自動実行

### 4.5 Merge

- CI が緑、AC を満たす、テスト追加済み（または合理的理由あり）で merge

---

## 5. Troubleshooting

### 5.1 `scripts/run doctor` を使う

環境や設定に問題がある場合、`doctor` が不足項目と次の一手を表示する。

```bash
./scripts/run doctor
```

**出力例**：
```
[FAIL] os-template.yml が見つかりません
  → ./scripts/init を実行してください

[FAIL] commands.lint が未設定です
  → os-template.yml の commands.lint にリンターコマンドを設定してください

[FAIL] commands.test が未設定です
  → os-template.yml の commands.test にテストコマンドを設定してください

[OK] runtime.mode = docker
[OK] features.secret_scan = true
```

### 5.2 よくある詰まりポイント

| 症状 | 原因 | 対処 |
|------|------|------|
| CI が動かない | `os-template.yml` が未生成 | `./scripts/init` を実行する |
| `lint` / `test` が失敗する | コマンドが未設定 or 空 | `os-template.yml` の `commands` を埋める |
| docker 関連のエラー | `docker_image` が未指定 | `runtime.docker_image` にイメージを指定する |
| `typecheck` でエラー | 言語が型チェック未対応 | `commands.typecheck` を空にし、`.ai-context.md` に理由を記載 |
| 巨大 PR の警告 | `policy.max_diff_warning` 超過 | PR を分割する（1 PR = 1 Issue を徹底） |

---

## 6. OS の運用

### 6.1 Definition of Done（DoD）— PR の完了条件

PR を merge する最低条件：

- [ ] CI が緑（`scripts/run ci` が成功）
- [ ] Acceptance Criteria を満たしている
- [ ] テストが追加されている（または追加できない合理的理由が PR にある）
- [ ] Risk / Rollback が記載されている

### 6.2 Maintenance ポリシー（推奨：週次 30 分）

- CI 落ちの原因トップを潰す
- Guardrail で同じ指摘が続く場合は Template 側を改善する
- Template 自体の Changelog を更新する

### 6.3 Template の進化ルール

- Instance 側でテンプレ構造を変えるのは**例外扱い**（原則禁止）
- 変更が必要な場合は Template に Issue を切り、Template 側で修正して全 Instance に還元する
- Template は「壊れにくさ」を最優先し、段階導入（warn → block）を許容する

---

## 参照ドキュメント

| ドキュメント | 用途 |
|-------------|------|
| `01_OS Overview.md` | OS の思想・原則・全体像（地図） |
| `02_OS_Template_Spec.md` | Template Repo の仕様（設計図） |
| `03_Project_Instance_Guide.md` | Instance の立ち上げ手順（手順書） |
| `docs/architecture.md` | アーキテクチャ・設計方針 |
| `.ai-instructions.md` | AI エージェント向け共通規約 |
| `.ai-context.md` | 現在の状態・進行中 Issue・次の手 |
