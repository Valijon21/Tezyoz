"""
Base database repository module for TypeMaster.
Provides unified query and write execution with transaction support and error logging.
"""
import sqlite3
import logging
from database.connection import db

logger = logging.getLogger("database.repositories.base_repository")

class BaseRepository:
    """
    Abstract Base Repository providing unified query execution, connection lifecycle management,
    transactions, error handling, and simple CRUD helper utilities.
    """
    def __init__(self, table_name: str = None):
        self.table_name = table_name

    def execute_query(self, query: str, params: tuple = (), use_transaction: bool = False) -> list:
        """
        Executes a SELECT query and returns a list of mapped Row dicts.
        """
        try:
            ctx = db.transaction() if use_transaction else db.get_connection()
            with ctx as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows] if rows else []
        except sqlite3.Error as err:
            logger.error(f"SQL query execution failed: {err}\nQuery: {query}\nParams: {params}")
            raise err

    def execute_write(self, query: str, params: tuple = (), use_transaction: bool = True) -> int:
        """
        Executes an INSERT/UPDATE/DELETE query and returns lastrowid or affected row counts.
        """
        try:
            ctx = db.transaction() if use_transaction else db.get_connection()
            with ctx as conn:
                cursor = conn.execute(query, params)
                return cursor.lastrowid
        except sqlite3.Error as err:
            logger.error(f"SQL write execution failed: {err}\nQuery: {query}\nParams: {params}")
            raise err

    def execute_many(self, query: str, params_list: list, use_transaction: bool = True) -> None:
        """
        Executes a query against a sequence of parameters (executemany).
        """
        try:
            ctx = db.transaction() if use_transaction else db.get_connection()
            with ctx as conn:
                conn.executemany(query, params_list)
        except sqlite3.Error as err:
            logger.error(f"SQL executemany failed: {err}\nQuery: {query}")
            raise err

