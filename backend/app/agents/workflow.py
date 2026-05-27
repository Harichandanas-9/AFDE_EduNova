"""
LangGraph multi-agent workflow.

User Input
   |
   v
Guardrail Agent --(blocked)--> END
   |
   v
Router Agent
   |
   v
Specialized Agent (chat | quiz | study_plan | resume | skill_gap | recommendation)
   |
   v
DeepEval Evaluation
   |
   +-- pass --> END
   |
   +-- fail (retries < max) --> Specialized Agent
   |
   +-- fail (retries == max) --> END (return best-effort response)

If LangGraph isn't installed we fall back to a hand-rolled sequential runner
with identical semantics, so the API never breaks.
"""
from __future__ import annotations

from typing import Optional

from app.agents.chat_agent import chat_node
from app.agents.evaluation_agent import evaluation_node
from app.agents.guardrail_agent import guardrail_node
from app.agents.quiz_agent import quiz_node
from app.agents.recommendation_agent import recommendation_node
from app.agents.resume_agent import resume_node
from app.agents.router_agent import router_node
from app.agents.skill_gap_agent import skill_gap_node
from app.agents.state import AgentState
from app.agents.study_planner_agent import study_planner_node
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("edunova.workflow")

# Map intents to specialised node functions
SPECIALIST_NODES = {
    "chat": chat_node,
    "quiz": quiz_node,
    "study_plan": study_planner_node,
    "resume": resume_node,
    "skill_gap": skill_gap_node,
    "recommendation": recommendation_node,
}


# --------------------------------------------------------------------------- #
# Try to build a real LangGraph; fall back gracefully if unavailable.
# --------------------------------------------------------------------------- #
def _build_langgraph():
    try:
        from langgraph.graph import StateGraph, END
    except Exception as e:
        logger.info("langgraph not available (%s); using sequential fallback runner.", e)
        return None

    graph = StateGraph(AgentState)

    graph.add_node("guardrail", guardrail_node)
    graph.add_node("router", router_node)
    for name, fn in SPECIALIST_NODES.items():
        graph.add_node(name, fn)
    graph.add_node("evaluate", evaluation_node)

    graph.set_entry_point("guardrail")

    # guardrail -> router (or END if blocked)
    def guardrail_branch(state: AgentState) -> str:
        return END if state.get("blocked") else "router"

    graph.add_conditional_edges("guardrail", guardrail_branch, {END: END, "router": "router"})

    # router -> specialist
    def router_branch(state: AgentState) -> str:
        intent = state.get("intent", "chat")
        return intent if intent in SPECIALIST_NODES else "chat"

    graph.add_conditional_edges("router", router_branch, {k: k for k in SPECIALIST_NODES})

    # specialist -> evaluate
    for name in SPECIALIST_NODES:
        graph.add_edge(name, "evaluate")

    # evaluate -> retry or END
    def eval_branch(state: AgentState) -> str:
        if state.get("eval_passed") or state.get("retries", 0) >= settings.DEEPEVAL_MAX_RETRIES:
            return END
        state["retries"] = state.get("retries", 0) + 1
        intent = state.get("intent", "chat")
        return intent if intent in SPECIALIST_NODES else "chat"

    eval_targets = {END: END, **{k: k for k in SPECIALIST_NODES}}
    graph.add_conditional_edges("evaluate", eval_branch, eval_targets)

    compiled = graph.compile()
    logger.info("LangGraph workflow compiled successfully.")
    return compiled


_compiled_graph = _build_langgraph()


# --------------------------------------------------------------------------- #
# Public runner
# --------------------------------------------------------------------------- #
async def run_workflow(
    user_input: str,
    session_id: str,
    user_id: Optional[int] = None,
    context: Optional[list] = None,
) -> AgentState:
    """Execute the full multi-agent workflow and return the final state."""
    initial: AgentState = {
        "user_input": user_input,
        "session_id": session_id,
        "user_id": user_id,
        "context": context or [],
        "retries": 0,
        "final": False,
    }

    if _compiled_graph is not None:
        try:
            final_state = await _compiled_graph.ainvoke(initial)
            return final_state
        except Exception as e:
            logger.exception("LangGraph execution failed, falling back to sequential runner: %s", e)

    return await _sequential_runner(initial)


# --------------------------------------------------------------------------- #
# Sequential fallback runner (semantically identical to LangGraph)
# --------------------------------------------------------------------------- #
async def _sequential_runner(state: AgentState) -> AgentState:
    # 1. Guardrail
    state = await guardrail_node(state)
    if state.get("blocked"):
        return state

    # 2. Router
    state = await router_node(state)
    intent = state.get("intent", "chat")
    specialist = SPECIALIST_NODES.get(intent, chat_node)

    # 3. Specialist + 4. Evaluate (with retry)
    for attempt in range(settings.DEEPEVAL_MAX_RETRIES + 1):
        state["retries"] = attempt
        state = await specialist(state)
        state = await evaluation_node(state)
        if state.get("eval_passed"):
            break

    return state
