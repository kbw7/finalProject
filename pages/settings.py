# Settings page where user enters preferences, allergens, etc. 
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from home import render_sidebar
from notification import init_favorites_table, add_favorite_dish, get_user_favorite_dishes
# To make sure it is not accessible unless they log in
render_sidebar()
if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

# Initialize user_id with a default value if not present
if 'user_id' not in st.session_state:
    # Use email if available, otherwise use a default value
    if 'email' in st.session_state:
        st.session_state['user_id'] = st.session_state['email']
    else:
        # Set a default user_id - consider using a timestamp or random string
        st.session_state['user_id'] = "default_user"
        # Debug info
        st.write("Debug: Using default_user since email is not in session state")

st.title("Settings ⚙️")

# Add go-to dining hall preference
st.markdown("Select your **go-to** or **favorite** dining hall (for Home Page Menu)")

# Use session_state to save go-to dining hall!

favDiningHall = st.selectbox("Choose One", ["Tower", "Bae", "Stone D", "Bates"])
st.write("You selected " + favDiningHall)

# Favorite Dishes Section
st.header("Favorite Dishes")
st.markdown("Add your favorite dishes to get notified when they're available")

# Simple search bar for favorite dishes
favorite_dish = st.text_input("Enter a favorite dish", key="favorite_dish")

# Add button for the dish
if favorite_dish and st.button("Add Favorite"):
    # Connect to database
    conn = sqlite3.connect('wellesley_crave.db')
    c = conn.cursor()
    
    # Create table if it doesn't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS user_favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        dish_name TEXT,
        UNIQUE(user_id, dish_name)
    )
    ''')
    
    # Try to add the favorite dish
    try:
        c.execute(
            "INSERT INTO user_favorites (user_id, dish_name) VALUES (?, ?)",
            (st.session_state['user_id'], favorite_dish)
        )
        conn.commit()
        st.success(f"Added '{favorite_dish}' to your favorites!")
    except sqlite3.IntegrityError:
        # Dish already exists as a favorite
        st.info(f"'{favorite_dish}' is already in your favorites.")
    finally:
        conn.close()

# Display current favorites
st.subheader("Your Favorite Dishes")

# Get user favorites from database
conn = sqlite3.connect('wellesley_crave.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute(
    "SELECT dish_name FROM user_favorites WHERE user_id = ?",
    (st.session_state['user_id'],)
)
favorites = [row['dish_name'] for row in c.fetchall()]
conn.close()

if favorites:
    for favorite in favorites:
        st.write(f"• {favorite}")
else:
    st.info("You haven't added any favorite dishes yet.")
