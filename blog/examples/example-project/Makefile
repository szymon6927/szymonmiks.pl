.DEFAULT_GOAL := all

toml_sort:
	toml-sort pyproject.toml --all --in-place

isort:
	poetry run isort .

black:
	poetry run black .

flake8:
	poetry run flake8 .

pylint:
	poetry run pylint src

dockerfile_linter:
	docker run --rm -i hadolint/hadolint < Dockerfile

validate_openapi_schema:
	poetry run openapi-spec-validator example-project/docs/api/openapi.yaml

mypy:
	poetry run mypy --install-types --non-interactive .

audit_dependencies:
	poetry export --without-hashes -f requirements.txt | poetry run safety check --full-report --stdin

bandit:
	poetry run bandit -r . -x ./tests,./test

test:
	poetry run pytest

lint: toml_sort isort black flake8 pylint mypy validate_openapi_schema

audit: audit_dependencies bandit

tests: test

all: lint audit tests
