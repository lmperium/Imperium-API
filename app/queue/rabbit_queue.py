import os
import pika


class RQueue:

    def __init__(self):
        self.host = os.environ.get('RABBITMQ_HOST')
        self.user = os.environ.get('RABBITMQ_USER')
        self.password = os.environ.get('RABBITMQ_PWD')
        self.port = os.environ.get('RABBITMQ_PORT')
        self.v_host = os.environ.get('RABBITMQ_VHOST')

    def _connect(self):

        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(host=self.host, virtual_host=self.v_host, credentials=credentials)
        connection = pika.BlockingConnection(parameters=parameters)

        return connection

    def send_job(self, job):
        connection = self._connect()

        channel = connection.channel()
        channel.exchange_declare(exchange='work',
                                 exchange_type='direct')

        channel.confirm_delivery()

        targets = job['targets']

        for command in job['description']:
            for target in targets:
                p = channel.basic_publish(exchange='work',
                                          routing_key=target,
                                          body=str(command))
                if not p:
                    return False

        connection.close()

        return True

    def send_heartbeat(self):

        connection = self._connect()

        channel = connection.channel()
        channel.exchange_declare(exchange='heartbeat',
                                 exchange_type='fanout')

        pass
