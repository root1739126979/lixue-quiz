from datetime import datetime, time

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import PointRule, PointTransaction


def normalize_answer(value: str) -> str:
    normalized = value.replace("，", ",").replace("、", ",").replace("；", ",")
    labels = [part.strip().upper() for part in normalized.split(",") if part.strip()]
    return ",".join(sorted(labels))


def is_answer_correct(selected_answer: str, correct_answer: str) -> bool:
    return normalize_answer(selected_answer) == normalize_answer(correct_answer)


def points_for_answer(is_correct: bool, base_points: int, correct_bonus: int) -> int:
    return base_points + (correct_bonus if is_correct else 0)


def get_or_create_point_rule(db: Session) -> PointRule:
    rule = db.scalar(select(PointRule).limit(1))
    if rule:
        return rule
    rule = PointRule()
    db.add(rule)
    db.flush()
    return rule


def award_points_with_daily_limit(
    db: Session,
    *,
    user_id: int,
    bank_id: int | None,
    desired_points: int,
    reason: str,
) -> int:
    if desired_points <= 0:
        return 0
    rule = get_or_create_point_rule(db)
    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    earned_today = db.scalar(
        select(func.coalesce(func.sum(PointTransaction.points), 0)).where(
            PointTransaction.user_id == user_id,
            PointTransaction.created_at >= today_start,
        )
    )
    remaining = max(rule.daily_point_limit - int(earned_today or 0), 0)
    awarded = min(desired_points, remaining)
    if awarded > 0:
        db.add(
            PointTransaction(
                user_id=user_id,
                bank_id=bank_id,
                points=awarded,
                reason=reason,
            )
        )
    return awarded
