> **[ARCHIVED]** このドキュメントは 2026-03-17 にアーカイブされました。
> Antigravity（Gemini Code Assist）拡張機能を前提とした内容のため、シングルエージェント移行（Antigravity廃止）により陳腐化しています。
> 現行の Claude Code 向けガイドは [`docs/remote-dev-setup-guide.md`](../remote-dev-setup-guide.md) を参照してください。

---

# [ARCHIVED] リモート開発環境セットアップガイド（Antigravity版）

自宅MacBookを出先（iPhone/iPad）から安全に操作し、Antigravity（Gemini Code Assist）で開発を行うための手順書です。

---

## 全体構成

```
出先（iPhone / iPad）
  │
  ├─ ブラウザ → vscode.dev（VS Code Remote Tunnel）  ← メイン作業
  ├─ ターミナルアプリ → SSH（Tailscale経由）          ← git操作・コマンド実行
  └─ VNCアプリ → 画面共有（Tailscale経由）            ← GUI必要時のみ
  │
  ↕  暗号化トンネル（Tailscale / Microsoft Tunnel）
  │
自宅 MacBook
  ├─ VS Code + Antigravity 拡張機能
  ├─ SSH サーバー
  └─ 画面共有（VNC）
```

---

## Part 1: Tailscale のセットアップ（VPN基盤）

Tailscaleは、自宅MacとiPhone/iPadを安全な仮想ネットワークでつなぐツールです。
ポート開放やルーター設定が不要で、インストールするだけで使えます。

### 1.1 アカウント作成

1. ブラウザで [https://tailscale.com](https://tailscale.com) にアクセス
2. 「Get Started」をクリック
3. Google / Microsoft / GitHub アカウントでサインアップ（どれでもOK）
4. 無料プラン（Personal）で十分です

### 1.2 自宅MacBookにインストール

1. [https://tailscale.com/download/mac](https://tailscale.com/download/mac) からダウンロード
2. `.dmg` ファイルを開き、Tailscale を `Applications` にドラッグ
3. Tailscale を起動
4. メニューバー（画面右上）にTailscaleアイコンが表示される
5. アイコンをクリック →「Log in」→ ブラウザが開くのでサインイン
6. 接続されると、Mac に固有のIPアドレス（例: `100.x.x.x`）が割り当てられる

> **確認方法**: メニューバーのTailscaleアイコンをクリックすると、自分のIPアドレスが表示されます。これをメモしておいてください。

### 1.3 iPhone / iPad にインストール

1. App Store で「Tailscale」を検索してインストール
2. アプリを起動 →「Sign in」→ 同じアカウントでログイン
3. VPN構成の許可を求められるので「Allow（許可）」をタップ
4. 接続されると、iPhone/iPad にも固有IPが割り当てられる

### 1.4 接続テスト

iPhone/iPad のTailscaleアプリで、自宅MacのIPアドレスが表示されていればOKです。
（「My Devices」に Mac と iPhone/iPad の両方が表示される状態）

---

## Part 2: VS Code Remote Tunnel のセットアップ（メイン作業環境）

これが一番よく使う方法です。出先のブラウザから、自宅MacのVS Codeをそのまま操作できます。

### 2.1 自宅Macでの準備

#### Step 1: VS Code がインストール済みか確認

ターミナルを開いて以下を実行：

```bash
code --version
```

バージョン番号が表示されればOK。表示されない場合は [https://code.visualstudio.com](https://code.visualstudio.com) からインストールしてください。

#### Step 2: `code` コマンドをPATHに追加（未設定の場合）

VS Codeを開き、`Cmd + Shift + P` → 「Shell Command: Install 'code' command in PATH」を選択。

#### Step 3: Remote Tunnel を起動する

ターミナルで以下を実行：

```bash
code tunnel
```

初回実行時に以下が起きます：

1. **利用規約の同意**: `y` を入力して Enter
2. **認証方法の選択**: 「Microsoft Account」か「GitHub Account」を選択（矢印キーで選んで Enter）
3. **認証コード**: 画面に8文字のコードが表示される
4. **ブラウザ認証**: 表示されたURL（`https://github.com/login/device` など）にアクセスし、コードを入力してサインイン
5. **トンネル名の入力**: Macの名前を入力（例: `my-macbook`）。後から識別に使います

成功すると以下のようなメッセージが表示されます：

```
Open this link in your browser https://vscode.dev/tunnel/my-macbook
```

#### Step 4: トンネルをバックグラウンドで常駐させる（重要）

外出中もトンネルが動いている必要があります。以下のコマンドでサービスとして登録します：

```bash
code tunnel service install
```

これで Mac を再起動してもトンネルが自動起動します。

> **停止したいとき**:
> ```bash
> code tunnel service uninstall
> ```

### 2.2 出先（iPhone / iPad）からの接続

1. Safari または Chrome で以下にアクセス：
   ```
   https://vscode.dev/tunnel/my-macbook
   ```
   （`my-macbook` は Step 3 で設定した名前に置き換え）

2. Microsoft または GitHub アカウントでサインイン
3. 自宅MacのVS Codeがブラウザ上に表示される
4. **Antigravity 拡張機能もそのまま使えます**

### 2.3 iPadでの操作のコツ

- **外付けキーボード推奨**: Apple Magic Keyboard や Bluetooth キーボードがあると快適
- **ショートカット**: `Cmd + Shift + P` でコマンドパレットが開く（Macと同じ）
- **ターミナル**: VS Code 内蔵ターミナル（`` Ctrl + ` ``）でgit操作もできる
- **画面分割**: iPadOS の Split View で、ブラウザ（VS Code）+ メモアプリなどを並べて使える

---

## Part 3: SSH のセットアップ（ターミナル操作用）

VS Code Remote Tunnel 内のターミナルでもコマンドは打てますが、
純粋なターミナル操作（git操作やスクリプト実行）はSSHの方が快適な場合もあります。

### 3.1 自宅MacでSSHを有効化

1. 「システム設定」→「一般」→「共有」を開く
2. 「リモートログイン」をONにする
3. 「次のユーザのみアクセスを許可」が選択されていることを確認（自分のユーザー名が入っている）

### 3.2 SSH鍵認証の設定（パスワード認証より安全）

#### 自宅Macで鍵ペアを生成（まだ作っていない場合）

```bash
# 鍵を生成（Enter連打でOK。パスフレーズはお好みで）
ssh-keygen -t ed25519 -C "my-remote-key"
```

以下の2ファイルが作られます：
- `~/.ssh/id_ed25519`（秘密鍵 — 絶対に外に出さない）
- `~/.ssh/id_ed25519.pub`（公開鍵 — サーバー側に置く）

#### 公開鍵を登録

```bash
# 公開鍵を authorized_keys に追加
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### パスワード認証を無効化（推奨）

```bash
# SSH設定ファイルを編集
sudo nano /etc/ssh/sshd_config
```

以下の行を探して変更（行頭の `#` があれば外す）：

```
PasswordAuthentication no
KbdInteractiveAuthentication no
```

変更を保存（`Ctrl + O` → Enter → `Ctrl + X`）してから、SSHを再起動：

```bash
# macOS Ventura以降
sudo launchctl kickstart -k system/com.openssh.sshd
```

### 3.3 iPhone / iPad に秘密鍵を転送

**方法A: AirDrop（最も簡単）**

1. Finderで `~/.ssh/id_ed25519` を見つける（`Cmd + Shift + .` で隠しファイルを表示）
2. AirDropでiPhone/iPadに送信
3. 受信したファイルをSSHアプリにインポート

**方法B: iCloud Drive経由**

1. 秘密鍵をiCloud Driveにコピー
2. iPhone/iPadのSSHアプリからインポート
3. **インポート後、iCloud Drive上の秘密鍵は必ず削除してください**

### 3.4 iPhone / iPad の SSH クライアントアプリ

| アプリ名 | 料金 | 特徴 |
|---------|------|------|
| **Termius** | 無料（基本機能） | UIが綺麗、鍵管理が簡単 |
| **Blink Shell** | 有料（買い切り） | 高機能、mosh対応、プロ向け |
| **a-Shell** | 無料 | ローカルシェルもある |

#### Termius での接続設定例

1. アプリを開く →「New Host」
2. 以下を入力：
   - **Alias**: `My MacBook`（好きな名前）
   - **Hostname**: Tailscaleで割り当てられたIP（例: `100.x.x.x`）
   - **Username**: Macのユーザー名
   - **Key**: インポートした秘密鍵を選択
3. 「Connect」をタップ

### 3.5 接続テスト

```bash
# 接続できたら、プロジェクトディレクトリに移動
cd ~/path/to/AI-First-Development-Operating-System

# 状態確認
git status

# Antigravity（Gemini CLI）が使えるか確認
# （ターミナルベースのGemini操作がある場合）
```

---

## Part 4: 画面共有（VNC）のセットアップ（GUI必要時のみ）

VS Code Remote Tunnel で大半の作業はできますが、
Antigravityの一部GUI操作やデバッグ画面を見たい場合に使います。

### 4.1 自宅Macで画面共有を有効化

1. 「システム設定」→「一般」→「共有」を開く
2. 「画面共有」をONにする
3. 「次のユーザのみアクセスを許可」が選択されていることを確認

### 4.2 iPhone / iPad のVNCクライアントアプリ

| アプリ名 | 料金 | 特徴 |
|---------|------|------|
| **Screens 5** | 有料（サブスク or 買い切り） | Mac特化、操作性◎ |
| **Jump Desktop** | 有料（買い切り） | 安定性が高い |
| **RealVNC Viewer** | 無料 | シンプル |

#### 接続設定

1. アプリを開く → 新しい接続を追加
2. **アドレス**: TailscaleのIP（例: `100.x.x.x`）
3. **ユーザー名 / パスワード**: Macのログインアカウント
4. 接続するとMacの画面がiPadに表示される

---

## Part 5: セキュリティ設定（不在中の保護）

これが最も重要な部分です。以下をすべて設定してください。

### 5.1 スクリーンロックの自動化

```
システム設定 → ロック画面
```

| 設定項目 | 推奨値 |
|---------|--------|
| スクリーンセーバを開始する時間 | 5分 |
| ディスプレイをオフにする時間 | 10分 |
| スクリーンセーバ開始後またはディスプレイがオフになった後にパスワードを要求 | **すぐに** |

### 5.2 スリープさせずにディスプレイだけオフにする設定（重要）

リモート接続するには Mac が起きている必要がありますが、
画面は消えていてもOKです。

```
システム設定 → バッテリー → オプション
```

- 「電源アダプタ接続中のスリープを防ぐ」→ ON（可能であれば）

または、ターミナルで以下を実行：

```bash
# スリープを無効化（電源接続時のみ推奨）
sudo pmset -c sleep 0
sudo pmset -c displaysleep 10

# 確認
pmset -g
```

> **意味**: Mac本体はスリープしない（リモート接続可能）が、ディスプレイは10分で消える（省エネ＋覗き見防止）

### 5.3 ファイアウォールの有効化

```
システム設定 → ネットワーク → ファイアウォール
```

- ファイアウォールを **ON** にする
- 「外部からの接続をすべてブロック」は **OFF** のまま（SSH/VNCが使えなくなるため）
- Tailscale経由の接続のみ許可される状態になるので安全です

### 5.4 Tailscale の追加セキュリティ

Tailscale管理画面（[https://login.tailscale.com/admin](https://login.tailscale.com/admin)）で以下を設定：

1. **デバイスの確認**: 「Machines」タブで、自分のデバイスだけが登録されていることを確認
2. **鍵の有効期限**: デバイスの鍵に有効期限を設定できる（デフォルトは180日）
3. **ACL（アクセス制御）**: 個人利用ならデフォルトのまま（全デバイス間で通信可能）でOK

### 5.5 Find My の有効化

```
システム設定 → Apple ID → 探す
```

- 「Macを探す」→ ON
- 万が一のときにリモートロック・ワイプが可能

---

## Part 6: 日常の運用フロー

### 外出前（自宅で）

```
1. MacBookを電源に接続
2. Tailscale が接続中であることを確認（メニューバーのアイコン）
3. VS Code Remote Tunnel が動いていることを確認
   → code tunnel service install 済みなら自動で起動している
4. MacBookの蓋を開けたまま or クラムシェルモード
   （外部ディスプレイ不要。蓋を閉じるとスリープするので注意）
```

> **蓋を閉じてもスリープさせない方法**:
> 外部ディスプレイ・キーボード・マウスが接続されていれば、蓋を閉じてもスリープしません（クラムシェルモード）。
> それ以外の場合は、`Amphetamine`（Mac App Store無料）等のアプリでスリープを防止できます。

### 出先で作業開始

```
1. iPhone/iPadでTailscaleアプリを開く → 接続を確認
2. ブラウザで https://vscode.dev/tunnel/my-macbook にアクセス
3. サインインして作業開始
4. 必要に応じてSSHやVNCも併用
```

### 作業終了

```
1. VS Code で .ai-context.md を更新（OS のハンドオフ・プロトコル）
2. 変更をコミット＆プッシュ
3. ブラウザのタブを閉じる（Mac側のトンネルはそのまま動き続ける）
```

---

## トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| vscode.dev に接続できない | Macがスリープしている | 自宅に連絡してMacを起こしてもらう / Amphetamine等で防止 |
| vscode.dev に接続できない | トンネルが停止している | `code tunnel service install` を再実行 |
| SSH接続がタイムアウト | Tailscaleが未接続 | 両方のデバイスでTailscaleアプリを開いて再接続 |
| VNCが遅い | 回線が細い | 画質を下げる設定にする / SSH+VS Code Tunnelに切り替え |
| Macのパスワードを忘れた | — | Apple IDでリセット可能 |
| 操作中に画面がロックされる | 自動ロックの設定 | リモート操作中はマウスを動かすか、ロック時間を延長 |

---

## 費用まとめ

| 項目 | 費用 |
|------|------|
| Tailscale（Personal） | **無料** |
| VS Code Remote Tunnel | **無料** |
| SSH（macOS標準） | **無料** |
| 画面共有（macOS標準） | **無料** |
| Termius（SSHアプリ・基本機能） | **無料** |
| Screens 5 等（VNCアプリ）※必要な場合のみ | 2,000〜4,000円程度 |

**基本構成はすべて無料で実現可能です。**
