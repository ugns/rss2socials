.PHONY: help install dev test lint coverage build publish clean freeze

help:
	@echo "Available targets:"
	@echo "  install     Install in editable mode"
	@echo "  dev         Install dev dependencies with pinned requirements"
	@echo "  test        Run tox test suite"
	@echo "  lint        Run tox lint checks"
	@echo "  coverage    Run tox coverage environment"
	@echo "  build       Build package distributions"
	@echo "  publish     Upload to PyPI via Twine"
	@echo "  clean       Remove build/test artifacts"
	@echo "  freeze      Update requirements.txt with current versions"

install:
	pip install -e .

dev:
	pip install pip-tools
	pip-compile --extra dev --strip-extras --output-file=requirements.txt pyproject.toml
	pip install -r requirements.txt

test:
	tox

lint:
	tox -e lint

coverage:
	tox -e coverage

build:
	python -m build

publish:
	twine upload dist/*

clean:
	rm -rf dist build **/*.egg-info .pytest_cache .coverage htmlcov

freeze:
	pip-compile --extra dev --strip-extras --output-file=requirements.txt pyproject.toml