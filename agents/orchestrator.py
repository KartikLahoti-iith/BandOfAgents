import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from utils.llm_client import ask_agent

# 1. The Strict Rules for the AI
ORCHESTRATOR_PROMPT = """
You are the Orchestrator Agent for a University Administrative System.
Your ONLY job is to read user requests and route them to the correct specialist agent. 
You do not solve the problem yourself.

AVAILABLE AGENTS:
- "Timetable_Agent": Reschedules classes, finds substitute professors, or handles course clashes.
- "Resource_Agent": Books physical rooms, hardware labs, or 3D printers.
- "Personnel_Agent": Handles TA (Teaching Assistant) shift assignments and limits.
- "Student_Agent": Checks if students are interested in a new elective or handles batch queries.

YOUR RESPONSE FORMAT:
You must reply ONLY with a valid JSON object. Do not include markdown formatting like ```json or any conversational text.
{
  "assigned_agent": "[Agent Name]",
  "intent": "[Brief summary of what needs to happen]",
  "extracted_entities": {
    "person": "[Name if applicable, else null]",
    "course": "[Course if applicable, else null]",
    "day": "[Day if applicable, else null]"
  }
}
"""

# 2. The Function that runs the Orchestrator
def run_orchestrator(user_message):
    print(f"🧠 Orchestrator is analyzing: '{user_message}'...")
    
    # We use the 'fast' Featherless brain because categorization is an easy task
    raw_response = ask_agent(
        system_prompt=ORCHESTRATOR_PROMPT,
        user_message=user_message,
        tier="fast" 
    )
    
    # Clean up the output in case the AI added invisible spaces
    clean_json_string = raw_response.strip().strip("```json").strip("```")
    
    try:
        decision = json.loads(clean_json_string)
        return decision
    except json.JSONDecodeError:
        print("❌ CRITICAL ERROR: The AI did not return valid JSON.")
        print("Raw Output:", raw_response)
        return None

# 3. A quick local test!
if __name__ == "__main__":
    test_input = "Dr. Faculty_3 called in sick for Tuesday, we need someone to cover his core course."
    result = run_orchestrator(test_input)
    
    if result:
        print("\n✅ Orchestrator Decision:")
        print(json.dumps(result, indent=2))