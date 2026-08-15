SHELL=/bin/bash

setup:
	uv sync --all-groups
	uv run pre-commit install

clean:
	rm -rf .venv

test:
	pytest --cov -vv
