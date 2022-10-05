+++
author = "Szymon Miks"
title = "How I start every new Python backend API project"
description = "How to setup everything and focus only on the implementation of our lovely business logic"
date = "2022-09-27"
image = "img/la-rel-easter-KuCGlBXjH_o-unsplash.jpg"
categories = [
     "Python", "Software_Development"
]
tags = [
    "python", "software development", "project setup"
]
draft = true
+++

## Intro

In today's blog post I would like to show you how I approach every new Python **backend API** project setup.

This blog post includes:
- project structure
- tools
- best practices
- automation

Let's go! :rocket:

## Poetry

[Poetry](https://python-poetry.org/) in my opinion is the best Python packaging and dependency management tool.

I'm using it in all of my projects since 2019.
If you have not heard about Poetry yet, I highly recommend reading about this tool.
In my opinion, it is the best option that we currently have on the Python market.

## Project creation

To create a new project with poetry you need to run this command:

```bash
$ poetry new <your-project-name>
```

## Project structure

```
├── .docker
├── .gitignore
├── .pre-commit-config.yaml
├── Makefile
├── README.md
├── docs
│ ├── adr
│ │   └── adr-001-example_adr.md
│ └── api
│     └── openapi.yaml
├── http_requests
│ ├── http-client.env.json
│ └── ping.http
├── iac
├── pyproject.toml
├── setup.cfg
├── src
│ ├── building_blocks
│ │ └── logger.py
│ ├── domain_module_a
│ │ ├── application
│ │ ├── domain
│ │ └── infrastructure
│ ├── domain_module_b
│ └── domain_module_c
└── tests
    ├── domain_module_a
    ├── domain_module_b
    └── domain_module_c
```

I will explain the purpose of each directory, starting from the top.

### :file_folder: .docker

If my project uses docker, I put all docker-related files here.
For example: init scripts for [localstack](https://github.com/localstack/localstack).

### :file_folder: docs

Inside this directory, I keep all things related to the project's documentation.

The `openapi.yaml` file resides inside `api` sub-directory.

Inside the `adr` sub-directory, I keep the project's ADRs.
I wrote a separate article about the ADRs, you can read it [here](https://blog.szymonmiks.pl/p/what-is-an-adr/).

### :file_folder: http_requests

I use [IntelliJ HTTP Client](https://www.jetbrains.com/help/idea/http-client-in-product-code-editor.html)
and here is where I keep request's definitions.

If you have not heard about this tool, I recommend you check it out. Having this, you do not have to have any
additional API clients like [postman](https://www.postman.com/) or [insomnia](https://insomnia.rest/).

### :file_folder: iac

If my project uses [Infrastructure as code](https://en.wikipedia.org/wiki/Infrastructure_as_code)
here is where I keep `terraform` or other files.

### :file_folder: src

Here I keep the code responsible for the application itself. This directory contains sub-directories.
I do not like splitting the project into technical layers. In opposition to that, I follow the convention
where each module is named accordingly and responsible for the business domain that it belongs to.

One of the benefits of it is that each module can have a different type of application architecture.
As you can see in the `domain_module_a` the separation is done by **hexagonal architecture** rules.
It has no impact on the other modules where such separation is not needed.

You can see there is a module called `building_blocks`.
Inside it, I keep all the utilities needed in the project, like a logger, serializers, and so on.
I did not make up this name, I borrowed it from this [repo](https://github.com/kgrzybek/modular-monolith-with-ddd/tree/master/src/BuildingBlocks).


## README.md

It is very important to take care of the README file because:
- it is the first thing that will be shown after opening the project's repo
- it allows new members of the team to start working with the project more smoothly

Here is my proposition for the `README` file

```markdown
# <project_name>

Quick project description.

## Table of contents

* [Stack](#stack)
* [Prerequisites](#prerequisites)
* [Setup](#setup)
* [Intellij / PyCharm configuration](#intellij-/-pycharm-configuration)
* [Tests](#tests)
* [CI/CD](#ci/cd)
* [Monitoring](#monitoring)
* [ADR](#adr)
* [HTTP requests](#http-requests)

## Stack

Description of the technology stack used in the project.

## Prerequisites

Information about all needed tools you have to install before you start the development.

## Setup

Description of how to setup the project to be able to start the development.

## Architecture

Description of the project's architecture. Diagrams, maps, etc.

## Intellij / PyCharm configuration

Info on how to setup a project inside Intellij or other IDE.

## Tests

Description of how to run the tests.

## CI/CD

Description of what the CI/CD process looks like and how it works. What is the deployment strategy, etc.

## Monitoring

Information about tools used to monitor the application, how to use them, what is the purpose, how to access etc.

## ADR

Information about ADRs.

## HTTP requests

Information about IntelliJ HTTP client.

```

You can find the complete **README** with some example descriptions for each section here:
https://github.com/szymon6927/szymonmiks.pl/tree/master/blog/examples/example-project


## Tools

Here is the list of tools that I always add while creating a new project:
- [pytest](https://docs.pytest.org/en/7.1.x/)
- [black](https://github.com/psf/black)
- [mypy](https://mypy.readthedocs.io/en/stable/)
- [flake8](https://flake8.pycqa.org/en/latest/)
- [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/)
- [isort](https://pycqa.github.io/isort/)
- [pylint](https://pylint.pycqa.org/en/latest/)
- [pre-commit](https://pre-commit.com/)
- [bandit](https://bandit.readthedocs.io/en/latest/)
- [openapi-spec-validator](https://github.com/p1c2u/openapi-spec-validator)
- [responses](https://github.com/getsentry/responses)
- [ipython](https://ipython.org/)

If my project uses **AWS** services, I also install [moto](https://github.com/spulec/moto) library.

I use `pyproject.toml` file to keep the config for each of them in one place.

This is what it looks like:
```toml
[tool.black]
line-length = 120
target-version = ["py39"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "pass",
    "if 0:",
    "if __name__ == .__main__.:",
    "nocov",
    "if TYPE_CHECKING:",
]
fail_under = 80
show_missing = true

[tool.coverage.run]
branch = true
omit = [
    "tests/*"
]

[tool.isort]
combine_as_imports = "true"
force_grid_wrap = 0
include_trailing_comma = "true"
known_first_party = "src"
line_length = 120
multi_line_output = 3

[tool.mypy]
disallow_untyped_defs = true
follow_imports = "silent"
ignore_missing_imports = true
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true

[tool.pylint.BASIC]
good-names = "id,i,j,k"

[tool.pylint.DESIGN]
max-args = 5
max-attributes = 8
min-public-methods = 1

[tool.pylint.FORMAT]
max-line-length = 120

[tool.pylint."MESSAGES CONTROL"]
disable = "missing-docstring, line-too-long, logging-fstring-interpolation, duplicate-code"

[tool.pylint.MISCELLANEOUS]
notes = "XXX"

[tool.pylint.SIMILARITIES]
ignore-comments = "yes"
ignore-docstrings = "yes"
ignore-imports = "yes"
min-similarity-lines = 6

[tool.pytest.ini_options]
addopts = "-v --cov=src --cov-report term-missing --no-cov-on-fail"
testpaths = ["tests"]

```

The only exception is `flake8` which does not support config inside `pyproject.toml` so we have to have an additional file
which is `setup.cfg`.

```
[flake8]
ignore = E501, W503, E203
max-line-length = 120
```

### pre-commit

[pre-commit](https://pre-commit.com/) allows you to add git hooks that will execute before you add your commit.

This is the config file that I use in my projects:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.3.0
    hooks:
      - id: trailing-whitespace
      - id: check-merge-conflict
      - id: check-yaml
        args: [--unsafe]
      - id: check-json
      - id: detect-private-key
      - id: end-of-file-fixer

  - repo: https://github.com/timothycrosley/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/psf/black
    rev: 22.8.0
    hooks:
      - id: black

  - repo: https://gitlab.com/pycqa/flake8
    rev: 3.9.2
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.971
    hooks:
      - id: mypy
        args: [ --warn-unused-configs, --ignore-missing-imports, --disallow-untyped-defs, --follow-imports=silent, --install-types, --non-interactive ]

```

### Makefile

I like using [Make](https://www.gnu.org/software/make/manual/make.html) to automate stuff in my projects.

Below you can see the Makefile that I use.

```makefile

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

```

## Complete example

You can find the complete example on my GitHub :rocket:

https://github.com/szymon6927/szymonmiks.pl/tree/master/blog/examples/example-project


## Summary

I hope it was useful to you, and I hope that after reading this article you adopt some concepts for your project.

If you have a different opinion, please let me know. I would like to know what you think about it.
