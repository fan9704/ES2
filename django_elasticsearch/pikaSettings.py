import logging
import os
import time

import pika

logger = logging.getLogger("Rabbitmq Configuration")


class RabbitmqServer(object):
    def __init__(self, username: str, password: str, serverip: str, port: str, virtual_host: str):
        self.username = username
        self.password = password
        self.serverip = serverip
        self.port = port
        self.virtual_host = virtual_host

    def connect(self):
        logger.info("Connect to Server")
        userPassword = pika.PlainCredentials(self.username, self.password)
        logger.info("Create MQ")
        logger.info("%s,%s,%s,%s,%s" % (self.virtual_host, self.serverip, self.port, self.password, self.username))

        s_conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.serverip, port=self.port, credentials=userPassword)
        )

        logger.info("Create Channel")
        self.channel = s_conn.channel()
        logger.info("Connect Successful")

    def produceMessage(self, queueName, message):
        self.channel.queue_declare(queue=queueName, durable=True)
        self.channel.basic_publish(
            exchange="",
            routing_key=queueName,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2, )  # Message Persist
        )

    def expense(self, queueName, func):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queueName,
            on_message_callback=func,
        )
        self.channel.start_consuming()


def callback(ch, method, properties, body):
    print("[Consumer] Received %r", body)
    time.sleep(1)
    print("[Consumer] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

# TODO: Setting Pull from Django Project Setting
RabbitmqClient = RabbitmqServer(
    os.getenv("RABBITMQ_USERNAME", "guest"),
    os.getenv("RABBITMQ_PASSWORD", "guest"),
    os.getenv("RABBITMQ_SERVER_IP", "127.0.0.1"),
    os.getenv("RABBITMQ_PORT", "5672"),
    os.getenv("RABBITMQ_VIRTUAL_HOST")
)
RabbitmqClient.connect()
if __name__ == "__main__":
    import json

    data = {"code": 3}
    RabbitmqClient.produceMessage("test3", json.dumps(data))
    RabbitmqClient.expense("test3", callback)
