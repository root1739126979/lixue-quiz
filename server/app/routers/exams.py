from datetime import datetime, timedelta
from decimal import Decimal
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import (
    ExamAnswer,
    ExamAttempt,
    ExamAttemptQuestion,
    Question,
    QuestionBank,
    User,
)
from app.security import get_current_user
from app.services.scoring import award_points_with_daily_limit, get_or_create_point_rule, is_answer_correct, normalize_answer


router = APIRouter(prefix="/api/exams", tags=["exams"])


class CreateExamAttemptRequest(BaseModel):
    bank_id: int


class SubmitExamAnswer(BaseModel):
    question_id: int
    selected_answer: str


class SubmitExamRequest(BaseModel):
    answers: list[SubmitExamAnswer]


@router.post("/attempts")
def create_exam_attempt(
    payload: CreateExamAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    bank = db.get(QuestionBank, payload.bank_id)
    if not bank or not bank.is_active:
        raise HTTPException(status_code=404, detail="题库不存在")
    questions = db.scalars(
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.bank_id == bank.id, Question.is_active.is_(True))
        .order_by(func.random())
        .limit(bank.exam_question_count)
    ).all()
    if not questions:
        raise HTTPException(status_code=400, detail="题库暂无可考试题目")

    attempt = ExamAttempt(
        user_id=current_user.id,
        bank_id=bank.id,
        question_count=len(questions),
        time_limit_minutes=bank.exam_time_limit_minutes,
    )
    db.add(attempt)
    db.flush()
    for question in questions:
        db.add(
            ExamAttemptQuestion(
                attempt_id=attempt.id,
                question_id=question.id,
                source_no=question.source_no,
                question_type=question.question_type.value,
                stem=question.stem,
                options_json=json.dumps(
                    [
                        {"label": option.label, "content": option.content}
                        for option in sorted(question.options, key=lambda item: item.label)
                    ],
                    ensure_ascii=False,
                ),
                correct_answer=question.correct_answer,
                correct_answer_text=question.correct_answer_text,
                explanation=question.explanation,
            )
        )
    db.commit()
    db.refresh(attempt)
    snapshot_questions = db.scalars(
        select(ExamAttemptQuestion).where(ExamAttemptQuestion.attempt_id == attempt.id)
    ).all()
    return {
        "attempt_id": attempt.id,
        "bank_id": bank.id,
        "time_limit_minutes": attempt.time_limit_minutes,
        "questions": [
            {
                "id": item.question_id,
                "question_type": item.question_type,
                "stem": item.stem,
                "options": json.loads(item.options_json),
            }
            for item in snapshot_questions
        ],
    }


@router.post("/attempts/{attempt_id}/submit")
def submit_exam_attempt(
    attempt_id: int,
    payload: SubmitExamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    attempt = db.get(ExamAttempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="考试不存在")
    if attempt.submitted_at is not None:
        raise HTTPException(status_code=400, detail="考试已提交")
    if datetime.utcnow() > attempt.created_at + timedelta(minutes=attempt.time_limit_minutes):
        raise HTTPException(status_code=400, detail="考试已超时")

    snapshots = {
        item.question_id: item
        for item in db.scalars(
            select(ExamAttemptQuestion).where(ExamAttemptQuestion.attempt_id == attempt_id)
        ).all()
    }
    submitted = {answer.question_id: normalize_answer(answer.selected_answer) for answer in payload.answers}
    correct_count = 0
    wrong_details = []
    for question_id, snapshot in snapshots.items():
        selected_answer = submitted.get(question_id, "")
        is_correct = is_answer_correct(selected_answer, snapshot.correct_answer)
        correct_count += 1 if is_correct else 0
        db.add(
            ExamAnswer(
                attempt_id=attempt.id,
                question_id=question_id,
                selected_answer=selected_answer,
                is_correct=is_correct,
            )
        )
        if not is_correct:
            wrong_details.append(
                {
                    "question_id": question_id,
                    "selected_answer": selected_answer,
                    "correct_answer": snapshot.correct_answer,
                    "explanation": snapshot.explanation or "",
                }
            )

    total_count = len(snapshots)
    score = Decimal(correct_count * 100) / Decimal(total_count)
    attempt.score = score
    attempt.correct_count = correct_count
    attempt.submitted_at = datetime.utcnow()
    rule = get_or_create_point_rule(db)
    points_awarded = award_points_with_daily_limit(
        db,
        user_id=current_user.id,
        bank_id=attempt.bank_id,
        desired_points=rule.exam_complete_points,
        reason="exam",
    )
    db.commit()
    return {
        "attempt_id": attempt.id,
        "score": float(score),
        "correct_count": correct_count,
        "total_count": total_count,
        "points_awarded": points_awarded,
        "wrong_details": wrong_details,
    }
