from collections import defaultdict

class State (object):
    UNKNOWN  = 0
    EMPTY    = 1
    OCCUPIED = 2
    VISITED  = 3
    MAX      = 4


class Node (defaultdict):
    def __init__(self, ident):
        super(Node, self).__init__(lambda: State.UNKNOWN)
        self.__dict__['ident'] = ident

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        if name == 'ident':
            raise KeyError('cannot reassign ident')
        if value not in range(State.MAX):
            raise ValueError('value must be a State')
        self[name] = value


class TemporalGraph (object):
    def __init__(self, start_time, end_time):
        self._start = start_time
        self._end = end_time
        self._nodes = dict()
        self._edges = dict()
        self.current = None

    def set_current_node(self, ident, time=None):
        if time is not None:
            ident = (ident, time)
        if ident not in self._nodes:
            raise KeyError('no such node id')
        self.current = ident

    def create_node(self, name):
        for t in range(self._start, self._end + 1):
            node = Node((name, t))
            self._nodes[node.ident] = node
            neighbors = set(map((lambda x: (name, x)), range(self._start, t)))
            self._edges[node.ident] = neighbors
            if t != self._end:
                self._edges[node.ident].add((name, t + 1))

    def direct_edge(self, node_name1, node_name2):
        for t in range(self._start, self._end):
            self._edges[(node_name1, t)].add((node_name2, t + 1))

    def node(self, ident, time=None):
        if time is not None:
            ident = (ident, time)
        return self._nodes[ident]

    def neighbors(self, ident, time=None):
        if time is not None:
            ident = (ident, time)
        return map((lambda i: self._nodes[i]), self._edges[ident])

    def is_consistent(self, item):
        targets = set(ident for ident, node in self._nodes.iteritems() \
                if node[item] == State.OCCUPIED)
        return self._check_consistency(item, [self.current], targets)

    ### PRIVATE ###

    def _check_consistency(self, item, path, targets):
        """Recursive depth-first search of graph.

        Return True if there exists a path through the graph from the current
        node to all target nodes; return False otherwise.
        """
        for neighbor in self._edges[path[-1]]:
            if neighbor in path:
                continue
            elif self._nodes[neighbor][item] in (State.EMPTY, State.VISITED):
                continue

            remaining = set(targets)
            if neighbor in targets:
                remaining.remove(neighbor)
                if len(remaining) == 0:
                    return True

            if self._check_consistency(item, path + [neighbor], remaining):
                return True

        return False
