# Azure OpenAI Agentic Framework

A Python framework for building intelligent agents using Azure OpenAI services. This framework provides a simple yet powerful way to create conversational AI agents with built-in conversation management and Azure OpenAI integration.

## Features

- 🤖 **Easy Agent Creation**: Simple API for creating intelligent agents
- 💬 **Conversation Management**: Built-in conversation history and context management
- 🔄 **Streaming Support**: Real-time streaming responses
- ⚙️ **Flexible Configuration**: Environment variable and programmatic configuration
- 🛠️ **Function Calling**: Register custom functions for agent tool use
- 📝 **Type Safety**: Full Pydantic model validation

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
git clone <repository-url>
cd azure-openai-agent

# Install dependencies
uv sync

# Copy environment configuration
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

## Configuration

Create a `.env` file with your Azure OpenAI credentials:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2023-07-01-preview
```

## Quick Start

### **Script Usage**

```python
from azure_openai_agent import SimpleAgent

# Create a simple agent
agent = SimpleAgent(
    name="Assistant",
    system_prompt="You are a helpful AI assistant."
)

# Have a conversation
response = agent.chat("Hello! How can you help me?")
print(response)

# Streaming response
for chunk in agent.chat("Tell me about Python", stream=True):
    print(chunk, end="", flush=True)
```

### **Interactive Python Session**

For interactive use with `uv run python`:

```python
# Step 1: Load environment variables (IMPORTANT!)
>>> from dotenv import load_dotenv
>>> load_dotenv()
True

# Step 2: Import and create agent
>>> from src.azure_openai_agent import SimpleAgent
>>> agent = SimpleAgent(name="My Assistant")

# Step 3: Ask questions
>>> response = agent.chat("What is Python?")
>>> print(response)

>>> agent.chat("How do I create a list in Python?")
>>> agent.chat("Show me a function example")

# Step 4: Streaming responses
>>> print("Agent: ", end="")
>>> for chunk in agent.chat("Explain machine learning", stream=True):
...     print(chunk, end="", flush=True)
>>> print()

# Step 5: Conversation management
>>> agent.chat("My name is John")
>>> agent.chat("What's my name?")  # Remembers context
>>> agent.reset_conversation()    # Fresh start
>>> agent.chat("What's my name?") # Won't remember now
```

### **Different Question Types**

```python
# Code questions
>>> agent.chat("How do I read a file in Python?")
>>> agent.chat("Show me list comprehensions")

# General questions  
>>> agent.chat("Explain the difference between lists and tuples")
>>> agent.chat("What are Python decorators?")

# Add context for better responses
>>> agent.add_context("User is a beginner programmer")
>>> agent.chat("How should I start learning?")
```

## Advanced Usage

### Custom Agent Configuration

```python
from azure_openai_agent import Agent, AgentConfig, AzureOpenAIConfig

# Custom Azure configuration
azure_config = AzureOpenAIConfig(
    azure_endpoint="https://your-resource.openai.azure.com/",
    azure_deployment="gpt-4",
    api_version="2023-07-01-preview"
)

# Agent configuration
agent_config = AgentConfig(
    name="Custom Agent",
    system_prompt="You are a specialized assistant.",
    temperature=0.8,
    max_tokens=1000,
    azure_config=azure_config
)

agent = Agent(agent_config)
```

### Conversation Management

```python
# Get conversation history
history = agent.get_conversation_history()

# Reset conversation
agent.reset_conversation()

# Add context
agent.add_context("The user is working on a Python project.")

# Update system prompt
agent.set_system_prompt("You are now a Python expert.")
```

### Function Registration (Future Feature)

```python
def get_weather(location: str) -> str:
    return f"The weather in {location} is sunny."

agent.register_function("get_weather", get_weather, "Get current weather")
```

## Project Structure

```
azure-openai-agent/
├── src/
│   └── azure_openai_agent/
│       ├── __init__.py          # Main exports
│       ├── agent.py             # Agent classes
│       ├── client.py            # Azure OpenAI client wrapper
│       └── conversation.py      # Message and conversation management
├── main.py                      # Example usage
├── pyproject.toml              # Project configuration
├── .env.example                # Environment template
└── README.md                   # This file
```

## API Reference

### SimpleAgent

The easiest way to get started:

```python
agent = SimpleAgent(
    name="Assistant",                    # Agent name
    system_prompt="You are helpful.",    # System prompt
    azure_endpoint="...",               # Azure endpoint (optional)
    azure_deployment="gpt-35-turbo",   # Deployment name (optional)
    temperature=0.7,                    # Generation temperature
    max_tokens=None                     # Max tokens (optional)
)
```

### Agent

Full-featured agent with complete configuration:

```python
config = AgentConfig(
    name="Agent",
    system_prompt="System prompt",
    model="gpt-4",
    temperature=0.7,
    max_tokens=1000,
    max_conversation_length=50,
    azure_config=AzureOpenAIConfig(...)
)
agent = Agent(config)
```

### Conversation

Manage conversation history:

```python
conversation = Conversation(system_prompt="You are helpful.")
conversation.add_user_message("Hello")
conversation.add_assistant_message("Hi there!")
messages = conversation.get_messages()
```

## Examples

Run the example:

```bash
uv run main.py
```

This will demonstrate:
1. Basic agent creation and chat
2. Custom Azure configuration
3. Streaming responses

## Requirements

- Python 3.10+
- Azure OpenAI resource
- Valid API key and endpoint

## Dependencies

- `openai>=1.12.0` - Azure OpenAI client
- `pydantic>=2.5.0` - Data validation
- `python-dotenv>=1.0.0` - Environment configuration
- `typing-extensions>=4.8.0` - Type hints

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the [documentation](README.md)
2. Search existing [issues](issues)
3. Create a new issue with detailed information