import os
import json
import warnings

from agents import (
    Agent,
    Runner,
    FunctionTool,
    gen_trace_id,
    trace,
)
from loguru import logger

from src.slack_integrations_online.application.agents.tools.memory_tools import add_to_memory, search_memory, Mem0Context
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

agent = Agent(
    name = "Mongodb Agent",
    instructions=INSTRUCTIONS,
    tools = [search_memory, mongodb_retriever_tool, get_complete_docs_with_url, add_to_memory],
    model = "o4-mini",

)

logger.info("Initializing agent with the following tools:")
for tool in agent.tools:
    if isinstance(tool, FunctionTool):
        logger.info(f"Tool name: {tool.name}")
        logger.info(f"Tool description: {tool.description}")
        logger.info(f"Tool parameters: {json.dumps(tool.params_json_schema, indent=2)}")


class SupportAgentsManager():
    """Manager for running support agents with memory context and trace logging."""
    
    def __init__(self) -> None:
        pass

    async def run(self, query:str, user_id: str = "default_user") -> None:
        
        trace_id = gen_trace_id()

        try:

            with trace("Support Agents Trace", trace_id=trace_id):

                logger.info("Starting the agent run")
                logger.info(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
                context = Mem0Context(user_id=user_id)
                result = await Runner.run(agent, input=f"User query: {query}", context=context)

                final_output = result.final_output
                logger.info(f"Agent response: {final_output}")

                return final_output

        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")