from hnstatistics.core.db import get_connection
from hnstatistics.core.repositories.sqlite_project_repo import SQLiteProjectRepository
from hnstatistics.core.repositories.statistics_repo import SQLiteStatisticsRepository

class UnitOfWork:
    def __enter__(self):
        self.conn = get_connection()

        self.projects = SQLiteProjectRepository(self.conn)
        self.statistics = SQLiteStatisticsRepository(self.conn)
        
        self.conn.execute("BEGIN;")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            self.conn.close()
        return False

    def commit(self):
        self.conn.commit()