import sqlite3


def create_database(db_path):
    """Create the database and necessary tables if they don't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Coldheads Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Coldheads (
        coldhead_id INTEGER PRIMARY KEY AUTOINCREMENT,
        serial_number VARCHAR(255) NOT NULL UNIQUE
    );
    ''')

    # Create WIPs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS WIPs (
        wip_number VARCHAR(255) PRIMARY KEY,
        coldhead_serial_number VARCHAR(255) NOT NULL,
        arrival_date DATE,
        teardown_date DATE,
        status VARCHAR(255),
        FOREIGN KEY (coldhead_serial_number) REFERENCES Coldheads(serial_number)
    );
    ''')

    # Create Displacers Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Displacers (
        displacer_serial_number VARCHAR(255) PRIMARY KEY,
        status VARCHAR(255),
        notes TEXT
    );
    ''')

    # Create Tests Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tests (
        test_id INTEGER PRIMARY KEY AUTOINCREMENT,
        wip_number VARCHAR(255) NOT NULL,
        coldhead_serial_number VARCHAR(255) NOT NULL,
        displacer_serial_number VARCHAR(255) NOT NULL,
        test_date DATE NOT NULL,
        test_attempt INTEGER,
        pass_fail VARCHAR(255) NOT NULL,
        temps TEXT,
        notes TEXT,
        FOREIGN KEY (wip_number) REFERENCES WIPs(wip_number),
        FOREIGN KEY (coldhead_serial_number) REFERENCES Coldheads(serial_number),
        FOREIGN KEY (displacer_serial_number) REFERENCES Displacers(displacer_serial_number)
    );
    ''')

    # Create unique index for WIP and Displacer pair in Tests Table
    cursor.execute('''
    CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_test ON Tests(wip_number, displacer_serial_number);
    ''')

    conn.commit()
    conn.close()
    print("Database and tables created successfully.")


def add_column_if_missing(db_path, table_name, column_name, column_type):
    """Adds a column to a table if it doesn't already exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if column already exists in the table
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [row[1] for row in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
        print(f"Column '{column_name}' added to '{table_name}' table.")
    else:
        print(f"Column '{column_name}' already exists in '{table_name}' table.")

    conn.commit()
    conn.close()


def update_tests_table(db_path):
    """Adds missing columns to the Tests table if they are not present."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Columns to add to the Tests table
    columns_to_add = [
        ('mode', 'VARCHAR(255)'),
        ('turns', 'INTEGER'),
        ('first_stage_heaters', 'DECIMAL(10,2)'),
        ('second_stage_heater', 'DECIMAL(10,2)'),
        ('first_stage_temp', 'DECIMAL(10,2)'),
        ('second_stage_temp', 'DECIMAL(10,2)'),
        ('efficiency1', 'DECIMAL(10,2)'),
        ('efficiency2', 'DECIMAL(10,2)')
    ]

    # Check and add each column
    for column_name, column_type in columns_to_add:
        try:
            cursor.execute(f'ALTER TABLE Tests ADD COLUMN {column_name} {column_type};')
        except sqlite3.OperationalError:
            print(f"Column '{column_name}' already exists in 'Tests' table.")

    conn.commit()
    conn.close()


if __name__ == '__main__':
    db_path = r'C:\Users\JColomba\Desktop\DBToolScratch\TestInsertion2\db_mngt\dbs\New_Database.db'

    # Create the database and tables
    create_database(db_path)

    # Add the displacer_serial_number column to the WIPs table if it doesn't exist
    add_column_if_missing(db_path, 'WIPs', 'displacer_serial_number', 'VARCHAR(255)')

    # Add the initial_open_date column to the Displacers table if it doesn't exist
    add_column_if_missing(db_path, 'Displacers', 'initial_open_date', 'DATE')

    # Update the Tests table with additional columns if necessary
    update_tests_table(db_path)

    print("Database created and updated successfully.")
