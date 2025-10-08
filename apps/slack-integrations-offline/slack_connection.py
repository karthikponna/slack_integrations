import os
import asyncio
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

slack_token = os.getenv("SLACK_BOT_TOKEN")
client = WebClient(token=slack_token)

if not slack_token:
    raise RuntimeError("SLACK_BOT_TOKEN not set in environment")

async def send_message():
    try:
        response = client.chat_postMessage(
            channel="C09K6JPAVQ9",
            text="Hello world :tada:"
        )

        return response

    except SlackApiError as e:
        assert e.response["error"]  

if __name__=="__main__":
    asyncio.run(send_message())