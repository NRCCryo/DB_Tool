import sqlite3
import pandas as pd

def mass_insert_from_excel(db_path, excel_path):
    # Load the Excel file
    df = pd.read_excel(excel_path)

    # Ensure the required columns are present in the DataFrame
    expected_columns = {'Arrival_Date', 'Coldhead_Serial_Number', 'WIP'}
    if not expected_columns.issubset(df.columns):
        raise ValueError(f"Excel file must contain columns: {', '.join(expected_columns)}")

    # Convert the Arrival_Date column to the correct date format
    df['Arrival_Date'] = pd.to_datetime(df['Arrival_Date'], errors='coerce').dt.strftime('%Y-%m-%d')

    # Establish a connection to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        # Insert into Coldheads table if the serial number does not exist
        coldhead_serial_number = row['Coldhead_Serial_Number']
        cursor.execute('''
            INSERT OR IGNORE INTO Coldheads (serial_number)
            VALUES (?)
        ''', (coldhead_serial_number,))

        # Insert into WIPs table
        wip_data = {
            'wip_number': row['WIP'],
            'coldhead_serial_number': coldhead_serial_number,
            'arrival_date': row['Arrival_Date'],
            'teardown_date': None,  # Assuming teardown_date is not provided in Excel
            'status': None  # Assuming status is not provided in Excel
        }
        cursor.execute('''
            INSERT OR REPLACE INTO WIPs (wip_number, coldhead_serial_number, arrival_date, teardown_date, status)
            VALUES (:wip_number, :coldhead_serial_number, :arrival_date, :teardown_date, :status)
        ''', wip_data)

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    print("Data inserted successfully from Excel.")

if __name__ == '__main__':
    db_path = r'C:\Users\JColomba\Desktop\DBToolScratch\TestInsertion2\db_mngt\dbs\New_Database.db'
    excel_path = r'C:\Users\JColomba\Desktop\DBToolScratch\TestInsertion2\db_mngt\dbs\arrival_date.xlsx'  # Update this path to your Excel file location

    # Insert data from the Excel file
    mass_insert_from_excel(db_path, excel_path)
