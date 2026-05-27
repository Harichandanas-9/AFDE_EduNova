"""Study plan schemas."""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class StudyPlanRequest(BaseModel):
    goal: str = Field(..., min_length=3, max_length=500)
    current_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    target_role: Optional[str] = Field(default=None, max_length=255)
    available_hours_per_week: int = Field(default=10, ge=1, le=80)
    duration_weeks: int = Field(default=8, ge=1, le=52)
    user_id: Optional[int] = None


class StudyPlanWeek(BaseModel):
    week: int
    title: str
    focus_areas: List[str]
    topics: List[str]
    resources: List[str]
    practice: List[str]
    milestone: Optional[str] = None


class StudyPlanResponse(BaseModel):
    plan_id: int
    goal: str
    target_role: Optional[str]
    duration_weeks: int
    schedule: List[StudyPlanWeek]
    milestones: List[str]
    overview: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
