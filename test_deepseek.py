"""Quick test script for DeepSeek API connectivity."""
import os
from openai import OpenAI

def test_deepseek():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: DEEPSEEK_API_KEY environment variable not set!")
        print("Please set it with: set DEEPSEEK_API_KEY=your_key_here")
        return False

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        print("Testing DeepSeek API connection...")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Reply with exactly: DeepSeek API is working!"}
            ],
            temperature=0.0,
            max_tokens=50,
        )

        result = response.choices[0].message.content
        print(f"Response: {result}")
        print("✓ DeepSeek API is working!")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    test_deepseek()
