"""
Azure OpenAI Agent Example

This example demonstrates how to use the Azure OpenAI agentic framework
to create intelligent agents.
"""
import os
from dotenv import load_dotenv
from src.azure_openai_agent import SimpleAgent, AzureOpenAIClient, AzureOpenAIConfig

# Load environment variables from .env file
load_dotenv()

def main():
    """Main example function"""
    print("Azure OpenAI Agentic Framework Example")
    print("=" * 40)
    
    # Example 1: Simple agent with default configuration
    print("\n1. Creating a simple assistant agent...")
    agent = SimpleAgent(
        name="Code Assistant",
        system_prompt="You are a helpful coding assistant. Provide clear and concise answers."
    )
    
    # Example conversation
    response = agent.chat("How do I output all files in a directory using Python?")
    print(f"Agent: {response}")
    
    # Example 2: Agent with custom Azure configuration
    print("\n2. Creating agent with custom Azure configuration...")
    
    # Check if environment variables are set
    if os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY"):
        custom_agent = SimpleAgent(
            name="Custom Assistant",
            system_prompt="You are an expert in Azure cloud services.",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")
        )
        
        response = custom_agent.chat("What are the benefits of using Azure OpenAI?")
        print(f"Custom Agent: {response}")
    else:
        print("Note: Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables for custom configuration")
    
    # Example 3: Streaming response
    print("\n3. Streaming response example...")
    agent.reset_conversation()
    print("Agent (streaming): ", end="")
    for chunk in agent.chat("Explain Python list comprehensions", stream=True):
        print(chunk, end="", flush=True)
    print("\n")
    
    print("\nExample completed!")

if __name__ == "__main__":
    main()
