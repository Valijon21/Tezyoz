"""
SQLite connection manager and transaction helper module.
Handles opening/closing connections, Row factory, foreign keys, and safe transaction rollbacks.
"""
import sqlite3
import logging
from contextlib import contextmanager
from pathlib import Path
from app.config import DATABASE_PATH

logger = logging.getLogger("database.connection")

class DatabaseConnection:
    """
    Manages the lifecycle of connections and transactions for the SQLite database.
    """
    def __init__(self, database_path: Path):
        self.database_path = database_path

    @contextmanager
    def get_connection(self):
        """
        Obtains a SQLite connection context.
        Configures the row factory and enables foreign key constraints.
        Closes the connection automatically upon exit.
        """
        conn = None
        try:
            conn = sqlite3.connect(str(self.database_path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
        except sqlite3.Error as err:
            logger.error(f"Database connection error: {err}")
            raise err
        finally:
            if conn:
                conn.close()

    @contextmanager
    def transaction(self):
        """
        Obtains a transactional context.
        Initiates a transaction block and automatically commits on completion,
        or rolls back if an exception occurs.
        """
        conn = None
        try:
            conn = sqlite3.connect(str(self.database_path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("BEGIN TRANSACTION;")
            yield conn
            conn.commit()
        except Exception as err:
            if conn:
                try:
                    conn.rollback()
                except sqlite3.Error as roll_err:
                    logger.error(f"Failed to rollback transaction: {roll_err}")
            logger.error(f"Transaction failed and was rolled back: {err}")
            raise err
        finally:
            if conn:
                conn.close()

# Global connection manager singleton
db = DatabaseConnection(DATABASE_PATH)
