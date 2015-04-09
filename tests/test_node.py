import unittest
from paradox.graph import Node, State

class TestNode (unittest.TestCase):
    def test_subclass(self):
        node = Node('foobar')
        self.assertEqual(node.foo, State.UNKNOWN)
        self.assertEqual(node.ident, 'foobar')

    def test_set_value(self):
        node = Node('foobar')
        node.agent = State.OCCUPIED
        self.assertEqual(node.agent, State.OCCUPIED)

    def test_key_error(self):
        node = Node('foobar')
        with self.assertRaises(KeyError):
            node.ident = State.UNKNOWN

    def test_value_error(self):
        node = Node('foobar')
        with self.assertRaises(ValueError):
            node.foo = 'BAD'
