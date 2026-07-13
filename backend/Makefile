infra:
	docker compose up -d

infra-down:
	docker compose down

docker-up:
	docker compose --profile app up --build

docker-down:
	docker compose --profile app down

run:
	uvicorn app.main:app --reload

run_loc:
	uvicorn app.main_offline:app --reload

worker:
	celery -A app.tasks.worker worker -l info

migrate:
	alembic upgrade head

makemigrations:
	alembic revision --autogenerate -m "$(m)"
