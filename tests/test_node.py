import unittest
from paradox.graph import Node, UNKNOWN, EMPTY, OCCUPIED, VISITED

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
        node.foo = EMPTY
        node.bar = OCCUPIED
        node.baz = VISITED
        copy = node.copy()
        self.assertEqual(Node, type(copy))
        copy.baz = OCCUPIED
        self.assertEqual(VISITED, node.baz)
        self.assertEqual(OCCUPIED, copy.baz)
        self.assertEqual(OCCUPIED, copy.bar)
        self.assertEqual(EMPTY, copy.foo)
