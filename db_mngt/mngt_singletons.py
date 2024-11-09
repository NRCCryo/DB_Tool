# db_mngt/mngt_singletons.py

import sqlite3
from threading import Lock
from .column_map import (
    COLDHEADS_TABLE_MAPPING,
    DISPLACERS_TABLE_MAPPING,
    WIPS_TABLE_MAPPING,
    TESTS_TABLE_MAPPING,
)
from db_ops.error_handler import DatabaseError, DuplicateEntryError, EmptyUpdateError  # Import additional exceptions
from logger import logger  # Import the logger


class RepTrackerSing:
    _instance = None
    _lock = Lock()

    def __new__(cls, db_path=None):
        with cls._lock:
            if cls._instance is None:
                if db_path is None:
                    raise ValueError("Database path must be provided for the first initialization")
                cls._instance = super(RepTrackerSing, cls).__new__(cls)
                cls._instance._initialize(db_path)
            return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise ValueError("Singleton not initialized. Please initialize with db_path first.")
        return cls._instance

    def _initialize(self, db_path):
        try:
            self.db_path = db_path
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # To access columns by name
            self.cursor = self.connection.cursor()
            self.table_map = {
                'coldheads': COLDHEADS_TABLE_MAPPING,
                'displacers': DISPLACERS_TABLE_MAPPING,
                'wips': WIPS_TABLE_MAPPING,
                'tests': TESTS_TABLE_MAPPING,
            }
            logger.info(f"Connected to database at: {self.db_path}")

            # Validate column mappings
            for table, mappings in self.table_map.items():
                self.cursor.execute(f"PRAGMA table_info({table});")
                columns = [row['name'] for row in self.cursor.fetchall()]
                logger.debug(f"Columns in table '{table}': {columns}")
                for logical, actual in mappings.items():
                    if actual not in columns:
                        error_msg = f"Mapping error: Column '{actual}' does not exist in table '{table}'"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    logger.debug(f"Mapping '{logical}' to '{actual}' for table '{table}'")
                logger.info(f"All mappings for table '{table}' are valid")
        except sqlite3.Error as e:
            logger.exception(f"Failed to connect to database at {db_path}: {e}")
            raise
        except ValueError as ve:
            logger.exception(ve)
            raise

    def execute_query(self, query, params=None):
        try:
            if params:
                logger.debug(f"Executing query: {query} with params: {params}")
                self.cursor.execute(query, params)
            else:
                logger.debug(f"Executing query: {query} with no params")
                self.cursor.execute(query)
            rows = self.cursor.fetchall()
            logger.debug(f"Query returned {len(rows)} rows")
            return rows
        except sqlite3.Error as e:
            logger.exception(f"SQLite error during execute_query: {e}")
            raise DatabaseError(f"SQLite error during execute_query: {e}") from e

    def execute_insert(self, table, data):
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            logger.debug(f"Executing insert: {query} with data: {tuple(data.values())}")
            self.cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            logger.info(f"Insert successful for table '{table}'")
        except sqlite3.IntegrityError as e:
            logger.exception(f"Integrity error during insert into '{table}': {e}")
            # Attempt to identify the field causing the IntegrityError
            error_message = str(e)
            if "UNIQUE constraint failed" in error_message:
                parts = error_message.split('.')
                if len(parts) > 1:
                    field = parts[1]
                    value = data.get(field, 'Unknown')
                    raise DuplicateEntryError(field=field, value=value) from e
            raise DuplicateEntryError(field='Unknown', value='Unknown') from e  # Fallback
        except sqlite3.Error as e:
            logger.exception(f"SQLite error during execute_insert into '{table}': {e}")
            raise DatabaseError(f"SQLite error during execute_insert into '{table}': {e}") from e

    def execute_update(self, table, data, conditions):
        """
        Executes an update operation on the table.

        :param table: Table name.
        :param data: Dictionary of data to update.
        :param conditions: Dictionary of conditions for WHERE clause.
        """
        if not data:
            logger.warning(f"No data provided for updating table '{table}'. Update operation skipped.")
            raise EmptyUpdateError(table)

        try:
            set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
            where_clause = ' AND '.join([f"{col} = ?" for col in conditions.keys()])
            params = list(data.values()) + list(conditions.values())

            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            logger.debug(f"Executing update: {query} with params: {params}")
            self.cursor.execute(query, params)
            self.connection.commit()
            logger.info(f"Update successful for table '{table}'")
        except sqlite3.IntegrityError as e:
            logger.exception(f"Integrity error during execute_update: {e}")
            raise DatabaseError(f"Integrity error during execute_update: {e}") from e
        except sqlite3.Error as e:
            logger.exception(f"SQLite error during execute_update: {e}")
            raise DatabaseError(f"SQLite error during execute_update: {e}") from e

    def execute_upsert(self, table, data, unique_keys):
        """
        Executes an upsert operation (insert or update) based on unique keys.

        :param table: Table name.
        :param data: Dictionary of data to insert/update.
        :param unique_keys: List of unique keys to determine conflict.
        """
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            update_clause = ', '.join([f"{col}=excluded.{col}" for col in data.keys()])
            conflict_columns = ', '.join(unique_keys)

            query = f"""
            INSERT INTO {table} ({columns})
            VALUES ({placeholders})
            ON CONFLICT({conflict_columns}) DO UPDATE SET {update_clause};
            """
            logger.debug(f"Executing upsert: {query} with data: {tuple(data.values())}")
            self.cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            logger.info(f"Upsert successful for table '{table}'")
        except sqlite3.Error as e:
            logger.exception(f"SQLite error during execute_upsert into '{table}': {e}")
            raise DatabaseError(f"SQLite error during execute_upsert into '{table}': {e}") from e

    def execute_update_no_raise(self, table, data, conditions):
        """
        Executes an update operation on the table without raising exceptions.

        :param table: Table name.
        :param data: Dictionary of data to update.
        :param conditions: Dictionary of conditions for WHERE clause.
        """
        if not data:
            logger.warning(f"No data provided for updating table '{table}'. Update operation skipped.")
            return

        try:
            set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
            where_clause = ' AND '.join([f"{col} = ?" for col in conditions.keys()])
            params = list(data.values()) + list(conditions.values())

            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            logger.debug(f"Executing update: {query} with params: {params}")
            self.cursor.execute(query, params)
            self.connection.commit()
            logger.info(f"Update successful for table '{table}'")
        except sqlite3.Error as e:
            logger.exception(f"SQLite error during execute_update_no_raise: {e}")
            # Do not re-raise to allow silent handling if needed

    def execute_insert_or_ignore(self, table, data):
        """
        Executes an insert operation with OR IGNORE clause.

        :param table: Table name.
        :param data: Dictionary of data to insert.
        """
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})"
            logger.debug(f"Executing insert or ignore: {query} with data: {tuple(data.values())}")
            self.cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            logger.info(f"Insert or ignore successful for table '{table}'")
        except sqlite3.Error as e:
            logger.exception(f"SQLite error during execute_insert_or_ignore into '{table}': {e}")
            raise DatabaseError(f"SQLite error during execute_insert_or_ignore into '{table}': {e}") from e

    def commit(self):
        try:
            self.connection.commit()
            logger.debug("Database commit successful")
        except sqlite3.Error as e:
            logger.exception(f"SQLite commit error: {e}")
            raise DatabaseError(f"SQLite commit error: {e}") from e

    def close_connection(self):
        try:
            self.connection.close()
            logger.info("Database connection closed")
        except sqlite3.Error as e:
            logger.exception(f"SQLite error during close_connection: {e}")
            raise DatabaseError(f"SQLite error during close_connection: {e}") from e

    def map_column(self, logical_column):
        """
        Maps a logical column name to the actual database column name.
        Handles table prefixes and column aliases.
        """
        # Split on ' AS ' to handle aliases
        parts = logical_column.split(' AS ')
        column_with_table = parts[0].strip()  # The actual column name before 'AS'
        alias = parts[1].strip() if len(parts) > 1 else None

        # Initialize actual_column as column_with_table
        actual_column = column_with_table

        # Split table and column
        if '.' in column_with_table:
            table_name, column_name = column_with_table.split('.', 1)
            table_name = table_name.lower()
            mapping = self.table_map.get(table_name, {})
            actual_column_name = mapping.get(column_name, column_name)
            actual_column = f"{table_name}.{actual_column_name}"
        else:
            # If no table name, attempt to map the column across all tables
            column_name = column_with_table
            for tbl_name, tbl_mapping in self.table_map.items():
                if column_name in tbl_mapping:
                    actual_column_name = tbl_mapping[column_name]
                    actual_column = f"{tbl_name}.{actual_column_name}"
                    break
            # If not found, actual_column remains as column_with_table

        # Reconstruct the column with alias if present
        if alias:
            actual_column = f"{actual_column} AS {alias}"

        logger.debug(f"Mapping column '{logical_column}' to '{actual_column}'")
        return actual_column

    def query(self, table, columns='*', conditions=None):
        """
        Basic query method for single-table queries.
        """
        try:
            select_clause = f"SELECT {columns} FROM {table}"
            where_clause = ""
            params = []
            if conditions:
                where_conditions = []
                for key, value in conditions.items():
                    mapped_key = self.map_column(f"{table}.{key}")
                    where_conditions.append(f"{mapped_key} = ?")
                    params.append(value)
                where_clause = " WHERE " + " AND ".join(where_conditions)
            final_query = select_clause + where_clause + ";"
            logger.debug(f"Executing query: {final_query} with params: {params}")
            return self.execute_query(final_query, params)
        except Exception as e:
            logger.exception(f"Error in query method for table '{table}': {e}")
            raise DatabaseError(f"Error in query method for table '{table}': {e}") from e
