"""
Basic usage example based on the original Azure OpenAI code.

This example shows how to migrate from the basic Azure OpenAI client usage 
to the agentic framework.
"""
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from src.azure_openai_agent import SimpleAgent, AzureOpenAIClient, AzureOpenAIConfig

# Load environment variables
load_dotenv()

def original_azure_openai_example():
    """
    Original Azure OpenAI usage pattern (for comparison)
    """
    print("=== Original Azure OpenAI Pattern ===")
    
    # Original pattern from your code
    api_version = "2023-07-01-preview"
    
    # gets the API Key from environment variable AZURE_OPENAI_API_KEY
    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://example-endpoint.openai.azure.com"),
    )

    completion = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo"),
        messages=[
            {
                "role": "user",
                "content": "How do I output all files in a directory using Python?",
            },
        ],
    )
    print("Original Response:", completion.choices[0].message.content[:100] + "...")


def agentic_framework_example():
    """
    Using the new agentic framework
    """
    print("\n=== Agentic Framework Pattern ===")
    
    # Method 1: Simple agent (easiest migration)
    agent = SimpleAgent(
        name="Python Helper",
        system_prompt="You are a helpful Python coding assistant.",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )
    
    response = agent.chat("How do I output all files in a directory using Python?")
    print("Agent Response:", response[:100] + "...")
    
    # Method 2: Advanced configuration
    azure_config = AzureOpenAIConfig(
        api_version="2023-07-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://example-endpoint.openai.azure.com"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )
    
    client = AzureOpenAIClient(azure_config)
    
    # Direct client usage (similar to original)
    from src.azure_openai_agent import Message
    messages = [Message.user("How do I output all files in a directory using Python?")]
    response = client.complete_chat(messages)
    print("Client Response:", response[:100] + "...")


def main():
    """Main example function"""
    print("Azure OpenAI Agentic Framework - Basic Usage Example")
    print("=" * 55)
    
    try:
        # Show original pattern
        original_azure_openai_example()
        
        # Show new agentic pattern
        agentic_framework_example()
        
        print("\n=== Benefits of Agentic Framework ===")
        print("✅ Built-in conversation management")
        print("✅ Easy agent configuration")
        print("✅ Streaming support")
        print("✅ Type safety with Pydantic")
        print("✅ Extensible with function calling")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure to set up your Azure OpenAI credentials in .env file")
        print("Copy .env.example to .env and fill in your details")


if __name__ == "__main__":
    main()
