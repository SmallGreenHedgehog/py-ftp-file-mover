import sqlite3
from abc import abstractmethod, ABC

from loguru import logger

import settings

logger.add(f'{settings.LOGS_DIR}/service.log', rotation='50 MB', retention=10, compression='gz')


class SQLDriver(ABC):
    def __init__(self, db_path: str, *args, **kwargs):
        self._db_path = db_path
        self._connection = None
        self._cursor = None

    def send_request(self, sql_query, params: tuple = (), write=False):
        try:
            self._create_connection()
            self._create_cursor()
            response = self._execute_query_and_get_response(
                sql_query=sql_query,
                params=params,
                write=write
            )
        except Exception as e:
            logger.error(f'Error executing query: {e}')
            response = None
        finally:
            self._close_cursor()
            self._close_connection()
        return response

    @abstractmethod
    def _create_connection(self):
        """Abstract method to get a database connection

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def _create_cursor(self):
        """Abstract method to get a database cursor

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def _execute_query_and_get_response(self, sql_query, params, write):
        """Abstract method to execute a query and get a response

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def _close_connection(self):
        """Close the database connection

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def _close_cursor(self):
        """Close the database cursor

        Must be implemented by subclasses.
        """
        pass


class SQLiteDriver(SQLDriver):
    def _create_connection(self):
        self._connection = sqlite3.connect(self._db_path)
        self._connection.row_factory = sqlite3.Row

    def _create_cursor(self):
        if self._connection is None:
            raise RuntimeError('Connection is not established')
        self._cursor = self._connection.cursor()

    def _close_cursor(self):
        if self._cursor is not None:
            self._cursor.close()
            self._cursor = None

    def _close_connection(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _execute_query_and_get_response(self, sql_query, params, write):
        if self._cursor is None:
            raise RuntimeError('Cursor is not created')

        self._cursor.execute(sql_query, params)

        if write:
            self._connection.commit()
            rows = []
            rowcount = self._cursor.rowcount
        else:
            rows = self._cursor.fetchall()
            rowcount = len(rows)

        result = {
            'rows': rows,
            'rowcount': rowcount,
        }
        return result
