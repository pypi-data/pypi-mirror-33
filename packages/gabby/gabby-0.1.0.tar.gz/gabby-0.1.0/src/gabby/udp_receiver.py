"""
Tools to encapsulate generic receive connectors
"""
import logging
import time
import mqttsn.client as mqttsn
from collections import namedtuple

from .settings import UDP_URL, UDP_PORT
from .decorators import ensure_udp_connection


log = logging.getLogger('udpreceiver')
UDPMessage = namedtuple('UDPMessage', ['payload', 'topic', 'qos'])


class UDPReceiver(mqttsn.Client, mqttsn.Callback):
    """
    Receive messages from specific mqttsn broker

    Args:
        topics (list):
            list of strings with the topic names

        url (str):
            mqttsn server url

        port (int):
            mqttsn server port
    """
    def __init__(self, topics, url=None, port=None):
        mqttsn.Client.__init__(
            self, host=(url or UDP_URL), port=(port or UDP_PORT)
        )
        self.input_topics = topics
        self._hack_udp_callbacks()

    def message_arrived(self, topic_name, payload, qos, retained, msg_id):
        """
        Callback to receive messsages
        """
        log.debug(f'Received UDP message from {topic_name} topic')
        log.debug(f'Message: {payload}')
        self.process(None, UDPMessage(payload, topic_name, qos))
        return True

    def _hack_udp_callbacks(self):
        # Hack to use callback inside Receiver
        # [FIXME] Should fix at mqttsn project
        self.register_callback(self)

    def process(self, userdata, message):
        raise NotImplementedError

    @ensure_udp_connection
    def run(self, join=True):
        UDPReceiver.listen(
            self, self.input_topics.filter_by(transmission='udp')
        )

        logging.info('Getting into the listening loop')
        self.running = True
        while self.running and join:
            time.sleep(1)

    @ensure_udp_connection
    def listen(self, topics):
        """
        Subscribe to a list of channels

        Args:
            topics (list):
                list of topics to subscribe the mqtt listener
        """
        logging.debug(f'Listen to {list(map(lambda x: x.name, topics))}')

        for topic in map(lambda x: x.name, topics):
            self.subscribe(topic)
            logging.debug(f'Subscribed the {topic} topic')

    def stop(self):
        """
        Stop running
        """
        self.running = False
