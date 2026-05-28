from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AnswerRecord, User, WrongQuestion


def build_dashboard(db: Session) -> dict:
    answer_count = db.scalar(select(func.count(AnswerRecord.id))) or 0
    correct_count = (
        db.scalar(select(func.count(AnswerRecord.id)).where(AnswerRecord.is_correct.is_(True))) or 0
    )
    participant_count = db.scalar(select(func.count(User.id))) or 0
    active_user_count = db.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0
    open_wrong_count = (
        db.scalar(select(func.count(WrongQuestion.id)).where(WrongQuestion.status == "open")) or 0
    )
    return {
        "participant_count": participant_count,
        "active_user_count": active_user_count,
        "answer_count": answer_count,
        "overall_accuracy": round(correct_count * 100 / answer_count, 2) if answer_count else 0,
        "bank_accuracy": [],
        "top_wrong_questions": [],
        "open_wrong_count": open_wrong_count,
        "exam_score_distribution": [],
        "ranking_preview": [],
    }
