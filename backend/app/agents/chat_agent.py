"""Chat assistant agent — handles general educational/career questions."""
from __future__ import annotations

from app.agents.prompts import CHAT_SYSTEM
from app.agents.state import AgentState
from app.services.llm_service import llm_service


async def chat_node(state: AgentState) -> AgentState:
    if state.get("final"):
        return state
    user_input = state.get("user_input", "")
    context = state.get("context") or []
    history = "\n".join(f"{m.get('role')}: {m.get('content')}" for m in context[-6:])
    prompt = f"Conversation so far:\n{history}\n\nUser: {user_input}" if history else user_input
    reply = await llm_service.complete(CHAT_SYSTEM, prompt)
    state["response"] = reply
    return state
