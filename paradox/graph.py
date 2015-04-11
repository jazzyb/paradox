import collections
import functools
from paradox.state import States, UNKNOWN, EMPTY, OCCUPIED, VISITED
from paradox.transaction import Transaction, TransactionError, \
        TransactionRollback


class Node (collections.defaultdict):
    def __init__(self, ident):
        super(Node, self).__init__(lambda: UNKNOWN)
        self.__dict__['ident'] = ident

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        if name == 'ident':
            raise KeyError('cannot reassign ident')
        if value not in States:
            raise ValueError('value must be a paradox state')
        self[name] = value

    def copy(self):
        """Return a deepcopy of this node."""
        copy = Node(self.ident)
        for k, v in self.iteritems():
            copy[k] = v
        return copy


def transaction_method(func):
    """Function decorator to force TemporalGraph methods to obey transaction
    functionality.

    Wraps a TemporalGraph method.  If the graph has started a transaction,
    then call the method of the transaction instead of the graph.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._transaction:
            return getattr(self._transaction, func.__name__)(*args, **kwargs)
        else:
            return func(self, *args, **kwargs)
    return wrapper


class TemporalGraph (object):
    def __init__(self, start_time, end_time):
        """Initialize an empty TemporalGraph that operates between
        'start_time' and 'end_time' inclusive.
        """
        self._start = start_time
        self._end = end_time
        self._nodes = dict()
        self._edges = dict()
        self._names = set()
        self.current = None
        self._transaction = None

    #@transaction_method # ???
    def copy(self):
        """Return a deepcopy of this graph."""
        copy = TemporalGraph(self._start, self._end)
        copy._nodes = {k: v.copy() for k,v in self._nodes.iteritems()}
        copy._edges = {k: set(v) for k,v in self._edges.iteritems()}
        copy._names = set(self._names)
        copy.current = self.current
        #copy._transaction = self._transaction # ???
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
        """Add a new set of nodes to the graph.

        The node 'name' represents the "spacial" identifier for the node.
        From this a set of "temporal" nodes are created -- one for each "tick"
        between the start and end of the graph time-period.  Each of these
        nodes is given the identifier of '(name, tick)'.  Each node by default
        has as its neighbors the next node and all prior nodes in time.
        """
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
        """Create an edge between sets of temporal nodes.

        'node_name1' and 'node_name2' are spacial node identifiers.
        """
        for t in range(self._start, self._end):
            self._edges[(node_name1, t)].add((node_name2, t + 1))

    @transaction_method
    def node(self, ident, time=None):
        """Return the node for the given identifier."""
        if time is not None:
            ident = (ident, time)
        return self._nodes[ident]

    @transaction_method
    def neighbors(self, ident, time=None):
        """Return all temporal neighbors of the node."""
        if time is not None:
            ident = (ident, time)
        return map((lambda i: self._nodes[i]), self._edges[ident])

    @transaction_method
    def is_consistent(self, item):
        """Return False if there is a temporal paradox in the graph."""
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
        """Return a transaction context manager."""
        return Transaction(self)

    def rollback(self):
        """Cancel a transaction within a with-statement."""
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
