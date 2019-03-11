import os
import pika


class RQueue:

    def __init__(self):
        self.host = os.environ.get('RABBIT_MQ_HOST')

    def _connect(self):

        parameters = pika.ConnectionParameters(host=self.host)
        connection = pika.BlockingConnection(parameters=parameters)

        return connection

    def send_job(self, job):

        # Initialize connection
        connection = self._connect()

        channel = connection.channel()
        channel.exchange_declare(exchange='work',
                                 exchange_type='direct')

        channel.confirm_delivery()

        for command in job['description']:
            p = channel.basic_publish(exchange='work',
                                      routing_key=job['target'],
                                      body=str(command))

        connection.close()

        if not p:
            return False

        return True

    def send_heartbeat(self):

        connection = self._connect()

        channel = connection.channel()
        channel.exchange_declare(exchange='heartbeat',
                                 exchange_type='fanout')

        pass
