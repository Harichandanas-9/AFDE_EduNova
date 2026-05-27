"""Chat schemas."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = Field(default=None)
    user_id: Optional[int] = None
    context: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    intent: str
    eval_score: Optional[float] = None
    blocked: bool = False
    retries: int = 0
    sources: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    role: str
    content: str
    intent: Optional[str] = None
    eval_score: Optional[float] = None
    created_at: datetime
