.PHONY: install run test lint format docker-up docker-down ingest load-test migrate

install:
	python -m pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

docker-up:
	docker compose up --build

docker-down:
	docker compose down

ingest:
	python scripts/ingest_documents.py

load-test:
	python scripts/benchmark.py

migrate:
	alembic upgrade head

