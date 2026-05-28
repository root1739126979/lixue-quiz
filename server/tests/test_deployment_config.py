from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[2]


def test_server_dependencies_include_postgresql_driver():
    pyproject = tomllib.loads((ROOT / "server" / "pyproject.toml").read_text(encoding="utf-8"))

    dependencies = pyproject["project"]["dependencies"]

    assert any(dependency.startswith("psycopg[binary]") for dependency in dependencies)


def test_env_example_uses_compose_postgresql_database():
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")

    assert "POSTGRES_PASSWORD=" in env_example
    assert "DATABASE_URL=postgresql+psycopg://" in env_example
    assert "@db:5432/" in env_example
