from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Replace with your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Change this to a secure random key
db = SQLAlchemy(app)

# Define the Threshold model
class Threshold(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    threshold_value = db.Column(db.Integer, nullable=False, default=8)
    threshold_value_round2 = db.Column(db.Integer, nullable=False, default=11)
    threshold_value_final_round = db.Column(db.Integer, nullable=False, default=13)

# Check if the columns exist in the threshold table and add them if they don't
with app.app_context():
    db.create_all()
    table = Threshold.__table__
    if not 'threshold_value_round2' in table.columns:
        try:
            db.session.execute(text('ALTER TABLE threshold ADD COLUMN threshold_value_round2 INTEGER DEFAULT 11'))
            db.session.commit()
            print("Column 'threshold_value_round2' added successfully!")
        except Exception as e:
            print("Error adding column 'threshold_value_round2':", e)
            db.session.rollback()

    if not 'threshold_value_final_round' in table.columns:
        try:
            db.session.execute(text('ALTER TABLE threshold ADD COLUMN threshold_value_final_round INTEGER DEFAULT 13'))
            db.session.commit()
            print("Column 'threshold_value_final_round' added successfully!")
        except Exception as e:
            print("Error adding column 'threshold_value_final_round':", e)
            db.session.rollback()

if __name__ == '__main__':
    app.run(debug=True)
