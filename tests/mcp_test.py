import asyncio
import json

from loguru import logger
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logger.bind(name="MCP Testing")


async def main():
    config_path = "../src/cli_agent/agent/mcp_servers/config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    assert isinstance(config, dict)
    logger.info(f"MCP Config: {config}")

    client = MultiServerMCPClient(config)
    tools = await client.get_tools()
    assert isinstance(tools, list)
    logger.debug(tools)


if __name__ == "__main__":
    asyncio.run(main())


