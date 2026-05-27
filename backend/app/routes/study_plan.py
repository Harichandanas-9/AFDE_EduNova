"""Study plan routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.study_planner_agent import generate_study_plan
from app.database.session import get_db
from app.models.study_plan import StudyPlan
from app.schemas.study_plan import StudyPlanRequest, StudyPlanResponse

router = APIRouter()


@router.post("/study-plan", response_model=StudyPlanResponse)
async def create_study_plan(req: StudyPlanRequest, db: AsyncSession = Depends(get_db)):
    payload = await generate_study_plan(
        req.goal,
        req.current_level,
        req.target_role,
        req.available_hours_per_week,
        req.duration_weeks,
    )
    schedule = payload.get("schedule", [])
    plan = StudyPlan(
        user_id=req.user_id,
        goal=req.goal,
        current_level=req.current_level,
        target_role=req.target_role,
        available_hours_per_week=req.available_hours_per_week,
        duration_weeks=req.duration_weeks,
        roadmap={"overview": payload.get("overview", "")},
        schedule=schedule,
        milestones=payload.get("milestones", []),
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)

    return StudyPlanResponse(
        plan_id=plan.id,
        goal=plan.goal,
        target_role=plan.target_role,
        duration_weeks=plan.duration_weeks,
        schedule=schedule,
        milestones=plan.milestones,
        overview=payload.get("overview", ""),
    )


@router.get("/study-plan/{plan_id}", response_model=StudyPlanResponse)
async def get_study_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    plan = await db.get(StudyPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found.")
    return StudyPlanResponse(
        plan_id=plan.id,
        goal=plan.goal,
        target_role=plan.target_role,
        duration_weeks=plan.duration_weeks,
        schedule=plan.schedule,
        milestones=plan.milestones,
        overview=(plan.roadmap or {}).get("overview", ""),
    )


@router.get("/study-plan")
async def list_study_plans(limit: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(StudyPlan).order_by(desc(StudyPlan.created_at)).limit(limit)
    res = await db.execute(stmt)
    plans = res.scalars().all()
    return [
        {
            "id": p.id,
            "goal": p.goal,
            "target_role": p.target_role,
            "duration_weeks": p.duration_weeks,
            "created_at": p.created_at,
        }
        for p in plans
    ]
