from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import json
import time
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    scores = db.relationship('Score', backref='user', lazy=True)

# Define the Score model
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    time_taken = db.Column(db.Float, nullable=False, default=0.0)
    date_completed = db.Column(db.DateTime, nullable=False, default=datetime.now)
    qualified = db.Column(db.String(3), nullable=False, default='no')  # Change to string

# Load quiz data from JSON file
with open('quiz_data.json', 'r') as f:
    quiz_data = json.load(f)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        # Create a new user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully', 'success')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            # Redirect to the quiz page after successful login
            return redirect(url_for('quiz'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:
        flash('You need to log in first', 'error')
        return redirect(url_for('login'))

    if request.method == 'GET':
        if 'total_attempted_questions' not in session:
            session['total_attempted_questions'] = 0
        if 'correct_answers' not in session:
            session['correct_answers'] = 0

        if session['total_attempted_questions'] >= 60:  # User already attempted 15 questions plus 2 buffer
            flash('You have completed the quiz', 'info')
            return redirect(url_for('index'))

        # Randomly select a question index from the quiz data
        question_indices = list(range(len(quiz_data)))
        if 'current_question' in session:
            current_question_index = session['current_question']
            question_indices.remove(current_question_index)
        question_index = random.choice(question_indices)

        # Store the selected question index in session
        session['current_question'] = question_index

        question = quiz_data[question_index]
        
        # Check if the question includes an image URL
        image_url = question.get('image_url')

        video_url = question.get('video_url')

        
        session['question_start_time'] = time.time()  # Store the start time
        return render_template('quiz.html', question=question, image_url=image_url , video_url=video_url)

    elif request.method == 'POST':
        selected_answer = request.form.get('answer')
        correct_answer = quiz_data[session['current_question']]['answer']
        time_taken = time.time() - session['question_start_time']

        # Update user's score card
        user = User.query.get(session['user_id'])
        score = user.scores[-1] if user.scores else None  # Get the latest score

        # If no score for today or the latest score is from a different day, create a new score
        if not score or score.date_completed.date() != datetime.now().date():
            score = Score(user_id=session['user_id'], username=user.username)  # Pass the username
            db.session.add(score)

        # Update the score or initialize if None
        if score is None:
            score = Score(user_id=session['user_id'], username=user.username)  # Pass the username
        score.correct_answers = (score.correct_answers or 0) + 1 if selected_answer == correct_answer else (score.correct_answers or 0)
        score.total_questions = (score.total_questions or 0) + 1
        score.time_taken = (score.time_taken or 0.0) + time_taken

        # Store user's answer, correctness, and time in the database
        db.session.commit()

        session['total_attempted_questions'] += 1  # Increment total attempted questions

        if session['total_attempted_questions'] == 60:  # After all questions attempted
            total_correct_answers = score.correct_answers  # Retrieve total correct answers from the database

            # Compare with the threshold for qualification
            if total_correct_answers >= 50:  # Adjust the threshold as needed
                score.qualified = 'yes'
            else:
                score.qualified = 'no'

            db.session.commit()  # Commit the qualification status

            if score.qualified == 'yes':
                return redirect(url_for('congrats'))
            else:
                return redirect(url_for('sorry'))

        return redirect(url_for('quiz'))

from flask import Flask, render_template
import sqlite3
import os

@app.route('/admin')
def dashboard():
    # Get the path to the users.db file inside the instance folder
    db_path = os.path.join(app.instance_path, 'users.db')

    # Connect to the database
    conn = sqlite3.connect(db_path)
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



@app.route('/clear_data', methods=['POST'])
def clear_data():
    # Get the path to the users.db file inside the instance folder
    db_path = os.path.join(app.instance_path, 'users.db')

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Delete all data from the 'score' and 'user' tables
    tables = ['score', 'user']
    for table_name in tables:
        cursor.execute("DELETE FROM " + table_name)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Redirect back to the admin dashboard
    flash('All table data has been cleared', 'info')
    return redirect(url_for('dashboard'))




@app.route('/reset', methods=['GET'])
def reset_quiz():
    session.pop('current_question', None)
    session.pop('total_attempted_questions', None)
    session.pop('correct_answers', None)
    session.pop('qualify_for_next_round', None)
    flash('Quiz has been reset', 'info')
    return redirect(url_for('quiz'))

@app.route('/congrats')
def congrats():
    return render_template('congrats.html')

@app.route('/sorry')
def sorry():
    return render_template('sorry.html')


@app.after_request
def after_request(response):
    response.headers['X-Frame-Options'] = 'ALLOW-FROM https://www.youtube.com'
    return response

if __name__ == '__main__':
    app.run(debug=True)
