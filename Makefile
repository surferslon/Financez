run:
	docker compose up

run_dev:
	poetry run python app/manage.py runserver

run_with_build:
	docker compose build
	docker compose up
