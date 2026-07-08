PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin

.PHONY: help venv test lint run compose-up compose-down docker-build k3d-up k3d-down

help:
	@echo "Targets:"
	@echo "  make venv          create local virtualenv and install dev deps"
	@echo "  make test          run pytest"
	@echo "  make lint          run ruff"
	@echo "  make run           run FastAPI locally without Docker"
	@echo "  make compose-up    start Docker stack"
	@echo "  make k3d-up        create k3d cluster and apply manifests"

venv:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -e ".[dev]"

test:
	$(BIN)/pytest

lint:
	$(BIN)/ruff check .

run:
	INIT_DB_ON_STARTUP=false LLM_BASE_URL=mock $(BIN)/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

compose-up:
	cp -n .env.example .env || true
	docker compose up --build

compose-down:
	docker compose down

docker-build:
	docker build -t private-ai-lab:local .

k3d-up:
	./infra/k3d/create-cluster.sh
	kubectl apply -k deploy/k8s/base

k3d-down:
	k3d cluster delete private-ai-lab
