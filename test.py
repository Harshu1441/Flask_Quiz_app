import sqlite3

# Connect to the database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Fetch table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Print table names
print("Tables:")
for table in tables:
    print(table[0])

# Fetch and print data from each table
for table in tables:
    print("\nData in table:", table[0])
    cursor.execute("SELECT * FROM " + table[0])
    data = cursor.fetchall()
    for row in data:
        print(row)

# Close the connection
conn.close()
