import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm_client import ask_agent
from utils.data_manager import DataManager

PERSONNEL_PROMPT = """
You are the University Personnel Agent. You manage TA assignments.
STRICT MANDATE: Theory courses require EXACTLY 0 TAs. Lab courses require EXACTLY 2 TAs. 
Never allocate 1 TA to a course under any circumstances. Ensure no TA exceeds 10 hours per week.

YOUR RESPONSE FORMAT:
State the current tracking metrics and explicitly list the TA IDs assigned or unassigned.
"""
'''
def handle_personnel_query(user_query):
    print("🔄 Initializing Unified Data Engine...")
    context = DataManager().get_personnel_summary()
    full_message = f"{context}\n\nQUERY:\n{user_query}"
    
    return ask_agent(system_prompt=PERSONNEL_PROMPT, user_message=full_message, tier="fast")

if __name__ == "__main__":
    print("\n" + handle_personnel_query("Find exactly 2 available and qualified TAs to cover the new Electrical lab."))'''

def handle_personnel_query(user_query):
    print("🔄 Initializing Unified Data Engine...")
    
    # Tracer 1: Checking the Data Manager
    try:
        context = DataManager().get_personnel_summary()
        print("✅ Data Manager successfully read the JSON files!")
    except Exception as e:
        print(f"❌ Data Manager crashed: {e}")
        return "Error reading data."

    full_message = f"{context}\n\nQUERY:\n{user_query}"
    
    # Tracer 2: Checking the Network API
    print("📡 Sending prompt to the LLM via ask_agent(). Waiting for response...")
    try:
        result = ask_agent(system_prompt=PERSONNEL_PROMPT, user_message=full_message, tier="fast")
        print("✅ LLM successfully responded!")
        return result
    except Exception as e:
        print(f"❌ Network API crashed or timed out: {e}")
        return "Error reaching LLM."