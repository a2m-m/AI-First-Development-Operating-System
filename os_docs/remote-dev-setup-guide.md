# リモート開発環境セットアップガイド（Claude Code 版）

自宅 Mac を出先（iPhone / iPad / 別PC）から Claude Code で操作するためのガイドです。

---

## 全体構成

```
出先デバイス（iPhone / iPad / 別PC）
  │
  ├─ ブラウザ → vscode.dev（VS Code Remote Tunnel）  ← メイン作業
  └─ ターミナルアプリ → SSH（Tailscale 経由）         ← git 操作・コマンド実行
  │
  ↕  暗号化トンネル（Tailscale）
  │
自宅 Mac
  ├─ Claude Code（CLI）
  ├─ SSH サーバー
  └─ VS Code + Remote Tunnel
```

---

## Part 1: Tailscale のセットアップ（VPN 基盤）

Tailscale はポート開放不要で Mac と出先デバイスを安全に接続します。

### 1.1 インストール・接続

1. [tailscale.com](https://tailscale.com) でアカウント作成（無料プランで十分）
2. Mac と出先デバイスの両方に Tailscale をインストール
3. 同じアカウントでログイン → 両方のデバイスがリスト表示されれば完了
4. Mac に割り当てられた IP（例: `100.x.x.x`）をメモ

---

## Part 2: VS Code Remote Tunnel（メイン作業環境）

### 2.1 自宅 Mac での準備

```bash
# VS Code の code コマンドが使えるか確認
code --version

# Remote Tunnel を起動（初回は GitHub/Microsoft 認証が必要）
code tunnel

# サービスとして登録（再起動後も自動起動）
code tunnel service install
```

トンネル名（例: `my-macbook`）を設定すると、以下の URL でアクセスできます：

```
https://vscode.dev/tunnel/my-macbook
```

### 2.2 Claude Code のインストール確認

```bash
# Claude Code がインストール済みか確認
claude --version

# 未インストールの場合
npm install -g @anthropic-ai/claude-code
```

### 2.3 API キーの設定

このプロジェクトでは `GEMINI_API_KEY` が guardrail / LCG 機能で必要です。

```bash
# .env などには書かず、シェルの設定ファイルに追加する
echo 'export GEMINI_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

> **セキュリティ注意**: `.env` ファイルは `.gitignore` に含まれていますが、
> guardrail フックが `.env` への読み書きを検知してブロックします（Issue #47 参照）。

### 2.4 出先からの接続

1. ブラウザで `https://vscode.dev/tunnel/my-macbook` にアクセス
2. GitHub / Microsoft アカウントでサインイン
3. VS Code が表示される → 内蔵ターミナル（`` Ctrl + ` ``）で Claude Code を起動

```bash
# プロジェクトに移動
cd ~/path/to/your-project

# Claude Code 起動
claude
```

---

## Part 3: SSH（ターミナル操作用）

VS Code のブラウザ版の代わりに、SSH + ターミナルで操作する場合の設定です。

### 3.1 Mac で SSH を有効化

```
システム設定 → 一般 → 共有 → リモートログイン → ON
```

### 3.2 SSH 鍵認証

```bash
# 鍵ペアを生成
ssh-keygen -t ed25519 -C "my-remote-key"

# 公開鍵を登録
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3.3 接続コマンド

```bash
# Tailscale IP 経由で接続
ssh username@100.x.x.x

# 接続後、プロジェクトに移動して Claude Code を起動
cd ~/path/to/your-project && claude
```

### 3.4 推奨 SSH アプリ（iPhone / iPad）

| アプリ | 料金 | 特徴 |
|--------|------|------|
| Termius | 無料（基本機能） | UI が綺麗、鍵管理が簡単 |
| Blink Shell | 有料（買い切り） | 高機能、mosh 対応 |

---

## Part 4: このリポジトリでの作業フロー

### 外出前チェック

```bash
# 環境依存チェック
./os_scripts/run doctor

# CI を通しておく
./os_scripts/run ci
```

### 出先での作業開始

```bash
# コンテキスト確認（必須）
cat .ai-context.md

# Claude Code 起動
claude
```

Claude Code 内での典型的なフロー：

```
1. アクティブ Issue の AC を確認（context-sync）
2. /plan でプランモードに入り実装方針を確認
3. 実装
4. /review で自己レビュー
5. /gate（./os_scripts/run ci）
6. コミット・プッシュ・PR 作成
```

### 作業終了

```bash
# .ai-context.md を更新してコミット（必須）
# 次のセッションで迷子にならないために

git add .ai-context.md
git commit -m "docs: .ai-context.md を更新"
```

---

## Part 5: セキュリティ設定

### スリープ防止（リモート接続維持のため）

```bash
# 電源接続時はスリープしない設定
sudo pmset -c sleep 0
sudo pmset -c displaysleep 10
```

### ファイアウォール

```
システム設定 → ネットワーク → ファイアウォール → ON
```

Tailscale 経由の接続のみ許可される状態で安全に使えます。

---

## トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| `claude` コマンドが見つからない | インストール未完了 | `npm install -g @anthropic-ai/claude-code` |
| vscode.dev に接続できない | Mac がスリープ / トンネル停止 | `code tunnel service install` を再実行 |
| SSH 接続がタイムアウト | Tailscale 未接続 | 両デバイスで Tailscale アプリを開いて再接続 |
| `GEMINI_API_KEY` が未設定 | シェル設定の読み込み漏れ | `source ~/.zshrc` / `echo $GEMINI_API_KEY` で確認 |
| guardrail が `.env` をブロック | 正常動作 | `.env` への読み書きは設計上ブロック対象（Issue #47） |

---

## 関連ドキュメント

- `03_Project_Instance_Guide.md` — プロジェクト Instance の立ち上げ手順
- `.ai-context.md` — 現在の作業状態・次のアクション
- `.claude/CLAUDE.md` — Claude Code のルール・スキル一覧
