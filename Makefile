SHELL := /bin/bash
VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python

.PHONY: help venv sync sync-project run new-project run-mcp run-ollama-proxy run-ollama-proxy-deepseek clean-venv

help:
	@echo "Global targets:"
	@echo "  make venv                        - create .venv and install all deps"
	@echo "  make sync                        - sync all deps into existing .venv"
	@echo ""
	@echo "Per-project targets:"
	@echo "  make run PROJECT=<path>          - run a project (auto-detects main.py / app.py / run.sh)"
	@echo "  make sync-project PROJECT=<path> - install only that project's requirements.txt"
	@echo "  make new-project PROJECT=<path>  - scaffold a new project folder"
	@echo ""
	@echo "Legacy targets:"
	@echo "  make run-mcp                     - run tools/mcp_youtube"
	@echo "  make run-ollama-proxy            - run tools/ollama_cursor_proxy"
	@echo "  make run-ollama-proxy-deepseek   - same, with OLLAMA_MODEL=deepseek-r1:latest"
	@echo "  make clean-venv                  - remove .venv"

# ── Environment ──────────────────────────────────────────────────────────────

venv:
	@command -v uv >/dev/null || (echo "uv is required. Install: https://docs.astral.sh/uv/" && exit 1)
	uv venv $(VENV_DIR)
	uv pip install --python $(PYTHON) -r requirements.txt

sync:
	@test -x "$(PYTHON)" || (echo "Virtualenv not found. Run: make venv" && exit 1)
	uv pip install --python $(PYTHON) -r requirements.txt

sync-project:
	@test -n "$(PROJECT)" || (echo "Usage: make sync-project PROJECT=<path>" && exit 1)
	@test -x "$(PYTHON)" || (echo "Virtualenv not found. Run: make venv" && exit 1)
	@test -f "$(PROJECT)/requirements.txt" || (echo "No requirements.txt found in $(PROJECT)/" && exit 1)
	uv pip install --python $(PYTHON) -r $(PROJECT)/requirements.txt

# ── Run ──────────────────────────────────────────────────────────────────────

run:
	@test -n "$(PROJECT)" || (echo "Usage: make run PROJECT=<path>" && exit 1)
	@test -x "$(PYTHON)" || (echo "Virtualenv not found. Run: make venv" && exit 1)
	@if [ -f "$(PROJECT)/main.py" ]; then \
		$(PYTHON) $(PROJECT)/main.py; \
	elif [ -f "$(PROJECT)/app.py" ]; then \
		$(PYTHON) $(PROJECT)/app.py; \
	elif [ -f "$(PROJECT)/server.py" ]; then \
		$(PYTHON) $(PROJECT)/server.py; \
	elif [ -f "$(PROJECT)/run.sh" ]; then \
		bash $(PROJECT)/run.sh; \
	else \
		echo "No entry point found in $(PROJECT)/"; \
		echo "Expected: main.py, app.py, server.py, or run.sh"; \
		exit 1; \
	fi

# ── Scaffold ─────────────────────────────────────────────────────────────────

new-project:
	@test -n "$(PROJECT)" || (echo "Usage: make new-project PROJECT=<path>" && exit 1)
	@test ! -d "$(PROJECT)" || (echo "$(PROJECT)/ already exists" && exit 1)
	mkdir -p $(PROJECT)
	@echo "# $(notdir $(PROJECT)) dependencies" > $(PROJECT)/requirements.txt
	@echo "# Entry point for $(notdir $(PROJECT))" > $(PROJECT)/main.py
	@echo "def main():" >> $(PROJECT)/main.py
	@echo "    pass" >> $(PROJECT)/main.py
	@echo "" >> $(PROJECT)/main.py
	@echo 'if __name__ == "__main__":' >> $(PROJECT)/main.py
	@echo "    main()" >> $(PROJECT)/main.py
	@echo ""
	@echo "Created $(PROJECT)/ with main.py and requirements.txt"
	@echo "Next steps:"
	@echo "  1. Add deps to $(PROJECT)/requirements.txt"
	@echo "  2. Add '-r $(PROJECT)/requirements.txt' to the root requirements.txt"
	@echo "  3. Run: make sync-project PROJECT=$(PROJECT)"

# ── Legacy named targets ──────────────────────────────────────────────────────

run-mcp:
	@$(MAKE) run PROJECT=tools/mcp_youtube

run-ollama-proxy:
	@$(MAKE) run PROJECT=tools/ollama_cursor_proxy

run-ollama-proxy-deepseek:
	OLLAMA_MODEL=deepseek-r1:latest $(MAKE) run PROJECT=tools/ollama_cursor_proxy

# ── Cleanup ───────────────────────────────────────────────────────────────────

clean-venv:
	rm -rf $(VENV_DIR)
