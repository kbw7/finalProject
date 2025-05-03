import streamlit as st
import sqlite3
import json
from datetime import datetime
from home import render_sidebar
from notification import get_all_menus_for_week
from user_profile import get_user_info
from db_sync import get_db_path, push_db_to_github

# ----------------- Login & Access Control ----------------- #
render_sidebar()
if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

# do we have user_id in session_State(check!)
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = st.session_state.get('email', 'default_user')

st.title("Settings ⚙️")

DB_PATH = get_db_path()
user_email = st.session_state['user_id'] # check this line!
access_token = st.session_state["access_token"]
user = get_user_info(access_token)

# ----------------- Dining Hall Preference ----------------- #
# call the method get user dinning hall fom update database
with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()
    c.execute("SELECT diningHall FROM users WHERE email = ?", (user.get("email"),))
    result = c.fetchone()
    diningHall = result[0] if result else None

if diningHall:
    st.write(f"Your current go-to dining hall is set to **{diningHall}**")
else:
    st.warning("No dining hall preference set.")

available_halls = ["Tower", "Bates", "Bae", "Stone D"]
default_index = available_halls.index(diningHall) if diningHall in available_halls else 0

favHall = st.selectbox("Select Dining Hall", available_halls, index=default_index)
st.write("You Selected:", favHall)

# move all queries to update database

if st.button("Update"):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE users SET diningHall = ? WHERE email = ?", (favHall, user.get("email")))
        conn.commit()
    push_db_to_github()
    st.success("Dining hall preference updated and synced!")

# ----------------- Favorite Dishes Section ----------------- #
st.header("Favorite Dishes")
st.markdown("Add your favorite dishes to get notified when they're available.")

with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()
    c.execute("SELECT favorites FROM users WHERE email = ?", (user_email,))
    row = c.fetchone()
    favorites = json.loads(row[0]) if row and row[0] else []

all_menu_items = get_all_menus_for_week()
dish_options = sorted({item["name"] for item in all_menu_items if item.get("name")})

selected_dish = st.selectbox("Search and select a favorite dish", options=[""] + list(dish_options))

if selected_dish and st.button("Add Favorite"):
    if selected_dish in favorites:
        st.info(f"'{selected_dish}' is already in your favorites.")
    else:
        favorites.append(selected_dish)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE users SET favorites = ? WHERE email = ?", (json.dumps(favorites), user_email))
            conn.commit()
        push_db_to_github()
        st.success(f"Added '{selected_dish}' to your favorites!")

st.subheader("Your Favorite Dishes")
if 'delete_favorite' in st.session_state and st.session_state['delete_favorite']:
    to_remove = st.session_state['delete_favorite']
    if to_remove in favorites:
        favorites.remove(to_remove)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE users SET favorites = ? WHERE email = ?", (json.dumps(favorites), user_email))
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

# ----------------- Allergy & Dietary Preferences ----------------- #
st.header("Allergy & Dietary Preferences")
aviAllergens = ["Peanut", "Soy", "Dairy", "Egg", "Wheat", "Sesame", "Shellfish", "Fish", "Tree Nut"]
restrictions = ["Vegetarian", "Vegan", "Gluten Sensitive", "Halal", "Kosher", "Lactose-Intolerant"]

with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()
    c.execute("SELECT allergens, dietaryRestrictions FROM users WHERE email = ?", (user_email,))
    row = c.fetchone()
    curr_allergens = json.loads(row[0]) if row and row[0] else []
    curr_restrictions = json.loads(row[1]) if row and row[1] else []

st.subheader("Select Allergies")
new_allergens = [a for a in aviAllergens if st.checkbox(a, value=(a in curr_allergens), key=f"allergen_{a}")]

st.subheader("Select Dietary Restrictions")
new_restrictions = [r for r in restrictions if st.checkbox(r, value=(r in curr_restrictions), key=f"restrict_{r}")]

if st.button("Save Allergy/Restriction Preferences"):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE users SET allergens = ?, dietaryRestrictions = ? WHERE email = ?", 
                     (json.dumps(new_allergens), json.dumps(new_restrictions), user_email))
        conn.commit()
    push_db_to_github()
    st.success("Preferences saved successfully!")
