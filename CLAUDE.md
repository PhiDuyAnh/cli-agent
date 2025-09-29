# CLI Agent Project Documentation

## Project Overview

**CLI Agent** is a sophisticated RAG (Retrieval-Augmented Generation) agent that operates in the command line interface, featuring web scraping capabilities, automatic knowledge ingestion, and persistent conversation memory using Pixeltable as a vector database.

**Key Features:**
- Interactive CLI interface with rich text formatting
- Persistent conversation memory across sessions
- Web scraping and internet search capabilities
- MCP (Model Context Protocol) server integration
- Vector database storage with Pixeltable
- Tool-enabled AI agent with file operations
- Containerized deployment support

## Project Structure

```
cli-agent/
├── src/cli_agent/
│   ├── __init__.py
│   ├── cli.py                 # Main CLI interface and application entry point
│   ├── config.py              # Configuration management with Pydantic settings
│   ├── utils.py               # Utility functions for chat history and time formatting
│   └── agent/
│       ├── __init__.py
│       ├── main_agent.py      # Core agent implementation using DeepAgents
│       ├── memory.py          # Memory management with Pixeltable integration
│       ├── prompts.py         # System prompts and instructions
│       └── tools.py           # Tool definitions (internet search)
├── tests/
│   ├── agent_test.py          # Agent functionality tests
│   └── mcp_test.py            # MCP server tests
├── notebooks/
│   └── pixeltable_funcs.ipynb # Pixeltable experimentation notebook
├── .env.example               # Environment variables template
├── pyproject.toml             # Python project configuration
├── Dockerfile                 # Container configuration
├── docker-compose.yml         # Multi-service container orchestration
└── README.md                  # Project documentation
```

## Technology Stack

### Core Dependencies
- **Python 3.12+** - Runtime environment
- **DeepAgents (0.0.5)** - AI agent framework for tool-enabled conversations
- **Pixeltable (0.4.14+)** - Vector database for persistent memory storage
- **LangChain OpenAI (0.3.33)** - LLM integration with OpenAI models
- **LangChain MCP Adapters (0.1.10)** - Model Context Protocol support
- **Tavily Python** - Web search and scraping capabilities
- **Rich (14.1.0+)** - Terminal UI with colors, panels, and formatting
- **Cutie (0.3.2+)** - Interactive CLI selection menus
- **Loguru (0.7.3+)** - Advanced logging with structured output

### Development Dependencies
- **IPython Kernel** - Jupyter notebook support for experimentation
- **UV** - Fast Python package installer and resolver

## Configuration

### Environment Variables (.env)
```bash
# API Keys
OPENAI_API_KEY=           # OpenAI API access
ANTHROPIC_API_KEY=        # Anthropic Claude API access
TAVILY_API_KEY=           # Tavily search API access

# MCP Configuration
MCP_CONFIG=               # Path to MCP servers configuration file

# Pixeltable Settings
PIXELTABLE_HOME=          # Pixeltable data directory path
PIXELTABLE_VERBOSITY=0    # Logging verbosity (0=minimal)

# LangSmith Tracing (Optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=
LANGSMITH_PROJECT=
```

### Application Settings (config.py)
- **MODEL**: Default LLM model (`openai:gpt-5-nano-2025-08-07`)
- **MEMORY_SIZE**: Number of conversation turns to retain (default: 10)
- **MCP_CONFIG**: Path to MCP server configuration file

## Core Components

### 1. Agent Implementation (main_agent.py)
- **Agent Class**: Main orchestrator for AI interactions
- **Tool Integration**: Built-in tools (write_todos, ls, write_file, read_file, edit_file)
- **MCP Support**: Dynamic loading of Model Context Protocol servers
- **Memory Management**: Automatic conversation history tracking
- **Streaming**: Real-time response streaming with tool call visibility

### 2. Memory System (memory.py)
- **Pixeltable Backend**: Vector database for persistent storage
- **MemoryRecord Model**: Structured conversation data (message_id, role, content, timestamp)
- **Session Management**: Unique conversation directories with auto-cleanup
- **Cache Tracking**: JSON-based conversation history indexing

### 3. CLI Interface (cli.py)
- **Rich Console**: Colorized terminal output with panels and markdown
- **Interactive Commands**: `/exit`, `/help`, `/resume`, `/clear`, `/new`, `/delete`, `/tools`
- **Session Resumption**: Browse and continue past conversations
- **Real-time Streaming**: Live tool execution feedback
- **Error Handling**: Graceful error recovery with user feedback

### 4. Tools System (tools.py)
- **Internet Search**: Tavily-powered web search with topic filtering
- **Built-in Tools**: File operations, todo management, directory listing
- **MCP Integration**: Dynamic tool loading from external servers

## Key Features

### Conversation Memory
- **Persistent Storage**: All conversations saved to Pixeltable vector database
- **Session Management**: Unique IDs for each conversation thread
- **History Navigation**: Browse past conversations with timestamps
- **Context Retention**: Configurable memory size for conversation context

### CLI Commands
- `/exit` - Graceful application shutdown
- `/help` - Display command reference panel
- `/resume` - Select and continue past conversations
- `/clear` or `/reset` - Clear current conversation memory
- `/new` - Start fresh conversation session
- `/delete [chat_id]` - Remove specific conversation
- `/tools` - List available tools and MCP servers

### Tool Capabilities
- **Web Search**: Internet research with Tavily API
- **File Operations**: Read, write, edit files in workspace
- **Todo Management**: Task tracking and organization
- **Directory Listing**: File system navigation
- **MCP Tools**: Extensible tool system via Model Context Protocol

## Development & Testing

### Running the Application
```bash
# Development mode
python src/cli_agent/cli.py

# Using UV (recommended)
uv run python src/cli_agent/cli.py
```

### Testing
```bash
# Run agent tests
python tests/agent_test.py

# Run MCP tests
python tests/mcp_test.py
```

### Experimentation
- **Jupyter Notebooks**: `notebooks/pixeltable_funcs.ipynb` for Pixeltable testing
- **Memory Exploration**: Direct database operations and schema testing

## Integration Points

### MCP Server Support
- **Dynamic Loading**: Runtime configuration of external tool servers
- **Tool Discovery**: Automatic tool registration from MCP endpoints
- **Error Handling**: Graceful fallback when MCP servers unavailable

### LangChain Integration
- **Model Adapters**: Seamless integration with various LLM providers
- **Tool Binding**: Automatic function calling and response parsing
- **Streaming Support**: Real-time response processing

### Pixeltable Features
- **Vector Storage**: Efficient conversation embeddings and retrieval
- **Schema Management**: Structured data types for conversation records
- **Performance**: Optimized for CLI response times
- **Persistence**: Durable storage across application restarts

## Performance Considerations

- **Memory Efficiency**: Configurable conversation context windows
- **Streaming Responses**: Non-blocking UI updates during AI processing
- **Database Optimization**: Indexed queries for fast conversation retrieval
- **Error Recovery**: Robust handling of API failures and network issues

## Security Notes

- **API Key Management**: Environment-based credential storage
- **File Operations**: Sandboxed within application directory
- **MCP Security**: Validated tool execution from trusted servers
- **Logging**: Sensitive data filtering in log outputs

## Future Enhancements

- **Plugin System**: Extensible architecture for custom tools
- **Multi-Model Support**: Provider switching within conversations
- **Export Features**: Conversation backup and migration
- **Advanced Search**: Semantic search across conversation history
- **Collaboration**: Multi-user conversation sharing