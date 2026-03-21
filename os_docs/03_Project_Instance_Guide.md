# 03\_Project\_Instance\_Guide

OS Template Repo から Project Instance（各プロジェクト実体）を作り、**プロジェクト固有のドキュメント/システム**を「安定かつ高品質」に構築して運用開始するためのガイド。

- 01：全体像（地図）  
- 02：Template Repoの仕様（設計図）  
- 03：TemplateからInstanceを作って走り出すための手順・型（手順書＋攻略本）

---

## 0\. このガイドの狙い（超重要）

プロジェクトごとに言語や作るものが変わる以上、**完全なテンプレ化は不可能**。  
なので03は、次の2レイヤで“ブレない立ち上げ”を実現する：

- **テンプレ化できる部分（固定）**：フォーマット／コントラクト／検証手順を固定し、AIが迷わず生成できるようにする  
- **テンプレ化できない部分（可変）**：選定そのものではなく「決め方」と「サンプル」を用意し、AIが対話で情報を集めて埋められるようにする

さらに、AIがドキュメントを読んで不足している部分だけをユーザーに質問し、対話を経て成果物に反映する「Interview Mode」を標準化する。

---

## 1\. 前提：Docs と Artifacts、03の責務

このOSはドキュメントだけでなく、対応する実体（リポジトリ/生成物）を含む“仕組み”。

- Docs：01/02/03（読むもの）  
- Artifacts：OS Template Repo / Project Instance（動くもの）

---

## 2\. まず守る：TemplateとInstanceの境界（破ると死ぬ）

Templateは固定（Invariants）、Instanceは差分（Variants）だけを書く。

### 2.1 Instanceで埋める・変更してよいもの（これだけ）

- プロジェクト識別情報（名前/owner/説明）  
- コマンド定義（lint/test/typecheck/format/build 等）  
- CI実行モード（docker / host）とセットアップ  
- 言語/フレームワーク固有ファイル（例：package.json, pyproject.toml）  
- 任意機能のON/OFF（guardrail, lcg 等）

**原則**：Templateのワークフローやスクリプト本体をプロジェクトごとに改造しない（変えたくなったらTemplateへ還元）。

---

## 3\. 標準開始フロー（Template → Instance）

1. OS Template Repo を GitHub Template として新規リポジトリを作成  
2. clone して os_scripts/init を実行  
3. Phase 0（DoR）を満たす（CIが走る/最低限の安全/教育フォーマット）  
4. 最小縦切りIssueで ①〜⑥ を1周し、運用を開始  
5. 詰まりはOSへ還元してチューニング（テンプレも育てる）

---

## 4\. Phase 0（運用開始条件：DoR）

**Phase 0 Minimum（DoR：準備完了条件）**

- PRを作るとCIが走り、失敗理由が見える  
- secrets混入を検知できる（止める or 警告）  
- 教育フィードバック（Summary+Quiz等）のフォーマットが決まっている

---

## 5\. Interview Mode（AIが読んで、不足だけ聞いて、反映する）

「プロジェクトごとに埋めるのが面倒」を解決する標準運用。

### 5.1 Inputs（AIに渡すもの）

- この 03\_Project\_Instance\_Guide  
- リポジトリ（最低：README / project_config.yml / docs / .ai-\* / 言語設定ファイル）  
- （あれば）要件メモ、制約（期限/法務/セキュリティ）

### 5.2 AIの作業手順（固定）

1) **Read & Auto-fill**  
   AIはまずリポと既存docsを読んで、推測できる部分を先に下書きする（不確実点は“仮”＋質問リスト化）  
     
2) **Interview（最大10問）**  
   足りない情報だけ短く聞く。答えが不明なら「デフォルト案」→ ADRに“見直し条件”つきで仮決め。  
     
3) **Apply（成果物へ反映）**  
   後述の Outputs をファイルとして生成/更新（差分がわかる形が理想）  
     
4) **Validate（合否判定）**  
   `./os_scripts/run doctor` と `./os_scripts/run ci` を通す。失敗したらログを貼り、原因特定→修正案→再検証の短いループにする。

### 5.3 Outputs（AIが作る成果物：固定）

- `os_docs/vision.md`（テンプレを埋めたもの）  
- `os_docs/architecture.md`（テンプレを埋めたもの）  
- `docs/decisions/README.md`（運用ルール）＋ `docs/decisions/0001-*.md`（主要決定のADR）  
- `project_config.yml`（commands.lint/testは必須）  
- `.ai-instructions.md` と `.ai-context.md`（固定フォーマットを維持）  
- 任意：`docs/project_profile.yml`（構造化プロフィール。Interview結果の唯一の事実置き場）

---

## 6\. テンプレ化できる部分（固定フォーム）

ここは「AIが機械的に埋める」ための章。

### 6.1 project_config.yml（Instance設定の唯一の入口）

Instanceは差分だけをこのファイルに書く。運用ルールはこれ：

- `commands.lint` と `commands.test` は必ず埋める（空は禁止）  
- `typecheck` は空OK（ただし理由を `.ai-context.md` に書く）  
- `runtime.mode=docker` 推奨（差分吸収が最も安定）

#### project_config.yml（最小テンプレ）

schema\_version: "1"

project:

  name: "YOUR\_PROJECT\_NAME"

  owner: "YOUR\_TEAM\_OR\_OWNER"

  description: "..."

runtime:

  mode: "docker"     \# docker|host

  docker\_image: ""   \# dockerなら必須

  host\_setup\_steps: \[\]

commands:

  format: ""

  lint: ""        \# required（空禁止）

  typecheck: ""

  test: ""        \# required（空禁止）

  build: ""

  ci: ""

features:

  secret\_scan: true

  dependency\_scan: true

  guardrail: true

  lcg: false

### 6.2 os_scripts/run（唯一の実行口）

人もCIも `os_scripts/run` だけ叩けばよい、を実現する。  
サブコマンドの期待：`doctor` は不足を診断し、`ci` は lint→（あれば）typecheck→test の標準順を持つ。

### 6.3 .ai-instructions.md（AIにやらせる時の規約）

最低限、以下を明記する：

- Templateのコントラクトを壊さない  
- 生成物は“小さく分けてPR”  
- 設定は project_config.yml に寄せる、巨大改修を勝手にしない

### 6.4 .ai-context.md（固定フォーマット）

枠を完全固定し、Instanceで埋める。推奨セクション：

- Status / Active Issues / Decisions / Next actions / Known pitfalls / Commands / CI Notes

---

## 7\. テンプレ化できない部分（決め方＋サンプル）

ここは「選定の再現性」を作る章。**決め方を固定**し、**サンプルを置く**。

### 7.1 言語・ツール選定（決め方）

判断軸（最低限）：

- 最小ゲート（lint/test）を確実に回せるか（最優先）  
- 実行環境（docker/host）との相性  
- チームの保守性（CI時間、依存更新、学習コスト）  
- セキュリティ/コンプラ要求（秘密情報、外部通信、監査）

#### サンプル：Python API（最小）

- lint: `ruff check .`  
- test: `pytest -q`  
- typecheck: `pyright`（無いなら理由をcontextに）

#### サンプル：Node Library（最小）

- lint: `npm run lint`（eslint）  
- test: `npm test`（vitest/jest）  
- typecheck: `npm run typecheck`（tsc）

#### サンプル：Go CLI（最小）

- lint: `golangci-lint run`（無いなら `go vet ./...` \+ ルール明記）  
- test: `go test ./...`

※選定理由はADRに残す（後で揉めない／AIが更新判断できる）

### 7.2 実行・CI設計（決め方）

CIは「言語を知らない」構造にする。やることは固定で doctor → ci、言語差分は `project_config.yml` に寄せる。

### 7.3 secrets / 安全（最小）

secretsスキャンはPRで必ず起動し、結果がPRで見える形にする。  
最初はwarn運用でも良いが、最終的にはfail推奨。

### 7.4 テスト方針（最小）

- まずは smoke でもよいが、**testが空は禁止**  
- 新機能はACに紐づくテストを最低1つ（追加できないなら合理的理由をPRに）

---

## 8\. Interview（最大10問）テンプレ

AIが聞く質問はこれで十分（答えが曖昧でも進む順）：

1) 何を作る？（API / CLI / バッチ / ライブラリ / フロント）  
2) 利用者は誰？（ユーザー/運用者）  
3) 成功条件は？（1〜3個）  
4) Non-goals（やらないこと）は？  
5) 実行環境：docker前提OK？デプロイ先は？  
6) 扱うデータの機微（個人情報/秘密/社外持ち出し不可）  
7) 外部依存（DB/外部API/認証/キュー）  
8) 最小テスト（unitのみ？integrationも？）  
9) 観測性の最低ライン（ログ/メトリクス）  
10) Day-1の縦切り（どこまで動けばOK？）

---

## 9\. 検証（合格条件）

- `./os_scripts/run doctor` が不足を出さない（出たら“何をどこに書くか”を埋める）  
- `./os_scripts/run ci` が通る（lint/testが回る）  
- PRでActionsが起動し、doctor→ciが走る  
- secretsスキャンがPRで起動し、結果が見える  
- Phase 0 DoR 3点を満たす

---

## 付録A：docsテンプレ（コピペ用）

### A1. os_docs/vision.md（1ページでOK）

\# Vision: \<PROJECT\_NAME\>

\#\# Problem

\- 誰が / 何に困っているか / 現状の痛み

\#\# Goal

\- このプロジェクトで達成したい状態（できれば測れる形）

\#\# Non-goals

\- 今回やらないこと（明確に）

\#\# Users / Stakeholders

\- ユーザー像、運用者、関係者

\#\# Success metrics

\- 指標（最大3つ）

\#\# Constraints

\- 期限、予算、法務/セキュリティ、環境、依存

\#\# Risks

\- 最大のリスク3つ（+対策の方向性）

\#\# Day-1 milestone（最小縦切り）

\- “動いた”の定義（最初に通したいシナリオ）

### A2. os_docs/architecture.md（最小スケッチ）

\# Architecture: \<PROJECT\_NAME\>

\#\# System overview

\- 箱と矢印（文章でもOK）

\#\# Key components

\- コンポーネント / 責務 / 境界

\#\# Data model / Domain

\- 重要な用語、型、データの流れ

\#\# Interfaces

\- API / CLI / Event / Cron など

\#\# Security & Compliance

\- データの機微、権限、秘匿、ログに残して良いもの

\#\# Observability

\- ログ（何を出すか）、最低限のメトリクス

\#\# Testing strategy

\- unit / integration / e2e の最小方針

\#\# Deployment / Runtime

\- docker/host、環境差分、設定の置き場

### A3. docs/decisions/README.md（ADR運用ルール：最小）

\# Decisions (ADR)

\- 重要な選定（言語/実行方式/依存/セキュリティ方針）は ADR に残す

\- “仮決め”でも良い。その場合は Revisit condition を必ず書く

\- 1 ADR \= 1 Decision

### A4. ADRテンプレ（docs/decisions/0001-\*.md）

\# ADR-000X: \<Decision title\>

\#\# Context

\#\# Decision

\#\# Options considered

\#\# Consequences

\#\# Revisit condition

---

## 付録B：project\_profile.yml（任意だが強い）

Interview結果の“唯一の事実置き場”。AIはここを更新→docs/project_config.ymlへ反映。

project:

  name: YOUR\_PROJECT\_NAME

  owner: YOUR\_TEAM

  type: api   \# api|cli|batch|library|frontend

  description: "..."

runtime:

  mode: docker

  docker\_image: your-image:tag

constraints:

  data\_sensitivity: internal  \# public|internal|confidential

  external\_network: true

success\_metrics:

  \- "..."

non\_goals:

  \- "..."

dependencies:

  \- "..."

testing:

  minimum: unit

observability:

  logs: true

  metrics: minimal

day1:

  milestone: "..."

---

## 付録C：AI実行プロンプト（コピペ用）

あなたはProject Instanceの立ち上げアシスタントです。

目的：このリポジトリに対して、Project固有の docs と systems を高品質に構築し、Phase 0（doctor/ciが通る）まで到達させること。

制約：

\- 03\_Project\_Instance\_Guideに従う。Templateのワークフロー/スクリプト本体の改造は避け、差分は project_config.yml とプロジェクト固有ファイルで吸収する。

\- まずリポジトリと既存ドキュメントを読み、推測できる項目は埋める。

\- 不足情報は最大10問の問診で回収する。答えが不明ならデフォルト案を提示し、ADRに「見直し条件」を書いて仮決めする。

\- 出力は必ずファイルパス単位で提示する：os_docs/vision.md, os_docs/architecture.md, docs/decisions/..., project_config.yml, .ai-context.md（可能なら project\_profile.yml も）

手順：

1\) 理解した前提・推測・未確定事項リストを提示

2\) 未確定事項を質問（最大10問）

3\) 回答を受けて成果物の生成/更新案を提示（差分が分かる形）

4\) doctor/ci の結果があれば解析し修正案を出す

---

## 付録D：project_config.yml（言語別サンプル：commandsだけ差し替え）

### Python

runtime:

  mode: docker

  docker\_image: ghcr.io/org/python:3.12

commands:

  lint: "ruff check ."

  typecheck: "pyright"

  test: "pytest \-q"

### Node

runtime:

  mode: docker

  docker\_image: ghcr.io/org/node:20

commands:

  lint: "npm run lint"

  typecheck: "npm run typecheck"

  test: "npm test"

### Go

runtime:

  mode: docker

  docker\_image: ghcr.io/org/golang:1.22

commands:

  lint: "golangci-lint run"

  typecheck: ""   \# 無しなら理由を.ai-context.mdへ

  test: "go test ./..."  
