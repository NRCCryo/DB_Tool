# db_ops/db_operations.py

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from db_ops.models import WIP, Test, Coldhead, Displacer
from logger import logger


class DBOperations:
    def __init__(self, db_session: Session):
        """
        Initialize DBOperations with a SQLAlchemy session.

        :param db_session: SQLAlchemy session object.
        """
        self.db_session = db_session
        logger.info("DBOperations initialized with SQLAlchemy session")

    def insert_record(self, table: str, data: dict):
        """
        Inserts a record into the specified table.

        :param table: Name of the table.
        :param data: Dictionary of data to insert.
        """
        try:
            if table.lower() == "coldheads":
                record = Coldhead(**data)
            elif table.lower() == "displacers":
                record = Displacer(**data)
            elif table.lower() == "wips":
                record = WIP(**data)
            elif table.lower() == "tests":
                record = Test(**data)
            else:
                error_msg = f"Table '{table}' is not recognized."
                logger.error(error_msg)
                raise ValueError(error_msg)

            self.db_session.add(record)
            self.db_session.commit()
            logger.info(f"Insert successful for table '{table}' with data {data}")
        except IntegrityError as ie:
            self.db_session.rollback()
            logger.error(f"Integrity error during insert into table '{table}': {ie}")
            raise
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error during insert into table '{table}': {e}")
            raise

    def update_or_insert(self, table: str, data: dict, unique_keys: list):
        """
        Updates a record if it exists based on unique keys; otherwise, inserts it.

        :param table: Name of the table.
        :param data: Dictionary of data to update or insert.
        :param unique_keys: List of unique keys to determine if the record exists.
        """
        try:
            if table.lower() == "coldheads":
                query = self.db_session.query(Coldhead)
            elif table.lower() == "displacers":
                query = self.db_session.query(Displacer)
            elif table.lower() == "wips":
                query = self.db_session.query(WIP)
            elif table.lower() == "tests":
                query = self.db_session.query(Test)
            else:
                error_msg = f"Table '{table}' is not recognized."
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Build filter based on unique_keys
            filters = [
                getattr(query.column_descriptions[0]["type"], key) == data[key]
                for key in unique_keys
            ]
            record = query.filter(*filters).first()

            if record:
                # Update existing record
                for key, value in data.items():
                    setattr(record, key, value)
                logger.info(f"Record updated in table '{table}' with data {data}")
            else:
                # Insert new record
                self.insert_record(table, data)
                return

            self.db_session.commit()
        except IntegrityError as ie:
            self.db_session.rollback()
            logger.error(f"Integrity error during upsert into table '{table}': {ie}")
            raise
        except Exception as e:
            self.db_session.rollback()
            logger.exception(f"Error during upsert into table '{table}': {e}")
            raise
