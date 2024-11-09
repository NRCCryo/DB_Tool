import sqlite3
import os

# Paths to your databases
OLD_DB_PATH = r"C:\Users\JColomba\Desktop\DBToolScratch\TestInsertion2\db_mngt\dbs\Repair_Tracker.db"
NEW_DB_PATH = r"C:\Users\JColomba\Desktop\DBToolScratch\TestInsertion2\db_mngt\dbs\CH_DB.db"


def create_new_schema(conn_new):
    """
    Creates the new database schema in the new database.
    """
    cursor_new = conn_new.cursor()
    # Enable foreign key constraints
    cursor_new.execute("PRAGMA foreign_keys = ON;")

    # Create coldheads table
    cursor_new.execute("""
    CREATE TABLE IF NOT EXISTS coldheads (
        coldhead_id INTEGER PRIMARY KEY AUTOINCREMENT,
        Coldhead_Serial_Number TEXT NOT NULL,
        Organization TEXT,
        WIP TEXT NOT NULL,
        Arrival_Date DATE,
        Teardown_Date DATE,
        Tech_Notes TEXT,
        Fail_Count INTEGER DEFAULT 0,
        Passed TEXT,
        CE_Notes TEXT,
        Date_Closed DATE,
        Test_ID INTEGER,
        Displacer_Serial_Number TEXT,
        Test_Date DATE,
        Station TEXT,
        Pass_Fail TEXT,
        Mode TEXT,
        Turns INTEGER,
        First_Stage_Heaters REAL,
        Second_Stage_Heater REAL,
        First_Stage_Temp REAL,
        Second_Stage_Temp REAL,
        Efficiency1 REAL,
        Test_Attempt INTEGER,
        Efficiency2 REAL,
        Notes TEXT
    );
    """)

    # Create displacers table
    cursor_new.execute("""
    CREATE TABLE IF NOT EXISTS displacers (
        displacer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        Passed TEXT,
        Total_Fails TEXT,
        Displacer_Serial_Number TEXT NOT NULL,
        WIP_1 TEXT,
        Coldhead_Serial_Number_1 TEXT,
        Initial_Open DATE,
        Installation_Date_1 DATE,
        Test_Date_1 DATE,
        Load_No_Load_1 TEXT,
        First_Stage_Temp_1 REAL,
        Second_Stage_Temp_1 REAL,
        Fail_Count_1 INTEGER DEFAULT 0,
        WIP_2 TEXT,
        Coldhead_Serial_Number_2 TEXT,
        Installation_Date_2 DATE,
        Test_Date_2 DATE,
        Load_No_Load_2 TEXT,
        First_Stage_Temp_2 REAL,
        Second_Stage_Temp_2 REAL,
        Fail_Count_2 INTEGER DEFAULT 0,
        WIP_3 TEXT,
        Coldhead_Serial_Number_3 TEXT,
        Installation_Date_3 DATE,
        Test_Date_3 DATE,
        Load_No_Load_3 TEXT,
        First_Stage_Temp_3 REAL,
        Second_Stage_Temp_3 REAL,
        Fail_Count_3 INTEGER DEFAULT 0,
        Test_ID_1 INTEGER,
        Test_ID_2 INTEGER,
        Test_ID_3 INTEGER,
        notes TEXT
    );
    """)

    # Create wip table
    cursor_new.execute("""
    CREATE TABLE IF NOT EXISTS wip (
        wip_id INTEGER PRIMARY KEY AUTOINCREMENT,
        coldhead_id INTEGER,
        wip_number TEXT NOT NULL UNIQUE,
        FOREIGN KEY (coldhead_id) REFERENCES coldheads(coldhead_id)
    );
    """)

    # Create tests table
    cursor_new.execute("""
    CREATE TABLE IF NOT EXISTS tests (
        test_id INTEGER PRIMARY KEY AUTOINCREMENT,
        WIP TEXT,
        Coldhead_Serial_Number TEXT,
        Displacer_Serial_Number TEXT,
        test_date DATE,
        station TEXT,
        pass_fail TEXT,
        mode TEXT,
        turns INTEGER,
        first_stage_heaters REAL,
        second_stage_heater REAL,
        first_stage_temp REAL,
        second_stage_temp REAL,
        efficiency1 REAL,
        passed TEXT,
        test_attempt INTEGER,
        efficiency2 REAL,
        notes TEXT
    );
    """)

    # Create displacer_coldhead_wip table
    cursor_new.execute("""
    CREATE TABLE IF NOT EXISTS displacer_coldhead_wip (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        displacer_id INTEGER,
        coldhead_id INTEGER,
        wip_id INTEGER,
        installation_date DATE,
        test_date DATE,
        load_no_load_status TEXT,
        first_stage_temp REAL,
        second_stage_temp REAL,
        fail_count INTEGER DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (displacer_id) REFERENCES displacers(displacer_id),
        FOREIGN KEY (coldhead_id) REFERENCES coldheads(coldhead_id),
        FOREIGN KEY (wip_id) REFERENCES wip(wip_id)
    );
    """)

    conn_new.commit()
    print("New schema created successfully.")


def table_exists(cursor, table_name):
    """
    Check if a table exists in the database.
    """
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    return cursor.fetchone() is not None


def migrate_data():
    """
    Migrates data from the old database to the new database.
    """
    # Connect to the old database
    conn_old = sqlite3.connect(OLD_DB_PATH)
    cursor_old = conn_old.cursor()

    # Connect to the new database
    conn_new = sqlite3.connect(NEW_DB_PATH)
    cursor_new = conn_new.cursor()

    # Enable foreign key constraints
    conn_new.execute("PRAGMA foreign_keys = ON;")

    # Step 1: Create the new schema in the new database
    create_new_schema(conn_new)

    # Step 2: Check existence of necessary tables in the old database
    required_tables = ['coldheads', 'displacers', 'tests']
    for table in required_tables:
        if not table_exists(cursor_old, table):
            print(f"Table '{table}' does not exist in the old database. Aborting migration.")
            return

    # Step 3: Migrate coldhead data
    print("Starting migration of coldheads data...")
    cursor_old.execute("SELECT * FROM coldheads")
    coldheads = cursor_old.fetchall()

    if not coldheads:
        print("No data found in 'coldheads' table.")
    else:
        print(f"Migrating {len(coldheads)} rows from 'coldheads' table.")
        columns = [desc[0] for desc in cursor_old.description]  # Get column names
        for row in coldheads:
            try:
                cursor_new.execute(f"""
                    INSERT INTO coldheads ({', '.join(columns)})
                    VALUES ({', '.join(['?' for _ in columns])})
                """, row)
            except sqlite3.Error as e:
                print(f"Error inserting record into 'coldheads': {e}")

    conn_new.commit()
    print("Coldheads data migrated successfully.")

    # Step 4: Migrate displacers data
    print("Starting migration of displacers data...")
    cursor_old.execute("SELECT * FROM displacers")
    displacers = cursor_old.fetchall()

    if not displacers:
        print("No data found in 'displacers' table.")
    else:
        print(f"Migrating {len(displacers)} rows from 'displacers' table.")
        columns = [desc[0] for desc in cursor_old.description]  # Get column names
        for row in displacers:
            try:
                cursor_new.execute(f"""
                    INSERT INTO displacers ({', '.join(columns)})
                    VALUES ({', '.join(['?' for _ in columns])})
                """, row)
            except sqlite3.Error as e:
                print(f"Error inserting record into 'displacers': {e}")

    conn_new.commit()
    print("Displacers data migrated successfully.")

    # Step 5: Migrate tests data
    print("Starting migration of tests data...")
    cursor_old.execute("SELECT * FROM tests")
    tests = cursor_old.fetchall()

    if not tests:
        print("No data found in 'tests' table.")
    else:
        print(f"Migrating {len(tests)} rows from 'tests' table.")
        columns = [desc[0] for desc in cursor_old.description]  # Get column names
        for row in tests:
            try:
                cursor_new.execute(f"""
                    INSERT INTO tests ({', '.join(columns)})
                    VALUES ({', '.join(['?' for _ in columns])})
                """, row)
            except sqlite3.Error as e:
                print(f"Error inserting record into 'tests': {e}")

    conn_new.commit()
    print("Tests data migrated successfully.")

    # Close connections
    conn_old.close()
    conn_new.close()
    print("Data migration completed successfully.")


if __name__ == "__main__":
    if not os.path.exists(OLD_DB_PATH):
        print(f"Old database not found at {OLD_DB_PATH}")
    else:
        # Create new database file or connect if it exists
        if not os.path.exists(NEW_DB_PATH):
            open(NEW_DB_PATH, 'w').close()
        migrate_data()
