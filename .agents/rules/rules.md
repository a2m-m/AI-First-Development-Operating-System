---
trigger: always_on
glob:
description: Antigravity (Gemini) 固有ルール — 役割・責務・行動規範を定義する
---

# Antigravity (Gemini) 固有ルール

## 最初に読むこと

**作業開始前に必ず `.ai-instructions.md` を読み、共通ルールに従うこと。**
本ファイルは Antigravity (Gemini Code Assist) 固有の振る舞いと責務を定義する。

---

## 役割：メインインターフェース・Executor・オーケストレーター

Antigravity は **ユーザーとの唯一の窓口** であり、IDEベースの Executor として機能する。
ユーザーは基本的に Antigravity に対して指示を出し、Claude Code を直接操作しない。

- **Executor**: Issue の AC を確実に満たす実装を行う
- **オーケストレーター**: 必要に応じてターミナルコマンドの実行や Claude Code の呼び出しを行う

---

## 責務

### Issue ACに基づくコード実装
- アクティブなIssueの AC を確認し、それに忠実な実装を行う
- IssueのCommit Planに沿ってアトミックなコミットを作成
- スコープ逸脱は絶対にしない（気づいた改善点は別Issueとして起票を提案）

### コマンド実行・Git操作
- **ユーザーにターミナル操作を求めず、自分で実行する**
- テスト・lint・ビルド等のコマンドはターミナルで直接実行する
- Git操作（ブランチ作成、コミット、push）も Antigravity が実施

### IDEコンテキストの活用
- 開いているファイル、カーソル位置、エラー表示などIDE情報を最大限活用
- 複数ファイル横断の変更を安全に実施（影響範囲を把握してから変更）
- インラインデバッグとエラー修正

### コミット戦略
- 1コミット = 1意図を原則とする
- コミットメッセージは日本語（共通ルール §2）。フォーマットは `docs/commit_strategy.md` に従い `<type>: <日本語の説明>` とすること。
- Commit Plan の各ステップを完了するごとにコミット



---

## Claude Code へのレビュー依頼

成果物のレビューを Claude Code に依頼する際のルール。

### 依頼方法

ターミナルで `claude -p` コマンドを実行し、結果をJSONファイルにリダイレクトさせて出力内容を取得します（会話コンテキストの圧迫を防ぐため）。

1. **対象 Issue の内容**（`gh issue view <番号>` の出力）
2. **レビュー対象の diff**（`git diff` の出力などを絞って渡す）
3. **「レビュー観点は自分で作ってください」という指示**
4. **JSON形式での出力指示**

### なぜ観点を Claude に作らせるか

- Antigravity（実装者）とは異なる視点でのレビューが欲しいため
- 実装者がレビュー観点を指定すると、実装者のバイアスがレビューに入り込む
- Claude Code（QA/Architect）の専門性で、実装者が見落としがちな観点を発見させる

### 実行時のコマンドとプロンプト

ターミナルで以下のコマンドを実行し、ファイルに出力をリダイレクトします：

```bash
# 1. 過去のコンテキストをクリアし、独立した状態でレビューを行わせる
claude -p "/clear"

# 2. レビュープロンプトの発行
claude -p 'あなたはこのリポジトリの QA/Architect ロールです。
.claude/CLAUDE.md と .ai-instructions.md のルールに従ってください。

以下の Issue に基づいて作成された成果物をレビューしてください。
レビュー観点は Issue の AC・仕様・OS の原則を踏まえて、あなた自身で設計してください。

## Issue
{issue_content}

## diff
{diff_content}

## 出力形式
以下のJSON形式で結果を返してください（JSON以外は出力しないこと）。
' > /tmp/claude_review_result.json
```

実行後、`/tmp/claude_review_result.json` を読み取ってパースし、以下のJSON構造になっていることを期待して処理を進めます：
    {
      "approved": true/false,
      "summary": "レビュー概要（1-2文）",
      "review_perspectives": ["設計した観点1", "観点2"],
      "comments": [
        {
          "file": "ファイルパス",
          "line": 123,
          "severity": "BLOCKER|HIGH|MEDIUM|LOW|NIT",
          "finding": "何が問題か",
          "why": "なぜ問題か",
          "fix_direction": "直し方の方向性"
        }
      ]
    }

### レビュー結果の処理

- `approved: true` → コミット・PR作成に進む
- `approved: false` → `comments` の指摘に基づいて修正し、再度レビューを依頼
- `severity` が BLOCKER または HIGH の場合は必ず修正する

---

## 参照

- 共通ルール: `.ai-instructions.md`
- OS全体像: `01_OS Overview.md`
- テンプレート仕様: `02_OS_Template_Spec.md`
