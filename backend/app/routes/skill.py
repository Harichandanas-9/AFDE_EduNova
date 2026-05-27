"""Skill gap analysis routes."""
from __future__ import annotations

from fastapi import APIRouter

from app.agents.skill_gap_agent import analyze_skill_gap
from app.schemas.skill import SkillGapRequest, SkillGapResponse

router = APIRouter()


@router.post("/skill-gap", response_model=SkillGapResponse)
async def skill_gap(req: SkillGapRequest):
    data = await analyze_skill_gap(req.current_skills, req.target_role, req.years_experience)
    return SkillGapResponse(**data)
