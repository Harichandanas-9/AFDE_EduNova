"""Shared state object passed between LangGraph nodes."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    """The single state dict that flows through the LangGraph workflow."""
    # Inputs
    user_input: str
    session_id: str
    user_id: Optional[int]
    context: List[Dict[str, Any]]

    # Routing
    intent: str
    routing_confidence: float

    # Guardrails
    guardrail_passed: bool
    guardrail_reason: str
    guardrail_category: str
    blocked: bool

    # Agent outputs
    response: str
    structured_payload: Dict[str, Any]

    # Evaluation
    eval_score: float
    eval_passed: bool
    eval_reasons: List[str]

    # Bookkeeping
    retries: int
    final: bool
    error: Optional[str]
