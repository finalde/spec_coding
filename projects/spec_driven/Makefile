# Makefile for spec_driven (FR-39).
#
# Targets do NOT use `uv run` without a pip fallback (per agent_refs/validation/development.md move #6).
# All runtime targets bind to 127.0.0.1:8765 only (FR-38, AC-29). LAN binds are forbidden.

PY ?= python
PIP ?= pip
NPM ?= npm
HOST := 127.0.0.1
PORT := 8765

.PHONY: help install install-backend install-frontend run run-backend run-frontend run-prod build-frontend test-backend test-frontend e2e boot-smoke clean

help:
	@echo "Targets: install run run-backend run-frontend run-prod build-frontend test-backend test-frontend e2e boot-smoke clean"

install: install-backend install-frontend

install-backend:
	$(PY) -m $(PIP) install -r backend/requirements.txt

install-frontend:
	cd frontend && $(NPM) install

run: run-backend

run-backend:
	cd backend && $(PY) main.py

run-frontend:
	cd frontend && $(NPM) run dev

run-prod: build-frontend
	cd backend && $(PY) main.py

build-frontend:
	cd frontend && $(NPM) run build

test-backend:
	cd backend && $(PY) -m pytest tests/ -v

test-frontend:
	cd frontend && $(NPM) test

e2e:
	cd frontend && $(NPM) run test:e2e

boot-smoke:
	cd backend && $(PY) -m pytest tests/system/test_sys1_boot_smoke.py -v

clean:
	rm -rf backend/__pycache__ backend/libs/__pycache__ backend/tests/__pycache__
	rm -rf frontend/dist frontend/node_modules frontend/.vite
