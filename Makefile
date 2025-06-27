.PHONY: help install dev test lint coverage build publish clean freeze

help:
	@echo "Available targets:"
	@echo "  install     Install in editable mode"
	@echo "  dev         Install dev dependencies with constraints"
	@echo "  test        Run pytest"
	@echo "  lint        Run flake8 lint checks"
	@echo "  coverage    Run tests with coverage"
	@echo "  build       Build package distributions"
	@echo "  publish     Upload to PyPI via Twine"
	@echo "  clean       Remove build/test artifacts"
	@echo "  freeze      Update constraints.txt with current versions"

install:
	pip install -e .

dev:
	pip install -r requirements-dev.txt -c constraints.txt

test:
	pytest

lint:
	flake8 src tests

coverage:
	coverage run -m pytest && coverage report -m && coverage html

build:
	python -m build

publish:
	twine upload dist/*

clean:
	rm -rf dist build **/*.egg-info .pytest_cache .coverage htmlcov

freeze:
	pip freeze | grep -Ff requirements-dev.txt > constraints.txt