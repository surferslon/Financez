FROM python:3.10

ADD . /usr/app
WORKDIR /usr/app

FROM nginx:1.18-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build-step /build/build /usr/share/nginx/html

RUN pip install poetry && poetry install
