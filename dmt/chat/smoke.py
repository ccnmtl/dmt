from smoketest import SmokeTest
import zmq
from django.conf import settings
from websocket import create_connection
import json
from .views import gen_token

zmq_context = zmq.Context()


class BrokerConnectivity(SmokeTest):
    def test_connect(self):
        """ a simple check to see if we can open up a socket
        to the zmq broker.

        We send a message and wait three seconds for a response.

        Send the message to room "0", which should never
        conflict with an actual chat room.
        """
        socket = zmq_context.socket(zmq.REQ)
        socket.setsockopt(zmq.LINGER, 0)
        socket.connect(settings.WINDSOCK_BROKER_URL)

        try:
            # the message we are broadcasting
            md = dict(project_pid=0,
                      username='smoketest',
                      message_text='smoketest')

            # an envelope that contains that message serialized
            # and the address that we are publishing to
            e = dict(address="%s.project_0" % (settings.ZMQ_APPNAME),
                     content=json.dumps(md))
            # send it off to the broker
            socket.send(json.dumps(e))
            # wait for a response from the broker to be sure it was sent

            # can't use the abstracted out proxy since we're doing
            # some timeout stuff
            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)
            if poller.poll(3 * 1000):  # 3s timeout in milliseconds
                socket.recv()
            else:
                raise IOError("Timeout connecting to broker")
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)
        finally:
            socket.close()


class DummyUser(object):
    username = "test"


class DummyRequest(object):
    def __init__(self):
        self.user = DummyUser()
        self.META = {'HTTP_X_FORWARDED_FOR': '127.0.0.1'}


class WindsockConnectivity(SmokeTest):
    def test_connect(self):
        try:
            r = DummyRequest()
            token = gen_token(r, 1)
            ws = create_connection(
                settings.WINDSOCK_WEBSOCKETS_BASE + "?token=" + token)
            ws.close()
            self.assertTrue(True)
        except Exception, e:
            print(e)
            self.assertTrue(False)
