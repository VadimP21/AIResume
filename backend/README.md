````md
# AI Resume + Cover Letter Builder

Production-ready backend for AI-powered resume and cover letter generation platform.

## Рабочие сценарии

- [Разработка](docs/workflows/development.md)
- [Тестирование](docs/workflows/testing.md)
- [Миграции](docs/workflows/migrations.md)
- [Code review](docs/workflows/code-review.md)
- [Git-ветки](docs/workflows/git-branches.md)
- [Коммиты](docs/workflows/commits.md)
- [Docker](docs/workflows/docker.md)

Built with:
- FastAPI
- PostgreSQL
- Redis
- Celery
- SQLAlchemy 2.0
- Docker
- JWT Auth

---

# Features

## Current
- JWT authentication
- User management
- Resume CRUD
- Resume sections
- Resume versioning and restoration
- Resume import from PDF and DOCX through a configured AI provider
- Resume export to PDF and DOCX
- PostgreSQL integration
- Redis integration
- Celery worker
- Docker support
- Rate limiting
- Structured logging
- Health checks

## Planned
- AI resume generation
- Cover letter generation
- ATS score checker
- Job matching
- Resume templates
- AI critique system

---

# Tech Stack

## Backend
- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pydantic v2

## Database
- PostgreSQL

## Queue
- Celery
- Redis

## Infrastructure
- Docker
- Docker Compose
- GitHub Actions

## Quality
- Ruff
- MyPy
- Pytest

---

# Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   ├── core/
│   ├── db/
│   ├── middleware/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── tasks/
│   ├── utils/
│   └── main.py
│
├── alembic/
├── tests/
├── static/
│
├── docker-compose.yaml
├── Dockerfile
├── pyproject.toml
└── README.md
````

---

# Local Development

## Requirements

* Python 3.12+
* Docker
* Docker Compose
* uv

Для локального PDF-экспорта в Windows установите MSYS2 и Pango командой
`pacman -S mingw-w64-x86_64-pango` в оболочке MSYS2. Перед запуском API
задайте `$env:WEASYPRINT_DLL_DIRECTORIES = "C:\msys64\mingw64\bin"` и
проверьте окружение командой `uv run python -m weasyprint --info`.

---

# Install uv

## Linux / macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

# Install dependencies

```bash
uv sync
```

---

# Environment Variables

Create `.env`:

```env
APP_NAME=AI Resume Builder
APP_ENV=development
DEBUG=false
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
LOG_LEVEL=INFO
TIMEZONE=UTC
ENABLE_FAKE_AUTH=false
FAKE_AUTH_EMAIL=
FAKE_AUTH_PASSWORD=
API_V1_PREFIX=/api/v1

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=resume_builder
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

JWT_SECRET=CHANGE_ME_AT_LEAST_32_CHARACTERS
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
REFRESH_TOKEN_EXPIRE_SECONDS=604800
JWT_ISSUER=airesume-api
JWT_AUDIENCE=airesume-client

CORS_ORIGINS=["http://localhost:3000"]

# Required only for resume import
AI_PROVIDER=gemini
AI_REQUEST_TIMEOUT_SECONDS=30

GEMINI_API_KEY=
GEMINI_MODEL=

DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

GIGACHAT_AUTH_KEY=
GIGACHAT_MODEL=
GIGACHAT_BASE_URL=https://gigachat.devices.sberbank.ru/api/v1

RESUME_IMPORT_MAX_FILE_SIZE=5242880
```

`POST /api/v1/auth/fake_auth` регистрируется только при
`APP_ENV=development|test` и `ENABLE_FAKE_AUTH=true`. При включении также
обязательны `FAKE_AUTH_EMAIL` и `FAKE_AUTH_PASSWORD`. В staging и production
включение endpoint запрещено конфигурацией.

### AI-провайдер для импорта резюме

`POST /api/v1/resumes/import` использует одного провайдера, выбранного через
`AI_PROVIDER`: `gemini` (по умолчанию), `deepseek` или `gigachat`. Заполняйте
ключ и модель только активного провайдера; переключение применяется после
перезапуска приложения. Для GigaChat `GIGACHAT_AUTH_KEY` — ключ авторизации,
а access token получается и кэшируется приложением автоматически.

При отсутствии конфигурации активного провайдера, таймауте, ошибке авторизации
или ответе провайдера 5xx endpoint возвращает `503 Service Unavailable` без
деталей внешнего сервиса. Fallback между провайдерами отсутствует.

---

# Run Infrastructure

Start PostgreSQL and Redis:

First copy `.env.docker.example` to `.env.docker` and replace every
`CHANGE_ME_*` value.

```bash
docker compose up -d
```

---

# Run Backend

```bash
uv run uvicorn app.main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

# Run Celery Worker

```bash
uv run celery -A app.tasks.worker worker -l info
```

---

# Database Migrations

## Create migration

```bash
uv run alembic revision --autogenerate -m "message"
```

## Apply migrations

```bash
uv run alembic upgrade head
```

---

# Docker

## Local Infrastructure Only

Starts:

* PostgreSQL
* Redis

```bash
docker compose up -d
```

---

# Full Docker Stack

Starts:

* API
* Celery
* PostgreSQL
* Redis

Copy `.env.docker.example` to `.env.docker`, replace every `CHANGE_ME_*` value,
then run:

```bash
docker compose --profile app up --build
```

The migration service applies Alembic migrations before API and Celery start.
PostgreSQL and Redis are published only on `127.0.0.1`.

Detailed commands: [Docker workflow](docs/workflows/docker.md).

---

# API Routes

## Auth

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
```

`POST /api/v1/auth/fake_auth` доступен только при `APP_ENV=development|test`,
`ENABLE_FAKE_AUTH=true` и заданных `FAKE_AUTH_EMAIL`/`FAKE_AUTH_PASSWORD`.

## Users

```text
GET /api/v1/users/me
```

## Health

```text
GET /api/v1/health
```

## Resumes

```text
GET    /api/v1/resumes
POST   /api/v1/resumes
GET    /api/v1/resumes/{id}
PATCH  /api/v1/resumes/{id}
DELETE /api/v1/resumes/{id}
POST   /api/v1/resumes/{id}/sections
PATCH  /api/v1/resumes/sections/{section_id}
GET    /api/v1/resumes/{id}/versions?limit=20&offset=0
GET    /api/v1/resumes/{id}/versions/{version_id}
POST   /api/v1/resumes/{id}/versions/{version_id}/restore
GET    /api/v1/resumes/{id}/export?format=pdf|docx
POST   /api/v1/resumes/import
```

`POST /api/v1/resumes/import` принимает текстовые PDF и DOCX до 5 MiB и
создаёт новое резюме. Для него требуются настройки активного AI-провайдера.
Исходный файл не сохраняется. `GET /api/v1/resumes/{id}/export` возвращает
единый ATS-friendly документ PDF или DOCX.

---

# Quality Tools

## Lint

```bash
uv run ruff check .
```

## Format

```bash
uv run ruff format --check .
```

## Type checking

```bash
uv run mypy app
```

## Tests

```bash
uv run pytest
```

---

# Makefile Commands

## Start infra

```bash
make infra
```

## Stop infra

```bash
make infra-down
```

## Run backend

```bash
make run
```

## Run worker

```bash
make worker
```

## Run tests

```bash
make test
```

---

# Security

Implemented:

* JWT authentication
* Password hashing
* Rate limiting
* Trusted hosts
* Security headers
* Request ID tracking
* Structured logging
* CORS protection

---

# Logging

Structured JSON logging via `structlog`.

Includes:

* request IDs
* status codes
* execution time
* errors
* startup/shutdown logs

---

# Health Checks

Health endpoint:

```text
GET /api/v1/health
```

Checks:

* PostgreSQL connection
* Redis connection

---

# Future Improvements

* S3 storage
* Kubernetes deployment
* OpenTelemetry
* Prometheus metrics
* AI orchestration
* Resume parser
* ATS engine
* WebSocket progress updates

---

# License

MIT

```
```
