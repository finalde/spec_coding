.PHONY: setup setup-hunyuan run validate help

PYTHON ?= python3
VENV   ?= .venv
PIP    := $(VENV)/bin/pip
PY     := $(VENV)/bin/python

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

setup: $(VENV)/bin/activate ## Create venv and install base dependencies
$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "\n=== Base deps installed. Now run: make setup-hunyuan ==="

setup-hunyuan: ## Install Hunyuan3D-2 + custom_rasterizer (needs nvcc; match PyTorch CUDA)
	$(PIP) install git+https://github.com/Tencent/Hunyuan3D-2.git
	$(PIP) install --no-build-isolation \
		"git+https://github.com/Tencent/Hunyuan3D-2.git#subdirectory=hy3dgen/texgen/custom_rasterizer"
	@echo "\n=== Hunyuan3D-2 + custom_rasterizer installed. Ready to generate! ==="

validate: ## Validate input images (FRONT=... SIDE=... BACK=...)
	$(PY) main.py --front $(FRONT) --side $(SIDE) --back $(BACK) --output /dev/null --skip-generation 2>/dev/null || \
	$(PY) -c "\
from pathlib import Path; \
from libs.validator import ImageValidator; \
v = ImageValidator(); \
r = v.validate(Path('$(FRONT)'), Path('$(SIDE)'), Path('$(BACK)')); \
print(r.summary())"

run: ## Generate 3D model (FRONT=... SIDE=... BACK=... OUTPUT=... PROMPT=...)
	$(PY) main.py \
		--front "$(FRONT)" \
		--side "$(SIDE)" \
		--back "$(BACK)" \
		--output "$(OUTPUT)" \
		--prompt "$(PROMPT)"

run-skip-val: ## Generate without validation (FRONT=... SIDE=... BACK=... OUTPUT=... PROMPT=...)
	$(PY) main.py \
		--front "$(FRONT)" \
		--side "$(SIDE)" \
		--back "$(BACK)" \
		--output "$(OUTPUT)" \
		--prompt "$(PROMPT)" \
		--skip-validation
