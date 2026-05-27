"""Course / resource recommendation routes."""
from __future__ import annotations

from fastapi import APIRouter

from app.agents.recommendation_agent import get_recommendations
from app.schemas.skill import RecommendationRequest, RecommendationResponse

router = APIRouter()


@router.post("/recommendations", response_model=RecommendationResponse)
async def recommendations(req: RecommendationRequest):
    data = await get_recommendations(
        interests=req.interests,
        target_role=req.target_role,
        weak_skills=req.weak_skills,
        learning_style=req.learning_style or "video",
    )
    return RecommendationResponse(
        target_role=req.target_role,
        items=data.get("items", []),
        notes=data.get("notes", ""),
    )
