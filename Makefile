PYTHON = .venv/bin/python3
PIP    = .venv/bin/pip3
MAIN   = a_maze_ing.py
CONFIG = config.txt

all: run

venv:
	rm -rf .venv
	python3 -m venv .venv

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

build:
	rm -rf dist build *.egg-info
	rm -f mazegen-1.0.0-py3-none-any.whl mazegen-1.0.0.tar.gz
	$(PYTHON) -m build
	mv dist/mazegen-1.0.0-py3-none-any.whl ./
	mv dist/mazegen-1.0.0.tar.gz ./
	rm -rf dist/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf dist build *.egg-info
	rm -f mazegen-1.0.0-py3-none-any.whl mazegen-1.0.0.tar.gz
	rm -rf .venv

.PHONY: all venv install run debug lint lint-strict build clean
