import unittest
from paradox.graph import Node
from paradox.state import UNKNOWN, EMPTY, OCCUPIED, VISITED

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

    def test_copy(self):
        node = Node('foobar')
        node.foo = 1
        node.bar = 2
        node.baz = 3
        copy = node.copy()
        self.assertEqual(Node, type(copy))
        copy.baz = 2
        self.assertEqual(3, node.baz)
        self.assertEqual(2, copy.baz)
        self.assertEqual(2, copy.bar)
        self.assertEqual(1, copy.foo)
