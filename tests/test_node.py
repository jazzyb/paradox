import unittest
from paradox.graph import Node
from paradox.state import UNKNOWN, EMPTY, OCCUPIED, VISITED, NUM_STATES

class TestNode (unittest.TestCase):
    def test_subclass(self):
        node = Node('foobar')
        self.assertEqual(node.foo, UNKNOWN)
        self.assertEqual(node.ident, 'foobar')

    def test_set_value(self):
        node = Node('foobar')
        node.agent = OCCUPIED
        self.assertEqual(node.agent, OCCUPIED)

    def test_key_error(self):
        node = Node('foobar')
        with self.assertRaises(KeyError):
            node.ident = UNKNOWN

    def test_value_error(self):
        node = Node('foobar')
        with self.assertRaises(ValueError):
            node.foo = 'BAD'
