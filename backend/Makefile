infra:
	docker compose up -d

infra-down:
	docker compose down

run:
	uvicorn app.main:app --reload

worker:
	celery -A app.tasks.worker worker -l info

migrate:
	alembic upgrade head

makemigrations:
	alembic revision --autogenerate -m "$(m)"