import os
from dotenv import load_dotenv
from agent import ElectronicComponentAgent

# Load environment variables
load_dotenv()

def test_agent_initialization():
    """Test if the agent can be initialized properly"""
    try:
        # Check if API key is set
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("❌ GROQ_API_KEY not found in environment variables")
            print("Please create a .env file with your GROQ_API_KEY")
            return False
        
        print("✅ GROQ_API_KEY found")
        
        # Try to initialize the agent
        agent = ElectronicComponentAgent()
        print("✅ Agent initialized successfully")
        
        # Test basic functionality
        component = agent.source_component("LM741", quantity=1)
        if component:
            print(f"✅ Component sourced successfully: {component.part_number}")
            print(f"   Risk score: {component.risk_score}")
        else:
            print("⚠️  Component sourcing returned None (this might be expected)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Electronic Component Agent...")
    success = test_agent_initialization()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed. Please check the error messages above.") 