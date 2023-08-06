from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from builtins import object
import pytest
import unittest

from calvin.runtime.north.plugins.port.endpoint.local import LocalInEndpoint, LocalOutEndpoint
from calvin.runtime.north.plugins.port import queue, DISCONNECT

pytest_unittest = pytest.mark.unittest

class DummyPort(object):
    pass
    
@pytest_unittest
class TestLocalInEndpoint(unittest.TestCase):

    routing = "fanout_fifo"
    num_peers = 3
    
    def create_port(self, direction):
        port = DummyPort()
        port.properties = {'routing': self.routing, "direction": direction,
                            'nbr_peers': self.num_peers}
        port.queue = queue.get(port)
        port.id = direction
        return port
    
    def setUp(self):
        port = self.create_port(direction="in")
        peer_port = self.create_port(direction="out")
        self.in_endpoint = LocalInEndpoint(port, peer_port)
        
    def tearDown(self):
        pass
        
    def testInit(self):
        assert self.in_endpoint

    def testIsConnected(self):
        self.assertTrue(self.in_endpoint.is_connected())

    def testAttached(self):
        self.in_endpoint.attached()
        # ?
        
    def testDetached_Terminate(self):
        self.in_endpoint.attached()
        self.in_endpoint.detached(DISCONNECT.TERMINATE)
        # Ensure reader is gone.
        self.assertFalse("out" in self.in_endpoint.port.queue.readers)

    def testDetached_Exhaust(self):
        self.in_endpoint.attached()
        [ self.in_endpoint.port.queue.write("data-%d" % i, None) for i in [1,2,3] ]
        self.in_endpoint.detached(DISCONNECT.EXHAUST)
        # for in ports, no remaining tokens
        self.assertEqual(self.in_endpoint.remaining_tokens, {"in": []})
        self.assertFalse("out" in self.in_endpoint.port.queue.readers)

    def testDetached_ExhaustPeer(self):
        self.in_endpoint.attached()
        [ self.in_endpoint.port.queue.write("data-%d" % i, None) for i in [1,2,3] ]
        self.in_endpoint.detached(DISCONNECT.EXHAUST_PEER)
        self.assertEqual(self.in_endpoint.port.queue.fifo[:3], ["data-%d" %i for i in [1,2,3]])
    
    def testGetPeer(self):
        self.assertEqual(('local', "out"), self.in_endpoint.get_peer())
