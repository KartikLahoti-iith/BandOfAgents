import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- CLIENT 1: The Fast Brain (Featherless) ---
featherless_client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key=os.getenv("FEATHERLESS_API_KEY")
)

# --- CLIENT 2: The Heavy Brain (AI/ML API) ---
aiml_client = OpenAI(
    base_url="https://api.aimlapi.com/v1", 
    api_key=os.getenv("AIML_API_KEY")
)

def ask_agent(system_prompt, user_message, tier="fast"):
    """
    Routes the request to the right API using EXACT model names.
    """
    
    if tier == "heavy":
        active_client = aiml_client
        # Exact string required by AI/ML API for their 70B model
        model_name = "meta-llama/llama-3.3-70b-versatile" 
    else:
        active_client = featherless_client
        # 100% Open model - No Hugging Face gating required
        model_name = "Qwen/Qwen2.5-7B-Instruct"  
        
    response = active_client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.1
    )
    
    return response.choices[0].message.content