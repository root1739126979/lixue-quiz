from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnswerRecord, PointTransaction, User, WrongQuestion
from app.security import create_access_token, get_current_user, verify_password


router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    account: str
    password: str


@router.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict:
    user = db.scalar(
        select(User).where(or_(User.work_no == payload.account, User.phone == payload.account))
    )
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")

    return {
        "token": create_access_token(subject=str(user.id), role="employee"),
        "user": user_payload(user),
    }


@router.get("/api/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    answer_rows = db.scalars(
        select(AnswerRecord).where(AnswerRecord.user_id == current_user.id)
    ).all()
    answer_count = len(answer_rows)
    correct_count = sum(1 for row in answer_rows if row.is_correct)
    points = sum(
        db.scalars(
            select(PointTransaction.points).where(PointTransaction.user_id == current_user.id)
        ).all()
    )
    wrong_count = (
        db.scalar(
            select(func.count(WrongQuestion.id)).where(
                WrongQuestion.user_id == current_user.id,
                WrongQuestion.status == "open",
            )
        )
        or 0
    )
    return {
        **user_payload(current_user),
        "total_points": points,
        "answer_count": answer_count,
        "accuracy": round(correct_count * 100 / answer_count, 2) if answer_count else 0,
        "wrong_count": wrong_count,
    }


def user_payload(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "work_no": user.work_no,
        "phone": user.phone,
        "department": user.department,
    }
