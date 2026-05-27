"""Quiz agent."""
from __future__ import annotations

import json

from app.agents.prompts import QUIZ_SYSTEM
from app.agents.state import AgentState
from app.services.llm_service import llm_service
from app.utils.logger import get_logger

logger = get_logger("edunova.agent.quiz")


async def generate_quiz(topic: str, difficulty: str, count: int, question_type: str) -> dict:
    """Generate a quiz payload (dict with a 'questions' list)."""
    user_prompt = (
        f"Topic: {topic}\nDifficulty: {difficulty}\nNumber of questions: {count}\n"
        f"Question type: {question_type}\nReturn strict JSON."
    )
    raw = await llm_service.complete(QUIZ_SYSTEM, user_prompt, json_mode=True, max_tokens=2000)
    try:
        data = json.loads(raw)
        if "questions" not in data:
            data = {"questions": data if isinstance(data, list) else []}
        # Ensure required fields exist
        for i, q in enumerate(data["questions"]):
            q.setdefault("id", i + 1)
            q.setdefault("type", question_type)
            q.setdefault("difficulty", difficulty)
            q.setdefault("explanation", "")
        return data
    except Exception as e:
        logger.warning("quiz parse failed: %s", e)
        return {"questions": []}


async def quiz_node(state: AgentState) -> AgentState:
    if state.get("final"):
        return state
    text = state.get("user_input", "")
    data = await generate_quiz(text, "medium", 5, "mcq")
    state["structured_payload"] = data
    questions = data.get("questions", [])
    summary_lines = [f"Here's a {len(questions)}-question quiz for you:"]
    for q in questions[:5]:
        summary_lines.append(f"- {q.get('question', '')}")
    state["response"] = "\n".join(summary_lines)
    return state
