# Daily arXiv Notification Bot

毎日指定した時間にarXivから特定のキーワードやカテゴリに関連する最新論文のリストを取得し、日本語に自動翻訳してDiscordへ通知する自動化スクリプトです。
GitHub Actionsを利用しているため、**完全無料・サーバーレス（常時起動のサーバー不要）**で運用できます。

---

## 🛠️ 機能概要
- **定期自動実行**: GitHub Actionsのスケジュール機能（`cron`）により、毎日1日1回自動で実行。
- **論文の自動取得**: `arxiv` ライブラリを用いて、設定したクエリ（例: "Large Language Models"、"Vision Transformer" など）の最新論文を検索。
- **日本語自動翻訳**: `deep-translator` ライブラリを使用して、論文のタイトルを自動で翻訳。
- **Discord通知**: Discord of Webhook機能を利用し、専用チャンネルへ即座に通知。
- **安全な認証情報管理**: Webhook URLなどの秘匿情報は「GitHub Secrets」で安全に管理。

---

## 📂 構成ファイル

プロジェクトは以下の2つのファイルのみで最小構成されています。

1. **`fetch_arxiv.py`** (Pythonスクリプト)
   - arXiv APIからデータを取得・翻訳し、Discordへ送信するメインロジック。
2. **`.github/workflows/arxiv_bot.yml`** (GitHub Actions設定ファイル)
   - 実行スケジュール（トリガー）や、実行環境（Ubuntu、Python環境の構築、依存ライブラリのインストール）を定義。

---

## 🚀 導入手順

### 1. リポジトリの準備
1. GitHubで新しいリポジトリ（PublicまたはPrivate）を作成します。
2. 本プロジェクトの `fetch_arxiv.py` と `.github/workflows/arxiv_bot.yml` をリポジトリに配置（プッシュ）します。

### 2. Discord Webhook URLの取得
1. 通知を受け取りたいDiscordサーバーのチャンネル設定を開きます。
2. **「連携サービス」 ＞ 「ウェブフック」** から新しいWebhookを作成し、URLをコピーします。

### 3. GitHub Secrets の設定（最重要）
1. GitHubのリポジトリ画面から **[Settings]** タブ ＞ 左メニューの **[Secrets and variables]** ＞ **[Actions]** をクリックします。
2. **[New repository secret]** ボタンを押し、以下を設定します。
   - **Name**: `DISCORD_WEBHOOK_URL`
   - **Secret**: （コピーしたDiscordのWebhook URLを貼り付け）

---

## ⚙️ カスタマイズ方法

### 検索キーワードの変更 (`fetch_arxiv.py`)
論文の検索キーワードを変更したい場合は、`arxiv.Search` 内の `query` 引数を書き換えてください。
```python
search = arxiv.Search(
    query="\"Large Language Models\"",  # 欲しいキーワードやカテゴリに変更
    max_results=3,                     # 取得する最大件数
    sort_by=arxiv.SortCriterion.SubmittedDate
)