import unittest
from paradox.graph import TemporalGraph as Graph
from paradox.graph import TransactionRollback, UNKNOWN, EMPTY, OCCUPIED, VISITED

class TestGraph (unittest.TestCase):
    def setUp(self):
        self.graph = Graph(0, 2)
        self.graph.create_node('a')
        self.graph.create_node('b')
        self.graph.create_node('c')
        self.graph.direct_edge('a', 'b')
        self.graph.direct_edge('b', 'c')

    def test_duplicate_node_ids(self):
        with self.assertRaises(ValueError):
            self.graph.create_node('a')

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

    def test_consistent(self):
        self.graph.set_current_node('a', 0)
        self.graph.node('a', 0).agent = VISITED
        self.graph.node('c', 2).agent = EMPTY
        self.graph.node('b', 2).agent = OCCUPIED
        self.graph.node('c', 0).agent = OCCUPIED
        self.assertEqual(True, self.graph.is_consistent('agent'))

    def test_inconsistent(self):
        self.graph.set_current_node('a', 0)
        self.graph.node('a', 0).agent = VISITED
        self.graph.node('b', 0).agent = EMPTY
        self.graph.node('b', 1).agent = VISITED
        self.graph.node('c', 0).agent = OCCUPIED
        self.assertEqual(False, self.graph.is_consistent('agent'))

    def test_transaction(self):
        self.graph.node('a', 0).flag = OCCUPIED
        with self.graph.transaction() as graph:
            graph.node('a', 0).flag = VISITED
        self.assertEqual(VISITED, self.graph.node('a', 0).flag)

    def test_rollback_transaction(self):
        self.graph.node('a', 0).flag = OCCUPIED
        with self.graph.transaction() as graph:
            graph.node('a', 0).flag = VISITED
            graph.rollback()
            self.assertEqual(True, False)   # should never reach this line
        self.assertEqual(OCCUPIED, self.graph.node('a', 0).flag)

    def test_rollback_error(self):
        with self.assertRaises(TransactionRollback):
            self.graph.rollback()
