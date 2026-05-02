.PHONY: help install run-backend run-frontend run-prod test clean

# Resolve the repo's pre-configured venv. This Makefile lives at projects/spec_driven/,
# so the repo root is two levels up.
REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))../..)
PY := $(REPO_ROOT)/.venv/Scripts/python
PIP := $(REPO_ROOT)/.venv/Scripts/pip
BACKEND_PORT ?= 8765
FRONTEND_PORT ?= 5173

help:
	@echo "spec_driven targets:"
	@echo "  make install        -- pip install backend deps + npm install frontend deps"
	@echo "  make run-backend    -- start FastAPI on http://127.0.0.1:$(BACKEND_PORT) with --reload"
	@echo "  make run-frontend   -- start Vite dev server on http://127.0.0.1:$(FRONTEND_PORT) (proxies /api -> 8765)"
	@echo "  make run-prod       -- build frontend bundle into backend/static/ and start a single FastAPI process"
	@echo "  make test           -- run backend pytest"
	@echo "  make clean          -- remove backend/static/ and frontend/dist/"
	@echo ""
	@echo "Use run-backend and run-frontend in two terminals during development."

install:
	$(PIP) install -r backend/requirements.txt
	$(PIP) install pytest httpx
	cd frontend && npm install

run-backend:
	cd backend && $(PY) -m uvicorn --factory libs.api:create_app --host 127.0.0.1 --port $(BACKEND_PORT) --reload

run-frontend:
	cd frontend && npm run dev -- --host 127.0.0.1 --port $(FRONTEND_PORT)

run-prod:
	cd frontend && npm run build
	mkdir -p backend/static
	cp -r frontend/dist/. backend/static/
	cd backend && SPEC_DRIVEN_PORT=$(BACKEND_PORT) $(PY) main.py

test:
	cd backend && $(PY) -m pytest

clean:
	rm -rf backend/static frontend/dist
