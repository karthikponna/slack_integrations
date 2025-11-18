import asyncio
import re
from pathlib import Path

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.errors import SlackApiError

from loguru import logger

from src.slack_integrations_online.application.agents import SupportAgentsManager
from src.slack_integrations_online.config import settings


slack_token = settings.SLACK_BOT_TOKEN
app_token = settings.SLACK_APP_TOKEN


client = SocketModeClient(
    app_token=app_token,
    web_client=WebClient(token=slack_token)
)


bot_user_id = None

async def get_bot_user_id():
    """Retrieve and cache the Slack bot's user ID via API authentication.
    
    Returns:
        str: The bot's Slack user ID.
    
    Raises:
        SlackApiError: If authentication or API call fails.
    """

    global bot_user_id

    try:
        response = client.web_client.auth_test()
        bot_user_id = response["user_id"]

        logger.info(f"Extracted bot user id: {bot_user_id}")
        return bot_user_id

    except SlackApiError as e:
        logger.error(f"Error getting bot user ID: {e.response['error']}")
        raise


async def extract_message_without_mention(text: str, bot_id: str) -> str:
    """Remove bot mentions and clean up message text.
    
    Args:
        text: Raw message text containing mentions.
        bot_id: Slack user ID of the bot to remove from mentions.
    
    Returns:
        str: Cleaned message text with mentions removed and whitespace normalized.
    """

    # Remove mention in format <@U12345>
    text = re.sub(f"<@{bot_id}>",'', text)
    
    # Remove any @mentions in plain text format
    text = re.sub(r"@\S+", '', text)

    text = ' '.join(text.split()).strip()

    return text


async def process_agent_query(query: str, channel: str, thread_ts: str = None):
    """Process user query through support agent and post response to Slack.
    
    Args:
        query: User's query text to process.
        channel: Slack channel ID to post response in.
        thread_ts: Thread timestamp for threaded replies. Defaults to None.
    
    Returns:
        Response object from Slack API, or None if error occurs.
    """

    try:

        agent = SupportAgentsManager()
        agent_response = await agent.run(query=query)

        if not agent_response:
            agent_response = "Didn't got a response from agent"

        agent_response = str(agent_response)

        # Add hint message at the end
        full_response = f"{agent_response}\n\n💡 *Hint:* Mention <@{bot_user_id}> in the thread for followups."


        response = client.web_client.chat_postMessage(
            channel=channel,
            text=full_response,
            thread_ts=thread_ts,
        )

        message_ts = response['ts']

        client.web_client.reactions_add(
            channel=channel,
            name="thumbsup",
            timestamp=message_ts
        )
        

        client.web_client.reactions_add(
            channel=channel,
            name="thumbsdown",
            timestamp=message_ts
        )

        return response


    except Exception as e:
        error_message = f"Sorry, got an error processing your request: {str(e)}"
        client.web_client.chat_postMessage(
            channel=channel,
            text=error_message,
            thread_ts=thread_ts
        )
        logger.error(f"Error processing query: {e}")



async def process_event(client: SocketModeClient, req: SocketModeRequest):
    """Handle incoming Slack Socket Mode events and route app mentions to agent.
    
    Args:
        client: Socket Mode client instance for Slack connection.
        req: Socket Mode request containing event payload.
    
    Returns:
        None
    """

    response = SocketModeResponse(envelope_id=req.envelope_id)
    client.send_socket_mode_response(response)


    if req.type == "events_api":
        event = req.payload.get("event", {})
        event_type = event.get("type")

        if event_type == "app_mention":

            channel = event.get("channel")
            text = event.get("text", "")
            user = event.get("user")
            thread_ts = event.get("thread_ts") or event.get("ts")


            if user == bot_user_id:
                return
            
            logger.info(f"Received mention in channel {channel}: {text}")

            query = await extract_message_without_mention(text=text, bot_id=bot_user_id)

            if query:

                logger.info(f"Extracted query: {query}")

                await process_agent_query(query=query, channel=channel, thread_ts=thread_ts)

            else:
                client.web_client.chat_postMessage(
                    channel=channel,
                    text="Please provide a query after mentioning me.",
                    thread_ts=thread_ts
                )


async def main():
    """Initialize and run the Slack bot with Socket Mode connection."""
    
    await get_bot_user_id()
    
    def event_handler(client: SocketModeClient, req: SocketModeRequest):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(process_event(client, req))
        else:
            asyncio.run_coroutine_threadsafe(process_event(client, req), loop)

    client.socket_mode_request_listeners.append(event_handler) # register event handler 

    logger.info("Slack bot is running")
    client.connect()

    await asyncio.Event().wait() # keeping the connection alive


if __name__=="__main__":
    asyncio.run(main())