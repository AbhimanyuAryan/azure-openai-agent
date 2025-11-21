"""
Azure OpenAI Client Wrapper for the agentic framework
"""
import os
from typing import Dict, Any, Optional, List
from openai import AzureOpenAI
from pydantic import BaseModel, Field
from .conversation import Message


class AzureOpenAIConfig(BaseModel):
    """Configuration for Azure OpenAI client"""
    api_version: str = Field(default="2023-07-01-preview", description="Azure OpenAI API version")
    azure_endpoint: str = Field(..., description="Azure OpenAI endpoint URL")
    azure_deployment: Optional[str] = Field(None, description="Azure deployment name")
    api_key: Optional[str] = Field(None, description="Azure OpenAI API key")
    
    class Config:
        env_prefix = "AZURE_OPENAI_"


class AzureOpenAIClient:
    """
    Azure OpenAI client wrapper that provides a simplified interface
    for the agentic framework.
    """
    
    def __init__(self, config: Optional[AzureOpenAIConfig] = None):
        """
        Initialize Azure OpenAI client
        
        Args:
            config: Configuration object. If None, will try to load from environment.
        """
        if config is None:
            # Load from environment variables
            config = AzureOpenAIConfig(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://example-endpoint.openai.azure.com"),
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY")
            )
        
        self.config = config
        
        # Initialize the client
        client_kwargs = {
            "api_version": config.api_version,
            "azure_endpoint": config.azure_endpoint
        }
        
        if config.api_key:
            client_kwargs["api_key"] = config.api_key
            
        if config.azure_deployment:
            client_kwargs["azure_deployment"] = config.azure_deployment
            
        self.client = AzureOpenAI(**client_kwargs)
    
    def complete_chat(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate a chat completion using Azure OpenAI
        
        Args:
            messages: List of conversation messages
            model: Model name (uses deployment name if not specified)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the completion
            
        Returns:
            The generated response content
        """
        # Convert Message objects to OpenAI format
        openai_messages = [msg.to_openai_format() for msg in messages]
        
        completion_kwargs = {
            "messages": openai_messages,
            "temperature": temperature,
            **kwargs
        }
        
        if model:
            completion_kwargs["model"] = model
        elif self.config.azure_deployment:
            completion_kwargs["model"] = self.config.azure_deployment
        else:
            completion_kwargs["model"] = "gpt-35-turbo"  # Default fallback
            
        if max_tokens:
            completion_kwargs["max_tokens"] = max_tokens
        
        completion = self.client.chat.completions.create(**completion_kwargs)
        
        return completion.choices[0].message.content
    
    def stream_chat(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Generate a streaming chat completion
        
        Args:
            messages: List of conversation messages
            model: Model name (uses deployment name if not specified)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the completion
            
        Yields:
            Streaming response chunks
        """
        # Convert Message objects to OpenAI format
        openai_messages = [msg.to_openai_format() for msg in messages]
        
        completion_kwargs = {
            "messages": openai_messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        
        if model:
            completion_kwargs["model"] = model
        elif self.config.azure_deployment:
            completion_kwargs["model"] = self.config.azure_deployment
        else:
            completion_kwargs["model"] = "gpt-35-turbo"  # Default fallback
            
        if max_tokens:
            completion_kwargs["max_tokens"] = max_tokens
        
        stream = self.client.chat.completions.create(**completion_kwargs)
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
