import streamlit as st
from datetime import datetime
import os

# Import the database functions
from database import init_db, add_user, add_food_entry, get_food_entries

# Initialize the app
st.title("Food Journal Tester")

# Initialize database
db_existed = init_db()
st.write(f"Database existed before app started: {db_existed}")

# Use a fixed test user ID for simplicity
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = add_user("test@example.com", "Test User")
    st.write(f"Created/retrieved user ID: {st.session_state['user_id']}")

# Simple food journal entry form
with st.form("food_entry_form"):
    st.subheader("Add Food to Journal")
    
    food_item = st.text_input("Food Item")
    meal_type = st.selectbox("Meal", ["Breakfast", "Lunch", "Dinner", "Snack"])
    dining_hall = st.selectbox("Dining Hall", ["Tower", "Bates", "Bae", "Stone D"])
    notes = st.text_area("Notes")
    
    date = datetime.now().strftime("%Y-%m-%d")
    
    submit = st.form_submit_button("Add to Journal")
    
    if submit and food_item:
        entry_id = add_food_entry(
            st.session_state['user_id'],
            date,
            meal_type,
            food_item,
            dining_hall,
            notes
        )
        st.success(f"Added entry: {entry_id}")

# Display entries
st.subheader("Today's Journal Entries")
today = datetime.now().strftime("%Y-%m-%d")
entries = get_food_entries(st.session_state['user_id'], today)

if entries:
    for entry in entries:
        with st.container(border=True):
            st.write(f"**{entry['food_item']}** - {entry['meal_type']}")
            st.write(f"Dining Hall: {entry['dining_hall']}")
            if entry['notes']:
                st.text_area("Notes", value=entry['notes'], disabled=True, height=100)
else:
    st.info("No entries for today")

# Show database path for verification
st.write(f"Database path: {os.path.abspath('wellesley_crave.db')}")