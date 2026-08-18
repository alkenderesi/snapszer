SHELL=/bin/bash

setup:
	uv sync --all-groups
	uv run pre-commit install

clean:
	rm -rf .venv

lint:
	SKIP=pytest uv run pre-commit run --all-files

test:
	uv run pre-commit run pytest --all-files
