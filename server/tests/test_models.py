from sqlalchemy import create_engine

from app import models
from app.database import Base


def test_models_create_all_tables_in_sqlite_memory():
    engine = create_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(engine)

    table_names = set(Base.metadata.tables)
    assert "users" in table_names
    assert "admins" in table_names
    assert "question_banks" in table_names
    assert "questions" in table_names
    assert "answer_records" in table_names
    assert "wrong_questions" in table_names
    assert "point_transactions" in table_names
    assert "exam_attempts" in table_names
    assert "ai_explanations" in table_names
    assert models.QuestionType.single.value == "single"
