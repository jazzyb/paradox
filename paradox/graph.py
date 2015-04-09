class State (object):
    UNKNOWN  = 0
    EMPTY    = 1
    OCCUPIED = 2
    VISITED  = 3
    MAX      = 4


class Node (dict):
    def __init__(self, ident):
        super(Node, self).__init__()
        self.__dict__['ident'] = ident

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return State.UNKNOWN

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

    def is_consistent(self, obj):
        pass

    ### PRIVATE ###
