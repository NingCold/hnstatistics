import sqlite3
from hnstatistics.core.errors import RepositoryError
from hnstatistics.core.repositories.base_sqlite_repo import BaseSQLiteRepository
from hnstatistics.core.statistics.model import StatisticsModel


class SQLiteStatisticsRepository(BaseSQLiteRepository):
    def __init__(self, conn):
        self.conn = conn

    def get_by_project_id(self, project_id: int) -> StatisticsModel:
        stats = StatisticsModel()
        try:
            cur = self.conn.execute(
                "SELECT key, frequency, probability FROM statistics WHERE project_id = ?;",
                (project_id,)
            )
            for row in cur.fetchall():
                stats.frequency[row["key"]] = row["frequency"]
                stats.probability[row["key"]] = row["probability"]
            stats._recalc()
        except sqlite3.Error as e:
            raise RepositoryError(str(e))
        return stats
    
    def delete_by_project_id(self, project_id: int) -> None:
        try:
            self.conn.execute(
                "DELETE FROM statistics WHERE project_id = ?;",
                (project_id,)
            )
        except sqlite3.Error as e:
            raise RepositoryError(str(e))
    
    def insert(self, project_id: int, stats: StatisticsModel) -> None:
        try:
            for key, freq in stats.frequency.items():
                self.conn.execute(
                    "INSERT INTO statistics (project_id, key, frequency, probability) VALUES (?, ?, ?, ?);",
                    (project_id, key, freq, stats.probability[key])
                )
        except sqlite3.Error as e:
            raise RepositoryError(str(e))
    
    def update(self, project_id: int, stats: StatisticsModel) -> None:
        try:
            self.delete_by_project_id(project_id)
            self.insert(project_id, stats)
        except sqlite3.Error as e:
            raise RepositoryError(str(e))