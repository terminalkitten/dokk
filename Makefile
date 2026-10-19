# Dev tasks. Install first: uv sync --all-extras
# --no-sync: use .venv as is (uv run's default sync would drop the extras).
RUN = uv run --no-sync

.PHONY: lint format typecheck test

lint: format typecheck test

format:
	$(RUN) ruff check --fix .
	$(RUN) ruff format .

typecheck:
	$(RUN) ty check

test:
	PYTHONWARNDEFAULTENCODING=1 $(RUN) pytest
