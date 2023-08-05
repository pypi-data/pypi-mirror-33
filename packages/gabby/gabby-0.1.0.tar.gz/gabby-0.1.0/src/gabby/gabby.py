"""
Gabby module witch creates the Gabby class to handle creation of
message queue nodes for intercommunication
"""
import types
import logging
from collections import namedtuple

from .node import TCPNode, UDPNode
from .topic import TopicCollection

log = logging.getLogger('gabby')
Connection = namedtuple('Connection', ['host', 'port', 'options'])


class Gabby:
    def __init__(self, input_topics=None, output_topics=None, decode_input=True,
                 url=None, port=None, keepalive=None, udp_url=None,
                 udp_port=None, transmission='tcp'):

        self.connections = dict((
            ('tcp', Connection(url, port, (keepalive,))),
            ('udp', Connection(udp_url, udp_port, [])),
        ))
        self.input_topics = TopicCollection(input_topics or [])
        self.output_topics = TopicCollection(output_topics or [])
        self.transmission = \
            [transmission] if isinstance(transmission, str) else transmission

        self._init_nodes(decode_input)
        self._setup_nodes()

    def _init_nodes(self, decode_input):
        self.nodes = {}
        for protocol, class_ in (('udp', UDPNode), ('tcp', TCPNode)):
            if protocol in self.transmission:
                conn = self.connections[protocol]
                node = class_(
                    self.input_topics, self.output_topics, decode_input,
                    conn.host, conn.port, *conn.options
                )
                self.nodes[protocol] = node
        log.debug(f'Registered nodes: {self.nodes}')

    def _setup_nodes(self):
        for node in self.nodes.values():
            node.transform = types.MethodType(self.transform, node.transform)
            node.binds(self.nodes.values())

    def transform(self, client, message):
        raise NotImplementedError

    def run(self):
        for protocol, node in self.nodes.items():
            log.debug(f'Running node for {protocol} protocol')
            node.run()

    def send(self, message):
        for node in self.nodes.values():
            node.send(message)
