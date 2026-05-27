"""Skill gap analyzer agent."""
from __future__ import annotations

import json
from typing import List

from app.agents.prompts import SKILL_GAP_SYSTEM
from app.agents.state import AgentState
from app.services.llm_service import llm_service
from app.utils.logger import get_logger

logger = get_logger("edunova.agent.skill_gap")


async def analyze_skill_gap(current_skills: List[str], target_role: str, years_experience: int = 0) -> dict:
    user_prompt = (
        f"Target role: {target_role}\nYears experience: {years_experience}\n"
        f"Current skills: {', '.join(current_skills)}\nReturn strict JSON."
    )
    raw = await llm_service.complete(SKILL_GAP_SYSTEM, user_prompt, json_mode=True, max_tokens=1800)
    try:
        data = json.loads(raw)
        data.setdefault("target_role", target_role)
        data.setdefault("readiness_percent", 0.0)
        data.setdefault("matched_skills", [])
        data.setdefault("missing_skills", [])
        data.setdefault("skill_breakdown", [])
        data.setdefault("learning_roadmap", [])
        data.setdefault("project_ideas", [])
        data.setdefault("estimated_weeks_to_ready", 8)
        return data
    except Exception as e:
        logger.warning("skill gap parse failed: %s", e)
        return {
            "target_role": target_role,
            "readiness_percent": 0.0,
            "matched_skills": current_skills,
            "missing_skills": [],
            "skill_breakdown": [],
            "learning_roadmap": [],
            "project_ideas": [],
            "estimated_weeks_to_ready": 8,
        }


async def skill_gap_node(state: AgentState) -> AgentState:
    if state.get("final"):
        return state
    text = state.get("user_input", "")
    data = await analyze_skill_gap([], text, 0)
    state["structured_payload"] = data
    state["response"] = (
        f"Readiness: **{data.get('readiness_percent', 0)}%** for {data.get('target_role')}.\n"
        f"Missing: {', '.join(data.get('missing_skills', [])[:5]) or 'none detected'}."
    )
    return state
