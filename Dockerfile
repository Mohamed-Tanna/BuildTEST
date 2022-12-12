# syntax=docker/dockerfile:1

# build stage
FROM python:3.10.8-alpine AS build-stage

WORKDIR /wheels

RUN apk add --update --no-cache gcc musl-dev python3-dev

COPY ./requirements.txt .

RUN pip install --upgrade pip

RUN pip wheel -r requirements.txt

#production stage
FROM python:3.10.8-alpine AS production-stage

USER runner

WORKDIR /code

COPY daemon.json /etc/docker/daemon.json

COPY --from=build-stage /wheels /wheels

RUN mkdir static

RUN pip install --upgrade pip

RUN pip install \
        -r /wheels/requirements.txt \
        -f /wheels \
        && rm -rf /wheels \
        && rm -rf /root/.cache/pip/*

COPY . /code/

RUN ["chmod", "777", "./startup.sh"]

EXPOSE 8000