import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm_client import ask_agent
from utils.data_manager import DataManager  # <-- Using our new unified engine

# --- 1. TIMETABLE AGENT SYSTEM PROMPT ---

TIMETABLE_PROMPT = """
You are the expert Timetable Agent for a university. Your job is to resolve scheduling conflicts, handling teacher leaves, or room reassignments.
You must be mathematically rigorous and absolute in enforcing operational rules.

CRITICAL OPERATIONAL RULES:
1. No Professor can be double-booked in the same Day and Slot.
2. No Room can host two courses in the same Day and Slot.
3. You must only substitute a professor with another professor from the SAME department who shares at least one required qualification.
4. Keep structural changes minimal. Swap slots or change a professor only if absolutely necessary.

YOUR OUTPUT FORMAT:
You must reply with your step-by-step reasoning first, and end your response with a structured summary of the specific changes made.
"""

# --- 2. CORE RUN EXECUTION ---

def handle_timetable_crisis(crisis_message):
    print("🔄 Initializing Unified Data Engine...")
    dm = DataManager()
    
    print("🔄 Stitching database records into cross-referenced context...")
    context_data = dm.get_comprehensive_summary()
    
    # Combine the system instructions with the actual current state of the university
    full_user_message = f"{context_data}\n\nCRISIS TO SOLVE:\n{crisis_message}"
    
    print("🧠 Waking up the Heavy Brain (AI/ML API) to process calculations...")
    solution = ask_agent(
        system_prompt=TIMETABLE_PROMPT,
        user_message=full_user_message,
        tier="heavy" # Uses your high-reasoning credit tier
    )
    
    return solution

if __name__ == "__main__":
    # Let's test a realistic scenario: Dr. Faculty_1 needs someone to cover a class
    test_crisis = "Dr. Faculty_1 has an urgent medical leave on Monday. Find a qualified professor from their department to step in and teach their Monday class, or propose a safe reschedule."
    
    result = handle_timetable_crisis(test_crisis)
    print("\n================ FINAL AGENT PROPOSAL ================")
    print(result)