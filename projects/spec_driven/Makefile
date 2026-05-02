.PHONY: install install-backend install-frontend run run-backend run-frontend test test-backend test-frontend clean

PORT ?= 8765
FRONTEND_DIST := backend/static

ifeq ($(OS),Windows_NT)
    VENV_BIN := .venv/Scripts
else
    VENV_BIN := .venv/bin
endif

PYTHON := $(VENV_BIN)/python

install: install-backend install-frontend

install-backend:
	python -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r backend/requirements.txt

install-frontend:
	cd frontend && npm install

run:
	cd frontend && npm run build
	rm -rf $(FRONTEND_DIST)
	mkdir -p $(FRONTEND_DIST)
	cp -r frontend/dist/* $(FRONTEND_DIST)/
	SPEC_DRIVEN_PORT=$(PORT) $(PYTHON) backend/main.py

run-backend:
	SPEC_DRIVEN_PORT=$(PORT) $(PYTHON) backend/main.py

run-frontend:
	cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	cd backend && ../$(VENV_BIN)/python -m pytest -q

test-frontend:
	cd frontend && npm test --silent || true

clean:
	rm -rf $(FRONTEND_DIST) frontend/dist frontend/node_modules backend/__pycache__ backend/libs/__pycache__ backend/tests/__pycache__ backend/tests/unit/__pycache__ backend/.pytest_cache .venv
