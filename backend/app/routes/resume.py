"""Resume routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.resume_agent import build_resume
from app.database.session import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeRequest, ResumeResponse

router = APIRouter()


@router.post("/resume/build", response_model=ResumeResponse)
async def create_resume(req: ResumeRequest, db: AsyncSession = Depends(get_db)):
    payload = await build_resume(req.model_dump())

    resume = Resume(
        user_id=req.user_id,
        target_role=req.target_role,
        template=req.template,
        full_name=req.full_name,
        email=req.email,
        phone=req.phone,
        summary=payload.get("summary"),
        skills=req.skills,
        experience=[e.model_dump() for e in req.experience],
        education=[e.model_dump() for e in req.education],
        projects=[p.model_dump() for p in req.projects],
        achievements=req.achievements,
        generated_markdown=payload.get("markdown"),
        ats_score=payload.get("ats_score"),
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return ResumeResponse(
        resume_id=resume.id,
        target_role=resume.target_role,
        template=resume.template,
        summary=resume.summary or "",
        markdown=resume.generated_markdown or "",
        ats_score=resume.ats_score or 0.0,
        suggestions=payload.get("suggestions", []),
    )


@router.get("/resume/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: int, db: AsyncSession = Depends(get_db)):
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return ResumeResponse(
        resume_id=resume.id,
        target_role=resume.target_role,
        template=resume.template,
        summary=resume.summary or "",
        markdown=resume.generated_markdown or "",
        ats_score=resume.ats_score or 0.0,
        suggestions=[],
    )


@router.get("/resume/{resume_id}/markdown", response_class=PlainTextResponse)
async def get_resume_markdown(resume_id: int, db: AsyncSession = Depends(get_db)):
    resume = await db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return resume.generated_markdown or ""
