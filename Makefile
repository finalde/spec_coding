SHELL := /bin/bash
VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python

.PHONY: help venv sync run-mcp run-ollama-proxy clean-venv

help:
	@echo "Targets:"
	@echo "  make venv            - create .venv with uv and sync repo requirements"
	@echo "  make sync            - sync repo requirements into existing .venv"
	@echo "  make run-mcp         - run local YouTube MCP server with .venv python"
	@echo "  make run-ollama-proxy - run Ollama–Cursor proxy (use with ngrok for Cursor)"
	@echo "  make clean-venv      - remove .venv"

venv:
	@command -v uv >/dev/null || (echo "uv is required. Install: https://docs.astral.sh/uv/" && exit 1)
	uv venv $(VENV_DIR)
	uv pip install --python $(PYTHON) -r requirements.txt

sync:
	@test -x "$(PYTHON)" || (echo "Virtualenv not found. Run: make venv" && exit 1)
	uv pip install --python $(PYTHON) -r requirements.txt

run-mcp:
	@test -x "$(PYTHON)" || (echo "Virtualenv not found. Run: make venv" && exit 1)
	$(PYTHON) tools/mcp_youtube/server.py

run-ollama-proxy:
	@test -x "$(PYTHON)" || (echo "Virtualenv not found. Run: make venv" && exit 1)
	$(PYTHON) tools/ollama_cursor_proxy/app.py

clean-venv:
	rm -rf $(VENV_DIR)

