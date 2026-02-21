# **01\_OS Overview**

AI（Claude Code / Antigravity）× GitHub を前提に、速度と安全性を両立しながら、学習も自然に生まれる開発エコシステムを作る。

---

## **0\. このOSの構造：Docs（ガイド）と Artifacts（実体）**

このOSは「ドキュメント」だけではなく、ドキュメントに対応する **実体（リポジトリ/生成物）** を含む“仕組み”である。  
以降では、ドキュメント群を **Docs**、実体を **Artifacts** と呼ぶ。

### **0.1 Docs（ガイド・仕様・手順）**

* **01\_OS\_Overview（本書）**  
  思想・原則・フェーズ設計・責務分担・ゲート・教育の全体像を示す「地図」。  
  読者：全員（新規参加者、意思決定者、運用者）  
* **02\_OS\_Template\_Spec**  
  OS Template Repo に何を入れるか（ディレクトリ、テンプレ、CI/教育、init仕様）、それをどのように作成するか（背景、目的、効果など）を定義する「設計図」。  
  読者：テンプレを育てる人（プラットフォーム担当）  
* **03\_Project\_Instance\_Guide**  
  OS Template Repoから新規プロジェクト（Project Instance）を作り、運用開始するための「手順書」。  
  読者：新プロジェクト立ち上げ担当

  ### **0.2 Artifacts（実体・使い回す資産）**

* **OS Template Repo（テンプレリポ）**  
  “プロジェクトの起点”となる実体。各プロジェクトはここから作られる。  
  含むもの：ドキュメントテンプレ、GitHubテンプレ、CI/Guardrail/LCG、initスクリプト  
* **Project Instance（各プロジェクト実体）**  
  テンプレから生成されるプロジェクト固有の実体。開発はここで行う。  
  含むもの：vision/architecture/typesなどの固有文脈＋プロジェクト固有のコード

要点：01/02/03は「読むもの」。Template Repo / Project Instanceは「動くもの」。

---

## **0.3 開始フロー（Template → Instance）**

新規プロジェクトの開始は次の流れを標準とする：

1. OS Template Repo を GitHub Template として新規リポジトリを作成  
2. clone して `scripts/init` を実行  
3. Phase 0（準備完了条件：DoR）を満たす（CIが走る/最低限の安全/教育フォーマット）  
4. 最小縦切りIssueで ①〜⑥ を1周し、運用を開始  
5. 詰まりはOSへ還元してチューニング（テンプレも育てる）  
   ---

   ## **0.4 更新ポリシー（どれをいつ更新するか）**

* **01\_OS\_Overview**：思想・原則のため更新頻度は低め（ブレない軸）  
* **02\_OS\_Template\_Spec**：テンプレ改修時の基準（仕様変更に合わせて更新）  
* **03\_Project\_Instance\_Guide**：立ち上げ手順に合わせて更新（現場で読む頻度が高い）  
* **OS Template Repo**：改善の主戦場（仕組みとテンプレを育てる）  
* **Project Instance**：個別最適（ただし共通化できるならテンプレへ還元）  
  ---

  # **1\. 目的（Why）**

* AIで実装速度を上げつつ、セキュリティ/コンプラ/安全性を落とさない  
* 出先（ブラウザ）⇄ 自宅/オフィス（デスクトップ）で文脈を失わない  
* 初心者でも「仕組み」で堅牢さを担保し、同時に学べる状態を作る  
* ルール無視・コミット荒めでも破綻しない（ただし改善ループで寄せる）  
  ---

  # **2\. 問題設定（何に勝つOSか）**

* “動いた”が優先され、後から事故（回帰/漏洩/破壊）で手戻り  
* 文脈が会話に閉じて消える  
* レビューが属人化し、初心者が学べない/怖い  
* コミットやPRが巨大になって、品質担保が重くなる  
  ---

  # **3\. 基本原則（Principles）**

  ### **P1. Context-as-Code**

重要事項は会話ではなく、リポジトリのドキュメント/テンプレ/ログに落とす。

### **P2. Issue-Driven Development**

意図はIssueに落とす。Issueは命令書。成功率はIssueの品質で決まる。

### **P3. Two-Mode Work（A/B）**

* A（出先）＝検証・設計・指示化（QA/Architect）  
* B（自宅）＝実装・テスト・PR（Executor）

  ### **P4. Gates over Hope**

希望ではなく、pre-push / post-push / CI で品質を担保する。

### **P5. Guardrail teaches humans**

仕組み（ガードレール）が堅牢さを補正し、その過程が学習になる。

### **P6. Rules \+ Mechanisms \+ Fallbacks**

ルールは期待値。守らせる仕組みと、守れなくても壊れないフォールバックを必ず用意する。

### **P7. Small, sharp feedback**

教育/監査は「最大3点」「優先度つき」「次の一手が明確」。ノイズを増やさない。

---

# **4\. 役割分担（Claude Code / Antigravity / GitHub）**

## **4.1 QA/Architect & Reviewer（例：Claude Code）**

* 仕様×実装の整合確認、論理の穴出し  
* テスト観点（境界値/異常系）設計  
* Issueを命令書化（再現・方針・AC・Non-goals・Commit Plan）  
* ゲート担当（pre-push / post-push）  
* 定期メンテ起票と改善ループ運用

  ## **4.2 Executor（例：Antigravity）**

* Issueに従って実装/修正  
* テスト実行→コミット→PR（可能な範囲で自律）

  ## **4.3 台帳（GitHub）**

* Issue：意図・再現・方針・ACの保管庫  
* PR：差分・合意・レビュー・議論の場  
* CI：品質ゲート（落ちたら原因が残る）  
  ---

  # **5\. 全体フロー：Phase 0 → ①〜⑥ → Tuning**

* **Phase 0（開始前の仕込み）**：文書だけでなく“仕組みが動く状態”を作る  
* **Iteration Cycle（①〜⑥）**：回し続ける開発の呼吸  
* **Tuning（改善）**：詰まりをOSへ還元し、仕組み側を賢くする  
  ---

  # **6\. Phase 0（事前準備）の全体像**

Phase 0は「資料を作る」ではなく、**サイクルが“運用可能”な状態**を作る。  
準備物は4カテゴリで定義する：

1. Documents（文脈/規約/テンプレ）  
2. Mechanisms（CI/CD・教育・監査・自動化）  
3. Settings（GitHub設定・権限・Secrets・ブランチ運用）  
4. Operations（運用ルール・メトリクス・改善ループ）

   ## **6.1 Phase 0 Minimum（DoR：準備完了条件）**

* PRを作るとCIが走り、失敗理由が見える  
* secrets混入を検知できる（止める or 警告）  
* 教育フィードバック（Summary+Quiz等）のフォーマットが決まっている

Phase 0の具体物（チェックリストやファイル配置）は 02\_OS\_Template\_Spec に定義する。

---

# **7\. ハンドオフ・プロトコル（文脈断絶を防ぐ）**

* 開始前：`.ai-context.md` を読んで同期  
* 終了後：`.ai-context.md` を更新して次の手が迷子にならない状態にする  
* 決定事項：仕様/再現/改善案はIssueへ、状態/次の手はcontextへ  
* ログ/失敗：CI落ち・テスト失敗・コンフリクトは教材（残す）  
  ---

  # **8\. ハイブリッド運用（A/B）**

  ## **8.1 A：出先（QA/Architect）**

* ビルドするより検証する  
* 仕様×実装整合、テスト設計、Issue命令書化

  ## **8.2 B：自宅（Executor）**

* Antigravityで実装を進める  
* ゲート（pre-push / post-push / CI）で品質を締める  
  ---

  # **9\. Iteration Cycle：①〜⑥（回し続ける工程）**

  ## **① Spec & QA（命令書Issueを作る）**

* 仕様の穴、境界値、矛盾、影響範囲を潰す  
* 出力：再現/方針/AC/Non-goals/Commit Planが揃ったIssue

  ## **② Execute（実装）**

* Issueどおりに実装→テスト→コミット/PR  
* コミットが粗くなっても、後段の仕組みで吸収する（ただし改善は狙う）

  ## **③ Pre-Push Gate**

* lint/typecheck/unit test  
* 過剰変更・スコープ逸脱・テスト不足を止める  
* 不足はIssue追記で残す

  ## **④ Post-Push Gate**

* CI確認：落ちたら原因→Issue化  
* PRレビュー：What/Why/Test/Risk/Rollback  
* “今回やらない改善”は次Issueへ

  ## **⑤ Maintenance & Grooming**

* 負債棚卸し、依存更新、flaky対処  
* 指摘傾向を仕組みへ反映（規約/テンプレ/型/ガードレール/教材）

  ## **⑥ Fix**

* 再現＋ACが揃ったIssueから確実に潰す  
* テスト追加で再発を防ぐ  
  ---

  # **10\. Guardrail & Education Layer（AIガードレール×教育）**

  ## **10.1 二段構え**

* 攻め：IDE実装支援AI（速度最適化）  
* 守り：監査AI（第三者視点で安全性/コンプラ/品質を検証し、教育コメントを返す）

  ## **10.2 教育コメント規格（固定フォーマット）**

* Summary / Severity（BLOCKER〜NIT）/ Finding / Why（比喩OK）/ Fix direction / Example（最小）/ Learn more

  ## **10.3 ブロック方針（最小）**

* BLOCKER/HIGHだけ止める（事故るものだけ）  
* それ以外は学習用コメント（止めすぎない）  
  ---

  # **11\. Commit Strategy & Stability（コミット戦略）**

Antigravityや“前に進みたい”モードはルール無視が起きる。  
だから「理想のルール」ではなく **壊れない設計**として定義する。

* 原則（期待値）：1コミット=1意図、可能なら自己完結、巨大コミット回避  
* 誘導：IssueにCommit Planを必須化（1〜3コミット想定を明記）  
* 仕組み：巨大差分/巨大コミットはまず警告→必要なら段階導入でブロック  
* フォールバック：粗くても学習（LCG）が破綻しない（対象上位Nに絞る）  
  ---

  # **12\. Learning Content Generator（コミット教材化）**

エラーが消えている（綺麗な）状態でも学べるように、**実装を教材に変換**する。

* トリガー：commit / PR更新  
* 出力：Summary \+ Deep Dive（上位N部品） \+ Quiz（最大3問） \+ Explore next  
* 運用：PRコメントは短く（Summary+Quiz）、長文はArtifactやdocsへ退避  
* ノイズ制御：最大N部品、最大3問、巨大コミットは要約優先  
  ---

  # **13\. チューニング（改善の回し方）**

詰まりが出たら「人を注意」ではなく **仕組みを更新**する。

* 指示が弱い → Issueテンプレ/AC/Commit Planを強化  
* ゲートが弱い → CI/チェックを強化  
* 教育が弱い/うるさい → 出力量（最大3点）とトリガーを調整  
* 同じ指摘が3回 → `.ai-instructions.md` / templates / types / guardrail / LCG を更新  
  ---

  # **14\. 01/02/03 と Artifacts の関係（まとめ）**

* **01（本書）**：全体像（地図）  
* **02**：OS Template Repoの仕様（設計図）→ **Artifact：OS Template Repo**  
* **03**：TemplateからInstanceを作って走り出す手順（手順書）→ **Artifact：Project Instance**  
  ---

