run:
	docker compose up

run_build:
	docker compose build
	docker compose up

dev:
	poetry run python app/manage.py runserver
