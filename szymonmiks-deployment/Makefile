.DEFAULT_GOAL := all

isort:
	poetry run isort --recursive .

black:
	poetry run black .

flake8:
	poetry run flake8 .

mypy:
	poetry run mypy --install-types --non-interactive .

test:
	poetry run pytest

lint: isort black flake8 mypy

tests: test

all: lint tests
