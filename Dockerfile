# syntax=docker/dockerfile:1

FROM python:3.10.8-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN mkdir static

RUN pip install --upgrade pip

COPY requirements.txt /code/

RUN pip install -r requirements.txt

RUN  pip install -U pip setuptools wheel ruamel.yaml.clib==0.2.6

COPY daemon.json /etc/docker/daemon.json

COPY . /code/

RUN ["chmod", "777", "./startup.sh"]

EXPOSE 8000