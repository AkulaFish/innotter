import json
import logging.config
import socket

import pika

from kombu.exceptions import OperationalError

from innotter.celery import app
from innotter import settings


@app.task(name="produce")
def produce(method, body):
    """Sending message to RabbitMQ for stats microservice to consume"""
    try:
        # Setting up connection with RabbitMQ server
        # Creating new queue for message exchange
        params = pika.URLParameters(settings.CELERY_BROKER_URl)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue="stats")
        properties = pika.BasicProperties(method)

        channel.basic_publish(
            exchange="",
            routing_key="stats",
            body=json.dumps(body),
            properties=properties,
        )

        logging.info("Successfully published")
    except (OperationalError, socket.gaierror, Exception):
        logging.info("Could not connect to RabbitMQ server")
