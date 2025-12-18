import asyncio

from app.db.connection import db
from app.services.vector_search import find_similar_events
from app.agents.leader_agent import run_leader_agent

async def get_all_leaders() -> list[dict]:
    rows = await db.fetch("""
                          SELECT id, name, aggression, diplomacy, risk_tolerance, domestic_pressure, escalation_threshold
                          FROM leader_profiles
                          """)

    return [dict(row) for row in rows]


async def run_simulation(event_text: str) -> list[dict]:
    similar_events = await find_similar_events(event_text, limit = 3)
    leaders = await get_all_leaders()
    tasks = [
        run_leader_agent(leader, event_text, similar_events)
        for leader in leaders
    ]
    
    results = await asyncio.gather(*tasks)
    return list(results)
   
    