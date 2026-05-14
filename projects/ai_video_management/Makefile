# Makefile for ai_video_management (post follow-up 039: apps/+libs/ layout).
# Bind 127.0.0.1 only. pip-only (no `uv`).

PY  := python
PIP := pip
NPM := npm

.PHONY: install install-backend install-frontend run run-prod run-backend run-frontend build-frontend test test-backend test-frontend e2e boot-smoke clean

install: install-backend install-frontend

install-backend:
	$(PIP) install -r requirements.txt

install-frontend:
	cd apps/ui && $(NPM) install

run: run-backend

run-prod: build-frontend run-backend

run-backend:
	$(PY) -m apps.api.main

run-frontend:
	cd apps/ui && $(NPM) run dev

build-frontend:
	cd apps/ui && $(NPM) run build

test: test-backend test-frontend

test-backend:
	$(PY) -m pytest tests/ -v

test-frontend:
	cd apps/ui && $(NPM) test

e2e:
	cd apps/ui && $(NPM) run test:e2e

boot-smoke:
	$(PY) -m pytest tests/test_boot_smoke.py -v

clean:
	rm -rf apps/ui/node_modules apps/ui/dist apps/ui/.vite apps/api/static/assets apps/api/static/index.html
	find apps libs tests -type d -name __pycache__ -exec rm -rf {} + || true
	find . -type d -name .pytest_cache -exec rm -rf {} + || true
