"""
Azure OpenAI Agentic Framework

A framework for building intelligent agents using Azure OpenAI services.
"""

from .client import AzureOpenAIClient, AzureOpenAIConfig
from .agent import Agent, AgentConfig, SimpleAgent
from .conversation import Conversation, Message, MessageRole
from .logging_config import setup_logging, get_logger

__version__ = "0.1.0"

__all__ = [
    "AzureOpenAIClient",
    "AzureOpenAIConfig",
    "Agent",
    "AgentConfig",
    "SimpleAgent",
    "Conversation",
    "Message",
    "MessageRole",
    "setup_logging",
    "get_logger",
]
