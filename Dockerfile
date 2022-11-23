# syntax=docker/dockerfile:1
FROM python:3.10-alpine3.16
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /innotter

COPY . /innotter/

RUN pip install -r requirements.txt && \
    chmod +x /innotter/

CMD ./entrypoint.sh
