````md
# AI Resume + Cover Letter Builder

Production-ready backend for AI-powered resume and cover letter generation platform.

## Рабочие сценарии

- [Разработка](docs/workflows/development.md)
- [Тестирование](docs/workflows/testing.md)
- [Миграции](docs/workflows/migrations.md)
- [Code review](docs/workflows/code-review.md)

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
- PDF/DOCX export
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
DEBUG=true
ENABLE_FAKE_AUTH=false
FAKE_AUTH_EMAIL=
FAKE_AUTH_PASSWORD=

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=resume_builder
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_SECRET=CHANGE_ME
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
REFRESH_TOKEN_EXPIRE_SECONDS=604800

REDIS_PASSWORD=

CORS_ORIGINS=["http://localhost:3000"]
```

`POST /api/v1/auth/fake_auth` регистрируется только при
`APP_ENV=development|test` и `ENABLE_FAKE_AUTH=true`. При включении также
обязательны `FAKE_AUTH_EMAIL` и `FAKE_AUTH_PASSWORD`. В staging и production
включение endpoint запрещено конфигурацией.

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
uvicorn app.main:app --reload
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
celery -A app.tasks.worker worker -l info
```

---

# Database Migrations

## Create migration

```bash
alembic revision --autogenerate -m "message"
```

## Apply migrations

```bash
alembic upgrade head
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
POST /api/v1/auth/refresh
```

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
```

---

# Quality Tools

## Lint

```bash
ruff check .
```

## Format

```bash
ruff format .
```

## Type checking

```bash
mypy app
```

## Tests

```bash
pytest
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
