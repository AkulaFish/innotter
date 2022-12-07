import json
import pika
import os
import logging

from kombu.exceptions import OperationalError

from innotter.celery import app


LOGGER = logging.getLogger("PRODUCER")
LOGGER.setLevel(logging.INFO)
logging.basicConfig()


@app.task(name="produce")
def produce(method, body):
    """Sending message to RabbitMQ for stats microservice to consume"""
    try:
        # Setting up connection with RabbitMQ server, creating new queue for message exchange
        params = pika.URLParameters(os.getenv("CELERY_BROKER_URL"))
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

        LOGGER.info("Published")
    except OperationalError:
        LOGGER.info("Could not connect to RabbitMQ server")
