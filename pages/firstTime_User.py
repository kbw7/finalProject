import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
from home import render_sidebar

render_sidebar()
if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()


DB_PATH = "C:\\Users\\bajpa\\OneDrive\\Desktop\\Wellesley College\\2024-2025\\Spring Semester Classes\\CS 248\\finalProjectPrivate\\wellesley_crave.db"
# ADDING LOCAL PATH TO CONNECT TO PRIVATE REPO DB

def init_db():
    """Initialize the SQLite database with necessary tables"""
    conn = sqlite3.connect(DB_PATH) # adding local path to private repo
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        email TEXT
    )
    ''')

    conn.commit()
    conn.close()

def add_user(email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()

    if not user:
        user_id = str(uuid.uuid4())
        c.execute(
            "INSERT INTO users (user_id, username, email) VALUES (?, ?, ?)",
            (user_id, username, email)
        )
        conn.commit()
    else:
        user_id = user[0]

    conn.close()
    return user_id

init_db()
