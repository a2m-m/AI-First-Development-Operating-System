# Template Contract

## Status
Accepted

## Context
このリポジトリは「OS Template Repo」として、複数のプロジェクトで複製（Instance 化）して使用される前提があります。この際、Template 側で担保すべき「不変の仕組み」と、Instance 側で変更すべき「可変の設定・コード」の境界が曖昧になると、各プロジェクトが独自に CI やツールチェインをカスタマイズしてしまい、「一度作って育てる」というエコシステムが崩壊してしまいます。そのため、明確な Contract（境界・約束事）が必要です。

## Decision
「`02_OS_Template_Spec.md` Section 3」に基づき、Template と Instance 間の Controller Contract を以下の通り定義します。

### Template（不変: Invariants）
Template は以下を定義・維持し、Instance はこれらを原則変更してはなりません。
- リポジトリの基本構造（`docs/`, `.github/`, `scripts/` など）
- Issue / Pull Request のテンプレートフォーマット
- 言語差分を吸収するための実行口と設定ファイル (`scripts/run`, `os-template.yml`)
- CI ワークフローの骨格（セキュリティスキャン、ガードレール等含む）
- AI エージェント用コンテキスト (`.ai-context.md`, `.ai-instructions.md`)

### Instance（可変: Variants）
Instance 側で埋める・変更してよいものは以下に限定します。
- `os-template.yml`（プロジェクト固有の情報、実行コマンド定義、CI 実行モード）
- 追加の言語/フレームワーク固有のファイル群（`package.json`, `pyproject.toml` など）
- 任意機能の ON/OFF（guardrail, LCG等）
- アプリケーションやプロダクト自体のソースコードやアセット

※ CI などの基盤的な変更が必要な場合は Instance 側でオーバーライドするのではなく、Template 側へ Issue/PR を提出して全体へ還元するアプローチを優先する。

## Consequences
- **Positive:** 言語やツールに依存せず、すべてのデベロッパー・AI が統一されたコマンド（`scripts/run ci` 等）で開発に参加できる。OS のような一貫した開発体験を提供できる。
- **Negative:** プロジェクト固有の「ちょっとした CI スクリプトのハック」がやりづらくなるため、Template への提案を通じて改善する文化の醸成が必要になる。
