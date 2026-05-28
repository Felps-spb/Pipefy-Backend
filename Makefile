APP_MODULE := app.main:app
POSTGRES_SERVICE := postgres

.PHONY: help setup venv sync db-up db-down run test clean

help:
	@echo "Available commands:"
	@echo "  make setup    Create virtualenv and install dependencies"
	@echo "  make venv     Create uv virtualenv"
	@echo "  make sync     Install dependencies with uv"
	@echo "  make db-up    Start PostgreSQL with Docker Compose"
	@echo "  make db-down  Stop Docker Compose services"
	@echo "  make run      Run FastAPI locally"
	@echo "  make test     Run automated tests"
	@echo "  make clean    Remove Python cache files"

setup: venv sync

venv:
	uv venv

sync:
	uv sync

db-up:
	docker compose up -d $(POSTGRES_SERVICE)

db-down:
	docker compose down

run:
	uv run uvicorn $(APP_MODULE) --reload --reload-dir app --reload-exclude ".pytest_cache/*" --reload-exclude ".venv/*"

test:
	uv run pytest

clean:
	python -c "import pathlib, shutil; [shutil.rmtree(path) for path in pathlib.Path('.').rglob('__pycache__')]; [path.unlink() for path in pathlib.Path('.').rglob('*.pyc')]; shutil.rmtree('.pytest_cache', ignore_errors=True)"
