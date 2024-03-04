from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Fetch table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Fetch and store data from each table along with column names
    data = {}
    for table in tables:
        table_name = table[0]
        cursor.execute("PRAGMA table_info(" + table_name + ")")
        column_names = cursor.fetchall()
        cursor.execute("SELECT * FROM " + table_name)
        table_data = cursor.fetchall()
        data[table_name] = {'columns': [col[1] for col in column_names], 'data': table_data}

    # Close the connection
    conn.close()

    # Pass the data to the template for rendering
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)


    