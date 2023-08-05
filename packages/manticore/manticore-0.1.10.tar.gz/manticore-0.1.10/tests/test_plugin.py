import unittest

from manticore.utils.event import Eventful
from manticore.core.plugin import Plugin

class A(Eventful):
    def do_stuff(self):
        self._publish("eventA",1, 'a')

class B(Eventful):
    def __init__(self, child, **kwargs):
        super(B, self).__init__(**kwargs)
        self.child = child
        self.forward_events_from(child)

    def do_stuff(self):
        self._publish("eventB", 2, 'b')


class C():
    def __init__(self):
        self.received = []
    def callback(self, *args):
        self.received.append(args)

class ManticoreDriver(unittest.TestCase):
    _multiprocess_can_split_ = True
    def setUp(self):
        self.state = {}

    def tearDown(self):
        pass

    def test_basic(self):
        a = A()
        b = B(a)
        c = C()

        b.subscribe('eventA', c.callback)
        b.subscribe('eventB', c.callback)

        a.do_stuff()
        self.assertSequenceEqual(c.received, [(1, 'a')])

        b.do_stuff()
        self.assertSequenceEqual(c.received, [(1, 'a'), (2, 'b')])


if __name__ == '__main__':
    unittest.main()
