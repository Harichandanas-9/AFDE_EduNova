"""Chat route — drives the LangGraph workflow."""
from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.workflow import run_workflow
from app.database.session import get_db
from app.guardrails.content_filter import sanitize_output
from app.models.chat import ChatHistory
from app.schemas.chat import ChatHistoryItem, ChatRequest, ChatResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger("edunova.route.chat")


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)) -> ChatResponse:
    """Send a message through the LangGraph multi-agent workflow."""
    session_id = req.session_id or str(uuid.uuid4())

    # Persist user message
    db.add(ChatHistory(
        user_id=req.user_id,
        session_id=session_id,
        role="user",
        content=req.message,
    ))
    await db.commit()

    final_state = await run_workflow(
        user_input=req.message,
        session_id=session_id,
        user_id=req.user_id,
        context=req.context or [],
    )
    reply = sanitize_output(final_state.get("response", ""))

    # Persist assistant reply
    db.add(ChatHistory(
        user_id=req.user_id,
        session_id=session_id,
        role="assistant",
        content=reply,
        intent=final_state.get("intent"),
        eval_score=final_state.get("eval_score"),
        metadata_json={
            "guardrail": {
                "passed": final_state.get("guardrail_passed", True),
                "category": final_state.get("guardrail_category", ""),
                "reason": final_state.get("guardrail_reason", ""),
            },
            "eval_reasons": final_state.get("eval_reasons", []),
        },
    ))
    await db.commit()

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        intent=final_state.get("intent", "chat"),
        eval_score=final_state.get("eval_score"),
        blocked=bool(final_state.get("blocked")),
        retries=int(final_state.get("retries", 0)),
    )


@router.get("/chat/history/{session_id}", response_model=List[ChatHistoryItem])
async def get_chat_history(
    session_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Return the most recent messages for a session."""
    stmt = (
        select(ChatHistory)
        .where(ChatHistory.session_id == session_id)
        .order_by(desc(ChatHistory.created_at))
        .limit(limit)
    )
    res = await db.execute(stmt)
    rows = list(reversed(res.scalars().all()))
    return rows
