import sqlite3

# Replace 'your_database.db' with your database file name
db_path = 'CH_DB.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Get all table names in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if tables:
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * (len(table_name) + 7))
            
            # Get column information for each table
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Print the column details
            if columns:
                print("Column Details:")
                print("cid | name       | type       | notnull | dflt_value | pk")
                print("-" * 58)
                for column in columns:
                    print(" | ".join(str(x) if x is not None else "NULL" for x in column))
            else:
                print("No columns found.")
    else:
        print("No tables found in the database.")

finally:
    # Close the connection
    conn.close()
