# Settings page where user enters preferences, allergens, etc.
import streamlit as st
import sqlite3
import json
from datetime import datetime
from home import render_sidebar
from notification import add_favorite_dish, get_user_favorite_dishes, delete_favorite_dish, get_all_menus_for_week
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

# --- Fetch user's favorites from users table ---
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
user_email = st.session_state['user_id']

c.execute("SELECT favorites FROM users WHERE email = ?", (user_email,))
row = c.fetchone()
if row and row[0]:
    favorites = json.loads(row[0])
else:
    favorites = []

# --- Suggest dishes from past week's menu ---
all_menu_items = get_all_menus_for_week()
dish_options = sorted({item["name"] for item in all_menu_items if item.get("name")})

selected_dish = st.selectbox("Search and select a favorite dish", options=[""] + list(dish_options))

if selected_dish and st.button("Add Favorite"):
    if selected_dish in favorites:
        st.info(f"'{selected_dish}' is already in your favorites.")
    else:
        favorites.append(selected_dish)
        c.execute("UPDATE users SET favorites = ? WHERE email = ?", (json.dumps(favorites), user_email))
        conn.commit()
        push_db_to_github()
        st.success(f"Added '{selected_dish}' to your favorites!")

# --- Show user's favorite dishes ---
st.subheader("Your Favorite Dishes")

if 'delete_favorite' in st.session_state and st.session_state['delete_favorite']:
    to_remove = st.session_state['delete_favorite']
    if to_remove in favorites:
        favorites.remove(to_remove)
        c.execute("UPDATE users SET favorites = ? WHERE email = ?", (json.dumps(favorites), user_email))
        conn.commit()
        push_db_to_github()
    st.session_state['delete_favorite'] = None
    st.rerun()

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

conn.close()

# -------- Allergens & Restrictions Section -------- #
st.header("Allergy & Dietary Preferences")
aviAllergens = ["Peanut", "Soy", "Dairy", "Egg", "Wheat", "Sesame", "Shellfish", "Fish", "Tree Nut"]
restrictions = ["Vegetarian", "Vegan", "Gluten Sensitive", "Halal", "Kosher", "Lactose-Intolerant"]

# Load current selections from DB
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT allergens, dietaryRestrictions FROM users WHERE email = ?", (user_email,))
row = c.fetchone()
curr_allergens = json.loads(row[0]) if row and row[0] else []
curr_restrictions = json.loads(row[1]) if row and row[1] else []

st.subheader("Select Allergies")
new_allergens = []
for allergen in aviAllergens:
    if st.checkbox(allergen, value=(allergen in curr_allergens), key=f"allergen_{allergen}"):
        new_allergens.append(allergen)

st.subheader("Select Dietary Restrictions")
new_restrictions = []
for restrict in restrictions:
    if st.checkbox(restrict, value=(restrict in curr_restrictions), key=f"restrict_{restrict}"):
        new_restrictions.append(restrict)

if st.button("Save Allergy/Restriction Preferences"):
    c.execute("UPDATE users SET allergens = ?, dietaryRestrictions = ? WHERE email = ?", 
              (json.dumps(new_allergens), json.dumps(new_restrictions), user_email))
    conn.commit()
    push_db_to_github()
    st.success("Preferences saved successfully!")
conn.close()