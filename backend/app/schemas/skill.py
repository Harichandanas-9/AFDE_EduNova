"""Skill gap analysis schemas."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SkillGapRequest(BaseModel):
    current_skills: List[str] = Field(..., min_length=1)
    target_role: str = Field(..., min_length=2, max_length=255)
    years_experience: int = Field(default=0, ge=0, le=50)
    user_id: Optional[int] = None


class SkillMatch(BaseModel):
    skill: str
    has: bool
    importance: float  # 0..1
    category: str  # core | nice-to-have | tooling


class SkillGapResponse(BaseModel):
    target_role: str
    readiness_percent: float
    matched_skills: List[str]
    missing_skills: List[str]
    skill_breakdown: List[SkillMatch]
    learning_roadmap: List[str]
    project_ideas: List[str]
    estimated_weeks_to_ready: int


class RecommendationRequest(BaseModel):
    interests: List[str] = Field(default_factory=list)
    target_role: Optional[str] = None
    weak_skills: List[str] = Field(default_factory=list)
    learning_style: Optional[str] = "video"  # video | reading | hands-on
    user_id: Optional[int] = None


class RecommendationItem(BaseModel):
    title: str
    type: str  # course | youtube | doc | certification | practice
    provider: str
    url: Optional[str] = None
    reason: str
    duration: Optional[str] = None
    level: Optional[str] = None


class RecommendationResponse(BaseModel):
    target_role: Optional[str]
    items: List[RecommendationItem]
    notes: str
