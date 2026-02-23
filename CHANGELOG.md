# Changelog

すべての重要な変更は、このファイルに記録されます。

フォーマットは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づいており、
このプロジェクトは [Semantic Versioning](https://semver.org/spec/v2.0.0.html) に準拠しています。

## [Unreleased]

## [0.1.0] - 2026-02-23

### 追加
- **AI-First OS テンプレート基盤**: 開発用オペレーティングシステムの初期フレームワークとディレクトリ構成の実装 (#1, #2)
- **ワークフロー / Actions**:
  - CI パイプライン (`.github/workflows/ci.yml`) - Linter、テスト、フォーマットチェック、ビルド処理の自動実行 (#6)
  - テストレポート (`.github/workflows/test-report.yml`) - テスト結果をPRコメントへ自動パブリッシュする機能 (#8)
  - シークレットスキャン (`.github/workflows/secret-scan.yml`) - Gitleaksの統合によるクレデンシャル漏洩の防止 (#10)
  - 依存パッケージスキャン (`.github/workflows/dependency-scan.yml`) - Trivyの統合による脆弱性検知 (#19)
  - Guardrail CI (`.github/workflows/guardrail.yml`) - 初期段階のAI駆動PRレビューおよびアーキテクチャポリシー適用のモック実装 (#17)
  - Learning Content Generator (`.github/workflows/lcg.yml`) - AIと人間のインタラクションおよびPRコンテキストを学習資産として抽出するモック実装 (#18)
- **スクリプト**:
  - `scripts/run` - コマンドを管理し `os-template.yml` から変数を読み込むためのコアルーティングCLI (#5)
  - `scripts/init` - 環境変数に基づいてOSテンプレートをインスタンスに適用するための汎用ブートストラップスクリプト (#11)
  - `scripts/hooks/pre-push` - `os-template.yml` のポリシーに基づき、巨大なdiffを検知するGit pre-pushフック実装 (#15, #16)
- **設定とポリシー**:
  - `os-template.yml` - 機能フラグ、ポリシー、コマンド、リポジトリメタデータの統合一元設定ファイル (#4)
  - コミット戦略ドキュメント (`docs/commit_strategy.md`) の策定 (#14)
  - `.ai-instructions.md` - AIエージェントの制約と振る舞いを制御するシステムプロンプトルールの定義 (#3)
  - `.ai-context.md` - 継続的なAI実行のための現在の作業コンテキストの維持管理機能 (#7)

### 変更
- 厳格な受け入れ基準と方針コンテキストを確保するためのIssue/PRテンプレートの標準化 (#9)

[unreleased]: https://github.com/a2m-m/AI-First-Development-Operating-System/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/a2m-m/AI-First-Development-Operating-System/releases/tag/v0.1.0
