import json
import os
import socket
from datetime import datetime
from logging import getLogger

import arxiv
import requests
import typer
from deep_translator import GoogleTranslator

log = getLogger(__name__)

app = typer.Typer()
translator = GoogleTranslator(source="en", target="ja")


class DiscordWebhook:
    """DiscordのWebhook URLとチャンネルを指定して、メッセージを送信するクラス"""

    def __init__(self, url: str):
        """DiscordのWebhook URLとチャンネルを指定して初期化する。

        Args:
            url (str): DiscordのWebhook URL
            channel (str): メッセージを送信するDiscordのチャンネル名（例: "#general"）
        """
        if not url:
            raise ValueError("Webhook URLを指定してください")
        if not url.startswith("https://discordapp.com/api/webhooks/"):
            raise ValueError("Webhook URLが正しくありません")
        self.url = url

        self.hostname = socket.gethostname()
        self.icon_emoji = ":desktop_computer:"
        self.current_time = datetime.now().strftime("%Y/%m/%d-%H時%M分")

    def send(
        self, title: str, message: str, footer: bool = True, footer_text: str = ""
    ) -> None:
        """Discordにメッセージを送信する。

        Args:
            title (str): メッセージのタイトル
            message (str): メッセージの内容
            footer (bool): フッターを表示するかどうか
        """
        footer_data = (
            {}
            if not footer
            else {
                "text": self.current_time + "\n" + footer_text,
                "icon_url": "https://cdn.discordapp.com/embed/avatars/2.png",
            }
        )
        payload = {
            "username": str(self.hostname),
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": 0x00FF00,
                    "footer": footer_data,
                }
            ],
        }
        response = requests.post(
            self.url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        # エラーが出たらプリント
        if response.status_code == 204:
            log.info("メッセージを送信しました")
        else:
            log.error(f"エラーが発生しました: {response.status_code}")


def build_query(keywords: list[str], target: str = "all") -> str:
    """
    target:
      - "all": タイトル・概要など全体
      - "ti": タイトルのみ
      - "abs": 概要のみ
    """
    return " AND ".join(f'{target}:"{kw}"' for kw in keywords)


@app.command()
def fetch_arxiv_papers(
    keywords: list[str] = typer.Option(
        ["quantum", "annealing", "optimization"],
        "-k",
        "--keywords",
        help="検索キーワードのリスト。デフォルトは ['quantum', 'annealing', 'optimization']",
    ),
    webhook_url: str = typer.Option(
        None, "-w", "--webhook-url", help="DiscordのWebhook URL"
    ),
):  # Construct the default API client.
    client = arxiv.Client(
        page_size=10,
        delay_seconds=10.0,
        num_retries=5,
    )

    # Search for the 10 most recent articles matching the keyword "quantum."
    search = arxiv.Search(
        query=build_query(keywords, target="ti"),
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    WEBHOOK_URL = webhook_url or os.environ.get("DISCORD_WEBHOOK_URL")
    if not WEBHOOK_URL:
        raise ValueError("環境変数 'DISCORD_WEBHOOK_URL' が設定されていません")
    discord_bot = DiscordWebhook(url=WEBHOOK_URL)

    results = client.results(search)

    message_content = ""
    for result in results:
        log.info("Starting to process result.")
        message_content += f"🔹 **{result.title}**\n"
        message_content += f"🔗 URL: {result.entry_id}\n"
        log.info("Starting to send message for result.")
        discord_bot.send(
            title=result.title,
            message=translator.translate(
                "【"
                + result.title
                + "】\n \n"
                + result.summary
                + "\n"
                + result.entry_id
            ),
            footer_text=result.entry_id,
        )
    discord_bot.send(title="📚 **本日のarXiv新着関連論文** 📚", message=message_content)


if __name__ == "__main__":
    typer.run(fetch_arxiv_papers)
