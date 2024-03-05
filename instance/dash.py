from flask import Flask, render_template
import sqlite3


@app.route('/admin')
def dashboard():
    # Connect to the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Fetch the data for 'score' and 'user' tables only
    tables = ['score', 'user']
    data = {}

    for table_name in tables:
        # Fetch column names
        cursor.execute("PRAGMA table_info(" + table_name + ")")
        column_names = cursor.fetchall()
        
        # Fetch table data
        cursor.execute("SELECT * FROM " + table_name)
        table_data = cursor.fetchall()
        
        # Store data for the table
        data[table_name] = {'columns': [col[1] for col in column_names], 'data': table_data}

    # Close the connection
    conn.close()

    # Pass the data to the template for rendering
    return render_template('dashboard.html', data=data)

