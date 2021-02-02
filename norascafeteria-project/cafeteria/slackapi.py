import asyncio
import logging

from django.conf import settings
from slack import WebClient
from slack.errors import SlackApiError


# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger(__name__)


def send_async_notification(message):
    client = WebClient(
        token=settings.SLACK_API_TOKEN,
        run_async=True
    )

    future = client.chat_postMessage(
        channel=settings.CHANNEL,
        text=message
    )
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(future)
    except SlackApiError as e:
        logger.error(f"Got an error: {e}")
        # This will notify the admin that something is wrong with the slack configuration
        raise e
    except Exception as e:
        logger.error(f"Error {e}")
        raise e
    finally:
        loop.close()
