from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Question, User, WrongQuestion
from app.security import get_current_user


router = APIRouter(prefix="/api/wrong-questions", tags=["wrong-questions"])


@router.get("")
def list_wrong_questions(
    bank_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    query = (
        select(WrongQuestion)
        .options(
            selectinload(WrongQuestion.question).selectinload(Question.options),
            selectinload(WrongQuestion.bank),
        )
        .where(WrongQuestion.user_id == current_user.id, WrongQuestion.status == "open")
        .order_by(WrongQuestion.last_wrong_at.desc())
    )
    if bank_id is not None:
        query = query.where(WrongQuestion.bank_id == bank_id)
    rows = db.scalars(query).all()
    return {
        "bank_id": bank_id,
        "items": [
            {
                "question_id": row.question_id,
                "bank_id": row.bank_id,
                "bank_name": row.bank.name,
                "status": row.status,
                "stem": row.question.stem,
                "options": [
                    {"label": option.label, "content": option.content}
                    for option in sorted(row.question.options, key=lambda item: item.label)
                ],
                "correct_answer": row.question.correct_answer,
                "correct_answer_text": row.question.correct_answer_text or "",
                "explanation": row.question.explanation or "",
                "wrong_count": row.wrong_count,
                "last_wrong_at": row.last_wrong_at.isoformat(),
            }
            for row in rows
        ],
    }


@router.post("/{question_id}/master")
def mark_mastered(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    wrong = db.scalar(
        select(WrongQuestion).where(
            WrongQuestion.user_id == current_user.id,
            WrongQuestion.question_id == question_id,
            WrongQuestion.status == "open",
        )
    )
    if not wrong:
        raise HTTPException(status_code=404, detail="错题不存在")
    wrong.status = "mastered"
    wrong.mastered_at = datetime.utcnow()
    db.commit()
    return {"question_id": question_id, "status": "mastered"}
