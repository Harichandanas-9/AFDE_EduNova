"""Guardrail agent — first node in the LangGraph workflow."""
from __future__ import annotations

from app.agents.state import AgentState
from app.guardrails.content_filter import BLOCKED_RESPONSE, check_content
from app.utils.logger import get_logger

logger = get_logger("edunova.agent.guardrail")


async def guardrail_node(state: AgentState) -> AgentState:
    """Run guardrail checks on the user input."""
    user_input = state.get("user_input", "")
    result = check_content(user_input)
    state["guardrail_passed"] = result.allowed
    state["guardrail_reason"] = result.reason
    state["guardrail_category"] = result.category

    if not result.allowed:
        logger.info("guardrail_blocked category=%s reason=%s", result.category, result.reason)
        state["blocked"] = True
        state["response"] = BLOCKED_RESPONSE
        state["intent"] = "blocked"
        state["final"] = True
    else:
        state["blocked"] = False
    return state
