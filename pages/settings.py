import streamlit as st
from home import render_sidebar
from notification import get_all_menus_for_week
from user_profile import get_user_info
from db_sync import push_db_to_github
from update_database import (
    getUserFavDiningHall,
    update_user_dining_hall,
    get_user_favorites,
    add_favorite_dish,
    remove_favorite_dish,
    get_user_allergens_and_restrictions,
    update_user_allergy_preferences,
)

# ----------------- Login & Access Control ----------------- #
render_sidebar()
if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

st.title("Settings ⚙️")

access_token = st.session_state["access_token"]
user = get_user_info(access_token)

if user and 'email' in user:
    user_email = user['email']
    st.write("DEBUG - Using actual email:", user_email)
else:
    st.error("Could not retrieve user email from profile!")
    st.stop()

# ----------------- Dining Hall Preference ----------------- #
diningHall = getUserFavDiningHall(user)

if diningHall:
    st.write(f"Your current go-to dining hall is set to **{diningHall}**")
else:
    st.warning("No dining hall preference set.")

available_halls = ["Tower", "Bates", "Bae", "Stone D"]
default_index = available_halls.index(diningHall) if diningHall in available_halls else 0

favHall = st.selectbox("Select Dining Hall", available_halls, index=default_index)
st.write("You Selected:", favHall)

if st.button("Update"):
    update_user_dining_hall(user.get("email"), favHall)
    push_db_to_github()
    st.success("Dining hall preference updated and synced!")

# ----------------- Favorite Dishes Section ----------------- #
st.header("Favorite Dishes")
st.markdown("Add your favorite dishes to get notified when they're available.")

favorites = get_user_favorites(user_email)
all_menu_items = get_all_menus_for_week()
dish_options = sorted({item["name"] for item in all_menu_items if item.get("name")})

selected_dish = st.selectbox("Search and select a favorite dish", options=[""] + list(dish_options))

if selected_dish and st.button("Add Favorite"):
    if selected_dish in favorites:
        st.info(f"'{selected_dish}' is already in your favorites.")
    else:
        add_favorite_dish(user_email, selected_dish)
        push_db_to_github()
        st.success(f"Added '{selected_dish}' to your favorites!")

st.subheader("Your Favorite Dishes")

if 'delete_favorite' in st.session_state and st.session_state['delete_favorite']:
    to_remove = st.session_state['delete_favorite']
    remove_favorite_dish(user_email, to_remove)
    push_db_to_github()
    st.session_state['delete_favorite'] = None
    st.rerun()

favorites = get_user_favorites(user_email)
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

curr_allergens, curr_restrictions = get_user_allergens_and_restrictions(user_email)

st.subheader("Select Allergies")
new_allergens = [a for a in aviAllergens if st.checkbox(a, value=(a in curr_allergens), key=f"allergen_{a}")]

st.subheader("Select Dietary Restrictions")
new_restrictions = [r for r in restrictions if st.checkbox(r, value=(r in curr_restrictions), key=f"restrict_{r}")]

if st.button("Save Allergy/Restriction Preferences"):
    allergensUpdate = update_user_allergy_preferences(user_email, new_allergens, new_restrictions)
    push_db_to_github()
    st.success("Preferences saved successfully!")
