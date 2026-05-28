from collections.abc import Generator
import os
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[2]
SERVER_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_ROOT))
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")


def pytest_configure(config):
    temp_root = ROOT / ".pytest_tmp"
    temp_root.mkdir(exist_ok=True)
    config.option.basetemp = str(temp_root)


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    from app.database import Base, get_db
    from app.main import create_app

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def admin_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "admin123456"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['token']}"}
