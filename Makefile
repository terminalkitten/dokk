# Dev tasks. Install first: uv sync --all-extras
# --no-sync: use .venv as is (uv run's default sync would drop the extras).
RUN = uv run --no-sync

.PHONY: lint format typecheck test hooks

lint: format typecheck test

format:
	$(RUN) ruff check --fix .
	$(RUN) ruff format .
	$(RUN) dokk format

typecheck:
	$(RUN) ty check

test:
	PYTHONWARNDEFAULTENCODING=1 $(RUN) pytest

# Use the hooks in .githooks/ (pre-commit: docs/ must be formatted).
hooks:
	git config core.hooksPath .githooks
