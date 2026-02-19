
import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load env variables including API keys
load_dotenv()
load_dotenv('worker/.env')

async def test_nvidia():
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("❌ NVIDIA_API_KEY not found in env")
        return
    
    print(f"🔑 Testing NVIDIA API... (Key ends in {api_key[-4:]})")
    client = AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )
    try:
        completion = await client.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[{"role": "user", "content": "Say 'NVIDIA OK' if you can hear me."}],
            temperature=0.2,
            max_tokens=10
        )
        print(f"✅ NVIDIA Response: {completion.choices[0].message.content}")
    except Exception as e:
        print(f"❌ NVIDIA Failed: {e}")

async def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in env")
        return

    print(f"🔑 Testing Groq API... (Key ends in {api_key[-4:]})")
    client = AsyncOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )
    try:
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'Groq OK' if you can hear me."}],
            temperature=0.2,
            max_tokens=10
        )
        print(f"✅ Groq Response: {completion.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Groq Failed: {e}")

async def main():
    print("🚀 Starting LLM Connection Test...")
    await test_nvidia()
    await test_groq()

if __name__ == "__main__":
    asyncio.run(main())
