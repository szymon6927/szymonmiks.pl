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

deploy_blog:
	cd ../blog/ && hugo -D && cd ../szymonmiks-deployment && poetry run python deploy.py blog

deploy_website:
	poetry run python deploy.py website

deploy_all: deploy_blog deploy_website

lint: isort black flake8 mypy

tests: test

all: lint tests
