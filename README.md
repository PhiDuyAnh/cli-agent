# </>🧠 CLI AI Agent

A powerful AI Agent that lives in your command line. Built on LangChain's DeepAgents framework, it combines the flexibility of modern AI tooling with the convenience of terminal-based interaction. Intended to be a powerful RAG agent but right now it acts as a general purpose agent. More specific tools, mechanisms and prompts will be added soon.

## 💡 Key Features
- **Persistent Memory**: Conversation tracking and memory management with Pixeltable. Only user prompts, assistant final responses and key state attribute (in this case, the DeepAgent's files state) are saved to database to avoid context overload and large number of tokens consumption. Summarizing conversation if it exceeds configurable memory size will be implemented soon.
- **Rich Terminal Experience**: CLI interface with real-time streaming responses, tool calls and different helpful commands. You can also manage past and new chat history.
- **MCP Servers Integration**: Besides powerful DeepAgents' built-in tools such as file operations and sub-agents, MCP servers' tools can also be easily integrated and utilized.
- **Highly Customizable**: Easy configuration of models, tools, system prompts and MCP to match your workflow.

## 🚀 Getting Started

1. Follow the instructions from this link to install uv package: https://github.com/astral-sh/uv

2. Clone the repository:
```bash
git clone https://github.com/PhiDuyAnh/cli-agent.git
cd cli-agent
```

3. Install dependencies and create virtual environment with uv:
```bash
uv sync
```

4. Set up your `.env` file to configure the environment variables (for API keys, MCP config, Pixeltable, LangSmith, etc.):
```bash
cp .env.example .env
```

5. Launch the agent:
```bash
uv run src/cli_agent/cli.py
```

### 🐋 Run with Docker

- Build the image:
```bash
docker-compose build
```

- Start the container in interactive mode:
```bash
docker-compose run --rm cli-agent
```

## 🛠️ How to Customize

1. **Add new tools with Python code**: Add new tools in [tools.py](./src/cli_agent/agent/tools.py), these can be any Python functions that can help the agent in achieving particular goals.

2. **Configure MCP servers with a JSON file**: You can configure multiple MCP servers in one JSON file, the default one is in `src/cli_agent/agent/mcp_servers/config.json`.
Example:
```json
{
    "playwright": {
        "command": "npx",
        "args": [
            "@playwright/mcp@latest"
        ],
        "transport": "stdio"
    },
    "math": {
        "command": "python",
        "args": ["/path/to/math_server.py"],
        "transport": "stdio",
    },
    "weather": {
        "url": "http://localhost:8000/mcp/",
        "transport": "streamable_http",
    }
}
```

3. **Select different models**: Select different LangChain's chat models using the syntax `provider:model-name` in [config.py](./src/cli_agent/config.py).

4. **Modify system prompt**: Easily modify the system prompt of the agent in [prompts.py](./src/cli_agent/agent/prompts.py) or even add new prompts.

5. **Change agent's memory size**: Configure the conversation memory size with the variable `MEMORY_SIZE` in [config.py](./src/cli_agent/config.py). This setting controls how many recent message exchanges the agent retains in its context window during each session.

## 🎯 Roadmap
- [ ] Add summarizing mechanism if the conversation exceeds configurable memory size
- [ ] Add tools or MCP servers specfically design for RAG: scraping the web, adding scraped content to knowledge bases, querying knowledge bases, etc.
- [ ] Craft a detailed system prompt
- [ ] Utilize LangGraph's checkpointer such as PostgresSaver, SqliteSaver, etc. to better integrate with the framework and allow for human-in-the-loop.