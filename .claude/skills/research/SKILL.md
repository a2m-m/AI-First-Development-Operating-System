---
name: research
description: Explore エージェントが調査スコープを定義し、Codex が主導して深掘りリサーチを行う。双方向質疑を経て最終リサーチレポートを出力する。
argument-hint: <テーマ>
allowed-tools: Read, Grep, Glob, Agent(subagent_type=Explore), Bash(./os_scripts/codex_session.sh *), Bash(mktemp), Bash(cat *), Bash(rm *), Bash(ls *), Bash(date *), Bash(tee *)
---

# Explore → Codex リサーチフロー

## ステップ 0: 事前確認

`os_scripts/codex_session.sh` の存在を確認する：

```bash
ls os_scripts/codex_session.sh
```

存在しない場合は以下を出力して**停止する**：

```
Error: Codex セッション基盤 (os_scripts/codex_session.sh) が見つかりません。
Issue #94 の実装が完了しているか確認してください。
```

## ステップ 1: テーマを受け取る

引数 `$ARGUMENTS` をリサーチテーマとして使用する。

テーマが空の場合は以下を出力して**停止する**：

```
Error: リサーチテーマを指定してください。
使い方: /research <テーマ>
例:    /research Codex セッション管理の実装方針
```

## ステップ 2: Explore エージェントで調査スコープを定義する

Agent ツール（`subagent_type=Explore`）を使い、以下のプロンプトで調査を実行する：

```
リサーチテーマ: <テーマ>

以下を調査・定義してください：

1. **調査スコープ**: このテーマに関係するコードベース上の領域（ディレクトリ・ファイル群）
2. **調査観点**: テーマを深掘りするための具体的な問い（3〜5 個）
3. **対象ファイル一覧**: 関連するファイルのパスと各ファイルの役割
4. **現状サマリ**: 各観点に対してわかっていること・わかっていないこと

コードベースを探索してこれらを答えてください。
```

Explore の応答を変数に保持する。

## ステップ 3: Codex へのコンテキストを整形する

一時ファイルを作成し、以下の形式で書き込む：

```bash
CONTEXT_FILE=$(mktemp /tmp/research_context_XXXXXX.md)
```

書き込む内容：

```
# リサーチ依頼: <テーマ>

## Explore エージェントによる事前調査

### 調査スコープ
<Explore が特定したコードベース上の対象領域>

### 調査観点
<Explore が定義した問い（3〜5 個）>

### 対象ファイル一覧
<Explore が特定したファイルとその役割>

### 現状サマリ
<Explore が把握した現状（わかっていること・わかっていないこと）>

## リサーチ指示

上記の調査観点を中心に、コードベースを深掘りしてリサーチを行ってください。
不明な点や追加で確認したい事項があれば質問してください。
最終的に「## リサーチレポート」として構造化した報告をまとめてください。
```

## ステップ 4: Codex セッションを開始する

```bash
SESSION_ID="research-$(date +%s)"
./os_scripts/codex_session.sh start "${SESSION_ID}" "${CONTEXT_FILE}"
```

> **注意**: `start` コマンドが成功した後にエラーが発生した場合は、必ず「エラー時クリーンアップ手順」を実行してから停止すること。

Codex の初回応答を読み、以下を判断する：

- **質問を含む** → ステップ 5（双方向質疑）へ
- **質問なし・リサーチレポートを直接出力** → ステップ 6（レポート整形）へ

## ステップ 5: Codex と双方向質疑を行う

Codex の質問に対して Claude が調査・回答する。質問の種類別対応：

| 質問の種類 | 対応方法 |
|---|---|
| コードの実装詳細・挙動 | 対象ファイルを Read / Grep して回答 |
| 設計方針・アーキテクチャ | `CLAUDE.md` や Issue・決定事項を参照して回答 |
| ファイルの存在・構造 | Glob / Grep で確認して回答 |
| 依存関係・呼び出し元 | Grep で import / 使用箇所を調査して回答 |

```bash
./os_scripts/codex_session.sh reply "${SESSION_ID}" "<回答内容>"
```

**最大 5 往復** で質疑を打ち切る。5 往復を超えた場合は以下を reply して終了：

```
調査済みの情報で結論を出してください。これ以上の追加情報は提供できません。
```

Codex が「リサーチ完了」「以上がリサーチレポートです」等のシグナルを出したら質疑終了。

## ステップ 6: リサーチレポートを出力する

Codex の最終出力から `## リサーチレポート` セクションを抽出し、以下の形式で標準出力に出す：

```
# リサーチレポート: <テーマ>

## 調査観点と結果
<各観点に対する Codex の回答>

## 発見事項
<コードベースで見つかった重要な情報>

## 未解決の問い
<調査しても答えが出なかった点（あれば）>

## 結論
<テーマに対するまとめと推奨事項>
```

レポートをファイルにも保存する：

```bash
REPORT_FILE="os_scripts/codex_sessions/research-report-$(date +%Y%m%d-%H%M%S).md"
echo "${REPORT_CONTENT}" | tee "${REPORT_FILE}"
```

（`REPORT_CONTENT` は Codex の最終出力を格納した変数）

## ステップ 7: セッションを終了する

```bash
./os_scripts/codex_session.sh end "${SESSION_ID}"
```

セッション終了後、一時コンテキストファイルを削除する：

```bash
rm "${CONTEXT_FILE}"
```

最後に保存先を案内する：

```
リサーチレポートを保存しました: <REPORT_FILE>
```

## エラー時クリーンアップ手順

`./os_scripts/codex_session.sh start` が成功した後にエラーが発生した場合は、以下を必ず実行してから停止すること：

```bash
./os_scripts/codex_session.sh end "${SESSION_ID}"
rm "${CONTEXT_FILE}"
```

その後、エラー内容をユーザーに報告する。

## ルール

- `os_scripts/codex_session.sh` が存在しない場合は **必ずエラーを出して停止する**（Codex 基盤なしでは動作不可）
- テーマが空の場合は **必ずエラーを出して停止する**
- Codex への質問応答は **最大 5 往復** とする
- リサーチレポートは **必ず日本語** で出力する
- セッション終了（`end`）は途中エラーが発生しても **必ず実行する**（エラー時クリーンアップ手順を参照）
- 一時コンテキストファイルはセッション終了後に削除する
- レポートは `os_scripts/codex_sessions/` に保存する（セッションログと同じ場所）
