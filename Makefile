# Dev tasks. Install first: uv pip install -e ".[dev,serve,search,e2e]"
# --no-sync: use the installed .venv as is (a sync would drop the extras).
RUN = uv run --no-sync

.PHONY: lint format typecheck test

lint: format typecheck test

format:
	$(RUN) ruff check --fix .
	$(RUN) ruff format .

typecheck:
	$(RUN) ty check

test:
	$(RUN) pytest
