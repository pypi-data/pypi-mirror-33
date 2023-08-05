import logging
import paho.mqtt.client as mqtt

from .message import Message
from .decorators import ensure_connection


class Transmitter(mqtt.Client):
    """
    Handler for MQTT publishing

    Args:
        topics (dict):
            keys identify the topic,s for the mqtt topic
            names to publish
    """
    def __init__(self, topics, url=None, port=None, keepalive=None):
        self.output_topics = topics
        self.url = url
        self.port = port
        self.keepalive = keepalive

    @staticmethod
    def on_connect(self, userdata, flags, rc):
        """
        The callback for when the client receives a CONNACK response
        from the server.
        """
        logging.info(f'Connected with MQTT Server: (code) {rc}')

    @staticmethod
    def on_disconnect(self, userdata, rc):
        """
        Called when the client disconnects from the broker.
        """
        self.connected = False

    @ensure_connection
    def send(self, message):
        receivers = []
        if isinstance(message, Message):
            receivers = message.filter_topics(
                self.output_topics.filter_by(transmission='tcp')
            )

        logging.debug(f"Sending message to {receivers}")

        for topic in map(lambda x: x.name, receivers):
            logging.info(f'Publishing on topic {topic}')
            self.publish(topic, message.encoded)
