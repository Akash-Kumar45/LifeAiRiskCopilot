import os
from openai import OpenAI

# Load environment variables
from dotenv import load_dotenv
load_dotenv('backend/.env')

def test_openai_key():
    """Test if OpenAI API key is working"""
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No OpenAI API key found in environment variables")
        return False
    
    print(f"✅ OpenAI API key found: {api_key[:20]}...")
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Make a simple test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello, your OpenAI API key is working!'"}
            ],
            max_tokens=50
        )
        
        print("✅ OpenAI API key is working!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API key test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_key()