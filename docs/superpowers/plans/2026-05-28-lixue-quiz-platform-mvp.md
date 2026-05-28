# 砺学多题库刷题平台 MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deployable MVP for the 砺学 multi-question-bank quiz platform with CSV question import, employee login, practice, wrong questions, ranking, lightweight exams, on-demand AI explanations, admin dashboard, and exports.

**Architecture:** Use a single repository with a FastAPI backend and a React/Vite frontend. PostgreSQL stores users, question banks, questions, answers, points, exams, AI explanation cache, and admin configuration. The frontend contains two routed surfaces: employee H5 and admin web console.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, pytest, React, Vite, TypeScript, TanStack Query, React Router, Nginx, Docker Compose, OpenAI-compatible chat completions API.

---

## Confirmed Scope

MVP includes:

- Multi-question-bank employee H5.
- Employee login by work number or phone plus password.
- Admin-only backend console.
- Employee CSV/Excel import.
- Question CSV import using the existing `question/questions.csv` format.
- Question types: single choice, multiple choice, true/false.
- Random practice, answer feedback, original CSV explanation.
- On-demand LLM explanation with database cache.
- Wrong question list and mastered state.
- Configurable point rules.
- Global ranking and per-bank ranking.
- Lightweight simulated exam with fixed question count and time limit.
- Admin dashboard and CSV/Excel export.
- Cloud-server deployment plan with HTTPS.

MVP excludes:

- LLM automatic question generation.
- Real Feishu login and Feishu notifications.
- Multi-role admin permissions.
- Multi-base or department-level permissions.
- Badges, continuous check-in, and complex operation campaigns.

## Existing Input Data

Use `question/questions.csv` as the first real import fixture.

Observed columns:

```text
题号,题型,题干,选项A,选项B,选项C,选项D,选项E,正确答案,正确答案文本,解析
```

Observed question mix:

- 112 single-choice questions.
- 31 multiple-choice questions.
- 26 true/false questions.
- Option E appears in 2 questions.
- Some rows may have missing answer or explanation values and must be reported in import preview instead of crashing.

## Repository Structure

Create this structure:

```text
.
├── README.md
├── .env.example
├── docker-compose.yml
├── question/
│   └── questions.csv
├── server/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── seed.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── auth.py
│   │   │   ├── banks.py
│   │   │   ├── practice.py
│   │   │   ├── wrong_questions.py
│   │   │   ├── rankings.py
│   │   │   ├── exams.py
│   │   │   └── exports.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── csv_importer.py
│   │       ├── scoring.py
│   │       ├── llm.py
│   │       ├── dashboard.py
│   │       └── exports.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   └── tests/
│       ├── conftest.py
│       ├── test_csv_importer.py
│       ├── test_auth.py
│       ├── test_practice.py
│       ├── test_wrong_questions.py
│       ├── test_rankings.py
│       ├── test_exams.py
│       └── test_llm.py
└── web/
    ├── package.json
    ├── index.html
    ├── vite.config.ts
    ├── tsconfig.json
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api/client.ts
        ├── api/types.ts
        ├── styles.css
        ├── employee/
        │   ├── EmployeeLayout.tsx
        │   ├── LoginPage.tsx
        │   ├── BankSelectPage.tsx
        │   ├── PracticePage.tsx
        │   ├── WrongQuestionsPage.tsx
        │   ├── RankingPage.tsx
        │   ├── ExamPage.tsx
        │   └── ProfilePage.tsx
        └── admin/
            ├── AdminLayout.tsx
            ├── AdminLoginPage.tsx
            ├── DashboardPage.tsx
            ├── EmployeesPage.tsx
            ├── QuestionBanksPage.tsx
            ├── QuestionsPage.tsx
            ├── PointRulesPage.tsx
            ├── LlmConfigPage.tsx
            └── ExportsPage.tsx
```

## API Conventions

Use JSON for all normal API responses. Use `Authorization: Bearer <token>` for employee and admin sessions. Admin endpoints start with `/api/admin`. Employee endpoints start with `/api`.

Core endpoints:

```text
POST   /api/auth/login
GET    /api/me
GET    /api/banks
GET    /api/banks/{bank_id}/summary
POST   /api/practice/sessions
POST   /api/practice/answers
GET    /api/wrong-questions
POST   /api/wrong-questions/{question_id}/master
GET    /api/rankings/global
GET    /api/rankings/banks/{bank_id}
POST   /api/exams/attempts
POST   /api/exams/attempts/{attempt_id}/submit
POST   /api/questions/{question_id}/ai-explanation

POST   /api/admin/auth/login
POST   /api/admin/employees/import
GET    /api/admin/employees
POST   /api/admin/banks
GET    /api/admin/banks
POST   /api/admin/banks/{bank_id}/questions/import
GET    /api/admin/questions
PATCH  /api/admin/questions/{question_id}
GET    /api/admin/dashboard
GET    /api/admin/exports/users
GET    /api/admin/exports/answers
GET    /api/admin/exports/exams
GET    /api/admin/point-rules
PUT    /api/admin/point-rules
GET    /api/admin/llm-config
PUT    /api/admin/llm-config
```

---

### Task 1: Project Scaffold

**Files:**
- Create: `README.md`
- Create: `.env.example`
- Create: `server/pyproject.toml`
- Create: `server/app/main.py`
- Create: `server/app/config.py`
- Create: `server/app/database.py`
- Create: `server/tests/conftest.py`

- [ ] **Step 1: Create backend package metadata**

Create `server/pyproject.toml`:

```toml
[project]
name = "lixue-quiz-server"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn[standard]>=0.30.0",
  "sqlalchemy>=2.0.30",
  "alembic>=1.13.0",
  "psycopg[binary]>=3.2.0",
  "pydantic-settings>=2.4.0",
  "python-multipart>=0.0.9",
  "passlib[bcrypt]>=1.7.4",
  "python-jose[cryptography]>=3.3.0",
  "httpx>=0.27.0",
  "pandas>=2.2.0",
  "openpyxl>=3.1.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2.0",
  "pytest-asyncio>=0.23.0",
  "ruff>=0.6.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
line-length = 100
```

- [ ] **Step 2: Create environment template**

Create `.env.example`:

```env
APP_ENV=development
DATABASE_URL=postgresql+psycopg://lixue:lixue@localhost:5432/lixue
JWT_SECRET=change-this-in-production
JWT_EXPIRE_MINUTES=10080
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123456
LLM_ENABLED=false
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
```

- [ ] **Step 3: Create FastAPI app skeleton**

Create `server/app/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite+pysqlite:///./dev.db"
    jwt_secret: str = "dev-secret"
    jwt_expire_minutes: int = 10080
    admin_username: str = "admin"
    admin_password: str = "admin123456"
    llm_enabled: bool = False
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
```

Create `server/app/main.py`:

```python
from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="砺学刷题平台 API")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

- [ ] **Step 4: Add first health test**

Create `server/tests/conftest.py`:

```python
from fastapi.testclient import TestClient

from app.main import create_app


def make_client() -> TestClient:
    return TestClient(create_app())
```

Create `server/tests/test_health.py`:

```python
from tests.conftest import make_client


def test_health_endpoint_returns_ok():
    client = make_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 5: Run scaffold tests**

Run:

```powershell
cd server
python -m pytest tests/test_health.py -q
```

Expected: `1 passed`.

---

### Task 2: Database Models and Migrations

**Files:**
- Create: `server/app/models.py`
- Create: `server/app/database.py`
- Create: `server/alembic.ini`
- Create: `server/alembic/env.py`
- Create: `server/alembic/versions/0001_initial.py`
- Test: `server/tests/test_models.py`

- [ ] **Step 1: Define SQLAlchemy base and session**

Create `server/app/database.py`:

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: Define core models**

Create `server/app/models.py` with these tables and enum values:

```python
import enum
from datetime import datetime

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
    work_no: Mapped[str | None] = mapped_column(String(100), unique=True)
    phone: Mapped[str | None] = mapped_column(String(50), unique=True)
    department: Mapped[str | None] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(255))
    feishu_user_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


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
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    exam_question_count: Mapped[int] = mapped_column(Integer, default=20)
    exam_time_limit_minutes: Mapped[int] = mapped_column(Integer, default=30)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (UniqueConstraint("bank_id", "source_no", name="uq_question_bank_source_no"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    bank_id: Mapped[int] = mapped_column(ForeignKey("question_banks.id"))
    source_no: Mapped[str | None] = mapped_column(String(50))
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType))
    stem: Mapped[str] = mapped_column(Text)
    correct_answer: Mapped[str] = mapped_column(String(50))
    correct_answer_text: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)
    module: Mapped[str] = mapped_column(String(100), default="未分类")
    difficulty: Mapped[str] = mapped_column(String(50), default="普通")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    bank: Mapped[QuestionBank] = relationship()
    options: Mapped[list["QuestionOption"]] = relationship(cascade="all, delete-orphan")


class QuestionOption(Base):
    __tablename__ = "question_options"
    __table_args__ = (UniqueConstraint("question_id", "label", name="uq_option_question_label"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    label: Mapped[str] = mapped_column(String(5))
    content: Mapped[str] = mapped_column(Text)


class PointRule(Base):
    __tablename__ = "point_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    answer_base_points: Mapped[int] = mapped_column(Integer, default=1)
    correct_bonus_points: Mapped[int] = mapped_column(Integer, default=1)
    exam_complete_points: Mapped[int] = mapped_column(Integer, default=10)
    daily_point_limit: Mapped[int] = mapped_column(Integer, default=100)


class PointTransaction(Base):
    __tablename__ = "point_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    bank_id: Mapped[int | None] = mapped_column(ForeignKey("question_banks.id"))
    points: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AnswerRecord(Base):
    __tablename__ = "answer_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    bank_id: Mapped[int] = mapped_column(ForeignKey("question_banks.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    selected_answer: Mapped[str] = mapped_column(String(50))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    source: Mapped[str] = mapped_column(String(30), default="practice")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


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
    mastered_at: Mapped[datetime | None] = mapped_column(DateTime)


class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    bank_id: Mapped[int] = mapped_column(ForeignKey("question_banks.id"))
    question_count: Mapped[int] = mapped_column(Integer)
    time_limit_minutes: Mapped[int] = mapped_column(Integer)
    score: Mapped[Numeric | None] = mapped_column(Numeric(5, 2))
    correct_count: Mapped[int | None] = mapped_column(Integer)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExamAnswer(Base):
    __tablename__ = "exam_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("exam_attempts.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    selected_answer: Mapped[str | None] = mapped_column(String(50))
    is_correct: Mapped[bool | None] = mapped_column(Boolean)


class AiExplanation(Base):
    __tablename__ = "ai_explanations"
    __table_args__ = (UniqueConstraint("question_id", "model", name="uq_ai_explanation_question_model"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    model: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LlmConfig(Base):
    __tablename__ = "llm_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    base_url: Mapped[str | None] = mapped_column(String(255))
    api_key_encrypted: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(String(100))
```

- [ ] **Step 3: Add table creation test**

Create `server/tests/test_models.py`:

```python
from sqlalchemy import create_engine

from app.database import Base
from app import models


def test_models_create_all_tables_in_sqlite_memory():
    engine = create_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(engine)

    table_names = set(Base.metadata.tables)
    assert "users" in table_names
    assert "question_banks" in table_names
    assert "questions" in table_names
    assert "answer_records" in table_names
    assert "exam_attempts" in table_names
    assert models.QuestionType.single.value == "single"
```

- [ ] **Step 4: Run model test**

Run:

```powershell
cd server
python -m pytest tests/test_models.py -q
```

Expected: `1 passed`.

---

### Task 3: Security and Authentication

**Files:**
- Create: `server/app/security.py`
- Create: `server/app/routers/auth.py`
- Modify: `server/app/main.py`
- Test: `server/tests/test_auth.py`

- [ ] **Step 1: Write authentication tests**

Create `server/tests/test_auth.py`:

```python
from app.security import create_access_token, hash_password, verify_password


def test_password_hash_verification():
    password_hash = hash_password("secret123")

    assert verify_password("secret123", password_hash)
    assert not verify_password("wrong", password_hash)


def test_access_token_contains_subject_and_role():
    token = create_access_token(subject="42", role="employee")

    assert isinstance(token, str)
    assert token.count(".") == 2
```

- [ ] **Step 2: Implement password hashing and JWT helpers**

Create `server/app/security.py`:

```python
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str, role: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
```

- [ ] **Step 3: Run authentication tests**

Run:

```powershell
cd server
python -m pytest tests/test_auth.py -q
```

Expected: `2 passed`.

---

### Task 4: CSV Question Importer

**Files:**
- Create: `server/app/services/csv_importer.py`
- Test: `server/tests/test_csv_importer.py`

- [ ] **Step 1: Write importer tests for the real CSV**

Create `server/tests/test_csv_importer.py`:

```python
from pathlib import Path

from app.services.csv_importer import parse_question_csv


def test_parse_existing_question_csv_supports_all_question_types():
    result = parse_question_csv(Path("../question/questions.csv"))

    assert result.total_rows == 169
    assert result.valid_count >= 160
    assert {"single", "multiple", "judgment"}.issubset(result.type_counts)
    assert result.rows[0].source_no == "1"
    assert result.rows[0].stem
    assert result.rows[0].options


def test_parse_question_csv_reports_invalid_rows_without_crashing(tmp_path):
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text(
        "题号,题型,题干,选项A,选项B,选项C,选项D,选项E,正确答案,正确答案文本,解析\n"
        "1,单选题,题干,A,B,C,D,,A,A文本,解析\n"
        "2,单选题,缺答案,A,B,C,D,,,\n",
        encoding="utf-8-sig",
    )

    result = parse_question_csv(csv_file)

    assert result.total_rows == 2
    assert result.valid_count == 1
    assert len(result.errors) == 1
    assert result.errors[0].row_number == 3
    assert "正确答案" in result.errors[0].message
```

- [ ] **Step 2: Implement CSV parser**

Create `server/app/services/csv_importer.py`:

```python
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import csv


QUESTION_TYPE_MAP = {
    "单选题": "single",
    "多选题": "multiple",
    "判断题": "judgment",
}


@dataclass(frozen=True)
class ParsedOption:
    label: str
    content: str


@dataclass(frozen=True)
class ParsedQuestion:
    source_no: str
    question_type: str
    stem: str
    options: list[ParsedOption]
    correct_answer: str
    correct_answer_text: str
    explanation: str


@dataclass(frozen=True)
class ImportErrorItem:
    row_number: int
    message: str


@dataclass(frozen=True)
class ImportPreview:
    total_rows: int
    valid_count: int
    type_counts: set[str]
    rows: list[ParsedQuestion]
    errors: list[ImportErrorItem]


def normalize_answer(answer: str) -> str:
    labels = [part.strip().upper() for part in answer.replace("，", ",").split(",") if part.strip()]
    return ",".join(labels)


def parse_question_csv(path: Path) -> ImportPreview:
    rows: list[ParsedQuestion] = []
    errors: list[ImportErrorItem] = []
    type_counter: Counter[str] = Counter()

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row_index, row in enumerate(reader, start=2):
            question_type = QUESTION_TYPE_MAP.get((row.get("题型") or "").strip())
            stem = (row.get("题干") or "").strip()
            answer = normalize_answer(row.get("正确答案") or "")

            if not question_type:
                errors.append(ImportErrorItem(row_index, "题型必须是单选题、多选题或判断题"))
                continue
            if not stem:
                errors.append(ImportErrorItem(row_index, "题干不能为空"))
                continue
            if not answer:
                errors.append(ImportErrorItem(row_index, "正确答案不能为空"))
                continue

            options = []
            for label in ["A", "B", "C", "D", "E"]:
                content = (row.get(f"选项{label}") or "").strip()
                if content:
                    options.append(ParsedOption(label=label, content=content))
            if not options:
                errors.append(ImportErrorItem(row_index, "至少需要一个选项"))
                continue

            rows.append(
                ParsedQuestion(
                    source_no=(row.get("题号") or "").strip(),
                    question_type=question_type,
                    stem=stem,
                    options=options,
                    correct_answer=answer,
                    correct_answer_text=(row.get("正确答案文本") or "").strip(),
                    explanation=(row.get("解析") or "").strip(),
                )
            )
            type_counter[question_type] += 1

    return ImportPreview(
        total_rows=len(rows) + len(errors),
        valid_count=len(rows),
        type_counts=set(type_counter),
        rows=rows,
        errors=errors,
    )
```

- [ ] **Step 3: Run importer tests**

Run:

```powershell
cd server
python -m pytest tests/test_csv_importer.py -q
```

Expected: `2 passed`.

---

### Task 5: Admin Question Bank and Import APIs

**Files:**
- Create: `server/app/routers/admin.py`
- Modify: `server/app/main.py`
- Test: `server/tests/test_admin_import.py`

- [ ] **Step 1: Write admin import API test**

Create `server/tests/test_admin_import.py`:

```python
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def test_admin_can_create_bank_and_import_questions():
    client = TestClient(create_app())

    bank_response = client.post(
        "/api/admin/banks",
        json={"name": "设备知识题库", "description": "首批设备岗位知识题库"},
    )
    assert bank_response.status_code == 201
    bank_id = bank_response.json()["id"]

    csv_path = Path("../question/questions.csv")
    with csv_path.open("rb") as file:
        response = client.post(
            f"/api/admin/banks/{bank_id}/questions/import",
            files={"file": ("questions.csv", file, "text/csv")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_rows"] == 169
    assert payload["imported_count"] >= 160
    assert "single" in payload["type_counts"]
```

- [ ] **Step 2: Implement admin bank and import endpoints**

Create `server/app/routers/admin.py`:

```python
from pathlib import Path
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.services.csv_importer import parse_question_csv


router = APIRouter(prefix="/api/admin", tags=["admin"])

_memory_banks: dict[int, dict] = {}
_memory_questions: list[dict] = []


class CreateBankRequest(BaseModel):
    name: str
    description: str | None = None


@router.post("/banks", status_code=status.HTTP_201_CREATED)
def create_bank(payload: CreateBankRequest) -> dict:
    bank_id = len(_memory_banks) + 1
    bank = {"id": bank_id, "name": payload.name, "description": payload.description, "is_active": True}
    _memory_banks[bank_id] = bank
    return bank


@router.post("/banks/{bank_id}/questions/import")
async def import_questions(bank_id: int, file: UploadFile = File(...)) -> dict:
    if bank_id not in _memory_banks:
        raise HTTPException(status_code=404, detail="题库不存在")

    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(content)
        temp_path = Path(temp_file.name)

    preview = parse_question_csv(temp_path)
    for item in preview.rows:
        _memory_questions.append({"bank_id": bank_id, **item.__dict__})

    return {
        "total_rows": preview.total_rows,
        "imported_count": preview.valid_count,
        "type_counts": sorted(preview.type_counts),
        "errors": [error.__dict__ for error in preview.errors],
    }
```

Modify `server/app/main.py`:

```python
from fastapi import FastAPI

from app.routers import admin


def create_app() -> FastAPI:
    app = FastAPI(title="砺学刷题平台 API")
    app.include_router(admin.router)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

- [ ] **Step 3: Run admin import API test**

Run:

```powershell
cd server
python -m pytest tests/test_admin_import.py -q
```

Expected: `1 passed`.

- [ ] **Step 4: Replace memory storage with SQLAlchemy**

Modify the endpoint implementation to use `QuestionBank`, `Question`, and `QuestionOption` models with a database session. Keep the same response shape so tests continue to pass.

- [ ] **Step 5: Run all backend tests**

Run:

```powershell
cd server
python -m pytest -q
```

Expected: all existing tests pass.

---

### Task 6: Employee Import and Login

**Files:**
- Create: `server/app/routers/auth.py`
- Modify: `server/app/routers/admin.py`
- Modify: `server/app/main.py`
- Test: `server/tests/test_employee_import_and_login.py`

- [ ] **Step 1: Write employee import and login tests**

Create `server/tests/test_employee_import_and_login.py`:

```python
from io import BytesIO

from fastapi.testclient import TestClient

from app.main import create_app


def test_admin_imports_employee_and_employee_logs_in():
    client = TestClient(create_app())
    csv_bytes = "姓名,工号,手机号,部门,初始密码\n张三,E001,13800000001,装备部,123456\n".encode("utf-8-sig")

    import_response = client.post(
        "/api/admin/employees/import",
        files={"file": ("employees.csv", BytesIO(csv_bytes), "text/csv")},
    )
    assert import_response.status_code == 200
    assert import_response.json()["imported_count"] == 1

    login_response = client.post(
        "/api/auth/login",
        json={"account": "E001", "password": "123456"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["token"]
    assert login_response.json()["user"]["name"] == "张三"
```

- [ ] **Step 2: Implement employee import**

In `server/app/routers/admin.py`, add:

```python
@router.post("/employees/import")
async def import_employees(file: UploadFile = File(...)) -> dict:
    content = (await file.read()).decode("utf-8-sig")
    lines = content.splitlines()
    reader = csv.DictReader(lines)
    imported = 0
    errors = []
    for row_number, row in enumerate(reader, start=2):
        name = (row.get("姓名") or "").strip()
        work_no = (row.get("工号") or "").strip()
        phone = (row.get("手机号") or "").strip()
        password = (row.get("初始密码") or "123456").strip()
        if not name or not (work_no or phone):
            errors.append({"row_number": row_number, "message": "姓名以及工号或手机号不能为空"})
            continue
        # Insert or update the user in the `users` table with hash_password(password).
        # If both work_no and phone are empty, keep the row in `errors`.
        # If the work_no or phone already exists, update name, department, active state,
        # and only replace the password when `初始密码` is present in the import row.
        imported += 1
    return {"imported_count": imported, "errors": errors}
```

This endpoint must use the `User` model and commit imported users in one transaction. Roll back the transaction and return `400` if duplicate work numbers or phones appear inside the same uploaded file.

- [ ] **Step 3: Implement employee login**

Create `server/app/routers/auth.py`:

```python
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.security import create_access_token
from app.security import verify_password


router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    account: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict:
    user = db.scalar(
        select(User).where(or_(User.work_no == payload.account, User.phone == payload.account))
    )
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")

    return {
        "token": create_access_token(subject=str(user.id), role="employee"),
        "user": {
            "id": user.id,
            "name": user.name,
            "work_no": user.work_no,
            "phone": user.phone,
            "department": user.department,
        },
    }
```

Add a reusable authenticated-user dependency in this task before building employee endpoints:

```python
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="登录已失效") from exc
    if payload.get("role") != "employee":
        raise HTTPException(status_code=403, detail="权限不足")
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不可用")
    return user
```

Add the employee profile endpoint in the same router:

```python
@router.get("/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    total_points = 0
    answer_count = 0
    correct_count = 0
    wrong_count = 0
    # Fill these values with aggregate queries against point_transactions,
    # answer_records, and wrong_questions.
    accuracy = round(correct_count * 100 / answer_count, 1) if answer_count else 0
    return {
        "id": current_user.id,
        "name": current_user.name,
        "department": current_user.department,
        "total_points": total_points,
        "answer_count": answer_count,
        "accuracy": accuracy,
        "wrong_count": wrong_count,
    }
```

- [ ] **Step 4: Register auth router**

Modify `server/app/main.py`:

```python
from app.routers import admin, auth

app.include_router(auth.router)
app.include_router(admin.router)
```

- [ ] **Step 5: Run employee auth test**

Run:

```powershell
cd server
python -m pytest tests/test_employee_import_and_login.py -q
```

Expected: `1 passed`.

---

### Task 7: Practice Answer Flow and Scoring

**Files:**
- Create: `server/app/services/scoring.py`
- Create: `server/app/routers/practice.py`
- Modify: `server/app/main.py`
- Test: `server/tests/test_practice.py`

- [ ] **Step 1: Write scoring tests**

Create `server/tests/test_practice.py`:

```python
from app.services.scoring import is_answer_correct, points_for_answer


def test_single_choice_answer_scoring():
    assert is_answer_correct("A", "A")
    assert is_answer_correct(" a ", "A")
    assert not is_answer_correct("B", "A")


def test_multiple_choice_answer_scoring_is_order_insensitive():
    assert is_answer_correct("B,A,C", "A,B,C")
    assert not is_answer_correct("A,C", "A,B,C")


def test_points_for_answer_uses_rule_values():
    assert points_for_answer(is_correct=True, base_points=1, correct_bonus=2) == 3
    assert points_for_answer(is_correct=False, base_points=1, correct_bonus=2) == 1
```

- [ ] **Step 2: Implement scoring helpers**

Create `server/app/services/scoring.py`:

```python
def normalize_answer(value: str) -> str:
    labels = [part.strip().upper() for part in value.replace("，", ",").split(",") if part.strip()]
    return ",".join(sorted(labels))


def is_answer_correct(selected_answer: str, correct_answer: str) -> bool:
    return normalize_answer(selected_answer) == normalize_answer(correct_answer)


def points_for_answer(is_correct: bool, base_points: int, correct_bonus: int) -> int:
    return base_points + (correct_bonus if is_correct else 0)
```

- [ ] **Step 3: Implement practice endpoints**

Create `server/app/routers/practice.py`:

```python
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/api/practice", tags=["practice"])


class CreateSessionRequest(BaseModel):
    bank_id: int
    count: int = 10


class SubmitAnswerRequest(BaseModel):
    question_id: int
    selected_answer: str
    source: str = "practice"


@router.post("/sessions")
def create_practice_session(payload: CreateSessionRequest) -> dict:
    # Query active questions by bank_id, randomize in the database, and return
    # at most `payload.count` items with id, question_type, stem, and options.
    # Do not include correct_answer in this response.
    return {"bank_id": payload.bank_id, "questions": [{"id": 1, "question_type": "single", "stem": "示例题干", "options": []}]}


@router.post("/answers")
def submit_answer(payload: SubmitAnswerRequest) -> dict:
    # Load the question, compare selected_answer with correct_answer through
    # is_answer_correct(), insert AnswerRecord, update WrongQuestion, insert
    # PointTransaction within the daily limit, and return feedback.
    return {
        "question_id": payload.question_id,
        "is_correct": False,
        "correct_answer": "A",
        "explanation": "CSV 原解析",
        "points_awarded": 0,
    }
```

The accepted implementation must reject inactive questions with `404`, reject questions outside the selected bank with `400`, and never award points beyond the configured daily limit.

- [ ] **Step 4: Register practice router**

Modify `server/app/main.py`:

```python
from app.routers import admin, auth, practice

app.include_router(practice.router)
```

- [ ] **Step 5: Run scoring tests**

Run:

```powershell
cd server
python -m pytest tests/test_practice.py -q
```

Expected: `3 passed`.

---

### Task 8: Wrong Questions

**Files:**
- Create: `server/app/routers/wrong_questions.py`
- Modify: `server/app/main.py`
- Test: `server/tests/test_wrong_questions.py`

- [ ] **Step 1: Write wrong question behavior test**

Create `server/tests/test_wrong_questions.py`:

```python
from datetime import datetime


def test_wrong_question_lifecycle_contract():
    wrong_question = {
        "status": "open",
        "wrong_count": 1,
        "mastered_at": None,
    }

    wrong_question["status"] = "mastered"
    wrong_question["mastered_at"] = datetime.utcnow().isoformat()

    assert wrong_question["status"] == "mastered"
    assert wrong_question["mastered_at"] is not None
```

- [ ] **Step 2: Implement wrong question endpoints**

Create `server/app/routers/wrong_questions.py`:

```python
from fastapi import APIRouter


router = APIRouter(prefix="/api/wrong-questions", tags=["wrong-questions"])


@router.get("")
def list_wrong_questions(bank_id: int | None = None) -> dict:
    # Query WrongQuestion rows for the authenticated user where status == "open".
    # Join Question and QuestionBank so the response includes bank name, stem,
    # options, correct_answer, original explanation, wrong_count, and last_wrong_at.
    return {"items": [], "bank_id": bank_id}


@router.post("/{question_id}/master")
def mark_mastered(question_id: int) -> dict:
    # Update only the authenticated user's WrongQuestion row for this question.
    # Set status="mastered" and mastered_at=datetime.utcnow().
    return {"question_id": question_id, "status": "mastered"}
```

Both endpoints must depend on `get_current_user`. `mark_mastered` returns `404` if the question is not in the user's open wrong-question list.

- [ ] **Step 3: Register router and run test**

Modify `server/app/main.py` to include `wrong_questions.router`.

Run:

```powershell
cd server
python -m pytest tests/test_wrong_questions.py -q
```

Expected: `1 passed`.

---

### Task 9: Rankings and Point Rules

**Files:**
- Create: `server/app/routers/rankings.py`
- Modify: `server/app/routers/admin.py`
- Modify: `server/app/main.py`
- Test: `server/tests/test_rankings.py`

- [ ] **Step 1: Write ranking calculation test**

Create `server/tests/test_rankings.py`:

```python
from collections import defaultdict


def build_ranking(transactions, bank_id=None):
    totals = defaultdict(int)
    for item in transactions:
        if bank_id is None or item["bank_id"] == bank_id:
            totals[item["user"]] += item["points"]
    return sorted(totals.items(), key=lambda pair: pair[1], reverse=True)


def test_global_and_bank_rankings_are_separate():
    transactions = [
        {"user": "张三", "bank_id": 1, "points": 10},
        {"user": "李四", "bank_id": 1, "points": 8},
        {"user": "李四", "bank_id": 2, "points": 20},
    ]

    assert build_ranking(transactions)[0] == ("李四", 28)
    assert build_ranking(transactions, bank_id=1)[0] == ("张三", 10)
```

- [ ] **Step 2: Implement ranking endpoints**

Create `server/app/routers/rankings.py`:

```python
from fastapi import APIRouter


router = APIRouter(prefix="/api/rankings", tags=["rankings"])


@router.get("/global")
def global_ranking(limit: int = 50) -> dict:
    # SELECT user_id, SUM(points) FROM point_transactions GROUP BY user_id
    # ORDER BY SUM(points) DESC LIMIT :limit, then join users for name and department.
    return {"items": [], "limit": limit}


@router.get("/banks/{bank_id}")
def bank_ranking(bank_id: int, limit: int = 50) -> dict:
    # Same aggregate as global_ranking, filtered by point_transactions.bank_id.
    return {"bank_id": bank_id, "items": [], "limit": limit}
```

Returned ranking items must include `rank`, `user_id`, `name`, `department`, and `points`. Users with equal points keep deterministic ordering by `user_id`.

- [ ] **Step 3: Implement point rules endpoints**

In `server/app/routers/admin.py`, add:

```python
@router.get("/point-rules")
def get_point_rules() -> dict:
    return {
        "answer_base_points": 1,
        "correct_bonus_points": 1,
        "exam_complete_points": 10,
        "daily_point_limit": 100,
    }


@router.put("/point-rules")
def update_point_rules(payload: dict) -> dict:
    return payload
```

Persist rules in the single-row `PointRule` table. If the row does not exist, create it with defaults before applying updates.

- [ ] **Step 4: Register router and run tests**

Run:

```powershell
cd server
python -m pytest tests/test_rankings.py -q
```

Expected: `1 passed`.

---

### Task 10: Lightweight Simulated Exams

**Files:**
- Create: `server/app/routers/exams.py`
- Modify: `server/app/main.py`
- Test: `server/tests/test_exams.py`

- [ ] **Step 1: Write exam scoring test**

Create `server/tests/test_exams.py`:

```python
from decimal import Decimal


def exam_score(correct_count: int, total_count: int) -> Decimal:
    return Decimal(correct_count * 100) / Decimal(total_count)


def test_exam_score_is_percentage():
    assert exam_score(8, 10) == Decimal("80")
```

- [ ] **Step 2: Implement exam endpoints**

Create `server/app/routers/exams.py`:

```python
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/api/exams", tags=["exams"])


class CreateExamAttemptRequest(BaseModel):
    bank_id: int


class SubmitExamAnswer(BaseModel):
    question_id: int
    selected_answer: str


class SubmitExamRequest(BaseModel):
    answers: list[SubmitExamAnswer]


@router.post("/attempts")
def create_exam_attempt(payload: CreateExamAttemptRequest) -> dict:
    return {"attempt_id": 1, "bank_id": payload.bank_id, "questions": [], "time_limit_minutes": 30}


@router.post("/attempts/{attempt_id}/submit")
def submit_exam_attempt(attempt_id: int, payload: SubmitExamRequest) -> dict:
    return {"attempt_id": attempt_id, "score": 0, "correct_count": 0, "total_count": len(payload.answers)}
```

Final behavior:

- Use bank `exam_question_count` and `exam_time_limit_minutes`.
- Randomly pick active questions.
- Store `ExamAttempt` and `ExamAnswer` rows.
- Score each answer with `is_answer_correct`.
- Award configured exam completion points once per submitted attempt.

- [ ] **Step 3: Register router and run tests**

Run:

```powershell
cd server
python -m pytest tests/test_exams.py -q
```

Expected: `1 passed`.

---

### Task 11: LLM Explanation Service

**Files:**
- Create: `server/app/services/llm.py`
- Modify: `server/app/routers/practice.py`
- Test: `server/tests/test_llm.py`

- [ ] **Step 1: Write LLM prompt and cache tests**

Create `server/tests/test_llm.py`:

```python
from app.services.llm import build_explanation_prompt


def test_build_explanation_prompt_contains_question_and_original_explanation():
    prompt = build_explanation_prompt(
        stem="三联件的组成及顺序正确的是",
        options={"A": "油雾器、电磁阀、过滤器", "C": "过滤器、减压阀、油雾器"},
        correct_answer="C",
        original_explanation="安装正确顺序：过滤器、减压阀、油污器。",
    )

    assert "三联件" in prompt
    assert "正确答案：C" in prompt
    assert "不要编造" in prompt
```

- [ ] **Step 2: Implement LLM service**

Create `server/app/services/llm.py`:

```python
import httpx


def build_explanation_prompt(
    stem: str,
    options: dict[str, str],
    correct_answer: str,
    original_explanation: str,
) -> str:
    option_lines = "\n".join(f"{label}. {content}" for label, content in options.items())
    return (
        "你是企业内部培训刷题系统的讲解助手。请基于题目、选项、正确答案和原解析，"
        "给出简洁、准确、适合员工复习的补充讲解。不要编造题目没有支持的事实。\n\n"
        f"题目：{stem}\n"
        f"选项：\n{option_lines}\n"
        f"正确答案：{correct_answer}\n"
        f"原解析：{original_explanation or '无'}\n\n"
        "请输出三段：答案解释、易错点、关联知识。"
    )


async def request_chat_completion(base_url: str, api_key: str, model: str, prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            base_url.rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
```

- [ ] **Step 3: Add AI explanation endpoint**

Add an endpoint:

```text
POST /api/questions/{question_id}/ai-explanation
```

Behavior:

- If LLM disabled, return `409` with message `AI讲解未启用`.
- If cached explanation exists for `question_id + model`, return it.
- Otherwise build prompt, call OpenAI-compatible API, store result in `ai_explanations`, and return content.

- [ ] **Step 4: Run LLM tests**

Run:

```powershell
cd server
python -m pytest tests/test_llm.py -q
```

Expected: `1 passed`.

---

### Task 12: Admin Dashboard and Exports

**Files:**
- Create: `server/app/services/dashboard.py`
- Create: `server/app/services/exports.py`
- Create: `server/app/routers/exports.py`
- Modify: `server/app/routers/admin.py`
- Test: `server/tests/test_exports.py`

- [ ] **Step 1: Write export CSV test**

Create `server/tests/test_exports.py`:

```python
from app.services.exports import rows_to_csv


def test_rows_to_csv_includes_utf8_bom_and_headers():
    content = rows_to_csv(
        headers=["姓名", "累计答题数"],
        rows=[["张三", 12]],
    )

    assert content.startswith("\ufeff")
    assert "姓名,累计答题数" in content
    assert "张三,12" in content
```

- [ ] **Step 2: Implement CSV export helper**

Create `server/app/services/exports.py`:

```python
import csv
from io import StringIO


def rows_to_csv(headers: list[str], rows: list[list[object]]) -> str:
    output = StringIO()
    output.write("\ufeff")
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return output.getvalue()
```

- [ ] **Step 3: Implement dashboard service**

Create `server/app/services/dashboard.py`:

```python
def empty_dashboard() -> dict:
    return {
        "participant_count": 0,
        "active_user_count": 0,
        "answer_count": 0,
        "overall_accuracy": 0,
        "bank_accuracy": [],
        "top_wrong_questions": [],
        "exam_score_distribution": [],
        "ranking_preview": [],
    }
```

Replace with SQL aggregate queries after answer, point, and exam tables are wired.

- [ ] **Step 4: Implement admin dashboard and export endpoints**

Add endpoints:

```text
GET /api/admin/dashboard
GET /api/admin/exports/users
GET /api/admin/exports/answers
GET /api/admin/exports/exams
```

Use `StreamingResponse` with `text/csv; charset=utf-8`.

- [ ] **Step 5: Run export tests**

Run:

```powershell
cd server
python -m pytest tests/test_exports.py -q
```

Expected: `1 passed`.

---

### Task 13: Frontend Scaffold

**Files:**
- Create: `web/package.json`
- Create: `web/index.html`
- Create: `web/vite.config.ts`
- Create: `web/tsconfig.json`
- Create: `web/src/main.tsx`
- Create: `web/src/App.tsx`
- Create: `web/src/api/client.ts`
- Create: `web/src/api/types.ts`
- Create: `web/src/styles.css`

- [ ] **Step 1: Create frontend package**

Create `web/package.json`:

```json
{
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "build": "tsc && vite build",
    "preview": "vite preview --host 0.0.0.0"
  },
  "dependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^5.4.0",
    "typescript": "^5.5.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.26.0",
    "@tanstack/react-query": "^5.51.0",
    "lucide-react": "^0.468.0"
  },
  "devDependencies": {}
}
```

- [ ] **Step 2: Create API client**

Create `web/src/api/client.ts`:

```ts
const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("lixue_token");
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}
```

- [ ] **Step 3: Create router shell**

Create `web/src/App.tsx`:

```tsx
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { LoginPage } from "./employee/LoginPage";
import { BankSelectPage } from "./employee/BankSelectPage";
import { PracticePage } from "./employee/PracticePage";
import { WrongQuestionsPage } from "./employee/WrongQuestionsPage";
import { RankingPage } from "./employee/RankingPage";
import { ExamPage } from "./employee/ExamPage";
import { ProfilePage } from "./employee/ProfilePage";
import { AdminLoginPage } from "./admin/AdminLoginPage";
import { DashboardPage } from "./admin/DashboardPage";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/banks" element={<BankSelectPage />} />
        <Route path="/practice/:bankId" element={<PracticePage />} />
        <Route path="/wrong" element={<WrongQuestionsPage />} />
        <Route path="/ranking" element={<RankingPage />} />
        <Route path="/exam/:bankId" element={<ExamPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/admin/login" element={<AdminLoginPage />} />
        <Route path="/admin" element={<DashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

- [ ] **Step 4: Build frontend**

Run:

```powershell
cd web
npm install
npm run build
```

Expected: Vite build succeeds.

---

### Task 14: Employee H5 Pages

**Files:**
- Create: `web/src/employee/LoginPage.tsx`
- Create: `web/src/employee/BankSelectPage.tsx`
- Create: `web/src/employee/PracticePage.tsx`
- Create: `web/src/employee/WrongQuestionsPage.tsx`
- Create: `web/src/employee/RankingPage.tsx`
- Create: `web/src/employee/ExamPage.tsx`
- Create: `web/src/employee/ProfilePage.tsx`
- Create: `web/src/employee/EmployeeLayout.tsx`
- Modify: `web/src/styles.css`

- [ ] **Step 1: Implement employee layout**

Create `web/src/employee/EmployeeLayout.tsx`:

```tsx
import { BookOpen, ClipboardList, Trophy, User } from "lucide-react";
import { Link, Outlet } from "react-router-dom";

export function EmployeeLayout() {
  return (
    <div className="mobile-shell">
      <main className="mobile-main">
        <Outlet />
      </main>
      <nav className="bottom-tabs">
        <Link to="/banks"><BookOpen size={18} />题库</Link>
        <Link to="/wrong"><ClipboardList size={18} />错题</Link>
        <Link to="/ranking"><Trophy size={18} />排行</Link>
        <Link to="/profile"><User size={18} />我的</Link>
      </nav>
    </div>
  );
}
```

- [ ] **Step 2: Implement login page**

Create `web/src/employee/LoginPage.tsx`:

```tsx
import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiRequest } from "../api/client";

export function LoginPage() {
  const navigate = useNavigate();
  const [account, setAccount] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const result = await apiRequest<{ token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ account, password }),
      });
      localStorage.setItem("lixue_token", result.token);
      navigate("/banks");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    }
  }

  return (
    <main className="login-page">
      <h1>砺学</h1>
      <form onSubmit={submit} className="panel">
        <input value={account} onChange={(e) => setAccount(e.target.value)} placeholder="工号或手机号" />
        <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="密码" type="password" />
        {error && <p className="error">{error}</p>}
        <button type="submit">登录</button>
      </form>
    </main>
  );
}
```

- [ ] **Step 3: Implement bank select page**

Create `web/src/employee/BankSelectPage.tsx`:

```tsx
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "../api/client";

type BankSummary = {
  id: number;
  name: string;
  description: string;
  question_count: number;
  practiced_count: number;
  accuracy: number;
  points: number;
};

export function BankSelectPage() {
  const { data } = useQuery({
    queryKey: ["banks"],
    queryFn: () => apiRequest<{ items: BankSummary[] }>("/banks"),
  });

  return (
    <section>
      <h1>选择题库</h1>
      <div className="card-list">
        {data?.items.map((bank) => (
          <article className="card" key={bank.id}>
            <h2>{bank.name}</h2>
            <p>{bank.description}</p>
            <div className="metrics">
              <span>{bank.question_count} 题</span>
              <span>正确率 {bank.accuracy}%</span>
              <span>{bank.points} 分</span>
            </div>
            <div className="actions">
              <Link to={`/practice/${bank.id}`}>开始练习</Link>
              <Link to={`/exam/${bank.id}`}>模拟考试</Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
```

- [ ] **Step 4: Implement practice, wrong questions, ranking, exam, and profile pages**

Create `web/src/employee/PracticePage.tsx`:

```tsx
import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { apiRequest } from "../api/client";

type PracticeQuestion = {
  id: number;
  question_type: "single" | "multiple" | "judgment";
  stem: string;
  options: { label: string; content: string }[];
};

export function PracticePage() {
  const { bankId } = useParams();
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<string[]>([]);
  const [feedback, setFeedback] = useState<any>(null);
  const [aiContent, setAiContent] = useState("");
  const { data } = useQuery({
    queryKey: ["practice", bankId],
    queryFn: () =>
      apiRequest<{ questions: PracticeQuestion[] }>("/practice/sessions", {
        method: "POST",
        body: JSON.stringify({ bank_id: Number(bankId), count: 10 }),
      }),
  });
  const questions = data?.questions ?? [];
  const question = questions[index];
  const selectedAnswer = useMemo(() => selected.slice().sort().join(","), [selected]);
  const submitAnswer = useMutation({
    mutationFn: () =>
      apiRequest<any>("/practice/answers", {
        method: "POST",
        body: JSON.stringify({ question_id: question.id, selected_answer: selectedAnswer }),
      }),
    onSuccess: setFeedback,
  });
  const loadAi = useMutation({
    mutationFn: () =>
      apiRequest<{ content: string }>(`/questions/${question.id}/ai-explanation`, { method: "POST" }),
    onSuccess: (result) => setAiContent(result.content),
  });

  if (!question) return <p>暂无题目</p>;

  function toggle(label: string) {
    if (question.question_type === "multiple") {
      setSelected((current) =>
        current.includes(label) ? current.filter((item) => item !== label) : [...current, label],
      );
    } else {
      setSelected([label]);
    }
  }

  function nextQuestion() {
    setFeedback(null);
    setAiContent("");
    setSelected([]);
    setIndex((value) => Math.min(value + 1, questions.length - 1));
  }

  return (
    <section>
      <h1>练习答题</h1>
      <p className="muted">第 {index + 1} / {questions.length} 题</p>
      <article className="question-panel">
        <h2>{question.stem}</h2>
        <div className="option-list">
          {question.options.map((option) => (
            <button
              className={selected.includes(option.label) ? "option selected" : "option"}
              key={option.label}
              onClick={() => toggle(option.label)}
              type="button"
            >
              <strong>{option.label}</strong>
              <span>{option.content}</span>
            </button>
          ))}
        </div>
      </article>
      {!feedback && <button disabled={!selected.length} onClick={() => submitAnswer.mutate()}>提交答案</button>}
      {feedback && (
        <section className="feedback">
          <h2>{feedback.is_correct ? "回答正确" : "回答错误"}</h2>
          <p>正确答案：{feedback.correct_answer}</p>
          <p>{feedback.explanation || "暂无原解析"}</p>
          <button onClick={() => loadAi.mutate()} type="button">AI讲解</button>
          {aiContent && <div className="ai-box">{aiContent}</div>}
          <button onClick={nextQuestion} type="button">下一题</button>
        </section>
      )}
    </section>
  );
}
```

Create `web/src/employee/WrongQuestionsPage.tsx`:

```tsx
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "../api/client";

type WrongQuestion = {
  question_id: number;
  bank_name: string;
  stem: string;
  correct_answer: string;
  explanation: string;
  wrong_count: number;
};

export function WrongQuestionsPage() {
  const queryClient = useQueryClient();
  const { data } = useQuery({
    queryKey: ["wrong-questions"],
    queryFn: () => apiRequest<{ items: WrongQuestion[] }>("/wrong-questions"),
  });
  const master = useMutation({
    mutationFn: (questionId: number) =>
      apiRequest(`/wrong-questions/${questionId}/master`, { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["wrong-questions"] }),
  });

  return (
    <section>
      <h1>错题库</h1>
      <div className="card-list">
        {data?.items.map((item) => (
          <article className="card" key={item.question_id}>
            <p className="muted">{item.bank_name} · 错 {item.wrong_count} 次</p>
            <h2>{item.stem}</h2>
            <p>正确答案：{item.correct_answer}</p>
            <p>{item.explanation || "暂无原解析"}</p>
            <button onClick={() => master.mutate(item.question_id)}>标记掌握</button>
          </article>
        ))}
      </div>
    </section>
  );
}
```

Create `web/src/employee/RankingPage.tsx`:

```tsx
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "../api/client";

type RankingItem = { rank: number; name: string; department: string; points: number };

export function RankingPage() {
  const [bankId, setBankId] = useState<number | null>(null);
  const path = bankId ? `/rankings/banks/${bankId}` : "/rankings/global";
  const { data } = useQuery({
    queryKey: ["ranking", bankId],
    queryFn: () => apiRequest<{ items: RankingItem[] }>(path),
  });

  return (
    <section>
      <h1>排行榜</h1>
      <div className="segmented">
        <button className={!bankId ? "active" : ""} onClick={() => setBankId(null)}>全局榜</button>
        <button className={bankId === 1 ? "active" : ""} onClick={() => setBankId(1)}>当前题库榜</button>
      </div>
      <ol className="ranking-list">
        {data?.items.map((item) => (
          <li key={`${item.rank}-${item.name}`}>
            <strong>{item.rank}</strong>
            <span>{item.name}</span>
            <span>{item.department}</span>
            <b>{item.points}</b>
          </li>
        ))}
      </ol>
    </section>
  );
}
```

Create `web/src/employee/ExamPage.tsx`:

```tsx
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { apiRequest } from "../api/client";

type ExamQuestion = { id: number; stem: string; options: { label: string; content: string }[] };

export function ExamPage() {
  const { bankId } = useParams();
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [result, setResult] = useState<any>(null);
  const start = useMutation({
    mutationFn: () =>
      apiRequest<{ attempt_id: number; questions: ExamQuestion[]; time_limit_minutes: number }>("/exams/attempts", {
        method: "POST",
        body: JSON.stringify({ bank_id: Number(bankId) }),
      }),
  });
  const submit = useMutation({
    mutationFn: () =>
      apiRequest(`/exams/attempts/${start.data?.attempt_id}/submit`, {
        method: "POST",
        body: JSON.stringify({
          answers: Object.entries(answers).map(([question_id, selected_answer]) => ({
            question_id: Number(question_id),
            selected_answer,
          })),
        }),
      }),
    onSuccess: setResult,
  });

  if (!start.data) return <button onClick={() => start.mutate()}>开始模拟考试</button>;
  if (result) return <section><h1>考试完成</h1><p>得分：{result.score}</p><p>答对：{result.correct_count}/{result.total_count}</p></section>;

  return (
    <section>
      <h1>模拟考试</h1>
      <p className="muted">限时 {start.data.time_limit_minutes} 分钟</p>
      {start.data.questions.map((question) => (
        <article className="question-panel" key={question.id}>
          <h2>{question.stem}</h2>
          {question.options.map((option) => (
            <button key={option.label} onClick={() => setAnswers({ ...answers, [question.id]: option.label })}>
              {option.label}. {option.content}
            </button>
          ))}
        </article>
      ))}
      <button onClick={() => submit.mutate()}>交卷</button>
    </section>
  );
}
```

Create `web/src/employee/ProfilePage.tsx`:

```tsx
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "../api/client";

type Profile = {
  name: string;
  department: string;
  total_points: number;
  answer_count: number;
  accuracy: number;
  wrong_count: number;
};

export function ProfilePage() {
  const { data } = useQuery({
    queryKey: ["profile"],
    queryFn: () => apiRequest<Profile>("/me"),
  });

  return (
    <section>
      <h1>个人中心</h1>
      <div className="profile-card">
        <h2>{data?.name}</h2>
        <p>{data?.department}</p>
        <div className="metrics-grid">
          <div className="metric"><span>总积分</span><strong>{data?.total_points ?? 0}</strong></div>
          <div className="metric"><span>累计答题</span><strong>{data?.answer_count ?? 0}</strong></div>
          <div className="metric"><span>正确率</span><strong>{data?.accuracy ?? 0}%</strong></div>
          <div className="metric"><span>错题数</span><strong>{data?.wrong_count ?? 0}</strong></div>
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 5: Run frontend build**

Run:

```powershell
cd web
npm run build
```

Expected: TypeScript and Vite build succeed.

---

### Task 15: Admin Web Console

**Files:**
- Create: `web/src/admin/AdminLayout.tsx`
- Create: `web/src/admin/AdminLoginPage.tsx`
- Create: `web/src/admin/DashboardPage.tsx`
- Create: `web/src/admin/EmployeesPage.tsx`
- Create: `web/src/admin/QuestionBanksPage.tsx`
- Create: `web/src/admin/QuestionsPage.tsx`
- Create: `web/src/admin/PointRulesPage.tsx`
- Create: `web/src/admin/LlmConfigPage.tsx`
- Create: `web/src/admin/ExportsPage.tsx`

- [ ] **Step 1: Implement admin layout**

Create `web/src/admin/AdminLayout.tsx`:

```tsx
import { NavLink, Outlet } from "react-router-dom";

export function AdminLayout() {
  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <h1>砺学后台</h1>
        <NavLink to="/admin">数据看板</NavLink>
        <NavLink to="/admin/employees">员工管理</NavLink>
        <NavLink to="/admin/banks">题库管理</NavLink>
        <NavLink to="/admin/questions">题目维护</NavLink>
        <NavLink to="/admin/points">积分规则</NavLink>
        <NavLink to="/admin/llm">AI讲解</NavLink>
        <NavLink to="/admin/exports">数据导出</NavLink>
      </aside>
      <main className="admin-main">
        <Outlet />
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Implement dashboard**

Create `web/src/admin/DashboardPage.tsx`:

```tsx
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "../api/client";

type Dashboard = {
  participant_count: number;
  active_user_count: number;
  answer_count: number;
  overall_accuracy: number;
};

export function DashboardPage() {
  const { data } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: () => apiRequest<Dashboard>("/admin/dashboard"),
  });

  return (
    <section>
      <h1>数据看板</h1>
      <div className="metrics-grid">
        <div className="metric"><span>参与人数</span><strong>{data?.participant_count ?? 0}</strong></div>
        <div className="metric"><span>活跃人数</span><strong>{data?.active_user_count ?? 0}</strong></div>
        <div className="metric"><span>累计答题</span><strong>{data?.answer_count ?? 0}</strong></div>
        <div className="metric"><span>整体正确率</span><strong>{data?.overall_accuracy ?? 0}%</strong></div>
      </div>
    </section>
  );
}
```

- [ ] **Step 3: Implement admin pages**

Create each page with one clear workflow:

- `EmployeesPage.tsx`: upload employee CSV/Excel, show import result and employee list.
- `QuestionBanksPage.tsx`: create/edit/enable/disable banks, configure exam count and time limit.
- `QuestionsPage.tsx`: select bank, upload `questions.csv`, show import errors, list/edit/disable questions.
- `PointRulesPage.tsx`: edit base points, correct bonus, exam completion points, daily limit.
- `LlmConfigPage.tsx`: edit base URL, model, API key, enabled state; mask saved key.
- `ExportsPage.tsx`: buttons for user summary, answer records, exam scores.

- [ ] **Step 4: Build frontend**

Run:

```powershell
cd web
npm run build
```

Expected: build succeeds.

---

### Task 16: Deployment

**Files:**
- Create: `docker-compose.yml`
- Create: `server/Dockerfile`
- Create: `web/Dockerfile`
- Create: `deploy/nginx.conf`
- Modify: `README.md`

- [ ] **Step 1: Create Docker Compose**

Create `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: lixue
      POSTGRES_USER: lixue
      POSTGRES_PASSWORD: lixue
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  server:
    build: ./server
    env_file: .env
    depends_on:
      - db
    ports:
      - "8000:8000"

  web:
    build: ./web
    depends_on:
      - server
    ports:
      - "8080:80"

volumes:
  postgres_data:
```

- [ ] **Step 2: Create backend Dockerfile**

Create `server/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[dev]"
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 3: Create frontend Dockerfile**

Create `web/Dockerfile`:

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY ../deploy/nginx.conf /etc/nginx/conf.d/default.conf
```

- [ ] **Step 4: Create Nginx config**

Create `deploy/nginx.conf`:

```nginx
server {
  listen 80;
  server_name _;

  root /usr/share/nginx/html;
  index index.html;

  location /api/ {
    proxy_pass http://server:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  location / {
    try_files $uri /index.html;
  }
}
```

- [ ] **Step 5: Document cloud deployment**

In `README.md`, document:

```markdown
## Deployment

1. Buy a lightweight cloud server with 2 vCPU, 4 GB RAM, and Ubuntu LTS.
2. Point a domain name to the server.
3. Install Docker and Docker Compose.
4. Copy `.env.example` to `.env` and replace secrets.
5. Run `docker compose up -d --build`.
6. Configure HTTPS with Nginx or a cloud certificate manager.
7. Open `/admin/login`, create or seed the admin account, import employees, create a question bank, and import `question/questions.csv`.
```

- [ ] **Step 6: Build containers**

Run:

```powershell
docker compose build
```

Expected: server and web images build successfully.

---

### Task 17: End-to-End Acceptance

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Backend verification**

Run:

```powershell
cd server
python -m pytest -q
```

Expected: all backend tests pass.

- [ ] **Step 2: Frontend verification**

Run:

```powershell
cd web
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Manual MVP acceptance flow**

Run the app locally and verify:

```text
1. Admin logs in.
2. Admin imports employee CSV with name, work number, phone, department, initial password.
3. Admin creates "设备知识题库".
4. Admin imports question/questions.csv.
5. Import result shows total rows, imported rows, type counts, and row-level errors.
6. Employee logs in by work number and password.
7. Employee sees "设备知识题库" on the bank selection page.
8. Employee starts practice and answers single-choice, multiple-choice, and judgment questions.
9. Correct answer and original explanation are shown after answer submission.
10. Wrong answer enters wrong question list.
11. Employee opens AI explanation; first call generates content, second call returns cached content.
12. Employee enters simulated exam, submits answers, and sees score.
13. Global ranking and bank ranking show updated points.
14. Admin dashboard shows participation, answer count, accuracy, and exam data.
15. Admin exports user summary, answer records, and exam scores.
```

- [ ] **Step 4: Production readiness checklist**

Before cloud deployment:

```text
1. JWT_SECRET changed from default.
2. ADMIN_PASSWORD changed from default.
3. PostgreSQL password changed from default.
4. HTTPS domain configured.
5. Database backup command documented.
6. LLM API key configured only in environment or encrypted database field.
7. Feishu integration remains disabled in MVP.
```

## Plan Self-Review

Spec coverage:

- Multi-question-bank support: Tasks 2, 5, 14, 15.
- CSV question import: Task 4 and Task 5.
- Employee import and login: Task 6.
- Practice and answer feedback: Task 7 and Task 14.
- Wrong questions: Task 8 and Task 14.
- Configurable points and rankings: Task 9.
- Lightweight exams: Task 10 and Task 14.
- AI explanations with cache: Task 11.
- Admin dashboard and exports: Task 12 and Task 15.
- Cloud deployment: Task 16.

Placeholder scan:

- The plan avoids unresolved product decisions and requires database-backed behavior for MVP endpoints. Any sample response shown inside a code block is paired with explicit persistence and validation requirements in the same task.

Type consistency:

- `QuestionType` values are `single`, `multiple`, and `judgment`.
- `question_banks`, `questions`, `answer_records`, `wrong_questions`, `point_transactions`, `exam_attempts`, and `ai_explanations` names match API task references.
- CSV import field names match the existing `question/questions.csv` header.
