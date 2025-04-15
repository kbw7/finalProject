import streamlit as st
import pandas as pd
import sqlite3
import json
import uuid
from datetime import datetime, timedelta
import requests

# Import modules from the provided structure
from auth import google_login
from user_profile import render_user_profile

# Set page configuration
st.set_page_config(page_title="WellesleyCrave", layout="wide")

# Debug flag - keep False when testing Google Login
DEBUG = False  # set to True when you don't want to go through authentication

# -------------------- Database Functions --------------------

def init_db():
    """Initialize the SQLite database with necessary tables if they don't exist."""
    conn = sqlite3.connect('wellesley_crave.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        google_id TEXT UNIQUE,
        username TEXT,
        email TEXT UNIQUE,
        profile_picture TEXT,
        go_to_dining_hall TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create food journal entries table - simplified version
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

# -------------------- User Functions --------------------

def get_or_create_user():
    """Get or create user in the database based on Google login info."""
    if "access_token" not in st.session_state:
        return None
    
    # Get Google user info from session state
    user_info = {}
    if DEBUG:
        # Use fake info for debugging
        user_info = {
            "id": "fake_google_id",
            "name": st.session_state.get("fake_user_name", "Test User"),
            "email": "test@wellesley.edu",
            "picture": st.session_state.get("fake_user_picture", "https://i.pravatar.cc/60?img=25")
        }
    else:
        # In production, this would come from the Google API
        # We'll assume the auth module has put relevant info in session_state
        if "user_email" in st.session_state:
            user_info = {
                "id": st.session_state.get("user_id", ""),
                "name": st.session_state.get("user_name", ""),
                "email": st.session_state.get("user_email", ""),
                "picture": st.session_state.get("user_picture", "")
            }
    
    if not user_info or not user_info.get("email"):
        return None
    
    conn = sqlite3.connect('wellesley_crave.db')
    c = conn.cursor()
    
    # Check if user already exists
    c.execute("SELECT * FROM users WHERE google_id = ? OR email = ?", 
              (user_info.get("id", ""), user_info.get("email", "")))
    user_data = c.fetchone()
    
    if user_data:
        # Get column names
        column_names = [description[0] for description in c.description]
        user_dict = dict(zip(column_names, user_data))
        conn.close()
        return user_dict
    else:
        # Create new user
        user_id = str(uuid.uuid4())
        c.execute(
            "INSERT INTO users (user_id, google_id, username, email, profile_picture, go_to_dining_hall) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, user_info.get("id", ""), user_info.get("name", ""), 
             user_info.get("email", ""), user_info.get("picture", ""),
             "Tower")  # Default dining hall
        )
        conn.commit()
        
        # Get the newly created user
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_data = c.fetchone()
        column_names = [description[0] for description in c.description]
        user_dict = dict(zip(column_names, user_data))
        
        conn.close()
        return user_dict

# -------------------- Food Journal Functions --------------------

def add_food_entry(user_id, date, meal_type, food_item, dining_hall, notes=""):
    """Add a food entry to the journal."""
    conn = sqlite3.connect('wellesley_crave.db')
    c = conn.cursor()
    
    entry_id = str(uuid.uuid4())
    
    c.execute(
        "INSERT INTO food_journal (entry_id, user_id, date, meal_type, food_item, dining_hall, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (entry_id, user_id, date, meal_type, food_item, dining_hall, notes)
    )
    
    conn.commit()
    conn.close()
    return entry_id

def get_food_entries(user_id, start_date=None, end_date=None):
    """Get food entries for a user within a date range."""
    conn = sqlite3.connect('wellesley_crave.db')
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    c = conn.cursor()
    
    query = "SELECT * FROM food_journal WHERE user_id = ?"
    params = [user_id]
    
    if start_date and end_date:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    
    c.execute(query, params)
    rows = c.fetchall()
    
    # Convert rows to dictionaries
    entries = [dict(row) for row in rows]
    
    conn.close()
    return entries

def delete_food_entry(entry_id):
    """Delete a food entry."""
    conn = sqlite3.connect('wellesley_crave.db')
    c = conn.cursor()
    
    c.execute("DELETE FROM food_journal WHERE entry_id = ?", (entry_id,))
    
    conn.commit()
    conn.close()
    return c.rowcount > 0  # Return True if any rows were deleted

# -------------------- Menu API Functions --------------------

def fake_login():
    """Sets a fake access token and user info for debugging."""
    st.session_state["access_token"] = "fake-token"
    st.session_state["fake_user_name"] = "Test Student"
    st.session_state["fake_user_picture"] = "https://i.pravatar.cc/60?img=25"  # random placeholder
    st.session_state["user_email"] = "test@wellesley.edu"

# Dining hall data
dining_data = [
    {'location': 'Bae', 'meal': 'Breakfast', 'locationID': 96, 'mealID': 148},
    {'location': 'Bae', 'meal': 'Lunch', 'locationID': 96, 'mealID': 149},
    {'location': 'Bae', 'meal': 'Dinner', 'locationID': 96, 'mealID': 312},
    {'location': 'Bates', 'meal': 'Breakfast', 'locationID': 95, 'mealID': 145},
    {'location': 'Bates', 'meal': 'Lunch', 'locationID': 95, 'mealID': 146},
    {'location': 'Bates', 'meal': 'Dinner', 'locationID': 95, 'mealID': 311},
    {'location': 'Stone D', 'meal': 'Breakfast', 'locationID': 131, 'mealID': 261},
    {'location': 'Stone D', 'meal': 'Lunch', 'locationID': 131, 'mealID': 262},
    {'location': 'Stone D', 'meal': 'Dinner', 'locationID': 131, 'mealID': 263},
    {'location': 'Tower', 'meal': 'Breakfast', 'locationID': 97, 'mealID': 153},
    {'location': 'Tower', 'meal': 'Lunch', 'locationID': 97, 'mealID': 154},
    {'location': 'Tower', 'meal': 'Dinner', 'locationID': 97, 'mealID': 310},
]

# Create a dataframe to make it easy to look up the IDs
df_keys = pd.DataFrame(dining_data)

# Build a sorted list of unique locations and meals
locations = sorted(df_keys['location'].unique())
meals = sorted(df_keys['meal'].unique())

@st.cache_data
def get_weekly_menu(date_str, location_id, meal_id):
    """Retrieve the weekly menu for the given date, location, and meal."""
    base_url = "https://dish.avifoodsystems.com/api/menu-items/week"
    params = {
        "date": date_str,
        "locationId": location_id,
        "mealId": meal_id,
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()  
    else:
        st.error("Failed to retrieve data. Status code: " + str(response.status_code))
        return None

# -------------------- UI Components --------------------

def render_sidebar():
    """Handle the login in the sidebar."""
    st.sidebar.header("WellesleyCrave")
    
    if DEBUG and "access_token" not in st.session_state:
        fake_login()
    
    # If already logged in
    if "access_token" in st.session_state:
        render_user_profile()
        
        # Navigation
        st.sidebar.subheader("Navigation")
        
        # Default page is Home if not set
        if "page" not in st.session_state:
            st.session_state["page"] = "Home"
            
        # Navigation buttons
        if st.sidebar.button("🏠 Home", use_container_width=True):
            st.session_state["page"] = "Home"
            st.rerun()
            
        if st.sidebar.button("🍽️ Menu", use_container_width=True):
            st.session_state["page"] = "Menu"
            st.rerun()
            
        if st.sidebar.button("📝 Food Journal", use_container_width=True):
            st.session_state["page"] = "Food Journal"
            st.rerun()
        
        # Logout button at bottom
        st.sidebar.markdown("---")
        if st.sidebar.button("Logout", type="primary", use_container_width=True):
            for key in ["access_token", "oauth_state"]:
                st.session_state.pop(key, None)
            st.rerun()
            
    else:
        st.sidebar.warning("Not logged in.")
        st.sidebar.write("Please log in with your Google account:")
        logged_in = google_login()
        if logged_in:
            st.rerun()

def menu_page(user):
    """Display the menu page."""
    st.title("Wellesley Fresh Menu")
    
    # Menu search form
    with st.form("menu_search_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            user_date = st.date_input("Select a Date", datetime.now().date())
            formatted_date = user_date.strftime("%m/%d/%Y")
        
        with col2:
            user_location = st.selectbox("Select location", locations)
        
        with col3:
            user_meal = st.selectbox("Select meal", meals)
        
        submit_button = st.form_submit_button("View Menu", type="primary", use_container_width=True)
    
    # Display menu if user submits form
    if submit_button:
        row = df_keys[(df_keys['location'] == user_location) & (df_keys['meal'] == user_meal)]
        
        if not row.empty:
            location_id = row.iloc[0]['locationID']
            meal_id = row.iloc[0]['mealID']
            
            with st.spinner("Loading menu..."):
                menu_data = get_weekly_menu(formatted_date, location_id, meal_id)
                
                if menu_data:
                    # Convert to dataframe for display
                    df = pd.DataFrame(menu_data)
                    
                    st.subheader(f"{user_location} - {user_meal} - {user_date.strftime('%A, %B %d, %Y')}")
                    
                    # Display menu items with option to add to food journal
                    for i, row in df.iterrows():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"• {row['name']}")
                        
                        with col2:
                            if st.button("+ Add to Journal", key=f"add_menu_{i}"):
                                # Add to food journal entry form
                                st.session_state['add_food_item'] = {
                                    'food_item': row['name'],
                                    'dining_hall': user_location,
                                    'meal_type': user_meal,
                                    'date': user_date.strftime("%Y-%m-%d")
                                }
                                st.session_state['page'] = "Food Journal"
                                st.rerun()
                else:
                    st.warning("No menu items found for the selected date, location, and meal.")

def food_journal_page(user):
    """Display the food journal page."""
    st.title("Food Journal")
    
    # Date selection for viewing entries
    col1, col2 = st.columns([1, 3])
    with col1:
        date = st.date_input("Select date", datetime.now().date())
    
    with col2:
        # Quick date navigation
        date_range = st.radio(
            "Date range",
            ["Today", "Yesterday", "This Week", "This Month", "Custom"],
            horizontal=True
        )
        
        today = datetime.now().date()
        if date_range == "Today":
            selected_date = today
            start_date = today
            end_date = today
        elif date_range == "Yesterday":
            selected_date = today - timedelta(days=1)
            start_date = selected_date
            end_date = selected_date
        elif date_range == "This Week":
            start_date = today - timedelta(days=today.weekday())
            end_date = today
            selected_date = today
        elif date_range == "This Month":
            start_date = today.replace(day=1)
            end_date = today
            selected_date = today
        else:  # Custom
            start_date = st.date_input("Start date", today - timedelta(days=7), key="custom_start")
            end_date = st.date_input("End date", today, key="custom_end")
            selected_date = date
    
    # Convert dates to strings for SQLite
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    selected_date_str = selected_date.strftime("%Y-%m-%d")
    
    # Add new food entry form
    with st.expander("Add New Food Entry", expanded=True):
        with st.form("add_food_form"):
            st.subheader("Add Food to Journal")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pre-fill fields if coming from menu page
                if 'add_food_item' in st.session_state:
                    food_item = st.text_input(
                        "Food Item", 
                        value=st.session_state['add_food_item'].get('food_item', '')
                    )
                    meal_type = st.selectbox(
                        "Meal", 
                        meals,
                        index=meals.index(st.session_state['add_food_item'].get('meal_type', 'Lunch')) 
                        if st.session_state['add_food_item'].get('meal_type') in meals else 0
                    )
                else:
                    food_item = st.text_input("Food Item")
                    meal_type = st.selectbox("Meal", meals)
            
            with col2:
                if 'add_food_item' in st.session_state:
                    dining_hall = st.selectbox(
                        "Dining Hall", 
                        locations,
                        index=locations.index(st.session_state['add_food_item'].get('dining_hall', 'Tower'))
                        if st.session_state['add_food_item'].get('dining_hall') in locations else 0
                    )
                    entry_date = st.date_input(
                        "Date", 
                        datetime.strptime(st.session_state['add_food_item'].get('date', selected_date_str), "%Y-%m-%d")
                    )
                else:
                    dining_hall = st.selectbox("Dining Hall", locations)
                    entry_date = st.date_input("Date", selected_date)
            
            # Journal notes - free text area for reflections
            notes = st.text_area(
                "Journal Notes", 
                help="Write anything you'd like about this meal - how it tasted, how you felt, who you were with, etc."
            )
            
            submit = st.form_submit_button("Add to Journal")
            
            if submit:
                if food_item:
                    entry_date_str = entry_date.strftime("%Y-%m-%d")
                    entry_id = add_food_entry(
                        user['user_id'],
                        entry_date_str,
                        meal_type,
                        food_item,
                        dining_hall,
                        notes
                    )
                    
                    if entry_id:
                        st.success("Food added to journal!")
                        # Clear the session state
                        if 'add_food_item' in st.session_state:
                            del st.session_state['add_food_item']
                        st.rerun()  # Refresh to show the new entry
                else:
                    st.error("Please enter a food item name")
    
    # Display the current day's entries
    st.subheader(f"Journal Entries for {selected_date_str}")
    
    # Get food entries
    entries = get_food_entries(user['user_id'], start_date_str, end_date_str)
    
    # Filter entries for selected date
    daily_entries = [entry for entry in entries if entry['date'] == selected_date_str]
    
    if daily_entries:
        meal_tabs = ["Breakfast", "Lunch", "Dinner", "Snack"]
        tabs = st.tabs(meal_tabs)
        
        for i, meal in enumerate(meal_tabs):
            with tabs[i]:
                meal_entries = [entry for entry in daily_entries if entry['meal_type'] == meal]
                if meal_entries:
                    for entry in meal_entries:
                        with st.container(border=True):
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.write(f"**{entry['food_item']}**")
                                st.write(f"Dining Hall: {entry['dining_hall']}")
                                if entry['notes']:
                                    st.text_area("Notes", value=entry['notes'], disabled=True, height=100)
                            
                            # Delete button
                            with col2:
                                if st.button("Delete", key=f"delete_{entry['entry_id']}"):
                                    if delete_food_entry(entry['entry_id']):
                                        st.success("Entry deleted!")
                                        st.rerun()
                else:
                    st.info(f"No {meal.lower()} entries for this date")
    else:
        st.info("No entries for this date")

def home_page(user):
    """Display the home page."""
    st.title("WellesleyCrave Dashboard")
    
    # Get user info
    username = user.get('username', 'User')
    go_to_dining_hall = user.get('go_to_dining_hall', 'Tower')
    
    # Greeting based on time of day
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    st.header(f"{greeting}, {username}!")
    
    # Quick access to features
    st.subheader("What would you like to do today?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🍽️ View Today's Menu", use_container_width=True):
            st.session_state['page'] = "Menu"
            st.rerun()
    
    with col2:
        if st.button("📝 Open Food Journal", use_container_width=True):
            st.session_state['page'] = "Food Journal"
            st.rerun()
    
    # Tip of the day
    tips = [
        "Try to eat a variety of colorful fruits and vegetables each day!",
        "Staying hydrated helps your body function at its best - remember to drink water throughout the day.",
        "Mindful eating can help you enjoy your food more and may prevent overeating.",
        "Including protein with each meal can help you feel fuller longer.",
        "Found a new favorite dish at the dining hall? Record it in your food journal so you don't forget!"
    ]
    import random
    st.info(f"💡 **Tip of the day**: {random.choice(tips)}")

# -------------------- Main Application --------------------

def main():
    # Initialize database
    init_db()
    
    # Render sidebar with navigation
    render_sidebar()
    
    # Check if user is logged in
    if "access_token" not in st.session_state:
        st.title("Welcome to WellesleyCrave")
        st.write("Please log in using the sidebar to access the app.")
        st.stop()
    
    # Get or create user in database
    user = get_or_create_user()
    if not user:
        st.error("Failed to get user information. Please try logging in again.")
        st.stop()
    
    # Navigate to the selected page
    page = st.session_state.get("page", "Home")
    
    if page == "Home":
        home_page(user)
    elif page == "Menu":
        menu_page(user)
    elif page == "Food Journal":
        food_journal_page(user)

if __name__ == "__main__":
    main()