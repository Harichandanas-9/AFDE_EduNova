"""Quiz routes."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.quiz_agent import generate_quiz
from app.database.session import get_db
from app.models.quiz import Quiz, QuizResult
from app.schemas.quiz import (
    QuizGenerateRequest,
    QuizResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
)
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger("edunova.route.quiz")


@router.post("/quiz/generate", response_model=QuizResponse)
async def create_quiz(req: QuizGenerateRequest, db: AsyncSession = Depends(get_db)):
    payload = await generate_quiz(req.topic, req.difficulty, req.question_count, req.question_type)
    questions = payload.get("questions", [])
    if not questions:
        raise HTTPException(status_code=502, detail="Failed to generate quiz questions.")

    quiz = Quiz(
        user_id=req.user_id,
        topic=req.topic,
        difficulty=req.difficulty,
        question_count=req.question_count,
        question_type=req.question_type,
        questions=questions,
    )
    db.add(quiz)
    await db.commit()
    await db.refresh(quiz)

    return QuizResponse(
        quiz_id=quiz.id,
        topic=quiz.topic,
        difficulty=quiz.difficulty,
        questions=questions,
    )


@router.post("/quiz/submit", response_model=QuizSubmitResponse)
async def submit_quiz(req: QuizSubmitRequest, db: AsyncSession = Depends(get_db)):
    quiz = await db.get(Quiz, req.quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    answers_by_id = {a.question_id: a.answer for a in req.answers}
    per_question = []
    correct = 0
    for q in quiz.questions:
        qid = q.get("id")
        user_ans = (answers_by_id.get(qid) or "").strip()
        correct_ans = (q.get("correct_answer") or "").strip()
        is_correct = user_ans.lower() == correct_ans.lower()
        if is_correct:
            correct += 1
        per_question.append({
            "id": qid,
            "question": q.get("question"),
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })
    total = len(quiz.questions)
    score = round(100.0 * correct / max(1, total), 2)

    # Adaptive difficulty suggestion
    if score >= 85:
        suggested = "hard"
    elif score >= 60:
        suggested = "medium"
    else:
        suggested = "easy"

    feedback = (
        f"You scored {score}% ({correct}/{total}). "
        + ("Great job! Try a harder quiz next." if score >= 80
           else "Solid work. Review the explanations and try again." if score >= 50
           else "Don't worry — review the basics, then re-attempt.")
    )

    result = QuizResult(
        quiz_id=quiz.id,
        user_id=req.user_id,
        score=score,
        total=total,
        correct=correct,
        answers=[a.model_dump() for a in req.answers],
        feedback=feedback,
        duration_seconds=req.duration_seconds,
    )
    db.add(result)
    await db.commit()

    return QuizSubmitResponse(
        score=score,
        correct=correct,
        total=total,
        feedback=feedback,
        per_question=per_question,
        suggested_difficulty=suggested,
    )


@router.get("/quiz/recent")
async def recent_quizzes(limit: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(Quiz).order_by(desc(Quiz.created_at)).limit(limit)
    res = await db.execute(stmt)
    quizzes = res.scalars().all()
    return [
        {
            "id": q.id,
            "topic": q.topic,
            "difficulty": q.difficulty,
            "question_count": q.question_count,
            "created_at": q.created_at,
        }
        for q in quizzes
    ]


@router.get("/quiz/results/recent")
async def recent_results(limit: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(QuizResult).order_by(desc(QuizResult.created_at)).limit(limit)
    res = await db.execute(stmt)
    rows = res.scalars().all()
    return [
        {
            "id": r.id,
            "quiz_id": r.quiz_id,
            "score": r.score,
            "correct": r.correct,
            "total": r.total,
            "created_at": r.created_at,
        }
        for r in rows
    ]
