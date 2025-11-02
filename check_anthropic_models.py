#!/usr/bin/env python3
"""
Check which Anthropic Claude models are available with your API key.
"""
import asyncio
import os
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()

async def check_model(client: AsyncAnthropic, model: str) -> bool:
    """Test if a model is accessible."""
    try:
        response = await client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        return True
    except Exception as e:
        error_str = str(e)
        if "404" in error_str or "not_found" in error_str:
            return False
        elif "401" in error_str or "authentication" in error_str.lower():
            print(f"❌ Authentication failed. Check your ANTHROPIC_API_KEY")
            return None
        elif "429" in error_str or "rate_limit" in error_str.lower():
            print(f"⚠️  Rate limited. Try again later.")
            return None
        else:
            print(f"⚠️  {model}: {error_str[:100]}")
            return False

async def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("   Set it in .env file or export ANTHROPIC_API_KEY=your_key")
        return
    
    print(f"🔑 Using API key: {api_key[:20]}...")
    print("\n🔍 Testing Claude models...\n")
    
    client = AsyncAnthropic(api_key=api_key)
    
    models = [
        ("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet (Oct 2024)"),
        ("claude-3-5-sonnet-20240620", "Claude 3.5 Sonnet (June 2024)"),
        ("claude-3-5-sonnet-latest", "Claude 3.5 Sonnet (latest)"),
        ("claude-3-opus-20240229", "Claude 3 Opus (Feb 2024)"),
        ("claude-3-sonnet-20240229", "Claude 3 Sonnet (Feb 2024)"),
        ("claude-3-haiku-20240307", "Claude 3 Haiku (Mar 2024)"),
    ]
    
    available = []
    unavailable = []
    
    for model_id, model_name in models:
        result = await check_model(client, model_id)
        
        if result is True:
            print(f"✅ {model_name:<40} ({model_id})")
            available.append((model_id, model_name))
        elif result is False:
            print(f"❌ {model_name:<40} ({model_id})")
            unavailable.append((model_id, model_name))
        else:
            # Authentication or rate limit error
            return
    
    print("\n" + "="*70)
    print(f"\n📊 Summary:")
    print(f"   Available: {len(available)} models")
    print(f"   Unavailable: {len(unavailable)} models")
    
    if available:
        print(f"\n✅ Recommended model to use: {available[0][0]}")
        print(f"\n💡 Update src/llm_client.py AnthropicClient.__init__():")
        print(f'   self.model = "{available[0][0]}"')
    else:
        print("\n⚠️  No models available. Possible issues:")
        print("   1. API key doesn't have access to any models")
        print("   2. API key is invalid or expired")
        print("   3. Account doesn't have credits/subscription")
        print("\n   Check: https://console.anthropic.com/settings/keys")

if __name__ == "__main__":
    asyncio.run(main())
