#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="${PROJECT_DIR:-/www/wwwroot/lixue-quiz}"
SERVER_HEALTH_URL="${SERVER_HEALTH_URL:-http://127.0.0.1:8000/api/health}"
WEB_HEALTH_URL="${WEB_HEALTH_URL:-http://127.0.0.1:8080}"
HEALTH_CHECK_RETRIES="${HEALTH_CHECK_RETRIES:-30}"
HEALTH_CHECK_INTERVAL="${HEALTH_CHECK_INTERVAL:-2}"

log() {
  printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

fail() {
  printf '\nERROR: %s\n' "$*" >&2
  exit 1
}

run() {
  log "$*"
  "$@"
}

wait_for_http() {
  local url="$1"
  local mode="${2:-get}"
  local attempt

  for attempt in $(seq 1 "$HEALTH_CHECK_RETRIES"); do
    if [ "$mode" = "--head" ]; then
      if curl --fail --silent --show-error --head "$url" >/dev/null; then
        return 0
      fi
    else
      if curl --fail --silent --show-error "$url" >/dev/null; then
        return 0
      fi
    fi

    log "Waiting for ${url} (${attempt}/${HEALTH_CHECK_RETRIES})."
    sleep "$HEALTH_CHECK_INTERVAL"
  done

  return 1
}

rollback() {
  local previous_revision="$1"

  log "Deployment failed. Rolling back to ${previous_revision}."
  git reset --hard "$previous_revision"
  docker compose up -d --build
  wait_for_http "$SERVER_HEALTH_URL"
  wait_for_http "$WEB_HEALTH_URL" --head
  log "Rollback completed."
}

cd "$PROJECT_DIR" || fail "Project directory not found: $PROJECT_DIR"

if [ ! -d .git ]; then
  fail "This directory is not a Git repository. Clone the GitHub repository into $PROJECT_DIR first."
fi

if [ ! -f .env ]; then
  fail ".env is missing. Create it from .env.example before updating."
fi

command -v git >/dev/null 2>&1 || fail "git is not installed."
command -v docker >/dev/null 2>&1 || fail "docker is not installed."
docker compose version >/dev/null 2>&1 || fail "docker compose is not available."

if ! git diff --quiet || ! git diff --cached --quiet; then
  fail "Local tracked files have uncommitted changes. Commit or discard them before updating."
fi

previous_revision=$(git rev-parse HEAD)
log "Current revision: ${previous_revision}"

if ! run git fetch origin; then
  fail "git fetch origin failed."
fi

if ! run git pull --ff-only; then
  fail "git pull --ff-only failed. The server branch has diverged from GitHub."
fi

if ! run docker compose up -d --build; then
  rollback "$previous_revision"
  fail "Docker rebuild failed. Rolled back to the previous revision."
fi

log "Checking backend health."
if ! wait_for_http "$SERVER_HEALTH_URL"; then
  rollback "$previous_revision"
  fail "Backend health check failed. Rolled back to the previous revision."
fi

log "Checking frontend health."
if ! wait_for_http "$WEB_HEALTH_URL" --head; then
  rollback "$previous_revision"
  fail "Frontend health check failed. Rolled back to the previous revision."
fi

log "Update completed successfully."
docker compose ps
