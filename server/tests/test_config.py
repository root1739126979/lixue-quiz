from app.config import Settings


def test_settings_read_database_url_from_environment(monkeypatch):
    database_url = "postgresql+psycopg://lixue:secret@db:5432/lixue"
    monkeypatch.setenv("DATABASE_URL", database_url)

    settings = Settings()

    assert settings.database_url == database_url
