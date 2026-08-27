import os

class Config:
    SECRET_KEY = "interviewtracker_secret_key_2026"
    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc://localhost\\SQLEXPRESS/InterviewTracker_Web"
        "?driver=ODBC+Driver+17+for+SQL+Server"
        "&trusted_connection=yes"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False