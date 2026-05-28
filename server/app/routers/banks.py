from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnswerRecord, PointTransaction, Question, QuestionBank, User
from app.security import get_current_user


router = APIRouter(prefix="/api/banks", tags=["banks"])


@router.get("")
def list_banks(
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    banks = db.scalars(
        select(QuestionBank).where(QuestionBank.is_active.is_(True)).order_by(QuestionBank.id)
    ).all()
    return {"items": [bank_summary(db, bank, current_user.id if current_user else None) for bank in banks]}


@router.get("/{bank_id}/summary")
def get_bank_summary(
    bank_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    bank = db.get(QuestionBank, bank_id)
    if not bank or not bank.is_active:
        raise HTTPException(status_code=404, detail="题库不存在")
    return bank_summary(db, bank, current_user.id)


def bank_summary(db: Session, bank: QuestionBank, user_id: int | None) -> dict:
    question_count = (
        db.scalar(
            select(func.count(Question.id)).where(
                Question.bank_id == bank.id, Question.is_active.is_(True)
            )
        )
        or 0
    )
    practiced_count = 0
    accuracy = 0
    points = 0
    if user_id:
        answers = db.scalars(
            select(AnswerRecord).where(
                AnswerRecord.user_id == user_id, AnswerRecord.bank_id == bank.id
            )
        ).all()
        practiced_count = len({answer.question_id for answer in answers})
        accuracy = (
            round(sum(1 for answer in answers if answer.is_correct) * 100 / len(answers), 2)
            if answers
            else 0
        )
        points = (
            db.scalar(
                select(func.coalesce(func.sum(PointTransaction.points), 0)).where(
                    PointTransaction.user_id == user_id,
                    PointTransaction.bank_id == bank.id,
                )
            )
            or 0
        )
    return {
        "id": bank.id,
        "name": bank.name,
        "description": bank.description or "",
        "question_count": question_count,
        "practiced_count": practiced_count,
        "accuracy": accuracy,
        "points": int(points),
        "has_exam": question_count > 0,
    }
