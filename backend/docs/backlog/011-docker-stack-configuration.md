# 011. Docker stack configuration was incomplete

- **Severity:** High
- **Status:** Resolved
- **Affected files:** `Dockerfile`, `docker-compose.yaml`, `.dockerignore`,
  `.env.docker.example`, `.github/workflows/docker.yml`, `docs/workflows/docker.md`

## Description

The full Docker stack started API and Celery without applying Alembic migrations.
The runtime image did not provide the required libraries for WeasyPrint, Compose
configuration was duplicated, and project documentation used obsolete Compose
filenames.

## Impact

On a fresh PostgreSQL volume, the application could start before its schema was
available. PDF generation could fail in the container, while different Compose
commands could start inconsistent service sets.

## Resolution

The configuration is consolidated in `docker-compose.yaml`. The `app` profile
adds a one-time `migrate` service and starts API and worker only after a
successful migration. The runtime image includes WeasyPrint libraries and runs
as a non-root user. Docker build and Compose validation are covered by CI.
