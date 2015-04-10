class TransactionRollback (Exception):
    pass


class TransactionError (Exception):
    pass


class Transaction (object):
    def __init__(self, graph):
        self.graph = graph

    def __enter__(self):
        self.graph.start_transaction()
        return self.graph

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type == TransactionRollback:
            self.graph.cancel_transaction()
            return True
        self.graph.commit_transaction()
