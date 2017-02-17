import zmq
from django.conf import settings


zmq_context = zmq.Context()


class ZMQProxy():
    def send(self, msg):
        socket = zmq_context.socket(zmq.REQ)
        socket.connect(settings.WINDSOCK_BROKER_URL)
        socket.send(msg)


class DummyProxy():
    def send(self, msg):
        # we do nothing
        pass
