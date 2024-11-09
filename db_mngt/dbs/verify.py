# db_mngt/dbs/verify.py

from sqlalchemy import create_engine, inspect
import os

# Define the absolute path to the SQLite database based on the current script's location
current_dir = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(current_dir, 'New_Database.db')

# Create the engine pointing to 'New_Database.db'
engine = create_engine(f'sqlite:///{database_path}')

# Create an inspector
inspector = inspect(engine)

# Function to print columns of a given table
def print_table_columns(table_name):
    try:
        columns = inspector.get_columns(table_name)
        print(f"Columns in '{table_name}' table:")
        for column in columns:
            print(f"- {column['name']} ({column['type']})")
    except Exception as e:
        print(f"Error inspecting table '{table_name}': {e}")

if __name__ == "__main__":
    # Check if the 'tests' table exists
    if 'tests' in inspector.get_table_names():
        print_table_columns('tests')
    else:
        print("The 'tests' table does not exist in the database.")
