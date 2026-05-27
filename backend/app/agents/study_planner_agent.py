"""Study planner agent."""
from __future__ import annotations

import json

from app.agents.prompts import STUDY_PLAN_SYSTEM
from app.agents.state import AgentState
from app.services.llm_service import llm_service
from app.utils.logger import get_logger

logger = get_logger("edunova.agent.study_planner")


async def generate_study_plan(
    goal: str,
    current_level: str,
    target_role: str | None,
    hours_per_week: int,
    duration_weeks: int,
) -> dict:
    user_prompt = (
        f"Goal: {goal}\nCurrent level: {current_level}\nTarget role: {target_role or 'N/A'}\n"
        f"Hours per week: {hours_per_week}\nDuration: {duration_weeks} weeks\nReturn strict JSON."
    )
    raw = await llm_service.complete(STUDY_PLAN_SYSTEM, user_prompt, json_mode=True, max_tokens=2500)
    try:
        data = json.loads(raw)
        data.setdefault("overview", f"A {duration_weeks}-week plan toward: {goal}.")
        data.setdefault("schedule", [])
        data.setdefault("milestones", [])
        return data
    except Exception as e:
        logger.warning("study plan parse failed: %s", e)
        return {"overview": "", "schedule": [], "milestones": []}


async def study_planner_node(state: AgentState) -> AgentState:
    if state.get("final"):
        return state
    text = state.get("user_input", "")
    data = await generate_study_plan(text, "beginner", None, 10, 8)
    state["structured_payload"] = data
    schedule = data.get("schedule", [])
    response_lines = [data.get("overview", ""), "", "**Schedule preview:**"]
    for week in schedule[:4]:
        response_lines.append(f"- {week.get('title', '')}")
    state["response"] = "\n".join(response_lines)
    return state
