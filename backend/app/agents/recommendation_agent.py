"""Recommendation agent."""
from __future__ import annotations

import json
from typing import List, Optional

from app.agents.prompts import RECOMMEND_SYSTEM
from app.agents.state import AgentState
from app.services.llm_service import llm_service
from app.utils.logger import get_logger

logger = get_logger("edunova.agent.recommendation")


async def get_recommendations(
    interests: List[str],
    target_role: Optional[str],
    weak_skills: List[str],
    learning_style: str = "video",
) -> dict:
    user_prompt = (
        f"Target role: {target_role or 'N/A'}\nInterests: {', '.join(interests) or 'general'}\n"
        f"Weak skills: {', '.join(weak_skills) or 'none'}\nLearning style: {learning_style}\n"
        "Return strict JSON with items and notes."
    )
    raw = await llm_service.complete(RECOMMEND_SYSTEM, user_prompt, json_mode=True, max_tokens=1500)
    try:
        data = json.loads(raw)
        data.setdefault("items", [])
        data.setdefault("notes", "")
        return data
    except Exception as e:
        logger.warning("recommendation parse failed: %s", e)
        return {"items": [], "notes": ""}


async def recommendation_node(state: AgentState) -> AgentState:
    if state.get("final"):
        return state
    text = state.get("user_input", "")
    data = await get_recommendations([text], None, [], "video")
    state["structured_payload"] = data
    items = data.get("items", [])
    lines = ["Here are some hand-picked resources:"]
    for it in items[:5]:
        lines.append(f"- **{it.get('title')}** ({it.get('provider')}) — {it.get('reason')}")
    state["response"] = "\n".join(lines)
    return state
