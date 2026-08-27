from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    college = db.Column(db.String(100))

    dsa_problems = db.relationship("DSAProblem", backref="user", lazy=True)
    sql_topics = db.relationship("SQLPractice", backref="user", lazy=True)
    companies = db.relationship("Company", backref="user", lazy=True)
    mock_interviews = db.relationship("MockInterview", backref="user", lazy=True)


class DSAProblem(db.Model):
    __tablename__ = "dsa_problems"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    problem_name = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20))
    topic = db.Column(db.String(50))
    platform = db.Column(db.String(50))
    date_solved = db.Column(db.Date)


class SQLPractice(db.Model):
    __tablename__ = "sql_practice"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    topic = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))
    practice_date = db.Column(db.Date)
    status = db.Column(db.String(20))


class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # created_at = db.Column(db.DateTime,default=datetime.utcnow)
    company_name = db.Column(db.String(100))
    status = db.Column(db.String(20))
    notes = db.Column(db.String(500))


class MockInterview(db.Model):
    __tablename__ = "mock_interviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mock_date = db.Column(db.Date)
    score = db.Column(db.Integer)
    feedback = db.Column(db.String(500))


