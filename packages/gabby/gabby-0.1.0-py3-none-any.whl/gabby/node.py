import logging

from .udp_transmitter import UDPTransmitter
from .transmitter import Transmitter
from .udp_receiver import UDPReceiver
from .receiver import Receiver
from .message import Message

log = logging.getLogger('nodes')


class AbstractNode:
    def __init__(self):
        self.bindings = {self}

    def bind(self, node):
        if isinstance(node, AbstractNode):
            self.bindings.add(node)
        else:
            raise TypeError('You can bind only nodes')

    def binds(self, nodes):
        for node in nodes:
            self.bind(node)

    def process(self, userdata, message):
        if self.decode_input:
            topic_name = message.topic
            topics = self.input_topics.filter_by(name=topic_name)
            if not topics:
                raise "There are no topics that decode this message"
            message = Message.decode(message.payload, topics)

        log.debug(f'Processing message: {message}')
        response_messages = self.transform(message) or []
        for msg in response_messages:
            for node in self.bindings:
                node.send(msg)

    def transform(self, message):
        """
        Abstract method to process any received message

        Args:
            message (Message or paho.mqtt.MQTTMessage):
                message from queue decoded or not depending on 'decode' var
        Return:
            Collection of messages to be transmitted, an empty list or None
        """
        raise NotImplementedError


class TCPNode(AbstractNode, Transmitter, Receiver):
    def __init__(self, input_topics, output_topics, decode_input=True,
                 url=None, port=None, keepalive=None):
        AbstractNode.__init__(self)
        Receiver.__init__(self, input_topics, url, port, keepalive)
        Transmitter.__init__(self, output_topics, url, port, keepalive)
        self.decode_input = decode_input


class UDPNode(AbstractNode, UDPTransmitter, UDPReceiver):
    def __init__(self, input_topics, output_topics, decode_input=True,
                 url=None, port=None):
        AbstractNode.__init__(self)
        UDPReceiver.__init__(self, input_topics, url, port)
        Transmitter.__init__(self, output_topics, url, port)
        self.decode_input = decode_input

    def run(self):
        bindings_number = len(self.bindings)
        log.debug(f'BINDINGS: {bindings_number}')
        if(bindings_number > 1):
            UDPReceiver.run(self, join=False)
        else:
            UDPReceiver.run(self)
