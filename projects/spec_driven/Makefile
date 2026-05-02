.PHONY: install run dev test test-backend test-frontend clean

PORT ?= 8765
FRONTEND_DIST := backend/static
PYTHON := uv run python

install:
	uv sync
	cd frontend && npm install

run:
	cd frontend && npm run build
	rm -rf $(FRONTEND_DIST)
	mkdir -p $(FRONTEND_DIST)
	cp -r frontend/dist/* $(FRONTEND_DIST)/
	SPEC_DRIVEN_PORT=$(PORT) $(PYTHON) backend/main.py

dev:
	@echo "Start in two terminals:"
	@echo "  terminal 1:  cd projects/spec_driven && SPEC_DRIVEN_PORT=$(PORT) uv run python backend/main.py --reload"
	@echo "  terminal 2:  cd projects/spec_driven/frontend && npm run dev"

test: test-backend test-frontend

test-backend:
	cd backend && uv run pytest -q

test-frontend:
	cd frontend && npm test --silent || true

clean:
	rm -rf $(FRONTEND_DIST) frontend/dist frontend/node_modules backend/__pycache__ backend/libs/__pycache__ backend/tests/__pycache__ backend/tests/unit/__pycache__ backend/.pytest_cache
