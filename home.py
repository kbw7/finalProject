import streamlit as st
from auth import google_login
from user_profile import render_user_profile
import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import requests
from user_profile import get_user_info
from db_sync import download_db_from_github
from userWalkthrough import newUser
from update_database import checkNewUser
from update_database import init_db
from update_database import getUserFavDiningHall
from notification import check_favorites_available
import ast
from update_database import fetch_user_info


# -- Prof. Eni code start -- #
st.set_page_config(page_title="Wellesley Crave", layout="centered")

DEBUG = False # keep False when testing Google Login


# To access db
download_db_from_github() #initialize the database

# Access Logged-In User Email
access_token = st.session_state.get("access_token")
user = get_user_info(access_token) 


def render_sidebar():
    #URLs for the images used in the sidebar
    blank_square = "https://i.imgur.com/3Th4rvF.png"
    sidebar_image_url = "https://i.imgur.com/oyBooq2.jpeg"
    logo_image_url = "https://i.imgur.com/4vlJszs.png"

    # Adds a centered logo at the top of the page (not sidebar)
    st.markdown(
        f"""
        <style>
        .logo {{
            margin-top: 10px;
            z-index: 1000;
        }}
        </style>
        <div class="logo">
            <img src="{logo_image_url}" alt="Logo" width="600">
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Adds background image to sidebar
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("{sidebar_image_url}");
            background-size: cover;
            background-position: center;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            padding-bottom: 20px;
        }}
        .sidebar-content {{
            text-align: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Adds transparent square to push login section down (it's hard to read against a black background)
    st.sidebar.markdown(
        f"""
        <div class="sidebar-content">
            <img src="{blank_square}" alt="Logo" width="350">

        </div>
        """,
        unsafe_allow_html=True,
    )

    if "access_token" in st.session_state:
        render_user_profile()

        if st.sidebar.button("Logout"):
            for key in ["access_token", "oauth_state"]:
                st.session_state.pop(key, None)
            st.rerun()
    else:
        st.sidebar.warning("Not logged in.")
        st.sidebar.markdown("Please log in with your Google Account using your **Wellesley** Email:")
        logged_in = google_login()
        if logged_in:
            st.rerun()


# This data can also be in a CSV file and then directly loaded from the file
data = [
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

# -- Prof. Eni code end -- #

# Kaurvaki code #
# Functions
def get_menu(date, locationID, mealID):
    base_url = "https://dish.avifoodsystems.com/api/menu-items/week"

    params = {"date" : date, "locationID" : locationID, "mealID" : mealID}

    response = requests.get(base_url, params = params)

    fullUrl = response.url

    data = requests.get(fullUrl).json()

    # New code we are adding
    result = pd.DataFrame(data)

    return result

def transform(cell):
    result = ""
    if cell:
        # result is a string where each allergen in the list in the cell is brought together
        result = ",".join([item["name"] for item in cell])
    return result

def dropKeys(cell):
    cell.pop("id")
    cell.pop("corporateProductId")
    cell.pop("caloriesFromSatFat")
    return cell

def greeting_Menu():
    # Greeting at Top of Page
    # Get current datetime in Eastern Time
    device_datetime = datetime.datetime.now(tz=ZoneInfo("America/New_York"))
    
    hour = device_datetime.hour

    meal = ""

    greeting = ""
    if hour >= 1 and hour <= 10:
        greeting = "Good Morning ☀️"
        meal = "Breakfast"

    elif hour >= 11 and hour <= 16:
        greeting = "Good Afternoon ❤️ "
        meal = "Lunch"

    elif hour >= 17 and hour <= 23:
        greeting = "Good Evening 🌙"
        meal = "Dinner"

    st.title(greeting)

    return meal


def homePage(): # only show once user has walkthrough!
    download_db_from_github() # Kaurvaki - Chose to download again once new user has gone through walkthrough so that the home menu would be the of the dining hall they recently selected.
    
    userMeal = greeting_Menu()

    # ------------------------------------Aileen's code-------------------------------------------------- #
    # Display notification for favorite dish

    available_favs = check_favorites_available(user.get("email"))

    if available_favs:
        st.markdown("### 🔔 Favorite Dishes Available Today!")
        for fav in available_favs:
            dish = fav["dish_name"]
            for loc in fav["locations"]:
                st.success(f"**{dish}** available at {loc['location']} ({loc['meal']}) - {loc['station']}")

    # Kaurvaki's Code
    userDiningHall = getUserFavDiningHall(user)

    # In our user feedback form, we got that using "Bae" was confusing for people since we all call the dining hall "Lulu"
    # since WFresh AVI uses "Bae" I made a separate variable called "diningHall" that would be hold the actual dining hall name according to the API
    # "Bae" while the userDiningHall would remain "Lulu." Then, we can use "Bae" for the back-end but still show "Lulu" on front end
    # All SQL queries will be fed the variable "diningHall" now, NOT "userDiningHall" - Kaurvaki
    if userDiningHall == "Lulu":
        diningHall = "Bae"
    else:
        diningHall = userDiningHall

    # Prof. Eni function get_params()
    location_id, meal_id = get_params(dfKeys,
                                        diningHall,
                                        userMeal)

    d = datetime.date.today()

    df = get_menu(d, location_id, meal_id) # d is date

    st.expander(df)
    
    # We only want today's menu... not the whole week
    # format of date data in df: 2025-04-14T00:00:00
    # Source for strftime - https://www.geeksforgeeks.org/python-strftime-function/

    today = d + "T00:00:00"
    
    df = df[df["date"] == today]  # only today's meals

    # Aileen's Code
    if df.empty:
        st.warning(f"No menu available for {userMeal} at {userDiningHall} today.")
        return  # Exit early so nothing else runs

    # cleaning up df - Kaurvaki - lot of code from own Assignment 5 of CS248
    df = df.drop_duplicates(subset=["id"], keep="first")
    df = df.drop(columns=["date", "image", "id", "categoryName", "stationOrder", "price"], errors="ignore")

    df["allergens"] = df["allergens"].apply(transform) # for the allergens column, it goes through each row and turn them into a string
    df["preferences"] = df["preferences"].apply(transform)
    df["nutritionals"] = df["nutritionals"].apply(dropKeys)

    colNames = df.iloc[0].nutritionals.keys()
    for key in colNames:
        if key == "servingSizeUOM":
            df[key] = df["nutritionals"].apply(lambda dct: str(dct["servingSizeUOM"]))
        else:
            df[key] = df["nutritionals"].apply(lambda dct: float(dct[key]))

    df = df.drop("nutritionals", axis=1)


    # Menu Title and Info.
    st.subheader(userMeal + " Today at " + userDiningHall)

    with st.container(border = True):
        user_record = fetch_user_info(user["email"]) # Aileen's code from food_journal.py
        user_allergens = [] # Aileen's code from food_journal.py
        # user_preferences = [] not enough time to look into dietary restrictions/preferences

        if user_record: # Kaurvaki pulled Aileen's code from food_journal.py
            try:
                # ******ast library and method 
                user_allergens = ast.literal_eval(user_record[3]) if user_record[3] else []
                # user_preferences = ast.literal_eval(user_record[4]) if user_record[4] else []
            except Exception as e:
                st.warning("Could not parse stored user allergies/preferences.")

        apply_custom_filter = st.checkbox("Apply my saved allergy and dietary preferences to filter menu") # Aileen's code from food_journal.py

        # Aileen's Code
        params = {
        "date": d.strftime("%m-%d-%Y"),
        "locationID": location_id,
        "mealID": meal_id
        }

        r = requests.get("https://dish.avifoodsystems.com/api/menu-items", params=params)
        items = r.json()

        if items:
            st.subheader(f"{userMeal} at {userDiningHall}")
            header = st.columns(6)
            header[0].markdown("**Dish**")
            header[1].markdown("**Calories**")
            header[2].markdown("**Protein**")
            header[3].markdown("**Fat**")
            header[4].markdown("**Carbohydrates**")
            header[5].markdown("**Add to Food Journal Log?**")

        if 'selected_dishes' not in st.session_state:
            st.session_state['selected_dishes'] = []

        for i, item in enumerate(items): # Aileen's code from food_journal.py
            name = item.get("name", "")

            # explain a['name']
            allergies = [a['name'] for a in item.get("allergens", [])]

            # preferences = [p['name'] for p in item.get("preferences", [])]
            if apply_custom_filter:
                if any(allergen in user_allergens for allergen in allergies):
                    continue
                # if user_preferences and not any(pref in preferences for pref in user_preferences):
                #     continue

            nutrition = item.get("nutritionals", {})
            nutrition = dropKeys(nutrition) if nutrition else {}
            calories = nutrition.get("calories", 0.0)
            protein = nutrition.get("protein", 0.0)
            carbs = nutrition.get("carbohydrates", 0.0)
            fat = nutrition.get("fat", 0.0)

            row = st.columns(6)  # tighter layout
            row[0].write(name)
            row[1].write(f"{calories} cal")
            row[2].write(f"{protein} g")
            row[3].write(f"{fat} g")
            row[4].write(f"{carbs} g")
            checked = row[5].checkbox("", key=f"add_{userMeal}_{name}_{i}")
            if checked and name not in [x['name'] for x in st.session_state['selected_dishes']]:
                st.session_state['selected_dishes'].append({
                    "name": name,
                    "dining_hall": userDiningHall, # Changed to be userDiningHall because when logging meals in foodJournal.py I want users to see it as "Lulu" not "Bae." More info commented in foodJournal.py in about line 114
                    "meal_type": userMeal,
                    "calories": float(calories),
                    "protein": float(protein),
                    "carbs": float(carbs),
                    "fat": float(fat)
                })


#----------------- HOME Page -----------------#
# Show login

init_db()
print("Database initialized.")

render_sidebar()

if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

# After user logs in, have to call new_user() to see if new user needs walkthrough
if checkNewUser(user.get("email")): # if new user, then go through walkthrough
    result = newUser(user)

    if result:
        homePage()
        
else:
    homePage() # returning user