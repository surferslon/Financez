FROM python:3.12

ADD ./app /usr/app
ADD ./pyproject.toml /usr/app
WORKDIR /usr/app

RUN pip install poetry && poetry install
RUN pip install gunicorn

RUN poetry run python manage.py collectstatic --noinput
