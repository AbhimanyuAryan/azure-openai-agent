"""
Core agent implementation for the Azure OpenAI agentic framework
"""
from typing import Optional, Dict, Any, Callable, List, Union
from pydantic import BaseModel, Field
import logging
from .client import AzureOpenAIClient, AzureOpenAIConfig
from .conversation import Conversation, Message, MessageRole


logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    name: str = Field(..., description="Name of the agent")
    system_prompt: Optional[str] = Field(None, description="System prompt for the agent")
    model: Optional[str] = Field(None, description="Model to use for completions")
    temperature: float = Field(0.7, description="Temperature for generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    max_conversation_length: Optional[int] = Field(50, description="Maximum messages in conversation")
    
    # Azure OpenAI specific config
    azure_config: Optional[AzureOpenAIConfig] = Field(None, description="Azure OpenAI configuration")


class Agent:
    """
    An intelligent agent powered by Azure OpenAI that can maintain conversations
    and execute actions through function calling.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the agent
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.name = config.name
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAIClient(config.azure_config)
        
        # Initialize conversation
        self.conversation = Conversation(
            system_prompt=config.system_prompt,
            max_messages=config.max_conversation_length
        )
        
        # Function registry for tool calling
        self.functions: Dict[str, Callable] = {}
        
        logger.info(f"Agent '{self.name}' initialized")
    
    def register_function(self, name: str, func: Callable, description: str = ""):
        """
        Register a function that the agent can call
        
        Args:
            name: Name of the function
            func: The function to register
            description: Description of what the function does
        """
        self.functions[name] = func
        logger.info(f"Function '{name}' registered for agent '{self.name}'")
    
    def chat(self, message: str, stream: bool = False) -> Union[str, Any]:
        """
        Send a message to the agent and get a response
        
        Args:
            message: User message
            stream: Whether to return a streaming response
            
        Returns:
            Agent's response (string or stream)
        """
        # Add user message to conversation
        self.conversation.add_user_message(message)
        
        try:
            if stream:
                return self._generate_streaming_response()
            else:
                return self._generate_response()
                
        except Exception as e:
            logger.error(f"Error generating response for agent '{self.name}': {e}")
            error_response = f"I encountered an error while processing your request: {str(e)}"
            self.conversation.add_assistant_message(error_response)
            return error_response
    
    def _generate_response(self) -> str:
        """Generate a non-streaming response"""
        response = self.client.complete_chat(
            messages=self.conversation.get_messages(),
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        # Add assistant response to conversation
        self.conversation.add_assistant_message(response)
        
        return response
    
    def _generate_streaming_response(self):
        """Generate a streaming response"""
        response_chunks = []
        
        for chunk in self.client.stream_chat(
            messages=self.conversation.get_messages(),
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        ):
            response_chunks.append(chunk)
            yield chunk
        
        # Add complete response to conversation
        complete_response = "".join(response_chunks)
        self.conversation.add_assistant_message(complete_response)
    
    def reset_conversation(self):
        """Reset the conversation while keeping the system prompt"""
        self.conversation.clear()
        logger.info(f"Conversation reset for agent '{self.name}'")
    
    def get_conversation_history(self) -> List[Message]:
        """Get the conversation history"""
        return self.conversation.get_messages()
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt"""
        self.config.system_prompt = prompt
        self.conversation.system_prompt = prompt
        self.conversation.clear()  # Clear and reinitialize with new prompt
        self.conversation.add_system_message(prompt)
        logger.info(f"System prompt updated for agent '{self.name}'")
    
    def add_context(self, context: str):
        """Add contextual information as a system message"""
        self.conversation.add_system_message(f"Context: {context}")
    
    def __str__(self) -> str:
        return f"Agent(name='{self.name}', messages={len(self.conversation)})"
    
    def __repr__(self) -> str:
        return self.__str__()


class SimpleAgent(Agent):
    """
    A simplified agent for quick prototyping
    """
    
    def __init__(
        self,
        name: str = "Assistant",
        system_prompt: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        azure_deployment: Optional[str] = None,
        **kwargs
    ):
        """
        Create a simple agent with minimal configuration
        
        Args:
            name: Agent name
            system_prompt: System prompt
            azure_endpoint: Azure OpenAI endpoint
            azure_deployment: Azure deployment name
            **kwargs: Additional agent configuration options
        """
        azure_config = None
        if azure_endpoint or azure_deployment:
            azure_config = AzureOpenAIConfig(
                azure_endpoint=azure_endpoint or "https://example-endpoint.openai.azure.com",
                azure_deployment=azure_deployment
            )
        
        config = AgentConfig(
            name=name,
            system_prompt=system_prompt,
            azure_config=azure_config,
            **kwargs
        )
        
        super().__init__(config)
