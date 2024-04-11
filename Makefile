run:
	docker compose up

build:
	docker compose build
	docker compose up

dev:
	poetry run python app/manage.py runserver
