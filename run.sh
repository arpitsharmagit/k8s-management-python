#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run.sh — Enterprise IoT & K8s Platform Launcher
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-stack}"   # stack | fastapi | flask | worker | desktop

print_header() {
  echo ""
  echo "╔══════════════════════════════════════════════════════════╗"
  echo "║   🚀  Enterprise IoT & K8s Platform Suite               ║"
  echo "╚══════════════════════════════════════════════════════════╝"
  echo ""
}

run_stack() {
  echo "► Starting full Docker Compose stack..."
  cp -n "$ROOT_DIR/.env.example" "$ROOT_DIR/.env" 2>/dev/null || true
  docker compose -f "$ROOT_DIR/docker-compose.yml" up --build "$@"
}

run_fastapi_dev() {
  echo "► Starting FastAPI Gateway (dev)..."
  cd "$ROOT_DIR/services/fastapi-gateway"
  [ ! -d venv ] && python3 -m venv venv
  source venv/bin/activate
  pip install -q -r requirements.txt
  cp -n .env.example .env 2>/dev/null || true
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

run_flask_dev() {
  echo "► Starting Flask Admin UI (dev)..."
  cd "$ROOT_DIR/services/flask-admin"
  [ ! -d venv ] && python3 -m venv venv
  source venv/bin/activate
  pip install -q -r requirements.txt
  cp -n .env.example .env 2>/dev/null || true
  FLASK_APP=app FLASK_ENV=development flask run --host 0.0.0.0 --port 5000
}

run_worker_dev() {
  echo "► Starting Celery Worker + Redis Subscriber (dev)..."
  cd "$ROOT_DIR/services/celery-worker"
  [ ! -d venv ] && python3 -m venv venv
  source venv/bin/activate
  pip install -q -r requirements.txt
  cp -n .env.example .env 2>/dev/null || true
  celery -A app.celery_app worker --loglevel=info &
  python -m app.subscribers.redis_subscriber
}

run_desktop() {
  echo "► Launching PySide6 K8s Desktop App..."
  cd "$ROOT_DIR/services/desktop-app"
  [ ! -d venv ] && python3 -m venv venv
  source venv/bin/activate
  pip install -q -r requirements.txt
  python -m app.main
}

print_header

case "$MODE" in
  stack)   run_stack "${@:2}" ;;
  fastapi) run_fastapi_dev ;;
  flask)   run_flask_dev ;;
  worker)  run_worker_dev ;;
  desktop) run_desktop ;;
  *)
    echo "Usage: $0 [stack|fastapi|flask|worker|desktop]"
    echo "  stack    — Build & run all services via docker-compose (default)"
    echo "  fastapi  — Run FastAPI gateway locally (dev mode)"
    echo "  flask    — Run Flask admin UI locally (dev mode)"
    echo "  worker   — Run Celery worker + Redis subscriber locally"
    echo "  desktop  — Launch PySide6 K8s desktop app"
    exit 1
    ;;
esac