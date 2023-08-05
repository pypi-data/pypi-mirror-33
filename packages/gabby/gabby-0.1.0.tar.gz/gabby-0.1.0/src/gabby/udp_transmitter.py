import logging
from mqttsn import client as mqttsn

from .message import Message
from .decorators import ensure_udp_connection
from .settings import UDP_URL, UDP_PORT

log = logging.getLogger('udptransmitter')


class UDPTransmitter(mqttsn.Client):
    """
    Handler for MQTT-SN publishing

    Args:
        topics (dict):
            keys identify the topic,s for the mqtt topic
            names to publish
    """
    def __init__(self, topics, url=None, port=None):
        mqttsn.Client.__init__(
            self, host=(url or UDP_URL), port=(port or UDP_PORT)
        )
        self.output_topics = topics

    @ensure_udp_connection
    def send(self, message):
        """
        Publish string to the 2RSystem queue

        Args:
            data (str):
                string message to publish
        """
        receivers = []
        if isinstance(message, Message):
            receivers = message.filter_topics(
                self.output_topics.filter_by(transmission='udp')
            )

        for topic in map(lambda x: x.name, receivers):
            log.info(f'Publishing on topic {topic}')
            self.publish(topic, message.encoded)
