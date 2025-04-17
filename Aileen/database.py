import sqlite3
import os
import streamlit as st

# Database path - stored in a fixed location
DB_PATH = 'wellesley_crave.db'

def init_db():
    """Initialize the SQLite database with necessary tables if they don't exist."""
    # Check if database exists
    db_exists = os.path.exists(DB_PATH)
    
    # Connect to database (will create it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        email TEXT UNIQUE,
        go_to_dining_hall TEXT
    )
    ''')
    
    # Create food journal entries table
    c.execute('''
    CREATE TABLE IF NOT EXISTS food_journal (
        entry_id TEXT PRIMARY KEY,
        user_id TEXT,
        date TEXT,
        meal_type TEXT,
        food_item TEXT,
        dining_hall TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    # Print status for debugging
    if not db_exists:
        print(f"Created new database at {DB_PATH}")
    return db_exists

def add_user(email, username="User"):
    """Add a user to the database if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if user exists
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    
    if not user:
        # Generate a simple user ID
        import uuid
        user_id = str(uuid.uuid4())
        
        # Insert user
        c.execute(
            "INSERT INTO users (user_id, username, email, go_to_dining_hall) VALUES (?, ?, ?, ?)",
            (user_id, username, email, "Tower")
        )
        conn.commit()
        user_id = user_id
    else:
        user_id = user[0]  # First column is user_id
    
    conn.close()
    return user_id

def add_food_entry(user_id, date, meal_type, food_item, dining_hall, notes=""):
    """Add a food entry to the journal."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Generate unique ID for entry
    import uuid
    entry_id = str(uuid.uuid4())
    
    # Insert entry
    c.execute(
        "INSERT INTO food_journal (entry_id, user_id, date, meal_type, food_item, dining_hall, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (entry_id, user_id, date, meal_type, food_item, dining_hall, notes)
    )
    
    conn.commit()
    conn.close()
    return entry_id

def get_food_entries(user_id, date=None):
    """Get food entries for a user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    c = conn.cursor()
    
    if date:
        c.execute("SELECT * FROM food_journal WHERE user_id = ? AND date = ?", (user_id, date))
    else:
        c.execute("SELECT * FROM food_journal WHERE user_id = ?", (user_id,))
    
    rows = c.fetchall()
    
    # Convert rows to dictionaries
    entries = [dict(row) for row in rows]
    
    conn.close()
    return entries