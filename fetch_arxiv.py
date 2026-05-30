import json
import os
import socket
from datetime import datetime
from logging import getLogger

import arxiv
import requests
from deep_translator import GoogleTranslator

log = getLogger(__name__)

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


def main():
    # Construct the default API client.
    client = arxiv.Client()

    # Search for the 10 most recent articles matching the keyword "quantum."
    search = arxiv.Search(
        query="ti:quantum AND ti:annealing AND ti:optimization",
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
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
    main()
