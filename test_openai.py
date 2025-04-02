import os
from openai import OpenAI
import logging

logging.basicConfig(level=logging.DEBUG)

def test_openai_client():
    # Get API key from environment
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("No API key found in environment variables")
        return
    
    print(f"Using API key (masked): {api_key[:4]}...")
    
    try:
        # Create the most basic client just with the API key
        client = OpenAI(api_key=api_key)
        print("Successfully created OpenAI client")
        
        # Try a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use a different model here
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, world!"}
            ],
            max_tokens=10
        )
        
        print("Response:", response.choices[0].message.content)
        return "Success"
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"

if __name__ == "__main__":
    result = test_openai_client()
    print("\nTest result:", result)