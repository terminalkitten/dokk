# Dev tasks. Install first: uv sync --all-extras
# --no-sync: use .venv as is (uv run's default sync would drop the extras).
RUN = uv run --no-sync

.PHONY: lint format format-md typecheck test hooks

lint: format format-md typecheck test

format:
	$(RUN) ruff check --fix .
	$(RUN) ruff format .

format-md:
	$(RUN) mdformat docs

typecheck:
	$(RUN) ty check

test:
	PYTHONWARNDEFAULTENCODING=1 $(RUN) pytest

# Use the hooks in .githooks/ (pre-commit: docs/ must be formatted).
hooks:
	git config core.hooksPath .githooks
