"""Study plan model."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    goal: Mapped[str] = mapped_column(String(500), nullable=False)
    current_level: Mapped[str] = mapped_column(String(50), default="beginner")
    target_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    available_hours_per_week: Mapped[int] = mapped_column(Integer, default=10)
    duration_weeks: Mapped[int] = mapped_column(Integer, default=8)
    roadmap: Mapped[dict] = mapped_column(JSON, default=dict)
    schedule: Mapped[list] = mapped_column(JSON, default=list)
    milestones: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
