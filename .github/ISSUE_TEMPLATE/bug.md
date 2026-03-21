---
name: Bug
about: バグ報告・修正の命令書
title: "[Bug] "
labels: bug
assignees: ''
---

## Related Issues
<!-- 同じ機能グループ（認証・UIデザイン・CI など）に属する Issue を列挙する -->
<!-- scope/xxx ラベルも付与すること（例: scope/auth, scope/design, scope/ci） -->
- Related: #
<!-- 関連がない場合は "なし" と書く -->

## Repro Steps（再現手順）
<!-- 誰でも再現できる最小手順を書く -->
1.
2.
3.

## Expected（期待値）
<!-- こうなるはずだった -->

## Actual（実際）
<!-- こうなってしまった。エラーメッセージ・ログがあれば貼る -->

## Root Cause Hypothesis（仮説）
<!-- 原因の当たりをつける。調査ログや推測でも可（仮でOK）-->

## Fix Approach（修正方針）
<!-- どう直すか。複数案がある場合は比較して選択理由も書く -->

## Acceptance Criteria
<!-- 修正完了の定義。再発防止テストの追加を含める -->
- [ ] 再現手順を実行しても発生しない
- [ ] リグレッションテストが追加されている
- [ ] ...

## Test Plan
<!-- 修正後の確認方法。再発防止テストの方針 -->

## Commit Plan
<!-- 修正をどう分割してコミットするか -->
- Commit 1: 再現テスト追加
- Commit 2: 修正本体
- Commit 3: （任意）
