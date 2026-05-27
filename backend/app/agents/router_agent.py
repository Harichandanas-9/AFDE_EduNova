"""Router agent — classifies user intent."""
from __future__ import annotations

import json

from app.agents.prompts import ROUTER_SYSTEM
from app.agents.state import AgentState
from app.services.llm_service import llm_service
from app.utils.logger import get_logger

logger = get_logger("edunova.agent.router")

VALID_INTENTS = {"quiz", "study_plan", "resume", "skill_gap", "recommendation", "chat"}


async def router_node(state: AgentState) -> AgentState:
    """Classify the request into one of the supported intents."""
    if state.get("final"):
        return state

    user_input = state.get("user_input", "")
    raw = await llm_service.complete(ROUTER_SYSTEM, user_input, json_mode=True, max_tokens=200)
    intent, confidence = _parse_intent(raw)
    state["intent"] = intent
    state["routing_confidence"] = confidence
    logger.info("router intent=%s confidence=%.2f", intent, confidence)
    return state


def _parse_intent(raw: str) -> tuple[str, float]:
    try:
        data = json.loads(raw)
        intent = str(data.get("intent", "chat")).lower().strip()
        confidence = float(data.get("confidence", 0.5))
    except Exception:
        intent, confidence = "chat", 0.5
    if intent not in VALID_INTENTS:
        intent = "chat"
    return intent, max(0.0, min(1.0, confidence))
