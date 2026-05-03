# Makefile for spec_driven (FR-39).
# Every target binds 127.0.0.1 — NEVER 0.0.0.0 (SEC-13 audit / NFR-7).
# pip-only — no `uv` invocation (validation/development.md move 6).

PY   := python
PIP  := pip
NPM  := npm

.PHONY: install install-backend install-frontend \
        run run-backend run-frontend run-prod \
        build-frontend test-backend test-frontend e2e \
        boot-smoke clean

install: install-backend install-frontend

install-backend:
	cd backend && $(PY) -m $(PIP) install -r requirements.txt

install-frontend:
	cd frontend && $(NPM) install

run: run-backend

run-backend:
	cd backend && $(PY) main.py

run-frontend:
	cd frontend && $(NPM) run dev

build-frontend:
	cd frontend && $(NPM) run build

run-prod: build-frontend
	cd backend && $(PY) main.py

test-backend:
	cd backend && $(PY) -m pytest tests/ -v

test-frontend:
	cd frontend && $(NPM) test

e2e:
	cd frontend && $(NPM) run test:e2e

boot-smoke:
	cd backend && $(PY) -m pytest tests/unit/test_boot_smoke.py -v

clean:
	rm -rf frontend/node_modules frontend/dist frontend/.vite
	rm -rf backend/static/assets backend/static/index.html
	find backend -type d -name __pycache__ -exec rm -rf {} +
	find backend -type d -name .pytest_cache -exec rm -rf {} +
