import sqlite3
from collections.abc import Generator
from pathlib import Path

from app.core.config import settings


def get_database_path() -> Path:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings.database_path


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(get_database_path(), check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                summary TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                detected_context TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                total_faces INTEGER NOT NULL,
                total_objects INTEGER NOT NULL,
                average_confidence REAL,
                output_path TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
