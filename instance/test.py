import sqlite3

def clear_table_data(database_file):
    # Connect to the database
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Fetch table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Clear data from each table
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DELETE FROM {table_name};")
        print(f"All data cleared from table: {table_name}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Specify the path to your SQLite database file
database_file = 'users.db'

# Call the function to clear data from all tables
clear_table_data(database_file)
