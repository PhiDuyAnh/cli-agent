import uuid
import json
from datetime import datetime
from typing import Optional, Sequence, Union, Any, Callable

from loguru import logger
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from deepagents import SubAgent, async_create_deep_agent, create_deep_agent
from deepagents.tools import write_todos, ls, write_file, read_file, edit_file

from cli_agent.config import get_settings
from cli_agent.agent.memory import Memory, MemoryRecord

logger = logger.bind(name="Agent Implementation")
settings = get_settings()


class Agent:
    """Main agent class."""
    def __init__(
        self,
        tools: Sequence[Union[BaseTool, Callable, dict[str, Any]]],
        system_prompt: str,
        model_name: str = None,
        subagents: list[SubAgent] = None,
        mcp_servers_config: Optional[str] = None,
        # disable_tools: Optional[list] = None,
        memory: Memory = None
    ):
        self._id = str(uuid.uuid4())
        
        self.tools = tools
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.subagents = subagents or []
        self.mcp_config = mcp_servers_config
        # self.disable_tools = disable_tools if disable_tools else []
        self.memory = memory if memory else Memory(memory_id=self._id)

        self.built_in_tools = [write_todos, ls, write_file, read_file, edit_file]
        self.mcp_tools: list = None

        self.main_agent = None

    async def setup(self):
        """Create the deep agent."""
        try:
            self.mcp_tools = await self._get_mcp_tools()
            all_tools = self.tools + self.mcp_tools
            self.main_agent = async_create_deep_agent(
                model=self.model_name,
                tools=all_tools,
                instructions=self.system_prompt,
                subagents=self.subagents,
            )
        except Exception:
            logger.critical("Encountered error during agent creation!")
            raise

    async def _get_mcp_tools(self):
        """Get MCP tools if MCP Servers are available."""
        if self.mcp_config is not None:
            try:
                with open(self.mcp_config, "r") as f:
                    config = json.load(f)
                
                client = MultiServerMCPClient(config)
                mcp_tools = await client.get_tools()
                
                return mcp_tools
            except Exception as e:
                logger.error(
                    f"Some errors occured during MCP connection, make sure the config file is correct: {e}"
                )
                return []
        else:
            return []
        
    def _build_chat_history(
        self,
        user_message: str,
        memory_size: int = settings.MEMORY_SIZE
    ) -> tuple[list[dict[str, Any]], Optional[dict[str, str]]]:
        latest_records = self.memory.get_latest_memory(memory_size)

        history = [{"role": "system", "content": self.system_prompt}]
        for record in latest_records:
            if record.role in ["user", "assistant"]:
                # If no memory saved yet then this will simply return an empty list []
                history += [{"role": record.role, "content": record.content}]

                # Summarization logic (not implemented)

        history.append({"role": "user", "content": user_message})
        
        files = None
        for record in reversed(latest_records):
            if record.role == "state_files":
                files = json.loads(record.content)
                break # Only get the latest state

        return history, files
    
    def _add_to_memory(self, role: str, message: str):
        """Add a message to the memory."""
        try:
            self.memory.insert_memory(
                MemoryRecord(
                    message_id=str(uuid.uuid4()),
                    role=role,
                    content=message,
                    timestamp=datetime.now()
                )
            )
        except Exception as e:
            logger.error(f"Errors occurred when adding message to memory: {e}")

    # def _add_memory_pair(self, user_message: str, assistant_message: str):
    #     """Add both the user messageg and the agent's last response to memory."""
    #     self._add_to_memory(role="user", message=user_message)
    #     self._add_to_memory(role="assistant", message=assistant_message)

    def _add_state_attribute_to_memory(self, state_files: dict[str, str]):
        """Add state attribute to memory. Only the files state attribute is added at the moment."""
        try:
            state_files_string = json.dumps(state_files)

            self.memory.insert_memory(
                MemoryRecord(
                    message_id=str(uuid.uuid4()),
                    role="state_files",
                    content=state_files_string,
                    timestamp=datetime.now()
                )
            )
        except Exception as e:
            logger.error(f"Errors occurred when adding state attribute to memory: {e}")


    def reset_memory(self):
        """Clear the current conversation history."""
        return self.memory.reset_current_memory()
    
    def list_tools(self) -> tuple[list, list, list]:
        """
        List all the tools and MCP servers the agent currently has.
        
        Returns:
            Lists of the agent's built in tools, added tools and MCP servers.
        """
        if self.mcp_config is not None:
            try:
                with open(self.mcp_config, "r") as f:
                    config = json.load(f)
                    mcp_servers = [str(key) for key in config.keys()]
            except (json.JSONDecodeError, IOError) as e:
                logger.error(
                    f"Could not read MCP config file: {e}"
                )
                mcp_servers = []
        else:
            mcp_servers = []

        built_in_tools_name = []
        tools_name = []

        for name, tool_type in zip([built_in_tools_name, tools_name], [self.built_in_tools, self.tools]):
            for tool in tool_type:
                if str(type(tool)) == "<class 'function'>":
                    name.append(tool.__name__)
                else:
                    name.append(tool.name)
        
        return built_in_tools_name, tools_name, mcp_servers


    async def chat(self, user_message: str):
        """
        Main entry point for processing user message.
        
        Args:
            user_message (str): A new user input message
        
        Returns:
            Output streams of the agent.
        """
        if self.main_agent is None:
            raise ValueError("Run setup() for the agent first before calling chat()!")
        
        try:
            chat_history, state_files = self._build_chat_history(user_message)
            all_files = state_files or {}

            self._add_to_memory(role="user", message=user_message)

            async for chunk in self.main_agent.astream({"messages": chat_history, "files": all_files}):
                if chunk.get("tools"):
                    files = chunk["tools"].get("files")
                    if files:
                        self._add_state_attribute_to_memory(files)
                yield chunk # When ever a chunk is streamed, it is passed to the main chat function and the function can resume here
            
            # Add the last streamed output (which belongs to the agent) and the user message to memory
            self._add_to_memory(role="assistant", message=chunk["agent"]["messages"][0].content)
            # self._add_memory_pair(
            #     user_message=user_message,
            #     assistant_message=chunk["agent"]["messages"][0].content
            # )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        