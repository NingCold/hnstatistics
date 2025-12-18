import sqlite3

DB_PATH = "hnstatistics.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS statistics (
        project_id INTEGER,
        key TEXT NOT NULL,
        frequency INTEGER NOT NULL,
        probability REAL NOT NULL,
        PRIMARY KEY (project_id, key),
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()