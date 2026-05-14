# Makefile for spec_driven (FR-39 + follow-up 014 layout).
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
	$(PY) -m $(PIP) install -r requirements.txt

install-frontend:
	cd apps/ui && $(NPM) install

run: run-backend

run-backend:
	$(PY) -m apps.api.main

run-frontend:
	cd apps/ui && $(NPM) run dev

build-frontend:
	cd apps/ui && $(NPM) run build

run-prod: build-frontend
	$(PY) -m apps.api.main

test-backend:
	$(PY) -m pytest tests/ -v

test-frontend:
	cd apps/ui && $(NPM) test

e2e:
	cd apps/ui && $(NPM) run test:e2e

boot-smoke:
	$(PY) -m pytest tests/unit/test_boot_smoke.py -v

clean:
	rm -rf apps/ui/node_modules apps/ui/dist apps/ui/.vite
	rm -rf apps/api/static/assets apps/api/static/index.html
	find apps libs tests -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
