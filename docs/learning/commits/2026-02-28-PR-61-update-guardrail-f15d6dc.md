# Learning Content: PR #61

**Topic**: update-guardrail

## Summary
設定ファイルの追加とLCGワークフローの骨格が整備されました。 (scripts/guardrail, test_review.txt 等)

## Deep Dive
- `.github/workflows/lcg.yml`: OSのフィーチャーフラグに基づいて動作を切り替える設計パターンです。

## Quiz
1. `features.lcg` が `false` の場合にワークフローがスキップされる仕組みはどのように実装されていますか？
2. Github Actions における `contents: write` 権限の用途は何ですか？

## Explore next
AIがソースコードをコンテキスト付きで解釈するための最適なプロンプト設計について
