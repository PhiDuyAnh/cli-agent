import asyncio
from dotenv import load_dotenv
load_dotenv()

import cutie
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

from cli_agent.config import get_settings
from cli_agent.utils import get_chat_history, print_past_conversation, delete_conversation
from cli_agent.agent.main_agent import Agent
from cli_agent.agent.prompts import INSTRUCTIONS
from cli_agent.agent.tools import TOOLS
from cli_agent.agent.memory import Memory

console = Console()
settings = get_settings()


def welcome_message():
    """Display welcome message."""
    welcome_panel = Panel(
        "[bold white]Scraping RAG Agent[/bold white]\n\n"
        "[dim gray100]Intelligent web scraping and knowledge base capabilities[/dim gray100]\n\n"
        "[dim gray100]Type '/exit' to quit, '/help' for commands[/dim gray100]",
        style="dark_orange",
        padding=(1,2),
        expand=False,
    )
    console.print(welcome_panel)


def help_message():
    """Display help text."""
    help_text = """
**Commands:**
- **/exit**: Exit the application
- **/help**: Show this help message panel
- **/resume**: Select past conversation history
- **/clear** or **/reset**: Clear the current chat history
- **/new**: Start a new conversation
- **/delete**: Delete a conversation with /delete [chat ID]
- **/tools**: List all the tools and MCP servers of the agent
"""
    console.print(Panel(Markdown(help_text), title="Help Panel", border_style="cyan"))


async def clear(retained_memory: Memory = None):
    """
    Clear the current terminal screen and setup a new Agent.
    
    Args:
        retained_memory (Memory): Provide the existed Memory to recreate the agent and resume past conversation
        
    Returns:
        New agent instance
    """
    console.clear()
    welcome_message()

    agent = Agent(
    model_name=settings.MODEL,
    tools=TOOLS,
    system_prompt=INSTRUCTIONS,
    mcp_servers_config=settings.MCP_CONFIG,
    memory=retained_memory,
    )
    await agent.setup()

    return agent


async def stream_agent_interactions(agent: Agent, user_input: str):
    """Stream real-time agent tool calls and responses."""
    try:
        async for chunk in agent.chat(user_input):
            if chunk.get("agent"):
                agent_message = chunk["agent"]["messages"][0]
                tool_calls = agent_message.tool_calls

                if tool_calls:
                    console.print(f"\n[bold dark_red]Assistant[/bold dark_red]:")
                    for tool_call in tool_calls:
                        console.print(f"🔹 [cyan]Calling tool:[/cyan] [bold]{tool_call["name"]}[/bold]")
                
                if agent_message.content and not tool_calls:
                    console.print(f"\n[bold dark_red]Assistant[/bold dark_red]: {agent_message.content}\n")
            
            elif chunk.get("tools"):
                if chunk["tools"]["messages"][0].name == "write_todos":
                    console.print("\u2514 [bold]Updated to-do list")
                    for task in chunk["tools"]["todos"]:
                        status = task["status"]
                        content = task["content"]
                        console.print("⏳" if status == "pending" else "🔄" if status == "in_progress" else "✅", end=" ")
                        console.print(content)
                else:
                    console.print(f"\u2514 [dim gray100]{chunk["tools"]["messages"][0].content}")
    except Exception as e:
        console.print(f"❌ [red]Encountered error: {e}")


async def main():
    welcome_message()
    try:
        agent = Agent(
            model_name=settings.MODEL,
            tools=TOOLS,
            system_prompt=INSTRUCTIONS,
            mcp_servers_config=settings.MCP_CONFIG,
        )
        await agent.setup()

        while True:
            try:
                user_input = Prompt.ask("[bold cornflower_blue]You").strip()
                
                if user_input.lower().strip() == "/exit":
                    console.print("\u2514 [bold]Catch you later!\n")
                    break

                elif user_input.lower().strip() == "/help":
                    help_message()
                    continue

                elif user_input.lower().strip() == "/resume":
                    try:
                        options, memory_ids = get_chat_history()
                        # chosen_option = Prompt.ask(
                        #     "Please choose an option",
                        #     choices=options,
                        #     default=""
                        # )
                        console.print("\u2514 [bold]Resume a conversation or press 'Ctrl-C' to go back:")
                        chosen_index = cutie.select(options)

                        # After choosing an option
                        chosen_option = memory_ids[chosen_index]
                        
                        agent = await clear(retained_memory=Memory(chosen_option))

                        print_past_conversation(chosen_option, console)
                        console.print(f"[bold green]Resuming conversation...\n")
                        continue
                    except KeyboardInterrupt:
                        continue
                
                elif user_input.lower().strip() in ["/clear", "/reset"]:
                    agent.reset_memory()
                    agent = await clear()
                    continue

                elif user_input.lower().strip() == "/new":
                    agent = await clear()
                    continue

                elif user_input.lower().startswith("/delete"):
                    if user_input.lower().strip() == "/delete":
                        console.print("\u2514 [bold red1]Please specify a chat ID to be deleted!")
                        continue
                    else:
                        splitted_input = user_input.lower().strip().split(" ")

                        if splitted_input[0] != "/delete" or len(splitted_input) > 2:
                            console.print("\u2514 [bold red1]Please use the correct command:[/bold red1]", end=" ")
                            console.print("/delete [chat ID]", markup=False)
                            continue
                        else:
                            memory_id = splitted_input[1]
                            _, chat_ids = get_chat_history()
                            if memory_id not in chat_ids:
                                console.print("\u2514 [bold red1]Please specify a correct chat ID to be deleted!")
                                continue

                            delete_conversation(agent, memory_id)
                            console.print(f"\u2514 [bold green]Conversation {memory_id} deleted successfully.")

                            # Handle case where user deletes the current chat or all chat history, we need to setup another memory table
                            if agent.memory.directory == memory_id:
                                console.print("\n[bold red]The current chat history was deleted. A new one will be created.\n")
                                agent = Agent(
                                model_name=settings.MODEL,
                                tools=TOOLS,
                                system_prompt=INSTRUCTIONS,
                                mcp_servers_config=settings.MCP_CONFIG,
                                )
                                await agent.setup()
                            continue

                elif user_input.lower().strip() == "/tools":
                    built_in_tools, tools, mcp_servers = agent.list_tools()
                    console.print("\u2514", end=" ")
                    if built_in_tools:
                        console.print("[bold white]Built in tools:")
                        for tool in built_in_tools:
                            console.print(f"○ {tool}")
                        console.print()
                    
                    if tools:
                        console.print("[bold white]Added tools:")
                        for tool in tools:
                            console.print(f"○ {tool}")
                        console.print()

                    if mcp_servers:
                        console.print("[bold white]MCP servers:")
                        for server in mcp_servers:
                            console.print(f"○ {server}")
                        console.print()

                    continue
                
                if not user_input: # User types nothing or types only whitespaces then enters
                    continue
                
                await stream_agent_interactions(agent, user_input)
            except KeyboardInterrupt:
                console.print("\n\u2514 [bold gold1]Please use '/exit' to quit!")
    finally:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass