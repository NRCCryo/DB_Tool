# db_ops/new_db.py

from database import engine, Base
from logger import logger

def initialize_database():
    """
    Initialize the database by dropping existing tables and creating new ones based on models.
    """
    try:
        logger.info("Dropping all tables...")
        Base.metadata.drop_all(engine)
        logger.info("All tables dropped successfully.")

        logger.info("Creating all tables based on models...")
        Base.metadata.create_all(engine)
        logger.info("All tables created successfully.")
    except Exception as e:
        logger.exception(f"Failed to initialize database: {e}")
        raise

if __name__ == "__main__":
    initialize_database()
