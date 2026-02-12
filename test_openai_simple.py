import os
from openai import OpenAI

def test_openai_key():
    """Test if OpenAI API key is working"""
    
    # Get API key directly from .env file
    try:
        with open('backend/.env', 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
            else:
                api_key = None
    except FileNotFoundError:
        api_key = None
    
    if not api_key:
        print("[ERROR] No OpenAI API key found in backend/.env file")
        return False
    
    print(f"[INFO] OpenAI API key found: {api_key[:20]}...")
    
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
        
        print("[SUCCESS] OpenAI API key is working!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"[ERROR] OpenAI API key test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_key()