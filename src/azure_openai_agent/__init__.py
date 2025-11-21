"""
Azure OpenAI Agentic Framework

A simple framework for building intelligent agents using Azure OpenAI services.
"""

from .agent import Agent, AgentConfig, SimpleAgent
from .client import AzureOpenAIClient, AzureOpenAIConfig
from .conversation import Conversation, Message, MessageRole
from .evaluation import EvaluationRunner, EvaluationSuite, TestCase, LessonPlanEvaluator
from .lesson_plan import LessonPlanAgent
from .logging_config import setup_logging, get_logger

__version__ = "0.1.0"

__all__ = [
    "Agent",
    "AgentConfig", 
    "SimpleAgent",
    "AzureOpenAIClient",
    "AzureOpenAIConfig", 
    "Conversation",
    "Message",
    "MessageRole",
    "EvaluationRunner",
    "EvaluationSuite", 
    "TestCase",
    "LessonPlanEvaluator",
    "LessonPlanAgent",
    "setup_logging",
    "get_logger",
]
