# Settings page where user enters preferences, allergens, etc. 
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from home import render_sidebar
from notification import init_favorites_table, add_favorite_dish, get_user_favorite_dishes, delete_favorite_dish
from user_profile import get_user_info

init_favorites_table()
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
        #st.write("Debug: Using default_user since email is not in session state")

st.title("Settings ⚙️")

# Use session_state to save go-to dining hall! Aileen's work but Kaurvaki figured out how to access db
# if 'favorite_dining_hall' not in st.session_state:
#     st.session_state.favorite_dining_hall = "Bates"  # Default value

# favDiningHall = st.selectbox("Choose One", ["Tower", "Bae", "Stone D", "Bates"], 
#                            index=["Tower", "Bae", "Stone D", "Bates"].index(st.session_state.favorite_dining_hall))

# # Save selection to session state when changed
# if favDiningHall != st.session_state.favorite_dining_hall:
#     st.session_state.favorite_dining_hall = favDiningHall
#     st.success(f"Default dining hall updated to {favDiningHall}!")

# retrieve current go-to dining hall from sql database and update it if user changes! Kaurvaki's updated code
DB_PATH = "C:\\Users\\bajpa\\OneDrive\\Desktop\\Wellesley College\\2024-2025\\Spring Semester Classes\\CS 248\\finalProjectPrivate\\wellesley_crave.db"
conn = sqlite3.connect(DB_PATH) # adding local path to private repo
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    diningHall TEXT
)
''') # USERNAME is nonexistent right now as we are not working on random-generated usernames currently!

conn.commit()

# Access Logged-In User Email
access_token = st.session_state.get("access_token")
user = get_user_info(access_token)

c.execute("SELECT diningHall FROM users WHERE email = ?", (user.get("email"),))

diningHall = c.fetchone()[0]

st.write("Your current go-to dining hall is set to " + diningHall)

st.write("Update your favorite or go-to dining hall for your Home Page!")
favHall = st.selectbox("Select", ["Tower", "Bates", "Bae", "Stone D"])
st.write("You Selected " + favHall)

choice = st.button("Update")

if choice: 
    c.execute("UPDATE users SET diningHall = ? WHERE email = ?", (favHall, user.get("email"),))
    conn.commit()

conn.close()



# Favorite Dishes Section
st.header("Favorite Dishes")
st.markdown("Add your favorite dishes to get notified when they're available")

# Simple search bar for favorite dishes
favorite_dish = st.text_input("Enter a favorite dish", key="favorite_dish")

# Add button for the dish
if favorite_dish and st.button("Add Favorite"):
    # Try to add the favorite dish
    success = add_favorite_dish(st.session_state['user_id'], favorite_dish)
    if success:
        st.success(f"Added '{favorite_dish}' to your favorites!")
    else:
        st.info(f"'{favorite_dish}' is already in your favorites.")

# Display current favorites
st.subheader("Your Favorite Dishes")

# Check if deletion was requested
if 'delete_favorite' in st.session_state and st.session_state['delete_favorite']:
    delete_favorite_dish(st.session_state['user_id'], st.session_state['delete_favorite'])
    # Clear the delete flag and refresh the page
    st.session_state['delete_favorite'] = None
    st.rerun()

# Get user favorites
favorites = get_user_favorite_dishes(st.session_state['user_id'])

if favorites:
    # Display each favorite with a delete button
    for i, favorite in enumerate(favorites):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(f"• {favorite}")
        with col2:
            if st.button("✕", key=f"delete_{i}"):
                st.session_state['delete_favorite'] = favorite
                st.rerun()
else:
    st.info("You haven't added any favorite dishes yet.")