# Claude Code MCP化 移行ガイド

> **現行の `claude -p` レビューフローから、MCP ワンショット方式への移行手順書**

---

## 1. 概要：何を・なぜ変えるのか

### 1.1 現行フロー（As-Is）

現在、Antigravity（Gemini）が Claude Code にレビューを依頼する際、`.agents/rules/rules.md` に定義された以下の方式を使っている：

```bash
claude -p "あなたはこのリポジトリの QA/Architect ロールです。
.claude/CLAUDE.md と .ai-instructions.md のルールに従ってください。

以下の Issue に基づいて作成された成果物をレビューしてください。
レビュー観点は Issue の AC・仕様・OS の原則を踏まえて、あなた自身で設計してください。

## Issue
$(gh issue view <番号>)

## レビュー対象
- <対象ファイル>

レビュー結果を日本語で出力してください。"
```

### 1.2 現行フローの課題

`claude -p` は**ワンショット実行**ではあるものの、以下の点で改善の余地がある：

| 課題 | 詳細 |
|------|------|
| **Antigravity側のコンテキスト消費** | `claude -p` の出力がAntigravityの会話コンテキストにそのまま載る。長いレビュー結果ほどAntigravity側のトークンも圧迫する |
| **構造化されていない出力** | テキストベースの出力のため、Antigravityが「approved か否か」「どのファイルのどの行か」をパースしづらい |
| **スケーラビリティ** | Manager View で複数エージェントが並列レビューする場合、各エージェントが個別に `claude -p` を叩く形になり、管理が煩雑 |
| **Claude Code側の拡張性** | `claude -p` だとClaude Codeのファイル操作能力（Bash, Read, GrepTool等）を活かしきれない |

### 1.3 移行後フロー（To-Be）

Claude Code を **MCPサーバー** として登録し、Antigravity のエージェントが **MCPツール呼び出し** でレビューを依頼する。

```
Antigravity エージェント
    │
    ├─ ① ISSUE を読み込み、実装を行う
    │
    ├─ ② git diff で変更内容を取得
    │
    ├─ ③ MCP ツール呼び出し: claude_code（ワンショット）
    │     入力: diff + ISSUE + 「レビュー観点は自分で作ってください」
    │     ┌─────────────────────────────────────────┐
    │     │  Claude Code（独立セッション）           │
    │     │  - .claude/CLAUDE.md のルールに従う      │
    │     │  - ISSUE AC に基づきレビュー観点を設計   │
    │     │  - 構造化された JSON で結果を返却        │
    │     └─────────────────────────────────────────┘
    │
    ├─ ④ レビュー結果（JSON）を受け取る
    │
    ├─ ⑤ approved: false なら修正 → ③へ戻る
    │     approved: true ならコミット・PR作成
    │
    └─ ⑥ .ai-context.md を更新
```

### 1.4 移行で得られるメリット

| 観点 | 効果 |
|------|------|
| **Claude Code側のトークン節約** | 毎回独立セッションで起動するため、前回のレビュー文脈が残らない。compactが発生しない |
| **Antigravity側のトークン節約** | 構造化JSON（必要最小限）だけが返るため、長文のレビューコメントでコンテキストが膨らまない |
| **並列レビュー** | Manager View の複数エージェントがそれぞれ独立にMCPツールを呼べる |
| **ファイル操作能力の活用** | Claude Codeが必要に応じてリポジトリ内のファイルを直接読み、より深いレビューが可能 |

---

## 2. 前提条件

### 2.1 必要なソフトウェア

| ソフトウェア | バージョン | 確認コマンド |
|-------------|-----------|-------------|
| Node.js | v20以上 | `node --version` |
| Claude Code | 最新版 | `claude --version` |
| Google Antigravity | 最新版 | アプリのバージョン情報を確認 |
| npx | Node.js に付属 | `npx --version` |

### 2.2 Anthropic APIキー

Claude Code を利用するために Anthropic の APIキー が必要。

```bash
# 環境変数に設定（.bashrc や .zshrc に追加推奨）
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

取得先: https://console.anthropic.com/

---

## 3. セットアップ手順

### 3.1 ステップ1: Claude Code のインストールと初回パーミッション承認

```bash
# Claude Code がまだインストールされていない場合
npm install -g @anthropic-ai/claude-code

# バージョン確認
claude --version

# パーミッションを承認（初回のみ・MCP サーバー動作に必要）
claude --dangerously-skip-permissions
```

> ⚠️ **注意**: `--dangerously-skip-permissions` は、Claude Code がファイル操作やコマンド実行を確認なしで行えるようにするオプション。MCP サーバーとして動かすために必要だが、信頼できる環境でのみ使用すること。

### 3.2 ステップ2: `claude mcp add` で MCP サーバーを登録

`.mcp.json` を手書きする必要はない。**`claude mcp add` コマンド**で登録するのが公式かつ確実な方法。

#### `claude mcp` の主要コマンド一覧

| コマンド | 用途 |
|---------|------|
| `claude mcp add <name> -- <command> [args...]` | MCPサーバーを追加 |
| `claude mcp add-json <name> '<json>'` | JSON形式で直接追加（複雑な設定向け） |
| `claude mcp list` | 登録済みサーバーの一覧表示 |
| `claude mcp get <name>` | 特定サーバーの詳細表示・接続テスト |
| `claude mcp remove <name>` | サーバーの削除 |

#### `--scope` オプション（設定の保存先を選ぶ）

| scope | 保存先 | 用途 |
|-------|--------|------|
| `local`（デフォルト） | `.claude/` 配下（ローカルのみ） | 自分だけが使う設定 |
| `project` | `.mcp.json`（リポジトリに含まれる） | **チーム全員で共有する場合に推奨** |
| `user` | ユーザーグローバル設定 | 全プロジェクト共通で使いたい場合 |

> 💡 **このプロジェクトでは `--scope project`** を推奨。`.mcp.json` がリポジトリに入るため、Antigravity 側からも参照でき、チームメンバー間で設定が統一される。

---

#### 方法A: steipete/claude-code-mcp を使う（推奨）

コミュニティ製のラッパーで、**ワンショット実行に特化**している。レビュー用途に最適。

```bash
# プロジェクトルートで実行
claude mcp add --scope project claude-code-review -- npx -y claude-code-mcp
```

APIキーを明示的に渡したい場合は `--env` を使う：

```bash
claude mcp add --scope project \
  --env ANTHROPIC_API_KEY=sk-ant-xxxxx \
  claude-code-review -- npx -y claude-code-mcp
```

> 💡 `ANTHROPIC_API_KEY` が環境変数に既に設定されていれば `--env` は不要。

#### 方法B: 公式の `claude mcp serve` を使う

Claude Code のビルトイン機能。ファイル操作ツール（Bash, Read, Write, Edit, GrepTool等）をそのまま MCP で公開する。

```bash
# プロジェクトルートで実行
claude mcp add --scope project claude-code-tools -- claude mcp serve
```

#### 方法A と B の違い

| 比較項目 | 方法A (steipete版) | 方法B (公式 mcp serve) |
|----------|-------------------|----------------------|
| 呼び出し方 | 単一の `claude_code` ツール | 複数のツール（Bash, Read, Write等）を個別に呼ぶ |
| ワンショット | ✅ 設計上最適化されている | △ ツール単位の呼び出しになる |
| コンテキスト節約 | ✅ 高い（1回の呼び出しで完結） | △ ツール呼び出し回数分コンテキストを消費 |
| ファイル操作の自由度 | △ プロンプトで間接的に指示 | ✅ 各ツールを直接制御可能 |
| 推奨用途 | **レビュー（今回のユースケース）** | 低レベルなファイル操作が必要な場合 |

**レビュー用途には方法A を推奨。**

#### 複雑な設定が必要な場合: `claude mcp add-json`

環境変数が多い場合など、JSON で直接渡す方が楽なケースもある：

```bash
claude mcp add-json claude-code-review '{
  "command": "npx",
  "args": ["-y", "claude-code-mcp"],
  "env": {
    "ANTHROPIC_API_KEY": "sk-ant-xxxxx",
    "MAX_MCP_OUTPUT_TOKENS": "15000"
  }
}'
```

### 3.3 ステップ3: 登録の確認

```bash
# 登録済みサーバーの一覧を表示
claude mcp list

# 特定サーバーの接続テスト
claude mcp get claude-code-review
```

正常に登録されていれば、以下のように表示される：

```
MCP Server Status

• claude-code-review: connected
```

### 3.4 ステップ4: Antigravity 側での動作確認

Antigravity を再起動し、エージェントのチャットで以下のように試す：

```
Claude Code を使って、現在のディレクトリのファイル一覧を取得して
```

エージェントが `claude_code` ツールを呼び出し、結果が返ってくれば成功。

### 3.5 サーバーの削除・再登録

設定を変更したい場合は、一度削除してから再登録する：

```bash
# 削除
claude mcp remove claude-code-review

# 再登録（設定を変更して）
claude mcp add --scope project claude-code-review -- npx -y claude-code-mcp
```

---

## 4. 既存ルールの移行

### 4.1 `.agents/rules/rules.md` の変更

現行の「Claude Code へのレビュー依頼」セクションを更新する。

#### Before（現行）

```markdown
## Claude Code へのレビュー依頼

### 依頼方法
`claude -p` コマンドで以下の情報を渡す：
（以下省略）
```

#### After（MCP移行後）

```markdown
## Claude Code へのレビュー依頼

### 依頼方法

`.mcp.json` に登録された `claude_code` MCPツールを使って以下の情報を渡す：

1. **対象 Issue の内容**（`gh issue view <番号>` の出力）
2. **レビュー対象の diff**（`git diff` の出力）
3. **「レビュー観点は自分で作ってください」という指示**
4. **JSON形式での出力指示**

### なぜ観点を Claude に作らせるか（変更なし）

- Antigravity（実装者）とは異なる視点でのレビューが欲しいため
- 実装者がレビュー観点を指定すると、実装者のバイアスがレビューに入り込む
- Claude Code（QA/Architect）の専門性で、実装者が見落としがちな観点を発見させる

### MCP呼び出し時のプロンプト

claude_code ツールに以下のプロンプトを渡す：

    あなたはこのリポジトリの QA/Architect ロールです。
    .claude/CLAUDE.md と .ai-instructions.md のルールに従ってください。

    以下の Issue に基づいて作成された成果物をレビューしてください。
    レビュー観点は Issue の AC・仕様・OS の原則を踏まえて、あなた自身で設計してください。

    ## Issue
    {issue_content}

    ## diff
    {diff_content}

    ## 出力形式
    以下のJSON形式で結果を返してください（JSON以外は出力しないこと）:
    {
      "approved": true/false,
      "summary": "レビュー概要（1-2文）",
      "review_perspectives": ["設計した観点1", "観点2", ...],
      "comments": [
        {
          "file": "ファイルパス",
          "line": 行番号または null,
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
```

### 4.2 `.claude/CLAUDE.md` の変更

Claude Code 側のルールには基本的に変更不要。MCP経由で呼び出されても、Claude Code は `.claude/CLAUDE.md` のルールに従って動作する。

ただし、JSON出力に対応するための補足を追加してもよい：

```markdown
## MCP経由のレビュー依頼への対応

Antigravity から MCP ツール経由でレビュー依頼を受けた場合：
- プロンプトで指定された出力形式（JSON等）に従うこと
- レビュー観点は自分で設計すること（`/review` スキルの手順に準拠）
- Guardrail コメント規格（Severity / Finding / Why / Fix direction）を守ること
```

### 4.3 `.ai-instructions.md` の変更

共通ルールには大きな変更は不要だが、以下を追記するとよい：

```markdown
## 8. MCP連携ルール

- MCP サーバーの登録は `claude mcp add --scope project` を使い、`.mcp.json` 経由でチーム共有する
- MCP サーバーの追加・変更は Issue を起票してから行う
- MCP 経由の Claude Code 呼び出し結果は構造化データ（JSON等）で受け取ること
- 登録状況の確認は `claude mcp list` で行う
```

---

## 5. トークン節約をさらに最適化するテクニック

### 5.1 入力の最適化（Claude Code に渡す情報を絞る）

```
❌ 悪い例: git diff をそのまま全部渡す
✅ 良い例: 変更のあったファイルだけをフィルタして渡す
```

```bash
# 変更ファイルのみのdiffを取得
git diff --name-only origin/main...HEAD | \
  xargs -I {} git diff origin/main...HEAD -- {}
```

### 5.2 出力の最適化（Claude Code から受け取る情報を絞る）

プロンプトで「JSON以外は出力しないこと」と明示することで、不要な説明文がコンテキストに載るのを防ぐ。

### 5.3 MAX_MCP_OUTPUT_TOKENS の設定

Claude Code の MCP 出力トークン上限を調整できる。デフォルトは25,000トークン。

```bash
# レビュー結果の規模に合わせて調整
export MAX_MCP_OUTPUT_TOKENS=10000
```

レビュー結果が切れる場合は値を増やし、無駄に大きい場合は減らす。

### 5.4 レビューのスコープを分割する

大きな変更は一度にレビューせず、機能単位で分割して複数回呼び出す方がトークン効率がよい。

```
# 例: フロントエンドとバックエンドを分けてレビュー

# 呼び出し1: フロントエンド
claude_code ツール: "src/frontend/ 配下の diff をレビューして..."

# 呼び出し2: バックエンド
claude_code ツール: "src/backend/ 配下の diff をレビューして..."
```

それぞれが独立セッションで実行されるため、コンテキストが混在しない。

---

## 6. トラブルシューティング

| 症状 | 原因 | 対処法 |
|------|------|--------|
| `Command not found: claude` | Claude Code が未インストール or PATH が通っていない | `npm install -g @anthropic-ai/claude-code` を実行。`which claude` で確認 |
| `claude mcp list` で表示されない | 登録時の `--scope` が違う or 登録失敗 | `claude mcp add` を再実行。`--scope project` ならリポルートの `.mcp.json` を確認 |
| MCP サーバーが `disconnected` | npx のキャッシュ問題 or コマンドのパスが通っていない | `claude mcp remove <n>` → `claude mcp add` で再登録。`npx -y claude-code-mcp` が単独で動くか確認 |
| `Permission denied` エラー | 初回の `--dangerously-skip-permissions` が未実行 | `claude --dangerously-skip-permissions` を一度実行 |
| レビュー結果が途中で切れる | 出力トークン上限を超えている | `MAX_MCP_OUTPUT_TOKENS` を増やすか、レビュー範囲を分割 |
| JSON パースエラー | デバッグログが JSON 出力に混入 | `claude mcp remove` → `--env MCP_CLAUDE_DEBUG=false` 付きで再登録 |
| レビュー結果が不正確 | 入力が多すぎて焦点がぼけている | diff を機能単位に分割して渡す |

---

## 7. 発展的な構成

### 7.1 並列レビュー（Manager View 活用）

Antigravity の Manager View は複数エージェントの並列実行をサポートしている。MCP 化により、以下のような並列レビューが可能になる：

- **エージェントA**: フロントエンドの実装 → Claude Code MCP でレビュー
- **エージェントB**: バックエンドの実装 → Claude Code MCP でレビュー
- **エージェントC**: テストの実装 → Claude Code MCP でレビュー

それぞれのレビューが独立セッションで実行されるため、コンテキストが混在せず、各レビューがクリーンな状態で動く。

### 7.2 Claude Code の二重の役割

Claude Code は以下の2つの役割を同時に担える：

- **MCP サーバー**（Antigravity からツールとして呼ばれる）
- **MCP クライアント**（GitHub MCP サーバーなど、他のツールを利用する）

ただし、Claude Code が接続している MCP サーバー（例: GitHub MCP）は、外部クライアント（Antigravity）からは直接アクセスできない（パススルーなし）。

### 7.3 `/review` スキルとの統合

現在 `.claude/skills/review/SKILL.md` に定義されている `/review` スキルは、MCP 経由の呼び出しでも自動的に適用される。Claude Code が `.claude/CLAUDE.md` を読み込む際にスキルも読み込まれるため、レビュー観点の設計ロジックや Guardrail コメント規格は引き続き機能する。

### 7.4 将来的な拡張: カスタム MCP サーバー

レビュー以外のユースケース（例: Issue の自動作成、テスト実行結果の分析）が増えた場合、Anthropic API を直接呼ぶカスタム MCP サーバーを自作することも検討できる。Claude Code のファイル操作能力が不要なら、API直接の方が軽量。

---

## 8. 移行チェックリスト

以下を順番に実施し、全て完了したら移行完了とする。

- [ ] Node.js v20以上がインストールされている
- [ ] Claude Code がインストールされている（`claude --version` で確認）
- [ ] `claude --dangerously-skip-permissions` を一度実行済み
- [ ] `ANTHROPIC_API_KEY` が環境変数に設定されている
- [ ] `claude mcp add` で MCP サーバーを登録済み
- [ ] `claude mcp list` で `connected` になっている
- [ ] Antigravity を再起動し、MCP ツールの呼び出しが成功している
- [ ] `.agents/rules/rules.md` のレビュー依頼セクションを更新済み
- [ ] （任意）`.claude/CLAUDE.md` にMCP対応の補足を追加済み
- [ ] （任意）`.ai-instructions.md` にMCP連携ルールを追記済み
- [ ] `.ai-context.md` に移行完了の記録を追加済み

---

## 9. 参考リンク

| リソース | URL |
|----------|-----|
| Claude Code MCP ドキュメント（公式） | https://code.claude.com/docs/en/mcp |
| steipete/claude-code-mcp (GitHub) | https://github.com/steipete/claude-code-mcp |
| claude-code-mcp Agent SDK版 (GitHub) | https://github.com/xihuai18/claude-code-mcp |
| Google Antigravity | https://antigravity.google/download |
| Anthropic APIキー取得 | https://console.anthropic.com/ |
| MCP プロトコル仕様 | https://modelcontextprotocol.io/ |