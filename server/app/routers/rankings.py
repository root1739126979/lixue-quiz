from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnswerRecord, PointTransaction, User


router = APIRouter(prefix="/api/rankings", tags=["rankings"])


@router.get("/global")
def global_ranking(limit: int = 50, db: Session = Depends(get_db)) -> dict:
    return {"items": ranking_items(db, bank_id=None, limit=limit), "limit": limit}


@router.get("/banks/{bank_id}")
def bank_ranking(bank_id: int, limit: int = 50, db: Session = Depends(get_db)) -> dict:
    return {"bank_id": bank_id, "items": ranking_items(db, bank_id=bank_id, limit=limit), "limit": limit}


def ranking_items(db: Session, *, bank_id: int | None, limit: int) -> list[dict]:
    points_query = select(
        PointTransaction.user_id,
        func.coalesce(func.sum(PointTransaction.points), 0).label("points"),
        func.max(PointTransaction.created_at).label("last_scored_at"),
    )
    if bank_id is not None:
        points_query = points_query.where(PointTransaction.bank_id == bank_id)
    points_subquery = points_query.group_by(PointTransaction.user_id).subquery()

    items = []
    rows = db.execute(
        select(User, points_subquery.c.points, points_subquery.c.last_scored_at)
        .join(points_subquery, points_subquery.c.user_id == User.id)
        .order_by(points_subquery.c.points.desc(), User.id.asc())
        .limit(limit)
    ).all()
    for index, (user, points, last_scored_at) in enumerate(rows, start=1):
        answer_query = select(AnswerRecord).where(AnswerRecord.user_id == user.id)
        if bank_id is not None:
            answer_query = answer_query.where(AnswerRecord.bank_id == bank_id)
        answers = db.scalars(answer_query).all()
        correct_count = sum(1 for answer in answers if answer.is_correct)
        accuracy = round(correct_count * 100 / len(answers), 2) if answers else 0
        items.append(
            {
                "rank": index,
                "user_id": user.id,
                "name": user.name,
                "department": user.department or "",
                "points": int(points or 0),
                "accuracy": accuracy,
                "answer_count": len(answers),
                "last_scored_at": last_scored_at.isoformat() if last_scored_at else None,
            }
        )
    return items
