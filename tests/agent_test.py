import asyncio
import os
from typing import Literal
from dotenv import load_dotenv
load_dotenv()

from tavily import TavilyClient
from loguru import logger

from cli_agent.config import get_settings
from cli_agent.agent.main_agent import Agent
from cli_agent.agent.prompts import INSTRUCTIONS

logger = logger.bind(name="Agent Testing")
settings = get_settings()
print(os.environ["OPENAI_API_KEY"])
print(os.environ["TAVILY_API_KEY"])
print(os.environ["PIXELTABLE_HOME"])

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


# Search tool to use to do research
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


async def main():
    agent = Agent(
        model_name=settings.MODEL,
        tools=[internet_search],
        system_prompt=INSTRUCTIONS,
    )

    await agent.setup()

    prompt = "Please use the write_file tool to write 'Hello' to an arbitrary 'README.md' file, then write 'Bye' to an arbitrary 'BYE.md' file and finally respond back to me when you are done."
    async for chunk in agent.chat(prompt):
        logger.info(chunk)

    try:
        while True:
            await asyncio.sleep(0.1)
    finally:
        agent.reset_memory()


if __name__ == "__main__":
    asyncio.run(main())