import pika
from logging import Logger


class MessagingConnectionProperties:
    def __init__(self, host: str,
                 user: str,
                 password: str,
                 queue: str,
                 exchange: str,
                 routingkey: str,
                 virtualhost: str,
                 port: int,
                 queuetype: str,
                 expires,
                 usessl: bool):
        self.host = host
        self.user = user
        self.password = password
        self.queue = queue
        self.exchange = exchange
        self.routingkey = routingkey
        self.virtualhost = virtualhost
        self.port = port
        self.queuetype = queuetype
        self.expires = expires
        self.usessl = usessl


class MessagingService:
    def __init__(self, connection_props: MessagingConnectionProperties, logger: Logger):
        self._connection_props = connection_props
        self._connection = None
        self._logger = logger

    def publish(self, message: str):

        try:
            # credentials = pika.credentials.PlainCredentials(self._connection_props.user,
            #                                                 self._connection_props.password)

            protocol = "amqp" if self._connection_props.usessl is not True else "amqps"

            url = "{PROTOCOL}://{USER}:{PASSWORD}@{HOST}/{VHOST}?heartbeat_interval=0".format(PROTOCOL=protocol,
                                                                                              USER=self._connection_props.user,
                                                                                              PASSWORD=self._connection_props.password,
                                                                                              HOST=self._connection_props.host,
                                                                                              VHOST=self._connection_props.virtualhost)
            params = pika.URLParameters(url=url)

            self._connection = pika.BlockingConnection(params)

            if self._connection is not None:
                arguments = {
                    "x-expires": self._connection_props.expires
                }

                channel = self._connection.channel()
                channel.queue_declare(queue=self._connection_props.queue, durable=True, arguments=arguments)

                channel.basic_publish(exchange=self._connection_props.exchange,
                                      routing_key=self._connection_props.routingkey,
                                      body=message)

                self._closeconnection()
                self._connection = None

        except Exception as exc:
            self._logger.error("an error occurred while connecting to a queue {exc}".format(exc=exc))

        self._closeconnection()
        self._connection = None

    def _closeconnection(self):
        try:
            if self._connection is not None:
                self._connection.close()
        except Exception as exc:
            self._logger.error("an error occurred while closing the RabbitMQ connection {exc}".format(exc=exc))

    # def __exit__(self, exc_type, exc_val,exc_tb):
    #     self.closeconnection()
