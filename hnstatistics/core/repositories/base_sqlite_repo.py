import sqlite3
from contextlib import contextmanager
from hnstatistics.core.errors import (
    DatabaseConnectionError,
    TransactionError
)

class BaseSQLiteRepository:
    def __init__(self, db_path: str):
        try:
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise DatabaseConnectionError(str(e))

    @contextmanager
    def transaction(self):
        try:
            yield
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise TransactionError(str(e))
