"""
Test script to verify Azure OpenAI credentials and framework functionality
"""
import os
from dotenv import load_dotenv
from src.azure_openai_agent import SimpleAgent, AzureOpenAIConfig, AzureOpenAIClient

def test_environment_variables():
    """Test that environment variables are loaded"""
    print("🔍 Checking environment variables...")
    load_dotenv()
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    print(f"✅ Endpoint: {endpoint}")
    print(f"✅ Deployment: {deployment}")
    print(f"✅ API Key: {'***' + api_key[-4:] if api_key and len(api_key) > 4 else 'Not set'}")
    
    if not endpoint or not deployment or not api_key:
        print("❌ Missing required environment variables!")
        return False
    
    return True

def test_simple_agent():
    """Test SimpleAgent with a basic conversation"""
    print("\n🤖 Testing SimpleAgent...")
    
    try:
        agent = SimpleAgent(
            name="Test Assistant",
            system_prompt="You are a helpful assistant. Keep responses brief.",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT")
        )
        
        print("✅ Agent created successfully")
        
        # Test basic chat
        response = agent.chat("Hello! Just say 'Hi' back to confirm you're working.")
        print(f"✅ Agent response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing SimpleAgent: {e}")
        return False

def test_direct_client():
    """Test direct Azure OpenAI client"""
    print("\n🔌 Testing direct client...")
    
    try:
        config = AzureOpenAIConfig(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        )
        
        client = AzureOpenAIClient(config)
        print("✅ Client created successfully")
        
        from src.azure_openai_agent import Message
        messages = [Message.user("Just respond with 'Connection successful!'")]
        
        response = client.complete_chat(messages)
        print(f"✅ Client response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing client: {e}")
        return False

def test_streaming():
    """Test streaming functionality"""
    print("\n🌊 Testing streaming...")
    
    try:
        agent = SimpleAgent(
            name="Streaming Test",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT")
        )
        
        print("Agent (streaming): ", end="", flush=True)
        chunk_count = 0
        for chunk in agent.chat("Count from 1 to 5, one number per word", stream=True):
            print(chunk, end="", flush=True)
            chunk_count += 1
            if chunk_count > 50:  # Safety limit
                break
                
        print(f"\n✅ Streaming test completed ({chunk_count} chunks)")
        return True
        
    except Exception as e:
        print(f"❌ Error testing streaming: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Azure OpenAI Agentic Framework - Credential Test")
    print("=" * 55)
    
    # Load environment variables
    load_dotenv()
    
    # Run tests
    tests = [
        ("Environment Variables", test_environment_variables),
        ("SimpleAgent", test_simple_agent),
        ("Direct Client", test_direct_client),
        ("Streaming", test_streaming)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results:")
    print("-" * 30)
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your Azure OpenAI setup is working correctly.")
    else:
        print("⚠️  Some tests failed. Check your Azure OpenAI configuration.")

if __name__ == "__main__":
    main()
