# syntax=docker/dockerfile:1
FROM python:3.10-alpine3.16
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /innotter

COPY . /innotter/

RUN pip install pipenv && \
    pipenv install --dev --system --deploy && \
    chmod +x /innotter/ && \
    chmod +x ./entrypoint.sh

CMD ["/bin/sh", "-c", "./entrypoint.sh"]


