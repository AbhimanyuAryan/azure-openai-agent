"""
Migration utility to convert original Azure OpenAI code to agentic framework

This script shows how to migrate from direct Azure OpenAI usage to the agentic framework.
"""
from src.azure_openai_agent import SimpleAgent, AzureOpenAIClient, AzureOpenAIConfig, Message

def migrate_basic_completion():
    """
    Original code:
    
    from openai import AzureOpenAI
    
    api_version = "2023-07-01-preview"
    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint="https://example-endpoint.openai.azure.com",
    )
    
    completion = client.chat.completions.create(
        model="deployment-name",
        messages=[
            {
                "role": "user",
                "content": "How do I output all files in a directory using Python?",
            },
        ],
    )
    print(completion.to_json())
    """
    
    print("🔄 Migrating basic completion...")
    
    # NEW: Using SimpleAgent (recommended for most cases)
    agent = SimpleAgent(
        name="Assistant",
        azure_endpoint="https://example-endpoint.openai.azure.com"
    )
    
    # Simple chat interface
    response = agent.chat("How do I output all files in a directory using Python?")
    print("Agent response:", response)
    
    # Or using direct client (closer to original)
    config = AzureOpenAIConfig(
        api_version="2023-07-01-preview",
        azure_endpoint="https://example-endpoint.openai.azure.com"
    )
    client = AzureOpenAIClient(config)
    
    messages = [Message.user("How do I output all files in a directory using Python?")]
    response = client.complete_chat(messages, model="deployment-name")
    print("Client response:", response)


def migrate_deployment_client():
    """
    Original code:
    
    deployment_client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint="https://example-resource.azure.openai.com/",
        azure_deployment="deployment-name",
    )
    
    completion = deployment_client.chat.completions.create(
        model="<ignored>",
        messages=[
            {
                "role": "user", 
                "content": "How do I output all files in a directory using Python?",
            },
        ],
    )
    print(completion.to_json())
    """
    
    print("\n🔄 Migrating deployment client...")
    
    # NEW: Using SimpleAgent with deployment
    agent = SimpleAgent(
        name="Deployment Assistant",
        azure_endpoint="https://example-resource.azure.openai.com/",
        azure_deployment="deployment-name"
    )
    
    response = agent.chat("How do I output all files in a directory using Python?")
    print("Deployment agent response:", response)


def advanced_migration_example():
    """
    Show advanced features available in the agentic framework
    """
    print("\n✨ Advanced agentic features...")
    
    # Create an agent with advanced configuration
    agent = SimpleAgent(
        name="Advanced Assistant",
        system_prompt="You are a Python expert. Always provide code examples.",
        temperature=0.8,
        max_tokens=500
    )
    
    # Conversation management
    agent.chat("Hello! I'm learning Python.")
    agent.chat("How do I read a file?")
    
    # Get conversation history
    history = agent.get_conversation_history()
    print(f"Conversation has {len(history)} messages")
    
    # Streaming response
    print("Streaming response:")
    for chunk in agent.chat("Explain list comprehensions", stream=True):
        print(chunk, end="", flush=True)
    print("\n")
    
    # Reset and start fresh
    agent.reset_conversation()
    agent.add_context("User is working on a web scraping project")
    
    response = agent.chat("How do I parse HTML?")
    print("Context-aware response:", response[:100] + "...")


def main():
    """
    Main migration demonstration
    """
    print("🚀 Azure OpenAI to Agentic Framework Migration")
    print("=" * 50)
    
    print("This script demonstrates how to migrate your existing")
    print("Azure OpenAI code to use the new agentic framework.")
    print()
    
    try:
        migrate_basic_completion()
        migrate_deployment_client() 
        advanced_migration_example()
        
        print("\n✅ Migration examples completed!")
        print("\n💡 Key Benefits of Migration:")
        print("   • Simplified API with SimpleAgent")
        print("   • Built-in conversation management")
        print("   • Streaming support")
        print("   • Type safety and validation")
        print("   • Context management")
        print("   • Extensible architecture")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        print("\n🔧 Setup required:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Azure OpenAI credentials")
        print("   3. Run: uv sync")


if __name__ == "__main__":
    main()
