.PHONY: help setup env up up-all down logs verify etl etl-dry test generate mock-etl clean run

PYTHON ?= .venv/bin/python3
PIP ?= .venv/bin/pip
PROJECT_ROOT := $(shell pwd)
DOCKER_COMPOSE ?= $(shell command -v docker-compose >/dev/null 2>&1 && echo docker-compose || echo docker compose)

help:
	@echo "Tehran Real Estate Pipeline"
	@echo ""
	@echo "  make setup      Create venv and install dependencies"
	@echo "  make env        Copy .env.example to .env"
	@echo "  make up         Start PostgreSQL"
	@echo "  make up-all     Start PostgreSQL + Airflow + PgAdmin"
	@echo "  make down       Stop all containers"
	@echo "  make etl        Run full ETL pipeline"
	@echo "  make etl-dry    Run extract/transform only"
	@echo "  make generate   Generate 50 mock records in data/incoming/"
	@echo "  make mock-etl   Generate mock data then run ETL"
	@echo "  make test       Run pytest"
	@echo "  make verify     Verify ETL + optional DB check"
	@echo "  make clean      Remove processed files and python cache"

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

env:
	cp -n .env.example .env || true

up: env
	$(DOCKER_COMPOSE) up -d postgres
	@echo "Waiting for PostgreSQL..."
	@sleep 5

up-all: env
	$(DOCKER_COMPOSE) --profile tools --profile airflow up -d
	@echo "Services:"
	@echo "  PostgreSQL : localhost:5432"
	@echo "  PgAdmin    : http://localhost:5050"
	@echo "  Airflow    : http://localhost:8080 (admin/admin)"

down:
	$(DOCKER_COMPOSE) --profile tools --profile airflow down

logs:
	$(DOCKER_COMPOSE) logs -f postgres

verify:
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON) scripts/verify_pipeline.py

etl:
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON) -m src.etl_pipeline

etl-dry:
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON) -m src.etl_pipeline --skip-load

generate:
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON) -m src.data_generator --count 50

mock-etl: generate etl

test:
	PYTHONPATH=$(PROJECT_ROOT) pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -f data/processed/*.csv

run: up etl
	@echo "Pipeline complete."
