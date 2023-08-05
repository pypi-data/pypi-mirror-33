"""
Decorators module
"""
from .settings import URL, PORT, KEEPALIVE


def ensure_connection(func):
    """
    Decorator to ensure connection before execute any decorated method
    """
    def wrapper(self, *args, **kwargs):
        try:
            getattr(self, "connected")
        except AttributeError:
            self.connected = False
        finally:
            if not self.connected:
                from paho.mqtt.client import Client
                Client.connect(
                    self,
                    self.url or URL,
                    self.port or PORT,
                    self.keepalive or KEEPALIVE
                )
                self.connected = True
        return func(self, *args, **kwargs)
    return wrapper


def ensure_udp_connection(func):
    """
    Decorator to ensure UDP connection before execute any decorated method
    """
    def wrapper(self, *args, **kwargs):
        try:
            getattr(self, "udp_connected")
        except AttributeError:
            self.udp_connected = False
        finally:
            if not self.udp_connected:
                from .udp_receiver import UDPReceiver
                UDPReceiver.connect(self)
                self.udp_connected = True
        return func(self, *args, **kwargs)
    return wrapper
