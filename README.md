# szymonmiks.pl
My personal website szymonmiks.pl

## Stack

- Python 3.9
- Hugo
- HTML
- CSS
- JS

## Prerequisites

Make sure you have installed all the following prerequisites on your development machine:

- [Poetry](https://python-poetry.org/)
- [GIT](https://git-scm.com/downloads)
- [Make](http://gnuwin32.sourceforge.net/packages/make.htm)
- [Python 3.9](https://www.python.org/downloads/)

## Setup

1. Install dependencies:

```bash
$ poetry install
```

2. Setup pre-commit hooks before committing:

```bash
$ poetry run pre-commit install
```

## Intellij / PyCharm configuration

1. In your terminal type `poetry shell`.
2. Copy the path to the virtualenv
3. Add new interpreter
   - In PyCharm go `Preferences > Project > Python Interpreter > Add Python Interpreter > Existing environment`
   - Paste the path that you copied before
   - Select `python3`
   - Click `OK`
4. Your IDE should be ready! Voilà!

#### Meta

If you have any questions/problems/thoughts drop me a line

[Szymon Miks](https://szymonmiks.pl/) – miks.szymon@gmail.com