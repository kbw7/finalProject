import sqlite3
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

# All of Prof. Eni Code from fresh-missing repo
# def get_et_now():
#     """Return current datetime in Eastern Time (America/New_York)."""
#     return datetime.now(tz=ZoneInfo("America/New_York"))

# Define the database schema
# DB_NAME = "wellesley_crave.db"

from db_sync import get_db_path
DB_PATH = get_db_path()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table for individual users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            diningHall TEXT,
            allergens TEXT,
            dietaryRestrictions TEXT
        )
    ''')

    # Table for submission summaries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_journal (
            entry_id TEXT PRIMARY KEY,
            user_id INTEGER AUTO_INCREMENT,
            date TEXT,
            meal_type TEXT,
            food_item TEXT,
            dining_hall TEXT,
            notes TEXT,
            calories FLOAT,
            protein FLOAT,
            carbs FLOAT,
            fat FLOAT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()

def fetch_food_journal():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM food_journal")
    entries = cursor.fetchall()
    conn.close()

    return entries

def fetch_user_info(email: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user_info = cursor.fetchone()
    conn.close()

    return user_info

# def store_missing_data(
#     missing_dish_ids: List[int],
#     date: str,
#     dining_hall: str,
#     meal: str,
#     comment: str,
#     username: str
# ):
#     timestamp = get_et_now().isoformat(timespec="seconds")
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     # Ensure user exists and fetch user_id
#     cursor.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', (username,))
#     cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
#     user_id = cursor.fetchone()[0]

#     # Insert summary record and get its ID
#     cursor.execute('''
#         INSERT INTO missing_summary (timestamp, total_missing, comment, user_id)
#         VALUES (?, ?, ?, ?)
#     ''', (timestamp, len(missing_dish_ids), comment, user_id))
#     summary_id = cursor.lastrowid

#     # Insert missing dish records linked to summary
#     for dish_id in missing_dish_ids:
#         cursor.execute('''
#             INSERT INTO missing_dishes (dish_id, date, dining_hall, meal, user_id, summary_id)
#             VALUES (?, ?, ?, ?, ?, ?)
#         ''', (dish_id, date, dining_hall, meal, user_id, summary_id))

#     conn.commit()
#     conn.close()

def checkNewUser(email:str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM users WHERE email = ?", (email,))

    userInfo = cursor.fetchone()

    return str(type(userInfo)) == "<class 'NoneType'>"



def store_new_user_info(email: str, diningHall: str, allergens: str, dietaryRestrictions: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (email, diningHall, allergens, dietaryRestrictions) VALUES (?, ?, ?, ?)", (email, diningHall, allergens, dietaryRestrictions))

    conn.commit()
    conn.close()


# ------ Food Journal Methods -------
def get_or_create_user(email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT
        )
    ''')
    c.execute("SELECT user_id FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    if result:
        user_id = result[0]
    else:
        c.execute("INSERT INTO users (email) VALUES (?)", (email,))
        conn.commit()
        user_id = c.lastrowid
    conn.close()
    return user_id

def add_food_entry(user_id, date, meal_type, food_item, dining_hall, notes="", calories=0.0, protein=0.0, carbs=0.0, fat=0.0):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    entry_id = str(uuid.uuid4())

    query = '''
    INSERT INTO food_journal 
    (entry_id, user_id, date, meal_type, food_item, dining_hall, notes, calories, protein, carbs, fat) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    c.execute(query, (entry_id, user_id, date, meal_type, food_item, dining_hall, notes, calories, protein, carbs, fat))

    conn.commit()
    conn.close()
    return entry_id

def get_food_entries(user_id, date=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if date:
        c.execute('''
    SELECT entry_id, user_id, date, meal_type, food_item, dining_hall, notes, 
           calories, protein, carbs, fat
    FROM food_journal 
    WHERE user_id = ? AND date = ? 
    ORDER BY meal_type
''', (user_id, date))
    else:
        c.execute('''
    SELECT entry_id, user_id, date, meal_type, food_item, dining_hall, notes, 
           calories, protein, carbs, fat
    FROM food_journal 
    WHERE user_id = ? 
    ORDER BY date DESC, meal_type
''', (user_id,))

    rows = c.fetchall()
    entries = [dict(row) for row in rows]
    conn.close()
    return entries

def delete_food_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM food_journal WHERE entry_id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return True


# Call this once in your main app to initialize the DB (if not already)
if __name__ == "__main__":
    init_db()
    print("Database initialized.")
