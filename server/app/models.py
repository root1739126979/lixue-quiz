import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QuestionType(str, enum.Enum):
    single = "single"
    multiple = "multiple"
    judgment = "judgment"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    work_no: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    feishu_user_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class QuestionBank(Base):
    __tablename__ = "question_banks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    exam_question_count: Mapped[int] = mapped_column(Integer, default=20)
    exam_time_limit_minutes: Mapped[int] = mapped_column(Integer, default=30)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    questions: Mapped[list["Question"]] = relationship(back_populates="bank")


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (UniqueConstraint("bank_id", "source_no", name="uq_question_bank_source_no"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    bank_id: Mapped[int] = mapped_column(ForeignKey("question_banks.id"))
    source_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType))
    stem: Mapped[str] = mapped_column(Text)
    correct_answer: Mapped[str] = mapped_column(String(50))
    correct_answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    module: Mapped[str] = mapped_column(String(100), default="未分类")
    difficulty: Mapped[str] = mapped_column(String(50), default="普通")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    bank: Mapped[QuestionBank] = relationship(back_populates="questions")
    options: Mapped[list["QuestionOption"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )


class QuestionOption(Base):
    __tablename__ = "question_options"
    __table_args__ = (UniqueConstraint("question_id", "label", name="uq_option_question_label"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    label: Mapped[str] = mapped_column(String(5))
    content: Mapped[str] = mapped_column(Text)

    question: Mapped[Question] = relationship(back_populates="options")


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    import_type: Mapped[str] = mapped_column(String(50))
    total_rows: Mapped[int] = mapped_column(Integer)
    imported_count: Mapped[int] = mapped_column(Integer)
    error_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PointRule(Base):
    __tablename__ = "point_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    answer_base_points: Mapped[int] = mapped_column(Integer, default=1)
    correct_bonus_points: Mapped[int] = mapped_column(Integer, default=1)
    wrong_retry_correct_points: Mapped[int] = mapped_column(Integer, default=1)
    exam_complete_points: Mapped[int] = mapped_column(Integer, default=10)
    daily_point_limit: Mapped[int] = mapped_column(Integer, default=100)


class PointTransaction(Base):
    __tablename__ = "point_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    bank_id: Mapped[int | None] = mapped_column(ForeignKey("question_banks.id"), nullable=True)
    points: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship()
    bank: Mapped[QuestionBank | None] = relationship()


class AnswerRecord(Base):
    __tablename__ = "answer_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    bank_id: Mapped[int] = mapped_column(ForeignKey("question_banks.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    selected_answer: Mapped[str] = mapped_column(String(50))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    source: Mapped[str] = mapped_column(String(30), default="practice")
    points_awarded: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship()
    bank: Mapped[QuestionBank] = relationship()
    question: Mapped[Question] = relationship()


class WrongQuestion(Base):
    __tablename__ = "wrong_questions"
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_wrong_user_question"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    bank_id: Mapped[int] = mapped_column(ForeignKey("question_banks.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    status: Mapped[str] = mapped_column(String(20), default="open")
    wrong_count: Mapped[int] = mapped_column(Integer, default=1)
    last_wrong_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    mastered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship()
    bank: Mapped[QuestionBank] = relationship()
    question: Mapped[Question] = relationship()


class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    bank_id: Mapped[int] = mapped_column(ForeignKey("question_banks.id"))
    question_count: Mapped[int] = mapped_column(Integer)
    time_limit_minutes: Mapped[int] = mapped_column(Integer)
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    correct_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship()
    bank: Mapped[QuestionBank] = relationship()
    questions: Mapped[list["ExamAttemptQuestion"]] = relationship(cascade="all, delete-orphan")


class ExamAttemptQuestion(Base):
    __tablename__ = "exam_attempt_questions"
    __table_args__ = (UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("exam_attempts.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    source_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    question_type: Mapped[str] = mapped_column(String(20))
    stem: Mapped[str] = mapped_column(Text)
    options_json: Mapped[str] = mapped_column(Text)
    correct_answer: Mapped[str] = mapped_column(String(50))
    correct_answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    question: Mapped[Question] = relationship()


class ExamAnswer(Base):
    __tablename__ = "exam_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("exam_attempts.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    selected_answer: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)


class AiExplanation(Base):
    __tablename__ = "ai_explanations"
    __table_args__ = (
        UniqueConstraint(
            "question_id",
            "question_updated_at",
            "model",
            "prompt_version",
            name="uq_ai_explanation_cache_key",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    question_updated_at: Mapped[datetime] = mapped_column(DateTime)
    model: Mapped[str] = mapped_column(String(100))
    prompt_version: Mapped[str] = mapped_column(String(50), default="v1")
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LlmRequestLog(Base):
    __tablename__ = "llm_request_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int | None] = mapped_column(ForeignKey("questions.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50))
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LlmConfig(Base):
    __tablename__ = "llm_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    base_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    api_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(50), default="v1")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_type: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(100))
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
