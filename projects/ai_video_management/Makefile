.PHONY: install install-backend install-frontend run run-prod run-backend run-frontend build-frontend test test-backend test-frontend e2e boot-smoke clean

install: install-backend install-frontend

install-backend:
	pip install -r backend/requirements.txt

install-frontend:
	cd frontend && npm install

run: run-backend

run-prod: build-frontend run-backend

run-backend:
	cd backend && PYTHONPATH=. python main.py

run-frontend:
	cd frontend && npm run dev

build-frontend:
	cd frontend && npm run build

test: test-backend test-frontend

test-backend:
	cd backend && PYTHONPATH=. python -m pytest tests/ -v

test-frontend:
	cd frontend && npm test

e2e:
	cd frontend && npm run test:e2e

boot-smoke:
	cd backend && PYTHONPATH=. python -m pytest tests/test_boot_smoke.py -v

clean:
	rm -rf frontend/node_modules frontend/dist frontend/.vite backend/static/assets backend/static/index.html
	find backend -type d -name __pycache__ -exec rm -rf {} + || true
	find backend -type d -name .pytest_cache -exec rm -rf {} + || true
