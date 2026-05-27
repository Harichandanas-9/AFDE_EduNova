"""Quiz schemas."""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class QuizGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    question_count: int = Field(default=5, ge=1, le=20)
    question_type: Literal["mcq", "coding", "short", "true_false", "mixed"] = "mcq"
    user_id: Optional[int] = None


class QuizQuestion(BaseModel):
    id: int
    question: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    type: str = "mcq"
    difficulty: str = "medium"


class QuizResponse(BaseModel):
    quiz_id: int
    topic: str
    difficulty: str
    questions: List[QuizQuestion]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QuizAnswer(BaseModel):
    question_id: int
    answer: str


class QuizSubmitRequest(BaseModel):
    quiz_id: int
    user_id: Optional[int] = None
    answers: List[QuizAnswer]
    duration_seconds: int = 0


class QuizSubmitResponse(BaseModel):
    score: float
    correct: int
    total: int
    feedback: str
    per_question: List[dict]
    suggested_difficulty: str
