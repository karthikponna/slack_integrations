import os
import asyncio
import json
import warnings
from typing import List
from pydantic import BaseModel

from agents import (
    Agent,
    ItemHelpers,
    MessageOutputItem,
    RunContextWrapper,
    Runner,
    ToolCallItem,
    ToolCallOutputItem,
    TResponseInputItem,
    function_tool,
    FunctionTool,
)

from src.slack_integrations_online.application.agents.tools.memory_tools import add_to_memory, search_memory
from src.slack_integrations_online.application.agents.tools.monogdb_retriever_tools import mongodb_retriever_tool, get_complete_docs_with_url

warnings.filterwarnings("ignore", category=DeprecationWarning)


INSTRUCTIONS="""You are a helpful agent that uses tools to answer user queries accurately.

**Step 1: Identify User Intent**
Determine if the user is asking about their previous memories/conversations or asking a new question.

**If user is asking about memories:**
- Use search_memory tool to retrieve relevant memories
- Provide the response based on retrieved memories
- Do NOT use other tools

**If user is asking a new question:**
1. First, use search_memory to check for relevant past context
2. Use mongodb_retriever_tool to search for relevant documents
3. Answer using ONLY information from the retrieved documents
4. If the chunks lack detail, use get_complete_docs_with_url to fetch complete documents
5. Finally, use add_to_memory to store this interaction for future reference

**Guidelines:**
- Be concise and accurate
- Quote relevant parts from documents when appropriate
- If information is not found, say "I don't have enough information to answer this question"
- Always cite document URLs in your final answer at the end, when using information from documents
- Only use get_complete_docs_with_url when chunks are relevant to the query but lack sufficient detail or context
"""



def get_agent() -> "AgentWrapper":
    pass


class AgentWrapper:

    @classmethod
    def building_agents(cls) -> "AgentWrapper":

        agent = Agent(
        name = "Mongodb Agent",
        instructions=INSTRUCTIONS,
        tools = [search_memory, mongodb_retriever_tool, get_complete_docs_with_url, add_to_memory],
        model = "o4-mini",
    )
