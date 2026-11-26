"""Database layer: SQLite connection handling and table creation."""
import os
import sqlite3

# Path of the SQLite file. Can be overridden with the TASK_DB_PATH
# environment variable (the tests point it to a temporary file).
DB_PATH = os.getenv("TASK_DB_PATH", "tasks.db")


def init_db() -> None:
    """Create the tasks table if it does not exist yet."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            description TEXT,
            due_date    TEXT,
            status      TEXT NOT NULL DEFAULT 'todo',
            priority    TEXT NOT NULL DEFAULT 'medium',
            created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def get_db():
    """FastAPI dependency: open a connection per request, close it after."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # lets us read rows like dictionaries
    try:
        yield conn
    finally:
        conn.close()
