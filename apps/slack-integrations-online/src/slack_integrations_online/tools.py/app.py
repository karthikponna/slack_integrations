import asyncio
from pathlib import Path

from src.slack_integrations_online.application.agents import SupportAgentsManager


async def main(user_query):
    agent = SupportAgentsManager()

    await agent.run(query=user_query)


if __name__=="__main__":
    user_query = f'Enter: {input()}'
    asyncio.run(main(user_query=user_query))