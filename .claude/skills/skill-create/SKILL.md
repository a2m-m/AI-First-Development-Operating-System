---
name: skill-create
description: 反復作業を新しい Claude Code スキルとしてモジュール化する。SKILL.md のテンプレート生成、Frontmatter 設計判断、配置まで自動で行う。
disable-model-invocation: true
argument-hint: [スキル名] [説明]
allowed-tools: Read, Write, Bash(mkdir *)
---

# スキル作成

反復する作業を `.claude/skills/` にスキルとして定義する（P6: Mechanisms）。

## 手順

1. 引数からスキル名と説明を取得する
   - `$ARGUMENTS[0]` = スキル名（例: `deploy`）
   - `$ARGUMENTS[1]` 以降 = スキルの説明

2. スキルの設計判断を行う（以下のフローで Frontmatter を決定）

   ```
   副作用があるか？（ファイル変更/Issue作成/push等）
     ├─ YES → disable-model-invocation: true
     └─ NO → 背景知識として常に必要か？
             ├─ YES → user-invocable: false
             └─ NO → デフォルト（両方OK）
   ```

3. `.claude/skills/<name>/SKILL.md` を以下のテンプレートで生成する

## SKILL.md テンプレート

```markdown
---
name: <スキル名>
description: <説明>
disable-model-invocation: <判断結果>
allowed-tools: <必要なツールのみ>
argument-hint: <引数ヒント（あれば）>
---

# <スキルのタイトル>

<1行でスキルの目的>

## 手順

1. ...
2. ...
3. ...

## 出力フォーマット（必要な場合）

## ルール

- ...
```

## Frontmatter リファレンス（設計時に参照）

| キー | 用途 |
|---|---|
| `name` | `/name` で呼び出せる |
| `description` | Claude の自動判断ヒント |
| `disable-model-invocation: true` | ユーザーのみ起動（副作用ある操作） |
| `user-invocable: false` | Claude のみ起動（背景知識系） |
| `allowed-tools` | ツール制限（最小権限） |
| `context: fork` | サブエージェントとして隔離実行 |
| `agent: Explore / Plan` | エージェントモード指定 |
| `argument-hint` | 引数のヒント表示 |

## 引数記法

| 記法 | 意味 |
|---|---|
| `$ARGUMENTS` | すべての引数 |
| `$ARGUMENTS[0]`, `$0` | 最初の引数 |
| `$ARGUMENTS[1]`, `$1` | 2番目の引数 |

## 動的コンテキスト注入

`!` プレフィックスでコマンド出力を埋め込める：
- `!`\`gh pr diff\` → PR の diff が埋め込まれる

## スキル化の判断基準（review スキルでも使用）

以下のいずれかを満たす作業はスキル化する：
1. **反復性**: 同じ手順を3回以上繰り返している
2. **テンプレ性**: 出力に決まったフォーマットがある
3. **品質一貫性**: 人によって品質がブレる作業
4. **文脈依存**: 毎回リポジトリの状態を読んでから判断する作業

スキル化しない方がよいもの：
- 1回きりの作業
- 毎回まったく判断が異なる作業
- `os_scripts/run` でカバー済みの単純なコマンド実行

## ルール

- Template 共通のスキルは `.claude/skills/` に配置
- Instance 固有のスキルも同じ構造で配置してよいが、Template のスキルは改造しない
- 作成後、ユーザーに `/name` でテスト実行を促す
- 出力は日本語
