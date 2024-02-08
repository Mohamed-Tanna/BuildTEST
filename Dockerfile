# syntax=docker/dockerfile:1

# build stage
FROM python:3.10.10-alpine3.17 AS build-stage

WORKDIR /wheels

RUN apk add --update --no-cache gcc musl-dev python3-dev

COPY ./requirements.txt .

RUN pip install --upgrade pip

RUN pip wheel -r requirements.txt

#production stage
FROM python:3.10.10-alpine3.17 AS production-stage

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY daemon.json /etc/docker/daemon.json

COPY --from=build-stage /wheels /wheels

RUN mkdir static

RUN apk add --no-cache bash

RUN pip install --upgrade pip

RUN pip install \
        -r /wheels/requirements.txt \
        -f /wheels \
        && rm -rf /wheels \
        && rm -rf /root/.cache/pip/*

COPY . /code/

RUN mkdir /cron
RUN touch /cron/django_cron.log
RUN ["chmod", "777", "./startup.sh"]

EXPOSE 8000

CMD service cron start