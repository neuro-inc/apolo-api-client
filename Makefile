.PHONY: all test clean
all test clean:


.PHONY: venv
venv:
	poetry lock;
	poetry sync --with dev;
	poetry run pre-commit install;

.PHONY: poetry-plugins
poetry-plugins:
	poetry self add \
		"poetry-dynamic-versioning[plugin]" \
		"poetry-plugin-export"

.PHONY: setup
setup: venv poetry-plugins


format:
	poetry run pre-commit run --all-files

.PHONY: lint
lint: format
	poetry run mypy apolo_api_client tests


.PHONY: test
test:
	poetry run pytest -vv --cov-config=pyproject.toml --cov-report xml:.coverage.xml tests
