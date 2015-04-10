import functools
from collections import defaultdict
from paradox.state import UNKNOWN, EMPTY, OCCUPIED, VISITED, NUM_STATES
from paradox.transaction import Transaction, TransactionError, \
        TransactionRollback


class Node (defaultdict):
    def __init__(self, ident):
        super(Node, self).__init__(lambda: UNKNOWN)
        self.__dict__['ident'] = ident

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        if name == 'ident':
            raise KeyError('cannot reassign ident')
        if value not in range(NUM_STATES):
            raise ValueError('value must be a paradox state')
        self[name] = value

    def copy(self):
        copy = Node(self.ident)
        copy.__dict__.update(self.__dict__)
        return copy


def transaction_method(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._transaction:
            return getattr(self._transaction, func.__name__)(*args, **kwargs)
        else:
            return func(self, *args, **kwargs)
    return wrapper


class TemporalGraph (object):
    def __init__(self, start_time, end_time):
        self._start = start_time
        self._end = end_time
        self._nodes = dict()
        self._edges = dict()
        self._names = set()
        self.current = None
        self._transaction = None

    # @transaction_method # ???
    def copy(self):
        copy = TemporalGraph(self._start, self._end)
        copy._nodes = {k: v.copy() for k,v in self._nodes.iteritems()}
        copy._edges = {k: set(v) for k,v in self._edges.iteritems()}
        copy._names = set(self._names)
        return copy

    @transaction_method
    def set_current_node(self, ident, time=None):
        if time is not None:
            ident = (ident, time)
        if ident not in self._nodes:
            raise KeyError('no such node id')
        self.current = ident

    @transaction_method
    def create_node(self, name):
        if name in self._names:
            raise ValueError('node identifier already exists')

        for t in range(self._start, self._end + 1):
            node = Node((name, t))
            self._nodes[node.ident] = node
            neighbors = set(map((lambda x: (name, x)), range(self._start, t)))
            self._edges[node.ident] = neighbors
            if t != self._end:
                self._edges[node.ident].add((name, t + 1))

        self._names.add(name)

    @transaction_method
    def direct_edge(self, node_name1, node_name2):
        for t in range(self._start, self._end):
            self._edges[(node_name1, t)].add((node_name2, t + 1))

    @transaction_method
    def node(self, ident, time=None):
        if time is not None:
            ident = (ident, time)
        return self._nodes[ident]

    @transaction_method
    def neighbors(self, ident, time=None):
        if time is not None:
            ident = (ident, time)
        return map((lambda i: self._nodes[i]), self._edges[ident])

    @transaction_method
    def is_consistent(self, item):
        targets = set(ident for ident, node in self._nodes.iteritems() \
                if node[item] == OCCUPIED)
        return self._check_consistency(item, [self.current], targets)

    ### Transaction methods:

    def start_transaction(self):
        if self._transaction:
            raise TransactionError('cannot execute nested transactions')
        self._transaction = self.copy()

    def cancel_transaction(self):
        self._transaction = None

    def commit_transaction(self):
        if self._transaction is None:
            raise TransactionError('no transaction to commit')
        self = self._transaction
        self._transaction = None

    def transaction(self):
        if self._transaction:
            raise TransactionError('cannot execute nested transactions')
        return Transaction(self)

    def rollback(self):
        raise TransactionRollback('rollback called outside of transaction')

    ### PRIVATE ###

    def _check_consistency(self, item, path, targets):
        """Recursive depth-first search of graph.

        Return True if there exists a path through the graph from the current
        node to all target nodes; return False otherwise.
        """
        for neighbor in self._edges[path[-1]]:
            if neighbor in path:
                continue
            elif self._nodes[neighbor][item] in (EMPTY, VISITED):
                continue

            remaining = set(targets)
            if neighbor in targets:
                remaining.remove(neighbor)
                if len(remaining) == 0:
                    return True

            if self._check_consistency(item, path + [neighbor], remaining):
                return True

        return False
