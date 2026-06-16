import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm_client import ask_agent
from utils.data_manager import DataManager

RESOURCE_PROMPT = """
You are the expert Resource Agent for a university. Your job is to allocate rooms and specialized lab hardware (FPGAs, GPUs, CNCs, 3D Printers).
You must maximize resource utilization without causing double-bookings or exceeding available physical inventory limits.

YOUR RESPONSE FORMAT:
Provide your logical assessment followed by a clear specification of the room or hardware asset allocated.
"""

def handle_resource_query(user_query):
    print("🔄 Initializing Unified Data Engine...")
    context = DataManager().get_resource_summary()
    full_message = f"{context}\n\nUSER REQUEST:\n{user_query}"
    
    return ask_agent(system_prompt=RESOURCE_PROMPT, user_message=full_message, tier="fast")

if __name__ == "__main__":
    print("\n" + handle_resource_query("The Mechanical department needs to verify if the CNC Routers are completely booked on Tuesday afternoon."))