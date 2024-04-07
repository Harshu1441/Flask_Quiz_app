import sqlite3


conn = sqlite3.connect('users.db')
cursor = conn.cursor()


cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables:")
for table in tables:
    print(table[0])


for table in tables:
    print("\nData in table:", table[0])
    cursor.execute("SELECT * FROM " + table[0])
    data = cursor.fetchall()
    for row in data:
        print(row)


conn.close()
