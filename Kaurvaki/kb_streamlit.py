import streamlit as st
from auth import google_login
from user_profile import render_user_profile
import datetime
import pandas as pd
import requests

st.set_page_config(page_title="Dining App", layout="centered")

DEBUG = False # keep False when testing Google Login
#DEBUG = True # set to True, when you don't want to go through authentication

def fake_login():
    """Sets a fake access token and user info for debugging."""
    st.session_state["access_token"] = "fake-token"
    st.session_state["fake_user_name"] = "Test Student"
    st.session_state["fake_user_picture"] = "https://i.pravatar.cc/60?img=25"  # random placeholder

def render_sidebar():
    """A function to handle the login in the sidebar."""
    st.sidebar.header("Login")

    if DEBUG and "access_token" not in st.session_state:
        fake_login()

    # If already logged in
    if "access_token" in st.session_state:
        render_user_profile()

        if st.sidebar.button("Logout"):
            for key in ["access_token", "oauth_state"]:
                st.session_state.pop(key, None)
            st.rerun()

    else:
        st.sidebar.warning("Not logged in.")
        st.sidebar.write("Please log in with your Google account:")
        logged_in = google_login()
        if logged_in:
            st.rerun()

#===================================================================

# Replace the show_dummy_menu() function with a function that calls the API.
@st.cache_data
def get_weekly_menu(date_str, location_id, meal_id):
    """
    Retrieve the weekly menu for the given date, location, and meal.
    The API returns data for the entire week (Sunday to Saturday) containing the given date.
    """
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

def show_dynamic_menu(menu_data):
    """
    Display the dynamic menu data returned by the API.
    Note from Eni: I'll fix the rest in the next version.
    """
    st.write("### Weekly Menu (Sunday - Saturday)")
    if menu_data:
        # Convert API data to a DataFrame.
        df = pd.DataFrame(menu_data)
        st.dataframe(df)
    else:
        st.write("No data available.")

#================================================================================
# This data can also be in a CSV file and then directly loaded from the file

data = [
    {'location': 'Bae', 'meal': 'Breakfast', 'locationID': 96, 'mealID': 148},
    {'location': 'Bae', 'meal': 'Lunch', 'locationID': 96, 'mealID': 149},
    {'location': 'Bae', 'meal': 'Dinner', 'locationID': 96, 'mealID': 312},
    {'location': 'Bates', 'meal': 'Breakfast', 'locationID': 95, 'mealID': 145},
    {'location': 'Bates', 'meal': 'Lunch', 'locationID': 95, 'mealID': 146},
    {'location': 'Bates', 'meal': 'Dinner', 'locationID': 95, 'mealID': 311},
    {'location': 'Stone', 'meal': 'Breakfast', 'locationID': 131, 'mealID': 261},
    {'location': 'Stone', 'meal': 'Lunch', 'locationID': 131, 'mealID': 262},
    {'location': 'Stone', 'meal': 'Dinner', 'locationID': 131, 'mealID': 263},
    {'location': 'Tower', 'meal': 'Breakfast', 'locationID': 97, 'mealID': 153},
    {'location': 'Tower', 'meal': 'Lunch', 'locationID': 97, 'mealID': 154},
    {'location': 'Tower', 'meal': 'Dinner', 'locationID': 97, 'mealID': 310},
]
# Create a dataframe to make it easy to look up the IDs
dfKeys = pd.DataFrame(data)

# Build a sorted list of unique locations.
locations = sorted({item["location"] for item in data}) # this is a set
meals = sorted({item["meal"] for item in data})

def get_params(df, loc, meal):
    """Return locationID and mealID"""
    matching_df = df[(df["location"] == loc) & (df["meal"] == meal)]
    location_id = matching_df["locationID"].iloc[0]
    meal_id = matching_df["mealID"].iloc[0]
    return location_id, meal_id

#================================================================================
# MAIN PAGE (Updated)

st.title("🍕Catching the missing dish!🍉 ")

# Clear state if user navigates away
if "selected_dining_hall" not in st.session_state:
    st.session_state.selected_dining_hall = None
if "selected_meal" not in st.session_state:
    st.session_state.selected_meal = None


render_sidebar()
if "access_token" not in st.session_state:
    st.stop()

# Show Dining Hall Buttons
st.markdown("### Choose a dining hall:")
cols = st.columns(len(locations))
for i, hall in enumerate(locations):
    if cols[i].button(hall):
        st.session_state.selected_dining_hall = hall
        st.session_state.selected_meal = None  # reset meal on new hall click

# If hall selected, show meal buttons
if st.session_state.selected_dining_hall:
    st.markdown(f"### Choose a meal for: {st.session_state.selected_dining_hall} ")
    meal_cols = st.columns(len(meals))
    for i, meal in enumerate(meals):
        if meal_cols[i].button(meal):
            st.session_state.selected_meal = meal


# If both hall and meal selected, show menu
if st.session_state.selected_meal:
    selected_date = datetime.date.today()  
    # 🔁 Call your own get_menu function here
    st.markdown(f"### Menu for {st.session_state.selected_dining_hall} — {st.session_state.selected_meal}")
    
    # Look up the IDs
    location_id, meal_id = get_params(dfKeys, 
                                      st.session_state.selected_dining_hall, 
                                      st.session_state.selected_meal)
    # Get dynamic menu data via the cached API function.
    menu_data = get_weekly_menu(selected_date, location_id, meal_id)
    
    # Show the dynamically fetched menu.
    show_dynamic_menu(menu_data)