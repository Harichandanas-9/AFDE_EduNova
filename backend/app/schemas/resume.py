"""Resume schemas."""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class Experience(BaseModel):
    company: str
    role: str
    duration: str
    description: Optional[str] = None
    achievements: List[str] = []


class Education(BaseModel):
    institution: str
    degree: str
    duration: str
    gpa: Optional[str] = None


class Project(BaseModel):
    name: str
    description: str
    tech_stack: List[str] = []
    link: Optional[str] = None


class ResumeRequest(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    target_role: str
    template: Literal["modern", "classic", "minimal", "creative"] = "modern"
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    projects: List[Project] = []
    achievements: List[str] = []
    user_id: Optional[int] = None


class ResumeResponse(BaseModel):
    resume_id: int
    target_role: str
    template: str
    summary: str
    markdown: str
    ats_score: float
    suggestions: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
