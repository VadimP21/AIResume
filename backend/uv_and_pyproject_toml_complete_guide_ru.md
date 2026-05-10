# Полное руководство по `uv` и `pyproject.toml`

## Содержание

1. Что такое `uv`
2. Что такое `pyproject.toml`
3. Почему современный Python перешёл на `pyproject.toml`
4. Архитектура Python packaging
5. Установка `uv`
6. Основные команды `uv`
7. Работа с виртуальными окружениями
8. Работа с Python-версиями
9. Создание проекта
10. Структура проекта
11. Полный разбор `pyproject.toml`
12. Секция `[project]`
13. Секция `[build-system]`
14. Секция `[tool.*]`
15. Зависимости
16. Dependency groups
17. Optional dependencies / extras
18. Lockfile `uv.lock`
19. Workspaces
20. Сборка и публикация пакетов
21. Интеграция с Ruff, Pytest, MyPy и другими инструментами
22. CI/CD
23. Docker + uv
24. Migration с pip/poetry/pipenv
25. Частые ошибки
26. Продвинутые возможности
27. Лучшие практики
28. Полные примеры проектов
29. Шпаргалка команд
30. FAQ

---

# 1. Что такое `uv`

`uv` — современный ultra-fast package manager и project manager для Python, написанный на Rust компанией Astral.

Он заменяет сразу несколько инструментов:

| Старый инструмент | Что заменяет uv |
|---|---|
| pip | установка пакетов |
| pip-tools | lock dependencies |
| poetry | project management |
| pipenv | dependency management |
| virtualenv | venv management |
| pyenv | Python version management |
| pipx | isolated tools |
| twine | publish packages |

Основные особенности:

- очень высокая скорость
- universal lockfile
- встроенное управление Python
- dependency resolution
- workspace support
- isolated tools
- reproducible builds
- pyproject.toml-based
- cross-platform

Согласно документации uv:

- может быть в 10–100 раз быстрее pip
- использует глобальный cache
- умеет работать как replacement для pip
- умеет создавать полноценные Python projects

Источники: ([docs.astral.sh](https://docs.astral.sh/uv/?utm_source=chatgpt.com))

---

# 2. Что такое `pyproject.toml`

`pyproject.toml` — стандартизированный файл конфигурации Python-проекта.

Он появился в PEP 518 и затем был расширен другими PEP:

| PEP | Назначение |
|---|---|
| PEP 518 | build system requirements |
| PEP 517 | build backend |
| PEP 621 | project metadata |
| PEP 660 | editable installs |
| PEP 735 | dependency groups |

Раньше Python-проекты использовали:

- setup.py
- setup.cfg
- requirements.txt
- tox.ini
- MANIFEST.in

Теперь почти всё переносится в `pyproject.toml`.

---

# 3. Почему Python перешёл на `pyproject.toml`

Проблемы старой системы:

## setup.py выполнялся как Python-код

Это было:

- небезопасно
- сложно анализировать
- не декларативно
- ломало reproducibility

## requirements.txt не описывает проект

Он хранит только зависимости.

Но проекту нужны:

- metadata
- build backend
- package settings
- tool configs
- linters
- formatters
- testing config

## pyproject.toml решает всё централизованно

Теперь один файл может хранить:

- metadata
- build settings
- dependencies
- dev dependencies
- linter configs
- formatter configs
- test configs
- build configs
- release configs

---

# 4. Архитектура современного Python packaging

Современный Python stack:

```text
pyproject.toml
        ↓
build backend
        ↓
wheel/sdist
        ↓
installer
        ↓
virtual environment
```

Основные build backends:

| Backend | Назначение |
|---|---|
| hatchling | современный backend |
| setuptools | legacy + modern |
| poetry-core | Poetry backend |
| flit_core | lightweight |
| pdm-backend | PDM |

---

# 5. Установка uv

## Linux/macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Через pip

```bash
pip install uv
```

## Проверка

```bash
uv --version
```

---

# 6. Основные команды uv

| Команда | Назначение |
|---|---|
| uv init | создать проект |
| uv add | добавить dependency |
| uv remove | удалить dependency |
| uv sync | синхронизация env |
| uv lock | создать lockfile |
| uv run | запуск внутри env |
| uv tree | dependency tree |
| uv build | build package |
| uv publish | publish package |
| uv tool install | install tool |
| uvx | запуск tool |
| uv python install | install Python |
| uv venv | create venv |

Источники: ([docs.astral.sh](https://docs.astral.sh/uv/getting-started/features/?utm_source=chatgpt.com))

---

# 7. Работа с виртуальными окружениями

## Создание окружения

```bash
uv venv
```

Создаётся:

```text
.venv/
```

## Использование конкретной версии Python

```bash
uv venv --python 3.12
```

## Активация

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

## Без активации

uv умеет запускать команды напрямую:

```bash
uv run python main.py
```

Это один из лучших features uv.

---

# 8. Работа с Python-версиями

uv умеет управлять Python.

## Установка Python

```bash
uv python install 3.12
```

## Список версий

```bash
uv python list
```

## Найти Python

```bash
uv python find
```

## Pin версии

```bash
uv python pin 3.12
```

Создаётся:

```text
.python-version
```

---

# 9. Создание проекта

## Простое создание

```bash
uv init myproject
```

Создаётся:

```text
myproject/
├── .gitignore
├── .python-version
├── README.md
├── main.py
└── pyproject.toml
```

Источники: ([docs.astral.sh](https://docs.astral.sh/uv/guides/projects/?utm_source=chatgpt.com))

---

# 10. Структура проекта

Типичный production проект:

```text
project/
├── src/
│   └── app/
├── tests/
├── scripts/
├── docs/
├── .venv/
├── pyproject.toml
├── uv.lock
├── README.md
├── .python-version
└── .gitignore
```

---

# 11. Полный разбор pyproject.toml

Минимальный пример:

```toml
[project]
name = "myapp"
version = "0.1.0"
dependencies = ["fastapi"]
```

Полноценный production example:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "awesome-app"
version = "0.1.0"
description = "Awesome application"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "John Doe", email = "john@example.com"}
]
keywords = ["api", "backend"]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]

dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.30.0",
    "sqlalchemy>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "ruff",
    "mypy"
]

[tool.ruff]
line-length = 88

[tool.pytest.ini_options]
pythonpath = ["src"]

[tool.mypy]
strict = true
```

---

# 12. Секция `[project]`

Главная секция.

## name

```toml
name = "myproject"
```

Имя пакета.

Требования:

- уникальное на PyPI
- lowercase preferred
- `-` и `_` допустимы

Ошибка:

```text
Invalid project name
```

---

## version

```toml
version = "1.2.3"
```

Используется SemVer:

```text
MAJOR.MINOR.PATCH
```

Примеры:

```toml
version = "0.1.0"
version = "1.0.0"
version = "2.5.1"
```

---

## description

```toml
description = "My awesome API"
```

Короткое описание.

---

## readme

```toml
readme = "README.md"
```

Можно:

```toml
readme = "README.rst"
```

или:

```toml
readme = {file = "README.md", content-type = "text/markdown"}
```

---

## requires-python

```toml
requires-python = ">=3.11"
```

Очень важно.

Возможные варианты:

```toml
requires-python = ">=3.10"
requires-python = ">=3.10,<4"
requires-python = "==3.12.*"
requires-python = ">=3.11,<3.13"
```

Ошибка:

```text
Python version incompatible
```

---

## authors

```toml
authors = [
  {name = "John"},
  {email = "john@example.com"},
  {name = "John", email = "john@example.com"}
]
```

---

## maintainers

```toml
maintainers = [
  {name = "Maintainer"}
]
```

---

## license

```toml
license = {text = "MIT"}
```

или:

```toml
license = {file = "LICENSE"}
```

---

## keywords

```toml
keywords = ["api", "backend", "fastapi"]
```

---

## classifiers

PyPI classifiers.

```toml
classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.12",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent"
]
```

---

## urls

```toml
[project.urls]
Homepage = "https://example.com"
Repository = "https://github.com/example/repo"
Documentation = "https://docs.example.com"
```

---

## scripts

CLI entry points.

```toml
[project.scripts]
mycli = "app.cli:main"
```

После install:

```bash
mycli
```

---

## gui-scripts

```toml
[project.gui-scripts]
myapp = "app.gui:start"
```

Для GUI apps.

---

## dependencies

Главные dependencies.

```toml
dependencies = [
  "fastapi",
  "sqlalchemy>=2.0",
  "pydantic~=2.10",
]
```

---

# 13. Секция `[build-system]`

Очень важна.

Пример:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## requires

Build dependencies.

## build-backend

Build engine.

Популярные:

| Backend | Значение |
|---|---|
| hatchling | hatchling.build |
| setuptools | setuptools.build_meta |
| poetry | poetry.core.masonry.api |
| flit | flit_core.buildapi |

---

# 14. Секция `[tool.*]`

Все инструменты складывают config сюда.

## Ruff

```toml
[tool.ruff]
line-length = 88
target-version = "py312"
```

---

## Ruff lint

```toml
[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]
```

---

## Ruff format

```toml
[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

---

## Pytest

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-ra -q"
```

---

## MyPy

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_unused_configs = true
```

---

## Black

```toml
[tool.black]
line-length = 88
```

---

## isort

```toml
[tool.isort]
profile = "black"
```

---

## Coverage

```toml
[tool.coverage.run]
source = ["src"]
```

---

## uv config

```toml
[tool.uv]
```

или:

```toml
[[tool.uv.index]]
url = "https://pypi.org/simple"
default = true
```

Источники: ([docs.astral.sh](https://docs.astral.sh/uv/reference/settings/?utm_source=chatgpt.com))

---

# 15. Зависимости

## Добавление

```bash
uv add fastapi
```

Автоматически:

- обновляется pyproject.toml
- обновляется uv.lock
- обновляется .venv

---

## Версионные constraints

```toml
"fastapi>=0.115"
"sqlalchemy==2.0.36"
"pydantic~=2.10"
"numpy<3"
```

---

## Environment markers

```toml
"uvloop; sys_platform != 'win32'"
```

---

## Git dependencies

```toml
"mypkg @ git+https://github.com/user/repo.git"
```

---

## Local dependencies

```toml
"mypkg @ file:///path/to/pkg"
```

---

# 16. Dependency groups

Современная замена dev-requirements.

```toml
[dependency-groups]
dev = [
  "pytest",
  "ruff",
  "mypy"
]
```

Установка:

```bash
uv sync --group dev
```

или:

```bash
uv add --dev pytest
```

Источники: ([docs.astral.sh](https://docs.astral.sh/uv/concepts/projects/dependencies/?utm_source=chatgpt.com))

---

# 17. Optional dependencies / extras

```toml
[project.optional-dependencies]
postgres = ["psycopg2"]
redis = ["redis"]
```

Install:

```bash
pip install mypkg[postgres]
```

или:

```bash
uv sync --extra postgres
```

---

# 18. uv.lock

Lockfile.

Содержит:

- exact versions
- hashes
- transitive dependencies
- platform data

Нужно ли коммитить?

Да.

Особенно:

- backend
- production
- team projects
- CI/CD

Источники: ([pydevtools.com](https://pydevtools.com/handbook/explanation/uv-complete-guide/?utm_source=chatgpt.com))

---

# 19. Workspaces

uv поддерживает monorepo.

Пример:

```toml
[tool.uv.workspace]
members = [
  "packages/api",
  "packages/core",
  "packages/utils"
]
```

Особенности:

- shared lockfile
- shared environment
- centralized dependency management

---

# 20. Сборка и публикация

## Build

```bash
uv build
```

Создаются:

```text
dist/
├── app.whl
└── app.tar.gz
```

---

## Publish

```bash
uv publish
```

Для PyPI token:

```bash
export UV_PUBLISH_TOKEN=...
```

---

# 21. Интеграция с инструментами

## Ruff

Install:

```bash
uv add --dev ruff
```

Run:

```bash
uv run ruff check .
```

Format:

```bash
uv run ruff format .
```

---

## Pytest

```bash
uv add --dev pytest
```

```bash
uv run pytest
```

---

## MyPy

```bash
uv add --dev mypy
```

```bash
uv run mypy src
```

---

# 22. CI/CD

GitHub Actions example:

```yaml
name: CI

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Sync deps
        run: uv sync

      - name: Run tests
        run: uv run pytest
```

---

# 23. Docker + uv

## Dockerfile

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "python", "main.py"]
```

---

# 24. Migration

## pip → uv

### Было

```bash
pip install -r requirements.txt
```

### Стало

```bash
uv sync
```

---

## poetry → uv

### Было

```bash
poetry add fastapi
```

### Стало

```bash
uv add fastapi
```

---

# 25. Частые ошибки

# Ошибка: Python version incompatible

Причина:

```toml
requires-python = ">=3.12"
```

Но установлен 3.11.

Решение:

```bash
uv python install 3.12
```

---

# Ошибка: No virtual environment found

Решение:

```bash
uv venv
```

или:

```bash
uv sync
```

---

# Ошибка: Lockfile out of date

Решение:

```bash
uv lock
```

---

# Ошибка: Resolution failed

Причины:

- dependency conflicts
- incompatible versions
- bad markers

Диагностика:

```bash
uv tree
```

---

# Ошибка: Build backend missing

Неправильно:

```toml
[build-system]
requires = []
```

Правильно:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

# 26. Продвинутые возможности

# Inline dependencies для scripts

```python
# /// script
# dependencies = ["requests"]
# requires-python = ">=3.11"
# ///

import requests
```

Run:

```bash
uv run script.py
```

Источники: ([pydevtools.com](https://pydevtools.com/handbook/reference/uv/?utm_source=chatgpt.com))

---

# uvx

Аналог npx.

```bash
uvx ruff check .
```

Без install.

---

# Tool install

```bash
uv tool install ruff
```

---

# Export requirements

```bash
uv export --format requirements-txt
```

---

# Sync frozen

```bash
uv sync --frozen
```

Гарантирует exact lock install.

---

# Editable install

```bash
uv pip install -e .
```

---

# 27. Лучшие практики

## Всегда commit:

- pyproject.toml
- uv.lock
- .python-version

## Никогда не commit:

- .venv
- __pycache__

## Используй src-layout

```text
src/package_name
```

## Используй dependency groups

Вместо:

```text
requirements-dev.txt
```

## Используй strict MyPy

```toml
strict = true
```

## Используй Ruff вместо:

- flake8
- isort
- pyupgrade
- autoflake

---

# 28. Полные примеры проектов

# FastAPI backend

```toml
[project]
name = "backend"
version = "0.1.0"
requires-python = ">=3.12"

dependencies = [
  "fastapi",
  "uvicorn",
  "sqlalchemy",
  "asyncpg",
  "pydantic",
]

[dependency-groups]
dev = [
  "pytest",
  "pytest-asyncio",
  "ruff",
  "mypy",
]
```

---

# ML project

```toml
[project]
name = "ml-project"
version = "0.1.0"

dependencies = [
  "numpy",
  "pandas",
  "scikit-learn",
  "matplotlib",
  "jupyter",
]
```

---

# CLI app

```toml
[project]
name = "mycli"
version = "0.1.0"

dependencies = [
  "typer",
  "rich",
]

[project.scripts]
mycli = "app.cli:main"
```

---

# 29. Шпаргалка команд

## Создать проект

```bash
uv init
```

## Добавить dependency

```bash
uv add requests
```

## Dev dependency

```bash
uv add --dev pytest
```

## Install all

```bash
uv sync
```

## Run command

```bash
uv run python main.py
```

## Lock

```bash
uv lock
```

## Dependency tree

```bash
uv tree
```

## Build

```bash
uv build
```

## Publish

```bash
uv publish
```

---

# 30. FAQ

# Нужно ли использовать requirements.txt?

Не обязательно.

Современный стек:

- pyproject.toml
- uv.lock

Но иногда requirements.txt нужен:

- legacy infra
- old Docker images
- old CI

Можно export:

```bash
uv export --format requirements-txt > requirements.txt
```

---

# Нужно ли использовать Poetry?

Нет.

uv покрывает почти все возможности Poetry.

---

# Можно ли использовать pip вместе с uv?

Да.

uv имеет pip-compatible interface:

```bash
uv pip install requests
```

---

# Что лучше: pip или uv?

Для новых проектов почти всегда лучше uv.

Причины:

- быстрее
- modern workflow
- lockfiles
- Python management
- workspace support
- better DX

---

# Нужно ли коммитить uv.lock?

Да.

Особенно:

- production
- backend
- CI/CD
- командная разработка

---

# Чем dependency groups отличаются от optional-dependencies?

## dependency-groups

Для development.

Не публикуются.

## optional-dependencies

Extras для пользователей пакета.

Публикуются на PyPI.

---

# pyproject.toml vs requirements.txt

| pyproject.toml | requirements.txt |
|---|---|
| metadata | только packages |
| dependencies | dependencies |
| tool configs | нет |
| build system | нет |
| publish support | нет |
| modern standard | legacy |

---

# Финальные рекомендации

Для современных Python-проектов рекомендуется:

- uv
- pyproject.toml
- uv.lock
- Ruff
- Pytest
- MyPy
- src-layout
- dependency groups
- CI/CD sync через uv sync --frozen

Минимальный production stack 2026:

```text
uv
pyproject.toml
uv.lock
ruff
pytest
mypy
```

Источники:

- Astral uv docs
- PEP 517/518/621/660/735
- pyproject.toml specification
- uv dependency management docs

Веб-источники: ([docs.astral.sh](https://docs.astral.sh/uv/?utm_source=chatgpt.com))

