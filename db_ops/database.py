# db_ops/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from logger import logger  # Ensure logger is imported

# Define the absolute path to the SQLite database
current_dir = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(current_dir, '..', 'db_mngt', 'dbs', 'New_Database.db')

# Ensure the 'db_mngt/dbs' directory exists
db_directory = os.path.dirname(database_path)
if not os.path.exists(db_directory):
    os.makedirs(db_directory)
    logger.info(f"Created directory for database at {db_directory}")

# Create the engine with the correct path
engine = create_engine(f'sqlite:///{database_path}', echo=True)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)
logger.info("Database engine and sessionmaker configured.")
