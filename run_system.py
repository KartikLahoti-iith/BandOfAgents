import os
import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver # ✅ Claude's memory upgrade

from band import Agent # ✅ Sticking to the proven v1.0 namespace
from band.adapters import LangGraphAdapter

# ✅ Using the flat data fetchers to avoid the async deadlock
from agents.personnel_agent import get_personnel_data
from agents.resource_agent import get_resource_data
from agents.timetable_agent import get_timetable_data

load_dotenv()

# ─── 1. FLAT TOOLS ────────────────────────────────────────────────────────────

@tool
def fetch_and_assign_tas() -> str:
    """Fetches the TA roster to assign TAs to courses."""
    return get_personnel_data()

@tool
def solve_timetable_crisis() -> str:
    """Fetches the master schedule to resolve scheduling conflicts."""
    return get_timetable_data()

@tool
def query_resources() -> str:
    """Fetches room capacities and specialized hardware inventory."""
    return get_resource_data()

# ─── 2. MAIN SYSTEM ───────────────────────────────────────────────────────────

async def main():
    print("🚀 Booting Ultimate Merged Architecture...")

    # Our stable, non-streaming brain
    llm = ChatOpenAI(
        model="Qwen/Qwen2.5-7B-Instruct",
        base_url="https://api.featherless.ai/v1",
        api_key=os.getenv("FEATHERLESS_API_KEY"),
        temperature=0.1,
        streaming=False,
        max_retries=3
    )

    # We use a shared memory saver for stability
    memory = InMemorySaver()

    # ── Personnel Agent ──
    personnel = Agent.create(
        adapter=LangGraphAdapter(
            llm=llm,
            checkpointer=memory,
            additional_tools=[fetch_and_assign_tas],
            custom_section="You manage TA assignments. Theory=0 TAs. Lab=exactly 2 TAs. Max 10hrs/week per TA."
        ),
        agent_id=os.getenv("PERSONNEL_ID"),
        api_key=os.getenv("PERSONNEL_TOKEN")
    )

    # ── Timetable Agent ──
    timetable = Agent.create(
        adapter=LangGraphAdapter(
            llm=llm,
            checkpointer=memory,
            additional_tools=[solve_timetable_crisis],
            custom_section="You resolve scheduling conflicts and professor leaves. No double-booking allowed."
        ),
        agent_id=os.getenv("TIMETABLE_ID"),
        api_key=os.getenv("TIMETABLE_TOKEN")
    )

    # ── Resource Agent ──
    resource = Agent.create(
        adapter=LangGraphAdapter(
            llm=llm,
            checkpointer=memory,
            additional_tools=[query_resources],
            custom_section="You allocate rooms and lab hardware. Maximize utilization without double-booking."
        ),
        agent_id=os.getenv("RESOURCE_ID"),
        api_key=os.getenv("RESOURCE_TOKEN")
    )

    print("✅ All 3 agents online with Memory Savers. Waiting for Band.ai messages...")

    await asyncio.gather(
        personnel.run(),
        timetable.run(),
        resource.run(),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 System shut down.")