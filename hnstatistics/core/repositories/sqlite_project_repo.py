import sqlite3
from hnstatistics.core.db import get_connection
from hnstatistics.core.errors import DuplicateError, NotFoundError, RepositoryError
from hnstatistics.core.project import Project
from hnstatistics.core.repositories.base_sqlite_repo import BaseSQLiteRepository

class SQLiteProjectRepository(BaseSQLiteRepository):
    def __init__(self, conn):
        self.conn = conn
    
    def get_all(self) -> list[Project]:
        try:
            cur = self.conn.execute(
                "SELECT id, name FROM projects ORDER BY id"
            )
            return [
                Project(name=row["name"], project_id=row["id"])
                for row in cur.fetchall()
            ]
        except sqlite3.Error as e:
            raise RepositoryError(str(e))
    
    def get_by_id(self, project_id: int) -> Project | None:
        try:
            cur = self.conn.execute(
                "SELECT id, name FROM projects WHERE id = ?;",
                (project_id,)
            )
            row = cur.fetchone()
            if not row:
                return None
            return Project(name=row["name"], project_id=row["id"])
        except sqlite3.Error as e:
            raise RepositoryError(str(e))
            
    def insert(self, name: str) -> int:
        try:
            cur = self.conn.execute(
                "INSERT INTO projects (name) VALUES (?);",
                (name,)
            )
            return cur.lastrowid
        except sqlite3.IntegrityError:
            raise DuplicateError(f"Project '{name}' already exists.") 
    
    def rename(self, project_id: int, new_name: str) -> None:
        try:
            cur = self.conn.execute(
                "UPDATE projects SET name = ? WHERE id = ?;",
                (new_name, project_id)
            )
            if cur.rowcount == 0:
                raise NotFoundError(f"Project {project_id} not found.")
        except sqlite3.IntegrityError:
            raise DuplicateError(new_name)
        
    def delete(self, project_id: int) -> None:
        try:
            cur = self.conn.execute(
                "DELETE FROM projects WHERE id = ?;",
                (project_id,)
            )
            if cur.rowcount == 0:
                raise NotFoundError(f"Project {project_id} not found.")
        except sqlite3.Error as e:
            raise RepositoryError(str(e))