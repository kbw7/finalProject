# Settings page where user enters preferences, allergens, etc. 
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from home import render_sidebar
from notification import init_favorites_table, add_favorite_dish, get_user_favorite_dishes, delete_favorite_dish

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