from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "deploy" / "update.sh"


def test_update_script_keeps_server_environment_file():
    content = SCRIPT.read_text(encoding="utf-8")

    assert "if [ ! -f .env ]" in content
    assert "cp .env" not in content
    assert "git checkout -- .env" not in content


def test_update_script_uses_fast_forward_git_update():
    content = SCRIPT.read_text(encoding="utf-8")

    assert "git fetch origin" in content
    assert "git pull --ff-only" in content


def test_update_script_rebuilds_and_checks_services():
    content = SCRIPT.read_text(encoding="utf-8")

    assert "docker compose up -d --build" in content
    assert "http://127.0.0.1:8000/api/health" in content
    assert "http://127.0.0.1:8080" in content


def test_update_script_waits_for_services_before_rollback():
    content = SCRIPT.read_text(encoding="utf-8")

    assert "HEALTH_CHECK_RETRIES" in content
    assert "wait_for_http" in content
    assert "sleep \"$HEALTH_CHECK_INTERVAL\"" in content
    assert "wait_for_http \"$SERVER_HEALTH_URL\"" in content
    assert "wait_for_http \"$WEB_HEALTH_URL\" --head" in content


def test_update_script_rolls_back_to_previous_revision():
    content = SCRIPT.read_text(encoding="utf-8")

    assert "previous_revision=$(git rev-parse HEAD)" in content
    assert "rollback" in content
    assert 'git reset --hard "$previous_revision"' in content
