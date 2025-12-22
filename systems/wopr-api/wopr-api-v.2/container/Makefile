# WOPR API - Makefile
# Copyright (c) 2025 Bob Bomar <bob@bomar.us>
# SPDX-License-Identifier: MIT

.PHONY: help install dev migrate migrate-create upgrade downgrade docker-up docker-down test lint format clean

help:
	@echo "WOPR API - Available Commands"
	@echo ""
	@echo "  make install        Install dependencies"
	@echo "  make dev            Run development server"
	@echo "  make migrate        Create new migration"
	@echo "  make upgrade        Apply migrations"
	@echo "  make downgrade      Rollback last migration"
	@echo "  make docker-up      Start docker-compose"
	@echo "  make docker-down    Stop docker-compose"
	@echo "  make test           Run tests"
	@echo "  make lint           Run linters"
	@echo "  make format         Format code"
	@echo "  make clean          Clean cache files"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	@read -p "Migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

test:
	pytest

lint:
	ruff app/
	mypy app/

format:
	black app/
	ruff --fix app/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache
