#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE="docker-compose"
else
  COMPOSE="docker compose"
fi

echo "Starting PostgreSQL..."
$COMPOSE up -d postgres
sleep 5

echo "Running ETL pipeline..."
PYTHONPATH="$ROOT" "${ROOT}/.venv/bin/python3" -m src.etl_pipeline

echo "Done. Connect Power BI to PostgreSQL on localhost:5432, view: vw_listings_analytics"
