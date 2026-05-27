"""DeepEval node — evaluates the final response."""
from __future__ import annotations

from app.agents.state import AgentState
from app.evaluation.deepeval_evaluator import evaluator
from app.utils.logger import get_logger

logger = get_logger("edunova.agent.eval")


async def evaluation_node(state: AgentState) -> AgentState:
    """Score the candidate response. Sets eval_passed and eval_score."""
    if state.get("blocked"):
        # Skip evaluation for blocked responses; they're already final.
        state["eval_passed"] = True
        state["eval_score"] = 1.0
        state["eval_reasons"] = ["blocked-bypass"]
        return state

    question = state.get("user_input", "")
    answer = state.get("response", "") or ""
    result = await evaluator.evaluate(question, answer)
    state["eval_passed"] = result.passed
    state["eval_score"] = result.score
    state["eval_reasons"] = result.reasons
    logger.info(
        "eval intent=%s score=%.2f passed=%s retries=%d",
        state.get("intent"),
        result.score,
        result.passed,
        state.get("retries", 0),
    )
    return state
