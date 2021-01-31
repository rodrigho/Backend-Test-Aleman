import asyncio

from django.conf import settings
from slack import WebClient
from slack.errors import SlackApiError


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
        # run_until_complete returns the Future's result, or raise its exception.
        response = loop.run_until_complete(future)
        assert response["message"]["text"] == message
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
    except Exception as e:
        print(f"Error {e}")
    finally:
        loop.close()

    print("Done")
