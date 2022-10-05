# <project_name>

Quick project description

## Table of contents

* [Stack](#stack)
* [Prerequisites](#prerequisites)
* [Setup](#setup)
* [Intellij / PyCharm configuration](#intellij-/-pycharm-configuration)
* [Tests](#tests)
* [CI/CD](#ci/cd)
* [Monitoring](#monitoring)
* [ADR](#adr)
* [Makefile](#makefile)
* [HTTP requests](#http-requests)

## Stack

Description of the technology stack used in the project.


**Example:**

- Python 3.9
- Starlette
- MongoDB

## Prerequisites

Information about all needed tools you have to install before you start the development.


**Example:**

Make sure you have installed all the following prerequisites on your development machine:

- [Python 3.9](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/)
- [GIT](https://git-scm.com/downloads)
- [Make](http://gnuwin32.sourceforge.net/packages/make.htm)
- [Docker version >= 20.10.7](https://www.docker.com/get-started)
- [docker-compose version >= 1.29.2](https://docs.docker.com/compose/install/)

## Setup

Description of how to setup the project to be able to start the development.


**Example:**

1. Install dependencies:

```bash
$ poetry install
```

2. Setup pre-commit hooks before committing:

```bash
$ poetry run pre-commit install
```

## Architecture

Description of the project's architecture. Diagrams, maps, etc.


## Intellij / PyCharm configuration

Info on how to setup a project inside Intellij or other IDE.


## Tests

Description of how to run the tests.


**Example:**

To run all tests you can use:

```bash
$ poetry run pytest
```

or

```bash
$ make tests
```

## CI/CD

Description of what the CI/CD process looks like and how it works. What is the deployment strategy etc?

## Monitoring

Information about tools used to monitor the application, how to use them, what is the purpose, how to access etc.

## ADR

Information about ADRs


**Example:**

We are using ADRs to describe our architecture/project decisions

[What is ADR?](https://github.com/joelparkerhenderson/architecture-decision-record)

If you are interesting take a look at `./docs/adr` directory.

## Makefile

Information about Makefile used in the project.


**Example:**

We use Makefile to automate some common stuff

If you want to run all linting tools
```bash
$ make lint
```

If you want to run all audit checks:
```bash
$ make audit
```

If you want to run tests:
```bash
$ make tests
```

## HTTP requests

Information about InteliJ HTTP client.


**Example:**

We are using http client build-in in Intelij IDEA (Pycharm, PHPStorm etc.)

Inside `http_requests` directory copy `/http-client.private.env.json.example` file to `/http-client.private.env.json`
and fill up required requests data.

[Tutorial how to use it](https://www.jetbrains.com/help/idea/http-client-in-product-code-editor.html)
