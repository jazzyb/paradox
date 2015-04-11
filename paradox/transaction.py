class TransactionRollback (Exception):
    """Raised by TemporalGraph.rollback() to cancel a transaction."""
    pass


class TransactionError (Exception):
    """Raised to indicate an invalid transaction action."""
    pass


class Transaction (object):
    """Context manager for TemporalGraph transactions.

    Wraps the calls:
        TemporalGraph.start_transaction()
        TemporalGraph.cancel_transaction()
        TemporalGraph.commit_transaction()
    """
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
