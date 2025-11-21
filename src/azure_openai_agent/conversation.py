"""
Conversation and message management for the agentic framework
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MessageRole(str, Enum):
    """Enumeration for message roles in a conversation"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class Message(BaseModel):
    """Represents a single message in a conversation"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert message to OpenAI API format"""
        message = {
            "role": self.role.value,
            "content": self.content
        }
        
        if self.name:
            message["name"] = self.name
            
        if self.function_call:
            message["function_call"] = self.function_call
            
        if self.tool_calls:
            message["tool_calls"] = self.tool_calls
            
        return message
    
    @classmethod
    def system(cls, content: str) -> "Message":
        """Create a system message"""
        return cls(role=MessageRole.SYSTEM, content=content)
    
    @classmethod
    def user(cls, content: str) -> "Message":
        """Create a user message"""
        return cls(role=MessageRole.USER, content=content)
    
    @classmethod
    def assistant(cls, content: str) -> "Message":
        """Create an assistant message"""
        return cls(role=MessageRole.ASSISTANT, content=content)


class Conversation(BaseModel):
    """Manages a conversation thread with multiple messages"""
    messages: List[Message] = Field(default_factory=list)
    system_prompt: Optional[str] = None
    max_messages: Optional[int] = None
    
    def __init__(self, system_prompt: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if system_prompt:
            self.system_prompt = system_prompt
            self.add_system_message(system_prompt)
    
    def add_message(self, message: Message):
        """Add a message to the conversation"""
        self.messages.append(message)
        self._enforce_message_limit()
    
    def add_system_message(self, content: str):
        """Add a system message"""
        self.add_message(Message.system(content))
    
    def add_user_message(self, content: str):
        """Add a user message"""
        self.add_message(Message.user(content))
    
    def add_assistant_message(self, content: str):
        """Add an assistant message"""
        self.add_message(Message.assistant(content))
    
    def get_messages(self) -> List[Message]:
        """Get all messages in the conversation"""
        return self.messages.copy()
    
    def get_recent_messages(self, count: int) -> List[Message]:
        """Get the most recent messages"""
        return self.messages[-count:] if count > 0 else []
    
    def clear(self):
        """Clear all messages except system prompt"""
        if self.system_prompt:
            self.messages = [Message.system(self.system_prompt)]
        else:
            self.messages = []
    
    def _enforce_message_limit(self):
        """Enforce maximum message count, keeping system messages"""
        if self.max_messages and len(self.messages) > self.max_messages:
            # Keep system messages and recent messages
            system_messages = [msg for msg in self.messages if msg.role == MessageRole.SYSTEM]
            non_system_messages = [msg for msg in self.messages if msg.role != MessageRole.SYSTEM]
            
            # Keep only the most recent non-system messages
            recent_count = self.max_messages - len(system_messages)
            if recent_count > 0:
                recent_messages = non_system_messages[-recent_count:]
                self.messages = system_messages + recent_messages
            else:
                self.messages = system_messages
    
    def to_openai_format(self) -> List[Dict[str, Any]]:
        """Convert conversation to OpenAI API format"""
        return [msg.to_openai_format() for msg in self.messages]
    
    def __len__(self) -> int:
        """Return the number of messages in the conversation"""
        return len(self.messages)
    
    def __iter__(self):
        """Iterate over messages in the conversation"""
        return iter(self.messages)
