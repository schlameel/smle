import requests
from smle.notification.service import Service
from typing import Literal

class Telegram(Service):
    """Telegram notification service using webhooks."""

    def __init__(
        self,
        parse_mode: Literal["Markdown", "HTML"] | None=None
    ):
        """Initialize Telegram service.

        Args:
            bot_token: Telegram bot token. If None, reads from TELEGRAM_BOT_TOKEN env var.
            chat_id: Telegram chat ID. If None, reads from TELEGRAM_CHAT_ID env var.

        Raises:
            ValueError: If webhook URL is not provided or found in environment.
        """
        super().__init__()

        telegram_api = self._keystore.get_key("TELEGRAM_SECRET")
        self._parse_mode = parse_mode
        self._telegram_api_url = f"https://api.telegram.org/bot{telegram_api}/sendMessage"

    def send_notification(self, message: str) -> None:
        """Send notification to Telegram chat.

        Args:
            message: The message to send.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """

        raise Exception("TODO: NOT IMPLEMENTED YET")

        data = {
            "chat_id": self._chat_id,
            "text": message,
            "disable_notification": False,
        }
        if self._parse_mode:
            data["parse_mode"] = self._parse_mode

        result = requests.post(self._telegram_api_url, json=data, timeout=10)
        result.raise_for_status()


        params = {}
        if self._parse_mode:
            params["parse_mode"] = self._parse_mode
        data = {
            "chat_id": self._chat_id,
            "text": message,
            "disable_notification": False,
        }

        try:
            result = requests.post(self._telegram_api_url, json=data, params=params, timeout=10)
            result.raise_for_status()
        except requests.exceptions.RequestException as err:
            raise requests.exceptions.RequestException(f"Failed to send Telegram notification: {err}")
