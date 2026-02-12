import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv('backend/.env')

# Initialize Groq client
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Test the API
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Hello, how are you?"}],
    model="llama-3.1-8b-instant"
)

print(response.choices[0].message.content)