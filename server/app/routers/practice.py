from datetime import datetime
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.database import get_db
from app.models import (
    AiExplanation,
    AnswerRecord,
    LlmConfig,
    LlmRequestLog,
    PointTransaction,
    Question,
    QuestionBank,
    QuestionOption,
    User,
    WrongQuestion,
)
from app.security import get_current_user
from app.services.llm import build_explanation_prompt, request_chat_completion
from app.services.scoring import (
    award_points_with_daily_limit,
    get_or_create_point_rule,
    is_answer_correct,
    normalize_answer,
    points_for_answer,
)


router = APIRouter(tags=["practice"])


class CreateSessionRequest(BaseModel):
    bank_id: int
    count: int = 10


class SubmitAnswerRequest(BaseModel):
    question_id: int
    selected_answer: str
    source: str = "practice"


@router.post("/api/practice/sessions")
def create_practice_session(
    payload: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    bank = db.get(QuestionBank, payload.bank_id)
    if not bank or not bank.is_active:
        raise HTTPException(status_code=404, detail="题库不存在")
    questions = db.scalars(
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.bank_id == payload.bank_id, Question.is_active.is_(True))
        .order_by(func.random())
        .limit(max(min(payload.count, 50), 1))
    ).all()
    return {
        "bank_id": payload.bank_id,
        "questions": [question_payload(question, include_answer=False) for question in questions],
    }


@router.post("/api/practice/answers")
def submit_answer(
    payload: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    question = db.scalar(
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.id == payload.question_id)
    )
    if not question or not question.is_active:
        raise HTTPException(status_code=404, detail="题目不存在")

    selected_answer = normalize_answer(payload.selected_answer)
    is_correct = is_answer_correct(selected_answer, question.correct_answer)
    rule = get_or_create_point_rule(db)
    desired_points = points_for_answer(
        is_correct=is_correct,
        base_points=rule.answer_base_points,
        correct_bonus=rule.correct_bonus_points,
    )
    points_awarded = award_points_with_daily_limit(
        db,
        user_id=current_user.id,
        bank_id=question.bank_id,
        desired_points=desired_points,
        reason=payload.source,
    )
    answer = AnswerRecord(
        user_id=current_user.id,
        bank_id=question.bank_id,
        question_id=question.id,
        selected_answer=selected_answer,
        is_correct=is_correct,
        source=payload.source,
        points_awarded=points_awarded,
    )
    db.add(answer)
    wrong_status = update_wrong_question(db, current_user.id, question, is_correct)
    db.commit()
    return {
        "question_id": question.id,
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
        "correct_answer_text": question.correct_answer_text or "",
        "explanation": question.explanation or "",
        "wrong_question_status": wrong_status,
        "points_awarded": points_awarded,
    }


@router.post("/api/questions/{question_id}/ai-explanation")
async def ai_explanation(
    question_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    config = db.scalar(select(LlmConfig).limit(1))
    enabled = bool(config.enabled) if config else settings.llm_enabled
    model = (config.model if config and config.model else settings.llm_model) or ""
    base_url = (config.base_url if config and config.base_url else settings.llm_base_url) or ""
    api_key = (
        config.api_key_encrypted if config and config.api_key_encrypted else settings.llm_api_key
    ) or ""
    prompt_version = (config.prompt_version if config else "v1") or "v1"
    if not enabled or not model or not base_url or not api_key:
        raise HTTPException(status_code=409, detail="AI讲解未启用")

    question = db.scalar(
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.id == question_id)
    )
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    cached = db.scalar(
        select(AiExplanation).where(
            AiExplanation.question_id == question.id,
            AiExplanation.question_updated_at == question.updated_at,
            AiExplanation.model == model,
            AiExplanation.prompt_version == prompt_version,
        )
    )
    if cached:
        return {"content": cached.content, "cached": True}

    prompt = build_explanation_prompt(
        stem=question.stem,
        options={option.label: option.content for option in sorted(question.options, key=lambda x: x.label)},
        correct_answer=question.correct_answer,
        original_explanation=question.explanation or "",
    )
    started = perf_counter()
    try:
        content = await request_chat_completion(base_url, api_key, model, prompt)
    except Exception as exc:  # pragma: no cover - network errors are environment-specific
        db.add(
            LlmRequestLog(
                question_id=question.id,
                status="failed",
                latency_ms=int((perf_counter() - started) * 1000),
                error_message=str(exc),
            )
        )
        db.commit()
        raise HTTPException(status_code=502, detail="AI讲解生成失败，请稍后再试") from exc

    db.add(
        AiExplanation(
            question_id=question.id,
            question_updated_at=question.updated_at,
            model=model,
            prompt_version=prompt_version,
            content=content,
        )
    )
    db.add(
        LlmRequestLog(
            question_id=question.id,
            status="success",
            latency_ms=int((perf_counter() - started) * 1000),
        )
    )
    db.commit()
    return {"content": content, "cached": False}


def update_wrong_question(db: Session, user_id: int, question: Question, is_correct: bool) -> str:
    wrong = db.scalar(
        select(WrongQuestion).where(
            WrongQuestion.user_id == user_id,
            WrongQuestion.question_id == question.id,
        )
    )
    now = datetime.utcnow()
    if is_correct:
        if wrong and wrong.status == "open":
            wrong.status = "mastered"
            wrong.mastered_at = now
            return "mastered"
        return "none"
    if wrong:
        wrong.status = "open"
        wrong.wrong_count += 1
        wrong.last_wrong_at = now
        wrong.mastered_at = None
    else:
        wrong = WrongQuestion(
            user_id=user_id,
            bank_id=question.bank_id,
            question_id=question.id,
            status="open",
            wrong_count=1,
            last_wrong_at=now,
        )
        db.add(wrong)
    return "open"


def question_payload(question: Question, *, include_answer: bool) -> dict:
    payload = {
        "id": question.id,
        "question_type": question.question_type.value,
        "stem": question.stem,
        "options": [
            {"label": option.label, "content": option.content}
            for option in sorted(question.options, key=lambda item: item.label)
        ],
    }
    if include_answer:
        payload.update(
            {
                "correct_answer": question.correct_answer,
                "correct_answer_text": question.correct_answer_text,
                "explanation": question.explanation,
            }
        )
    return payload
