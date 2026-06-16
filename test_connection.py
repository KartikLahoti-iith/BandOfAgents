from utils.llm_client import ask_agent

print("⏳ Testing Fast Brain (Featherless)...")
try:
    fast_response = ask_agent(
        system_prompt="You are a helpful assistant. Reply with exactly one word.",
        user_message="Say the word 'Fast'.",
        tier="fast"
    )
    print(f"✅ Fast Brain works! Response: {fast_response}\n")
except Exception as e:
    print(f"❌ Fast Brain failed: {e}\n")

print("⏳ Testing Heavy Brain (AI/ML API)...")
try:
    heavy_response = ask_agent(
        system_prompt="You are a helpful assistant. Reply with exactly one word.",
        user_message="Say the word 'Heavy'.",
        tier="heavy"
    )
    print(f"✅ Heavy Brain works! Response: {heavy_response}\n")
except Exception as e:
    print(f"❌ Heavy Brain failed: {e}\n")