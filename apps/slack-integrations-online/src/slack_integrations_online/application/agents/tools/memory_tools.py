import os
from mem0 import AsyncMemory
from openai import AsyncOpenAI
from pydantic import BaseModel

from mem0.configs.base import MemoryConfig, EmbedderConfig, VectorStoreConfig, LlmConfig
from agents import (
    RunContextWrapper,
    function_tool,
)

from src.slack_integrations_online.config import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY


custom_config = MemoryConfig(
    embedder=EmbedderConfig(
        provider="openai",
        config={
            "model": "text-embedding-3-small",
        }
    ),
    llm=LlmConfig(
        provider="openai",
        config={
            "model": "gpt-4o-mini",
            "temperature": 0.0,
        }
    ),
    vector_store=VectorStoreConfig(
        provider="mongodb",
        config={
            "db_name": settings.MONGODB_DATABASE_NAME,
            "collection_name": "mem0-collection",
            "mongo_uri": settings.MONGODB_URI
        }
    )
)


openai_client = AsyncOpenAI()
memory = AsyncMemory(config=custom_config)


class Mem0Context(BaseModel):
    user_id: str | None = None


@function_tool
async def search_memory(
    context: RunContextWrapper[Mem0Context],
    query: str
) -> str:
    """
    Search for memories
    Args:
        query: The search query.
    """
    
    user_id = context.context.user_id or "default_user"
    memories = await memory.search(query, user_id=user_id, limit=3)

    results = '\n'.join([result["memory"] for result in memories["results"]])

    return str(results)


@function_tool
async def add_to_memory(
    context: RunContextWrapper[Mem0Context],
    content: str,
) -> str:
    """
    Add a message to memory
    Args:
        content: The content to store in memory.
    """
    messages = [{"role": "user", "content": content}]
    user_id = context.context.user_id or "default_user"
    await memory.add(messages, user_id=user_id)
    return f"Stored message: {content}"