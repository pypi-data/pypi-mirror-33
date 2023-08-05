"""
Tools to encapsulate generic receive connectors
"""
import logging
import paho.mqtt.client as mqtt

from .decorators import ensure_connection


class Receiver(mqtt.Client):
    """
    Receive messages from specific mqtt queue

    Args:
        topics (list):
            list of strings with the topic names

        url (str):
            mqtt server url

        port (int):
            mqtt server port

        keepalive (int):
            mqtt keepalive time in seconds
    """
    def __init__(self, topics, url=None, port=None, keepalive=None):
        mqtt.Client.__init__(self)
        self.input_topics = topics
        self.url = url
        self.port = port
        self.keepalive = keepalive

    @staticmethod  # decorator to avoid double 'self' on paho callback
    def on_connect(self, userdata, flags, rc):
        """
        The callback for when the client receives a CONNACK response
        from the server.
        """
        logging.info(f'Connected with Mosquitto Server: (code) {rc}')

    @staticmethod  # decorator to avoid double 'self' on paho callback
    def on_message(self, userdata, message):
        """
        The callback for when a PUBLISH message is received from the server.
        """
        logging.debug(f"Message arrived from {message.topic}")
        self.process(userdata, message)

    def process(self, userdata, message, bind=None):
        raise NotImplementedError

    def run(self):
        """
        Blocking call that processes network traffic, dispatches callbacks and
        handles reconnecting.
        Other loop*() functions are available that give a threaded interface
        and a manual interface.
        """
        self.listen(self.input_topics.filter_by(transmission='tcp'))

        logging.info('Getting into the listening loop')
        self.running = True
        while self.running:
            self.loop()

    @ensure_connection
    def listen(self, topics):
        """
        Subscribe to a list of channels

        Args:
            topics (list):
                list of topics to subscribe the mqtt listener
        """
        logging.debug(f'Listen to {list(map(lambda x: x.name, topics))}')

        for topic in map(lambda x: x.name, topics):
            try:
                self.subscribe(topic)
                logging.debug(f'Subscribed the {topic} topic')
            except Exception:
                logging.debug(f"Can't subscribe the {topic} topic")

    def stop(self):
        """
        Stop running
        """
        self.running = False
