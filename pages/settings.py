# Settings page where user enters preferences, allergens, etc.
import streamlit as st
import sqlite3
from datetime import datetime
from home import render_sidebar
from notification import add_favorite_dish, get_user_favorite_dishes, delete_favorite_dish
from user_profile import get_user_info
from db_sync import get_db_path, push_db_to_github

# ----------------- Login & Access Control ----------------- #
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
        # st.write("Debug: Using default_user since email is not in session state")

st.title("Settings ⚙️")

# ----------------- Database Connection ----------------- #
# Access the shared synced database path
DB_PATH = get_db_path()
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# ----------------- Dining Hall Preference Section ----------------- #
# Access Logged-In User Email
access_token = st.session_state.get("access_token")
user = get_user_info(access_token)

# Retrieve current go-to dining hall from the users table
c.execute("SELECT diningHall FROM users WHERE email = ?", (user.get("email"),))
result = c.fetchone()

if result:
    diningHall = result[0]
    st.write(f"Your current go-to dining hall is set to **{diningHall}**")
else:
    diningHall = None
    st.warning("No dining hall preference set.")

# Let user select a new dining hall preference
st.write("Update your favorite or go-to dining hall for your Home Page!")

available_halls = ["Tower", "Bates", "Bae", "Stone D"]

# Default to previously selected dining hall, or fallback to first option
default_index = available_halls.index(diningHall) if diningHall in available_halls else 0

favHall = st.selectbox("Select Dining Hall", available_halls, index=default_index)
st.write("You Selected:", favHall)

# If user clicks update, push changes to database and GitHub
if st.button("Update"):
    c.execute("UPDATE users SET diningHall = ? WHERE email = ?", (favHall, user.get("email"),))
    conn.commit()
    push_db_to_github()
    st.success("Dining hall preference updated and synced!")

conn.close()

# ----------------- Favorite Dishes Section ----------------- #
st.header("Favorite Dishes")
st.markdown("Add your favorite dishes to get notified when they're available.")

# Input for adding a new favorite dish
favorite_dish = st.text_input("Enter a favorite dish", key="favorite_dish")

# Add dish to database when user clicks button
if favorite_dish and st.button("Add Favorite"):
    success = add_favorite_dish(st.session_state['user_id'], favorite_dish)
    if success:
        st.success(f"Added '{favorite_dish}' to your favorites!")
    else:
        st.info(f"'{favorite_dish}' is already in your favorites.")

# Display section title
st.subheader("Your Favorite Dishes")

# Handle dish deletion if requested
if 'delete_favorite' in st.session_state and st.session_state['delete_favorite']:
    delete_favorite_dish(st.session_state['user_id'], st.session_state['delete_favorite'])
    # Clear the delete flag and rerun the app
    st.session_state['delete_favorite'] = None
    st.rerun()

# Get current favorite dishes
favorites = get_user_favorite_dishes(st.session_state['user_id'])

# Display all favorites with delete buttons
if favorites:
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
