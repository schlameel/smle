import os
import requests
from .services.service import Service


class Slack(Service):
    """Slack notification service using webhooks."""
    
    def __init__(self, webhook_url: str = None):
        """Initialize Slack service.
        
        Args:
            webhook_url: Slack webhook URL. If None, reads from SLACK_WEBHOOK env var.
            
        Raises:
            ValueError: If webhook URL is not provided or found in environment.
        """
        self._webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK")
        if not self._webhook_url:
            raise ValueError("Slack webhook URL must be provided or set in SLACK_WEBHOOK environment variable")

    def send_notification(self, message: str) -> None:
        """Send notification to Slack channel.
        
        Args:
            message: The message to send.
            
        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        data = {
            "text": message,
            "username": "pysmle",
            "icon_emoji": ":robot_face:"
        }

        try:
            result = requests.post(self._webhook_url, json=data, timeout=10)
            result.raise_for_status()
        except requests.exceptions.RequestException as err:
            raise requests.exceptions.RequestException(f"Failed to send Slack notification: {err}")
