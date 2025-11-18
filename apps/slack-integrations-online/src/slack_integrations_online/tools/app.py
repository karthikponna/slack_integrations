import asyncio
from pathlib import Path

from src.slack_integrations_online.application.agents import SupportAgentsManager


async def main(user_query):
    """Run the app in CLI mode"""
    agent = SupportAgentsManager()

    await agent.run(query=user_query)


if __name__=="__main__":
    print('\n' + '-'*50 + '\n')
    user_query = input("Enter your query: ")
    asyncio.run(main(user_query=user_query))