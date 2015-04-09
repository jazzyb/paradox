import unittest
from paradox.graph import TemporalGraph as Graph

class TestGraph (unittest.TestCase):
    def setUp(self):
        self.graph = Graph(0, 2)
        self.graph.create_node('a')
        self.graph.create_node('b')
        self.graph.create_node('c')
        self.graph.direct_edge('a', 'b')
        self.graph.direct_edge('b', 'c')

    def test_neighbors(self):
        self.assertEqual(len(self.graph._nodes), 9)

        nodes = [('b', 1), ('a', 1)]
        neighbors = map((lambda x: self.graph.node(x)), nodes)
        self.assertEqual(self.graph.neighbors('a', 0), neighbors)

        nodes = [('b', 0), ('b', 2), ('c', 2)]
        neighbors = map((lambda x: self.graph.node(x)), nodes)
        self.assertEqual(self.graph.neighbors('b', 1), neighbors)

        nodes = [('c', 0), ('c', 1)]
        neighbors = map((lambda x: self.graph.node(x)), nodes)
        self.assertEqual(self.graph.neighbors('c', 2), neighbors)

    def test_current_node(self):
        self.graph.set_current_node('a', 1)
        self.assertEqual(self.graph.current, ('a', 1))
        with self.assertRaises(KeyError):
            self.graph.set_current_node('foobar')