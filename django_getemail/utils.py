import pika


class Publisher(object):

    def __init__(self, host, exchange, routing_key):
        self._params = pika.connection.ConnectionParameters(host=host)
        self.exchange = exchange
        self.routing_key = routing_key
        self._conn = None
        self._channel = None

    def connect(self):
        if not self._conn or self._conn.is_closed:
            self._conn = pika.BlockingConnection(self._params)
            self._channel = self._conn.channel()
            self._channel.exchange_declare(exchange=self.exchange)

    def _publish(self, msg):
        self._channel.basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=msg)

    def publish(self, msg):
        """Publish msg, reconnecting if necessary."""
        try:
            self._publish(msg)
        except pika.exceptions.ConnectionClosed:
            self.connect()
            self._publish(msg)

    def close(self):
        if self._conn and self._conn.is_open:
            self._conn.close()
