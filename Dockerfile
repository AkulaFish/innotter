# syntax=docker/dockerfile:1
FROM python:3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


COPY ./requirements.txt /requirements.txt

RUN pip install -r requirements.txt

RUN mkdir /innotter
WORKDIR /innotter
COPY ./innotter /innotter
