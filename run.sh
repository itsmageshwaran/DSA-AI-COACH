#!/bin/bash
set -e

echo "Running Alembic migrations..."
poetry run alembic upgrade head

echo "Seeding curriculum data..."
poetry run python scripts/seed_dsa_data.py || true
poetry run python scripts/create_demo_user.py || true

PORT_NUM="${PORT:-7860}"
echo "Starting FastAPI server on port $PORT_NUM..."
exec poetry run uvicorn src.main:app --host 0.0.0.0 --port "$PORT_NUM"
