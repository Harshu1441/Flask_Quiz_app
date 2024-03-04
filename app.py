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
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    time_taken = db.Column(db.Float, nullable=False, default=0.0)
    date_completed = db.Column(db.DateTime, nullable=False, default=datetime.now)

# Load quiz data from JSON file
with open('quiz_data.json', 'r') as f:
    quiz_data = json.load(f)

# Define the Threshold model
class Threshold(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    threshold_value = db.Column(db.Integer, nullable=False)

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    if not Threshold.query.first():
        threshold = Threshold(threshold_value=8)  # Threshold for the first round
        db.session.add(threshold)
        db.session.commit()

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
        if 'qualify_for_next_round' not in session:
            session['qualify_for_next_round'] = False

        if session['total_attempted_questions'] >= 17:  # User already attempted 15 questions plus 2 buffer
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

        session['question_start_time'] = time.time()  # Store the start time
        return render_template('quiz.html', question=question, image_url=image_url)

    elif request.method == 'POST':
        selected_answer = request.form.get('answer')
        correct_answer = quiz_data[session['current_question']]['answer']
        time_taken = time.time() - session['question_start_time']

        # Update user's score card
        user = User.query.get(session['user_id'])
        score = user.scores[-1] if user.scores else None  # Get the latest score

        # If no score for today or the latest score is from a different day, create a new score
        if not score or score.date_completed.date() != datetime.now().date():
            score = Score(user_id=session['user_id'])
            db.session.add(score)

        # Update the score or initialize if None
        if score is None:
            score = Score(user_id=session['user_id'])
        score.correct_answers = (score.correct_answers or 0) + 1 if selected_answer == correct_answer else (score.correct_answers or 0)
        score.total_questions = (score.total_questions or 0) + 1
        score.time_taken = (score.time_taken or 0.0) + time_taken

        # Store user's answer, correctness, and time in the database
        db.session.commit()

        session['total_attempted_questions'] += 1  # Increment total attempted questions

        if session['total_attempted_questions'] <= 15:  # Check if it's within the first 15 questions
            if selected_answer == correct_answer:
                session['correct_answers'] += 1

        elif session['total_attempted_questions'] == 17:  # After all questions attempted
            total_correct_answers = user.scores[-1].correct_answers  # Retrieve total correct answers from the database

            # Compare with the threshold for the first round
            if total_correct_answers >= 8:
                session['qualify_for_next_round'] = True

            if session['qualify_for_next_round']:
                return redirect(url_for('congrats'))
            else:
                return redirect(url_for('sorry'))

        return redirect(url_for('quiz'))

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

if __name__ == '__main__':
    app.run(debug=True)