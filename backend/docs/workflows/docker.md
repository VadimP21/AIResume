# Docker

## Цель

Запуск локальной инфраструктуры и полного контейнерного стека без передачи
секретов в образ Docker.

## Подготовка

1. Создать `.env.docker` из `.env.docker.example`.
2. Заменить все значения `CHANGE_ME_*` на уникальные секреты.
3. Не добавлять `.env.docker` в Git.

## Команды

Запуск только PostgreSQL и Redis для локальной разработки:

```powershell
docker compose up -d
```

Запуск полного стека с миграциями, API и Celery worker:

```powershell
docker compose --profile app up --build
```

Проверка состояния:

```powershell
docker compose ps
Invoke-WebRequest http://localhost:8000/api/v1/health
```

Остановка стека с сохранением данных:

```powershell
docker compose down
```

Удаление локальных данных PostgreSQL и Redis:

```powershell
docker compose down --volumes
```

Последняя команда удаляет данные локальной инфраструктуры.

## Ограничения

- PostgreSQL и Redis опубликованы только на `127.0.0.1`.
- Контейнеры API и worker используют непривилегированного пользователя.
- Миграции выполняются отдельным одноразовым сервисом до запуска API и worker.
